"""
Roblox Bionic Hand Motion Capture Tracker - Biomechanical Physics & PnP 3D Invariance Edition
- 3D Rigid Palm PnP Pose Estimator (cv2.solvePnP 6-point carpal-metacarpal geometry)
- Invariant Local Palm Reference Frame (zero false-curling under severe tilt/tunduk/miring)
- 22-DOF Kinematic Kalman Filter with constant velocity physics model & dynamic noise covariance
- Robust self-occlusion prediction for edge-on views (sideways yaw)
- Authentic Cybernetic Robotic Hand overlay & HUD telemetry on webcam feed
- Rate-limit safe continuous streaming (Roblox HttpService compliant)
"""

import sys
import time
import math
import json
import threading
import socketserver
from http.server import HTTPServer, BaseHTTPRequestHandler
import numpy as np
import cv2
import mediapipe as mp

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ==============================================================================
# GLOBAL TRACKING STATE
# ==============================================================================
tracking_state = {
    "detected": False,
    "handedness": "Right",
    "confidence": 1.0,
    "wrist": {"pitch": 0.0, "yaw": 0.0, "roll": 0.0},
    "thumb": {
        "cmc_spread": 0.5,
        "cmc_oppose": 0.0,
        "mcp_flex": 0.0,
        "ip_flex": 0.0,
        "spread": 0.5,
        "curl1": 0.0,
        "curl2": 0.0
    },
    "index": {"curl1": 0.0, "curl2": 0.0, "curl3": 0.0, "spread": 0.0},
    "middle": {"curl1": 0.0, "curl2": 0.0, "curl3": 0.0},
    "ring": {"curl1": 0.0, "curl2": 0.0, "curl3": 0.0, "spread": 0.0},
    "pinky": {"curl1": 0.0, "curl2": 0.0, "curl3": 0.0, "spread": 0.0},
    "fps": 0.0,
    "timestamp": 0.0
}

# ==============================================================================
# HTTP SERVER (Roblox Studio Stream)
# ==============================================================================
class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

class HandDataHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/hand" or self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Connection", "close")
            self.end_headers()
            payload = json.dumps(tracking_state)
            self.wfile.write(payload.encode("utf-8"))
        elif self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(404)
            self.send_header("Connection", "close")
            self.end_headers()

    def log_message(self, format, *args):
        pass

def start_http_server(port=8080):
    try:
        server = ThreadedHTTPServer(("127.0.0.1", port), HandDataHandler)
        server.serve_forever()
    except Exception as e:
        print(f"[ERROR] HTTP Server: {e}")

# ==============================================================================
# 22-DOF KINEMATIC KALMAN FILTER
# ==============================================================================
class KalmanJointFilter:
    """
    Second-order linear kinematic Kalman filter tracking:
    State: x = [angle, angular_velocity]^T
    Physics: constant-velocity transition with velocity damping lambda.
    Adaptive covariance: measurement variance R dynamically scales inversely with
    confidence, so during self-occlusion or edge-on views, the filter relies on
    velocity inertia rather than noisy landmark spikes.
    """
    def __init__(self, q_pos=0.005, q_vel=0.07, r_base=0.03, damping=0.92):
        self.x = np.array([0.0, 0.0], dtype=np.float64)
        self.P = np.eye(2, dtype=np.float64) * 0.1
        self.q_pos = q_pos
        self.q_vel = q_vel
        self.r_base = r_base
        self.damping = damping

    def predict(self, dt):
        dt = max(min(dt, 0.1), 0.001)
        F = np.array([
            [1.0, dt],
            [0.0, self.damping]
        ], dtype=np.float64)
        Q = np.array([
            [(dt**3) / 3.0 * self.q_pos, (dt**2) / 2.0 * self.q_pos],
            [(dt**2) / 2.0 * self.q_pos, dt * self.q_vel]
        ], dtype=np.float64)
        self.x = F @ self.x
        self.P = F @ self.P @ F.T + Q
        return float(self.x[0])

    def update(self, z, confidence=1.0):
        confidence = max(min(float(confidence), 1.0), 0.03)
        R = self.r_base / (confidence ** 2)
        H = np.array([[1.0, 0.0]], dtype=np.float64)
        y = z - (H @ self.x)[0]
        S = (H @ self.P @ H.T)[0, 0] + R
        K = (self.P @ H.T).flatten() / S
        self.x = self.x + K * y
        self.P = (np.eye(2) - np.outer(K, H.flatten())) @ self.P
        return float(self.x[0])

    def filter(self, z, dt, confidence=1.0):
        self.predict(dt)
        return self.update(z, confidence)

    def reset(self, val=0.0):
        self.x = np.array([val, 0.0], dtype=np.float64)
        self.P = np.eye(2, dtype=np.float64) * 0.1

# ==============================================================================
# BIOMECHANICAL GEOMETRY & PNP SOLVER
# ==============================================================================
def angle_between_vectors(v1, v2):
    n1 = np.linalg.norm(v1)
    n2 = np.linalg.norm(v2)
    if n1 < 1e-6 or n2 < 1e-6:
        return 0.0
    cos_val = np.clip(np.dot(v1, v2) / (n1 * n2), -1.0, 1.0)
    return float(np.arccos(cos_val))

def solve_rigid_palm_pnp(pts_2d, w, h, handedness="Right"):
    """
    Solves Perspective-n-Point for 6 rigid carpal-metacarpal palm landmarks:
    - 0: Wrist
    - 1: Thumb CMC base
    - 5: Index MCP
    - 9: Middle MCP
    - 13: Ring MCP
    - 17: Pinky MCP
    Returns camera-space rotation matrix R_pnp and translation vector tvec.
    """
    sign_x = 1.0 if handedness == "Right" else -1.0
    obj_pts = np.array([
        [0.0, 0.0, 0.0],
        [-20.0 * sign_x, 25.0, -8.0],
        [-28.0 * sign_x, 85.0, 0.0],
        [0.0, 95.0, 0.0],
        [26.0 * sign_x, 88.0, 0.0],
        [48.0 * sign_x, 78.0, 0.0]
    ], dtype=np.float32)

    indices = [0, 1, 5, 9, 13, 17]
    img_pts = np.array([pts_2d[i][:2] for i in indices], dtype=np.float32)

    focal_length = float(w)
    cam_matrix = np.array([
        [focal_length, 0.0, w / 2.0],
        [0.0, focal_length, h / 2.0],
        [0.0, 0.0, 1.0]
    ], dtype=np.float32)
    dist_coeffs = np.zeros((4, 1), dtype=np.float32)

    try:
        success, rvec, tvec = cv2.solvePnP(obj_pts, img_pts, cam_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE)
        if success:
            R, _ = cv2.Rodrigues(rvec)
            return R, tvec, True
    except Exception:
        pass
    return np.eye(3), np.zeros((3, 1)), False

def compute_orthonormal_palm_frame(w_pts):
    """
    Builds a robust orthonormal 3D reference frame for the palm:
    - Origin: Wrist (0)
    - u_distal (+Y): Distal axis pointing along middle metacarpal (0 -> 9)
    - u_across (+X): Lateral axis across knuckles (5 -> 17) orthogonalized to u_distal
    - u_normal (+Z): Dorsal-palmar normal vector perpendicular to palm plane
    """
    w_wrist = w_pts[0]
    w_mid = w_pts[9]
    w_idx = w_pts[5]
    w_pnk = w_pts[17]

    v_distal = w_mid - w_wrist
    norm_distal = np.linalg.norm(v_distal) + 1e-6
    u_distal = v_distal / norm_distal

    v_across_raw = w_pnk - w_idx
    v_across = v_across_raw - np.dot(v_across_raw, u_distal) * u_distal
    norm_across = np.linalg.norm(v_across) + 1e-6
    u_across = v_across / norm_across

    u_normal = np.cross(u_across, u_distal)
    norm_normal = np.linalg.norm(u_normal) + 1e-6
    u_normal /= norm_normal

    u_across = np.cross(u_distal, u_normal)
    u_across /= (np.linalg.norm(u_across) + 1e-6)

    R_palm = np.column_stack([u_across, u_distal, u_normal])
    return R_palm, w_wrist, u_distal, u_across, u_normal

def compute_invariant_finger_curls(w_pts, R_palm, w_wrist):
    """
    Calculates 3D finger flexion angles directly inside the palm's local reference frame:
    local_pt = R_palm^T * (world_pt - w_wrist)
    
    Because all vectors are expressed in the palm's coordinate system, global tilt,
    pitch, roll, and yaw are mathematically canceled out.
    When the hand tilts forward/downward toward the floor, straight fingers STAY straight (c=0)!
    When clenched, the curls respond with true physical fidelity.
    """
    def to_local(pt):
        return R_palm.T @ (pt - w_wrist)

    fingers_data = {}
    finger_defs = [
        ("index", 5, 6, 7, 8, -0.06),
        ("middle", 9, 10, 11, 12, 0.0),
        ("ring", 13, 14, 15, 16, 0.06),
        ("pinky", 17, 18, 19, 20, 0.14),
    ]

    for fname, mcp_i, pip_i, dip_i, tip_i, rest_sp in finger_defs:
        l_mcp = to_local(w_pts[mcp_i])
        l_pip = to_local(w_pts[pip_i])
        l_dip = to_local(w_pts[dip_i])
        l_tip = to_local(w_pts[tip_i])

        b1 = l_pip - l_mcp
        b2 = l_dip - l_pip
        b3 = l_tip - l_dip

        # 1. MCP Flexion (curl1): Sagittal bending into palmar side (-Z)
        # When straight: b1 aligns with +Y (curl1 = 0)
        # When bent into palm: -b1[2] > 0, angle increases up to 1.35 rad (~77 deg)
        c1 = float(np.clip(math.atan2(-b1[2], max(b1[1], 0.005)), 0.0, 1.35))

        # 2. PIP Flexion (curl2): True 3D joint angle between proximal and intermediate bones
        nb1 = b1 / (np.linalg.norm(b1) + 1e-6)
        nb2 = b2 / (np.linalg.norm(b2) + 1e-6)
        c2 = float(np.clip(math.acos(np.clip(np.dot(nb1, nb2), -1.0, 1.0)), 0.0, 1.45))

        # 3. DIP Flexion (curl3): True 3D joint angle between intermediate and distal bones
        nb3 = b3 / (np.linalg.norm(b3) + 1e-6)
        c3 = float(np.clip(math.acos(np.clip(np.dot(nb2, nb3), -1.0, 1.0)), 0.0, 1.15))

        # 4. Finger Spread: Lateral angle in X-Y plane relative to resting spread
        raw_spread = math.atan2(b1[0], max(b1[1], 0.01))
        sp = float(np.clip(raw_spread - rest_sp, -0.35, 0.45))

        fingers_data[fname] = {"curl1": c1, "curl2": c2, "curl3": c3, "spread": sp}

    # Anatomical Decoupled Thumb Biomechanics
    l_cmc = to_local(w_pts[1])
    l_thb_mcp = to_local(w_pts[2])
    l_thb_ip = to_local(w_pts[3])
    l_thb_tip = to_local(w_pts[4])

    v_mc = l_thb_mcp - l_cmc
    v_pp = l_thb_ip - l_thb_mcp
    v_dp = l_thb_tip - l_thb_ip
    dir_mc = v_mc / (np.linalg.norm(v_mc) + 1e-6)

    # CMC Spread (Abduction) in lateral plane
    spread_angle = math.atan2(abs(dir_mc[0]), max(dir_mc[1], 0.05))
    thb_spread = float(np.clip((spread_angle - 0.20) / (0.85 - 0.20), 0.0, 1.2))

    # CMC Opposition into palmar hemisphere
    thb_oppose = float(np.clip((-dir_mc[2] + 0.08) / 0.45, 0.0, 1.0))

    # MCP Flexion
    ang_mcp = angle_between_vectors(v_mc, v_pp)
    thb_mcp = float(np.clip((ang_mcp - 0.10) / (0.95 - 0.10), 0.0, 1.0))

    # IP Flexion
    ang_ip = angle_between_vectors(v_pp, v_dp)
    thb_ip = float(np.clip((ang_ip - 0.10) / (1.30 - 0.10), 0.0, 1.0))

    fingers_data["thumb"] = {
        "cmc_spread": thb_spread,
        "cmc_oppose": thb_oppose,
        "mcp_flex": thb_mcp,
        "ip_flex": thb_ip,
        "spread": thb_spread,
        "curl1": thb_mcp,
        "curl2": thb_ip
    }

    return fingers_data

# ==============================================================================
# VISUAL RENDERING: ROBLOX ROBOTIC HAND OVERLAY
# ==============================================================================
def draw_robotic_hand_overlay(frame, pts, state):
    """
    Renders an authentic cybernetic replica of the Roblox Robotic Hand directly
    over the detected hand in the webcam video!
    - Dark graphite/carbon armor segments
    - Luminous cyan neon strips (#00e6ff)
    - Chrome knuckle spheres
    - Neon palm reactor core
    - Futuristic cyber optics
    """
    h, w, _ = frame.shape
    overlay = frame.copy()

    # Roblox Color Palette (BGR)
    COLOR_ARMOR = (28, 32, 40)         # Charcoal matte armor (#1c2028)
    COLOR_ARMOR_BORDER = (75, 85, 100) # Metallic chrome border (#4b5564)
    COLOR_NEON_CYAN = (255, 230, 0)    # Luminous cyan neon (#00e6ff)
    COLOR_NEON_GLOW = (210, 160, 0)    # Soft cyan glow (#00a0d2)
    COLOR_KNUCKLE = (195, 205, 215)    # Polished chrome joint (#c3cdd7)
    COLOR_WHITE_HOT = (255, 255, 255)  # White core highlight

    # 1. PALM CHASSIS (Anatomical Hexagonal Armor Plate)
    palm_indices = [0, 1, 2, 5, 9, 13, 17]
    palm_poly = np.array([pts[i][:2] for i in palm_indices], dtype=np.int32)
    cv2.fillPoly(overlay, [palm_poly], COLOR_ARMOR)
    cv2.polylines(overlay, [palm_poly], isClosed=True, color=COLOR_ARMOR_BORDER, thickness=2)

    # Central Neon Reactor Core (PalmBackNeon)
    center_pt = ((pts[0][:2] + pts[5][:2] + pts[17][:2] + pts[9][:2]) / 4).astype(int)
    palm_span = np.linalg.norm(pts[5][:2] - pts[17][:2])
    core_sz = int(max(palm_span * 0.16, 7))

    cv2.rectangle(overlay,
                  (center_pt[0] - core_sz, center_pt[1] - core_sz),
                  (center_pt[0] + core_sz, center_pt[1] + core_sz),
                  COLOR_NEON_GLOW, -1)
    cv2.rectangle(overlay,
                  (center_pt[0] - core_sz + 2, center_pt[1] - core_sz + 2),
                  (center_pt[0] + core_sz - 2, center_pt[1] + core_sz - 2),
                  COLOR_NEON_CYAN, -1)
    cv2.circle(overlay, (center_pt[0], center_pt[1]), max(core_sz // 3, 2), COLOR_WHITE_HOT, -1)

    # Wrist Ring & Actuator Joint (landmark 0)
    wrist_pt = tuple(pts[0][:2].astype(int))
    wrist_r = int(max(palm_span * 0.22, 9))
    cv2.circle(overlay, wrist_pt, wrist_r, COLOR_ARMOR_BORDER, 2)
    cv2.circle(overlay, wrist_pt, wrist_r - 2, COLOR_KNUCKLE, -1)
    cv2.ellipse(overlay, wrist_pt, (wrist_r + 5, max(wrist_r // 3, 3)), 0, 0, 360, COLOR_NEON_CYAN, 2)

    # Blend palm chassis
    cv2.addWeighted(overlay, 0.82, frame, 0.18, 0, frame)

    # 2. FINGER SEGMENTS (Thick Armor Plates + Cyan Neon Light Strips)
    fingers = [
        ("Thumb", [1, 2, 3, 4], [16, 14, 12]),
        ("Index", [5, 6, 7, 8], [14, 12, 10]),
        ("Middle", [9, 10, 11, 12], [15, 13, 11]),
        ("Ring", [13, 14, 15, 16], [14, 12, 10]),
        ("Pinky", [17, 18, 19, 20], [12, 10, 8]),
    ]

    for fname, indices, thicks in fingers:
        for seg in range(len(indices) - 1):
            p1 = pts[indices[seg]][:2]
            p2 = pts[indices[seg + 1]][:2]
            t = thicks[seg]

            v = p2 - p1
            dist = np.linalg.norm(v) + 1e-6
            dir_v = v / dist
            perp = np.array([-dir_v[1], dir_v[0]])

            # Armor Segment Polygon
            poly = np.array([
                p1 + perp * (t * 0.52),
                p2 + perp * (t * 0.40),
                p2 - perp * (t * 0.40),
                p1 - perp * (t * 0.52),
            ], dtype=np.int32)

            # Draw cyber armor
            cv2.fillPoly(frame, [poly], COLOR_ARMOR)
            cv2.polylines(frame, [poly], isClosed=True, color=COLOR_ARMOR_BORDER, thickness=1)

            # Cyan Neon Light Strip (triple-layered for neon bloom)
            pt1 = (int(p1[0]), int(p1[1]))
            pt2 = (int(p2[0]), int(p2[1]))
            cv2.line(frame, pt1, pt2, COLOR_NEON_GLOW, max(t // 3 + 2, 4))
            cv2.line(frame, pt1, pt2, COLOR_NEON_CYAN, max(t // 4, 2))
            cv2.line(frame, pt1, pt2, COLOR_WHITE_HOT, 1)

    # 3. KNUCKLE ACTUATOR SPHERES (Chrome with Cyan Centers)
    knuckles = [1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15, 17, 18, 19]
    for idx in knuckles:
        k_pt = tuple(pts[idx][:2].astype(int))
        cv2.circle(frame, k_pt, 6, COLOR_ARMOR, -1)
        cv2.circle(frame, k_pt, 5, COLOR_KNUCKLE, -1)
        cv2.circle(frame, k_pt, 2, COLOR_NEON_CYAN, -1)

    # 4. SENSOR TIPS & OPTIC LENSES
    tips = [4, 8, 12, 16, 20]
    for idx in tips:
        t_pt = tuple(pts[idx][:2].astype(int))
        cv2.circle(frame, t_pt, 8, COLOR_ARMOR, -1)
        cv2.circle(frame, t_pt, 7, COLOR_ARMOR_BORDER, 1)
        cv2.circle(frame, t_pt, 4, COLOR_NEON_CYAN, -1)
        cv2.circle(frame, t_pt, 2, COLOR_WHITE_HOT, -1)

# ==============================================================================
# CYBER HUD TELEMETRY DISPLAY
# ==============================================================================
def draw_cyber_hud(frame, state):
    """Futuristic HUD showing 3D biomechanical telemetry, confidence, and wrist angles."""
    h, w, _ = frame.shape

    # HUD Background Box
    hud_bg = frame.copy()
    cv2.rectangle(hud_bg, (12, 12), (245, 225), (15, 18, 24), -1)
    cv2.rectangle(hud_bg, (12, 12), (245, 225), (0, 200, 255), 1)
    cv2.addWeighted(hud_bg, 0.75, frame, 0.25, 0, frame)

    detected = state["detected"]
    status_text = "BIO-PHYSICS // PNP ACTIVE" if detected else "BIO-PHYSICS // SEARCHING"
    status_color = (0, 255, 100) if detected else (0, 165, 255)
    cv2.putText(frame, status_text, (20, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.42, status_color, 1)

    conf_pct = int(state.get("confidence", 1.0) * 100)
    cv2.putText(frame, f"FPS: {state['fps']:.1f} | CONF: {conf_pct}%", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (200, 200, 200), 1)

    if detected:
        bars = [
            ("Thumb", state["thumb"]["mcp_flex"]),
            ("Index", state["index"]["curl1"] / 1.35),
            ("Middle", state["middle"]["curl1"] / 1.35),
            ("Ring", state["ring"]["curl1"] / 1.35),
            ("Pinky", state["pinky"]["curl1"] / 1.35),
        ]

        y_start = 72
        for name, val in bars:
            norm_val = float(np.clip(val, 0.0, 1.0))
            cv2.putText(frame, name, (20, y_start), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (220, 220, 220), 1)
            cv2.rectangle(frame, (80, y_start - 8), (225, y_start), (40, 45, 55), -1)
            bar_w = int(145 * norm_val)
            bar_col = (255, 230, 0) if norm_val < 0.75 else (0, 140, 255)
            cv2.rectangle(frame, (80, y_start - 8), (80 + bar_w, y_start), bar_col, -1)
            y_start += 18

        w_pitch = state["wrist"]["pitch"]
        w_yaw = state["wrist"]["yaw"]
        w_roll = state["wrist"]["roll"]
        cv2.putText(frame, f"W: P:{w_pitch:+.2f} Y:{w_yaw:+.2f} R:{w_roll:+.2f}", (20, 195), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 230, 255), 1)

        # Tilt angle telemetry
        tilt_deg = int(math.degrees(w_pitch))
        cv2.putText(frame, f"TILT: {tilt_deg:+d} deg [TUNDUK INVARIANT]", (20, 214), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (100, 255, 200), 1)

    cv2.putText(frame, "Press 'q' to exit", (15, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (160, 160, 160), 1)

# ==============================================================================
# MAIN TRACKING PIPELINE
# ==============================================================================
def run_tracker():
    t = threading.Thread(target=start_http_server, args=(8080,), daemon=True)
    t.start()
    print("[OK] Motion Capture Server listening on http://127.0.0.1:8080/hand")

    mp_hands = mp.solutions.hands

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        cap = cv2.VideoCapture(1)
        if not cap.isOpened():
            print("[FATAL] No webcam available!")
            return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)

    print("==================================================================")
    print("[+] ROBLOX BIONIC HAND TRACKER - BIOMECHANICAL PHYSICS & PNP ENGINE")
    print(" - Solusi 100% Invarian terhadap Tangan Tunduk & Miring (No False Curl)")
    print(" - Estimator PnP 3D Rigid Carpal-Metacarpal (cv2.solvePnP)")
    print(" - 22-DOF Kinematic Kalman Filter dengan prediksi inersia kecepatan")
    print(" - Wujud Tangan Robot Roblox & Cyber HUD Telemetri Real-Time")
    print(" Tekan 'q' pada jendela video untuk keluar.")
    print("==================================================================\n")

    # Initialize 22-DOF Kalman Filter Array
    kf = {
        "pitch": KalmanJointFilter(q_pos=0.005, q_vel=0.08, r_base=0.03),
        "yaw": KalmanJointFilter(q_pos=0.005, q_vel=0.08, r_base=0.03),
        "roll": KalmanJointFilter(q_pos=0.005, q_vel=0.08, r_base=0.03),

        "thb_spread": KalmanJointFilter(q_pos=0.006, q_vel=0.08, r_base=0.04),
        "thb_oppose": KalmanJointFilter(q_pos=0.006, q_vel=0.08, r_base=0.04),
        "thb_mcp": KalmanJointFilter(q_pos=0.006, q_vel=0.08, r_base=0.04),
        "thb_ip": KalmanJointFilter(q_pos=0.006, q_vel=0.08, r_base=0.04),

        "idx_c1": KalmanJointFilter(q_pos=0.006, q_vel=0.08, r_base=0.03),
        "idx_c2": KalmanJointFilter(q_pos=0.006, q_vel=0.08, r_base=0.03),
        "idx_c3": KalmanJointFilter(q_pos=0.006, q_vel=0.08, r_base=0.03),
        "idx_sp": KalmanJointFilter(q_pos=0.004, q_vel=0.05, r_base=0.04),

        "mid_c1": KalmanJointFilter(q_pos=0.006, q_vel=0.08, r_base=0.03),
        "mid_c2": KalmanJointFilter(q_pos=0.006, q_vel=0.08, r_base=0.03),
        "mid_c3": KalmanJointFilter(q_pos=0.006, q_vel=0.08, r_base=0.03),

        "rng_c1": KalmanJointFilter(q_pos=0.006, q_vel=0.08, r_base=0.03),
        "rng_c2": KalmanJointFilter(q_pos=0.006, q_vel=0.08, r_base=0.03),
        "rng_c3": KalmanJointFilter(q_pos=0.006, q_vel=0.08, r_base=0.03),
        "rng_sp": KalmanJointFilter(q_pos=0.004, q_vel=0.05, r_base=0.04),

        "pnk_c1": KalmanJointFilter(q_pos=0.006, q_vel=0.08, r_base=0.03),
        "pnk_c2": KalmanJointFilter(q_pos=0.006, q_vel=0.08, r_base=0.03),
        "pnk_c3": KalmanJointFilter(q_pos=0.006, q_vel=0.08, r_base=0.03),
        "pnk_sp": KalmanJointFilter(q_pos=0.004, q_vel=0.05, r_base=0.04),
    }

    prev_time = time.time()
    last_frame_time = time.time()
    fps_count = 0
    fps = 0.0

    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.70,
        min_tracking_confidence=0.70
    ) as hands:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                time.sleep(0.01)
                continue

            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            now = time.time()
            dt = max(min(now - last_frame_time, 0.1), 0.001)
            last_frame_time = now

            fps_count += 1
            if now - prev_time >= 1.0:
                fps = fps_count / (now - prev_time)
                fps_count = 0
                prev_time = now

            if results.multi_hand_landmarks:
                lms = results.multi_hand_landmarks[0]
                pts = [np.array([lm.x * w, lm.y * h, lm.z * w]) for lm in lms.landmark]

                handedness = "Right"
                if results.multi_handedness:
                    handedness = results.multi_handedness[0].classification[0].label

                if hasattr(results, "multi_hand_world_landmarks") and results.multi_hand_world_landmarks:
                    w_pts = [np.array([lm.x, lm.y, lm.z]) for lm in results.multi_hand_world_landmarks[0].landmark]
                else:
                    w_pts = pts

                # 1. 3D RIGID PALM PNP & ORTHONORMAL BASIS
                R_pnp, tvec, pnp_ok = solve_rigid_palm_pnp(pts, w, h, handedness)
                R_palm, w_wrist, u_distal, u_across, u_normal = compute_orthonormal_palm_frame(w_pts)

                # Palm Normal Cosine with camera optical axis [0, 0, 1]
                # High when facing camera; low when edge-on (sideways occlusion)
                palm_normal_cam = R_pnp[:, 2] if pnp_ok else u_normal
                cos_view = abs(palm_normal_cam[2])
                confidence = float(np.clip((cos_view - 0.15) / (0.75 - 0.15), 0.15, 1.0))

                # 2. WRIST ORIENTATION (Pitch, Yaw, Roll)
                wrist = pts[0]
                mcp_mid = pts[9]
                mcp_idx = pts[5]
                mcp_pnk = pts[17]

                v_up = mcp_mid - wrist
                norm_up = np.linalg.norm(v_up) + 1e-6
                dir_up = v_up / norm_up

                v_across = mcp_pnk - mcp_idx
                norm_across = np.linalg.norm(v_across) + 1e-6
                dir_across = v_across / norm_across

                dir_normal = np.cross(dir_up, dir_across)
                dir_normal /= (np.linalg.norm(dir_normal) + 1e-6)

                raw_roll = float(math.atan2(dir_up[0], -dir_up[1]))
                raw_pitch = float(math.asin(np.clip(-dir_up[2], -1.0, 1.0)))
                raw_yaw = float(math.atan2(dir_across[2], dir_normal[2]))

                filt_pitch = kf["pitch"].filter(np.clip(raw_pitch, -1.45, 1.45), dt, confidence)
                filt_yaw = kf["yaw"].filter(np.clip(raw_yaw, -1.25, 1.25), dt, confidence)
                filt_roll = kf["roll"].filter(np.clip(raw_roll, -1.45, 1.45), dt, confidence)

                # 3. 100% INVARIANT 3D LOCAL FINGER CURLS & SPREAD
                raw_curls = compute_invariant_finger_curls(w_pts, R_palm, w_wrist)

                idx_c1 = kf["idx_c1"].filter(raw_curls["index"]["curl1"], dt, confidence)
                idx_c2 = kf["idx_c2"].filter(raw_curls["index"]["curl2"], dt, confidence)
                idx_c3 = kf["idx_c3"].filter(raw_curls["index"]["curl3"], dt, confidence)
                idx_sp = kf["idx_sp"].filter(raw_curls["index"]["spread"], dt, confidence)

                mid_c1 = kf["mid_c1"].filter(raw_curls["middle"]["curl1"], dt, confidence)
                mid_c2 = kf["mid_c2"].filter(raw_curls["middle"]["curl2"], dt, confidence)
                mid_c3 = kf["mid_c3"].filter(raw_curls["middle"]["curl3"], dt, confidence)

                rng_c1 = kf["rng_c1"].filter(raw_curls["ring"]["curl1"], dt, confidence)
                rng_c2 = kf["rng_c2"].filter(raw_curls["ring"]["curl2"], dt, confidence)
                rng_c3 = kf["rng_c3"].filter(raw_curls["ring"]["curl3"], dt, confidence)
                rng_sp = kf["rng_sp"].filter(raw_curls["ring"]["spread"], dt, confidence)

                pnk_c1 = kf["pnk_c1"].filter(raw_curls["pinky"]["curl1"], dt, confidence)
                pnk_c2 = kf["pnk_c2"].filter(raw_curls["pinky"]["curl2"], dt, confidence)
                pnk_c3 = kf["pnk_c3"].filter(raw_curls["pinky"]["curl3"], dt, confidence)
                pnk_sp = kf["pnk_sp"].filter(raw_curls["pinky"]["spread"], dt, confidence)

                thb_sp = kf["thb_spread"].filter(raw_curls["thumb"]["cmc_spread"], dt, confidence)
                thb_op = kf["thb_oppose"].filter(raw_curls["thumb"]["cmc_oppose"], dt, confidence)
                thb_mc = kf["thb_mcp"].filter(raw_curls["thumb"]["mcp_flex"], dt, confidence)
                thb_ip = kf["thb_ip"].filter(raw_curls["thumb"]["ip_flex"], dt, confidence)

                # Update Global State
                tracking_state["detected"] = True
                tracking_state["handedness"] = handedness
                tracking_state["confidence"] = round(confidence, 2)
                tracking_state["wrist"] = {
                    "pitch": round(filt_pitch, 3),
                    "yaw": round(filt_yaw, 3),
                    "roll": round(filt_roll, 3)
                }
                tracking_state["thumb"] = {
                    "cmc_spread": round(thb_sp, 3),
                    "cmc_oppose": round(thb_op, 3),
                    "mcp_flex": round(thb_mc, 3),
                    "ip_flex": round(thb_ip, 3),
                    "spread": round(thb_sp, 3),
                    "curl1": round(thb_mc, 3),
                    "curl2": round(thb_ip, 3)
                }
                tracking_state["index"] = {
                    "curl1": round(idx_c1, 3),
                    "curl2": round(idx_c2, 3),
                    "curl3": round(idx_c3, 3),
                    "spread": round(idx_sp, 3)
                }
                tracking_state["middle"] = {
                    "curl1": round(mid_c1, 3),
                    "curl2": round(mid_c2, 3),
                    "curl3": round(mid_c3, 3)
                }
                tracking_state["ring"] = {
                    "curl1": round(rng_c1, 3),
                    "curl2": round(rng_c2, 3),
                    "curl3": round(rng_c3, 3),
                    "spread": round(rng_sp, 3)
                }
                tracking_state["pinky"] = {
                    "curl1": round(pnk_c1, 3),
                    "curl2": round(pnk_c2, 3),
                    "curl3": round(pnk_c3, 3),
                    "spread": round(pnk_sp, 3)
                }
                tracking_state["fps"] = round(fps, 1)
                tracking_state["timestamp"] = time.time()

                # DRAW ROBLOX ROBOTIC HAND REPLICA OVERLAY
                draw_robotic_hand_overlay(frame, pts, tracking_state)
            else:
                tracking_state["detected"] = False
                tracking_state["confidence"] = 0.0
                tracking_state["fps"] = round(fps, 1)

            # Draw Cyber HUD Telemetry
            draw_cyber_hud(frame, tracking_state)

            cv2.imshow("Roblox Robotic Hand Tracker", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] Tracker closed.")

if __name__ == "__main__":
    run_tracker()
