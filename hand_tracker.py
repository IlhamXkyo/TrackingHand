"""
Roblox Bionic Hand Motion Capture Tracker - Cybernetic Roblox Replica HUD Edition
- Direct visual replica of Roblox Robotic Hand rendered on camera feed!
- Dark armor plates, luminous cyan neon light strips, chrome knuckle actuators
- Cybernetic HUD telemetry with real-time finger curl & wrist bars
- Human thumb biomechanics (CMC saddle, MCP, IP) with orthonormal 3D frame
- Rate-limit safe continuous streaming (Roblox HttpService compliant)
"""

import sys
import time
import math
import json
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

tracking_state = {
    "detected": False,
    "handedness": "Right",
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
        print(f"[ERROR] Server: {e}")

def angle_between_vectors(v1, v2):
    n1 = np.linalg.norm(v1)
    n2 = np.linalg.norm(v2)
    if n1 < 1e-6 or n2 < 1e-6:
        return 0.0
    cos_val = np.clip(np.dot(v1, v2) / (n1 * n2), -1.0, 1.0)
    return float(np.arccos(cos_val))

def draw_robotic_hand_overlay(frame, pts, state):
    """
    Renders an authentic, cybernetic replica of the Roblox Robotic Hand directly
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

    # 1. PALM CHASSIS (Hexagonal/Anatomical Plate)
    palm_indices = [0, 1, 2, 5, 9, 13, 17]
    palm_poly = np.array([pts[i][:2] for i in palm_indices], dtype=np.int32)
    
    cv2.fillPoly(overlay, [palm_poly], COLOR_ARMOR)
    cv2.polylines(overlay, [palm_poly], isClosed=True, color=COLOR_ARMOR_BORDER, thickness=2)

    # Central Neon Reactor Core (Square like PalmBackNeon in Roblox)
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

    # Wrist Ball & Ring at base (landmark 0)
    wrist_pt = tuple(pts[0][:2].astype(int))
    wrist_r = int(max(palm_span * 0.22, 9))
    cv2.circle(overlay, wrist_pt, wrist_r, COLOR_ARMOR_BORDER, 2)
    cv2.circle(overlay, wrist_pt, wrist_r - 2, COLOR_KNUCKLE, -1)
    cv2.ellipse(overlay, wrist_pt, (wrist_r + 5, max(wrist_r // 3, 3)), 0, 0, 360, COLOR_NEON_CYAN, 2)

    # Blend palm chassis onto main frame
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

def draw_cyber_hud(frame, state):
    """Futuristic Sci-Fi HUD showing telemetry, angles, and connection status."""
    h, w, _ = frame.shape
    
    # HUD Background Box
    hud_bg = frame.copy()
    cv2.rectangle(hud_bg, (12, 12), (230, 210), (15, 18, 24), -1)
    cv2.rectangle(hud_bg, (12, 12), (230, 210), (0, 200, 255), 1)
    cv2.addWeighted(hud_bg, 0.75, frame, 0.25, 0, frame)

    # Header
    detected = state["detected"]
    status_text = "BIONIC RIG // LINK ACTIVE" if detected else "BIONIC RIG // SEARCHING"
    status_color = (0, 255, 100) if detected else (0, 165, 255)
    cv2.putText(frame, status_text, (20, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.45, status_color, 1)
    cv2.putText(frame, f"FPS: {state['fps']:.1f} | 60Hz Lerp Sync", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (200, 200, 200), 1)

    if detected:
        # Telemetry Bars
        bars = [
            ("Thumb", state["thumb"]["mcp_flex"]),
            ("Index", state["index"]["curl1"] / 1.35),
            ("Middle", state["middle"]["curl1"] / 1.35),
            ("Ring", state["ring"]["curl1"] / 1.35),
            ("Pinky", state["pinky"]["curl1"] / 1.35),
        ]
        
        y_start = 72
        for name, val in bars:
            norm_val = np.clip(val, 0.0, 1.0)
            cv2.putText(frame, name, (20, y_start), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (220, 220, 220), 1)
            # Bar background
            cv2.rectangle(frame, (80, y_start - 8), (215, y_start), (40, 45, 55), -1)
            # Filled bar
            bar_w = int(135 * norm_val)
            bar_col = (255, 230, 0) if norm_val < 0.75 else (0, 140, 255)
            cv2.rectangle(frame, (80, y_start - 8), (80 + bar_w, y_start), bar_col, -1)
            y_start += 18

        # Wrist Euler Angles
        w_pitch = state["wrist"]["pitch"]
        w_yaw = state["wrist"]["yaw"]
        w_roll = state["wrist"]["roll"]
        cv2.putText(frame, f"W: P:{w_pitch:+.2f} Y:{w_yaw:+.2f} R:{w_roll:+.2f}", (20, 195), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 230, 255), 1)

    cv2.putText(frame, "Press 'q' to exit", (15, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (160, 160, 160), 1)

def run_tracker():
    import threading
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

    print("\n==================================================================")
    print("[+] ROBLOX BIONIC HAND TRACKER - ROBOTIC REPLICA HUD EDITION")
    print(" - Visualisasi kerangka kini diganti wujud Tangan Robot Roblox!")
    print(" - Lapis baja karbon, lampu neon cyan, aktuator engsel krom")
    print(" - Telemetri HUD cybernetic real-time")
    print(" Tekan 'q' pada jendela video untuk keluar.")
    print("==================================================================\n")

    f = {
        "pitch": 0.0, "yaw": 0.0, "roll": 0.0,
        "thb_spread": 0.5, "thb_oppose": 0.0, "thb_mcp": 0.0, "thb_ip": 0.0,
        "idx_c1": 0.0, "idx_c2": 0.0, "idx_c3": 0.0, "idx_sp": 0.0,
        "mid_c1": 0.0, "mid_c2": 0.0, "mid_c3": 0.0,
        "rng_c1": 0.0, "rng_c2": 0.0, "rng_c3": 0.0, "rng_sp": 0.0,
        "pnk_c1": 0.0, "pnk_c2": 0.0, "pnk_c3": 0.0, "pnk_sp": 0.0,
    }

    def ema(prev, cur, alpha=0.35):
        return prev + alpha * (cur - prev)

    prev_time = time.time()
    fps_count = 0
    fps = 0.0

    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.75,
        min_tracking_confidence=0.75
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
            fps_count += 1
            if now - prev_time >= 1.0:
                fps = fps_count / (now - prev_time)
                fps_count = 0
                prev_time = now

            if results.multi_hand_landmarks:
                lms = results.multi_hand_landmarks[0]
                pts = [np.array([lm.x * w, lm.y * h, lm.z * w]) for lm in lms.landmark]

                if hasattr(results, "multi_hand_world_landmarks") and results.multi_hand_world_landmarks:
                    w_pts = [np.array([lm.x, lm.y, lm.z]) for lm in results.multi_hand_world_landmarks[0].landmark]
                else:
                    w_pts = pts

                # --- 1. WRIST ORIENTATION ---
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

                f["pitch"] = ema(f["pitch"], np.clip(raw_pitch, -1.45, 1.45))
                f["yaw"] = ema(f["yaw"], np.clip(raw_yaw, -1.25, 1.25))
                f["roll"] = ema(f["roll"], np.clip(raw_roll, -1.45, 1.45))

                # --- 2. FOUR FINGERS CURLS & SPREAD ---
                def calc_curl(mcp_i, pip_i, dip_i, tip_i):
                    bone_len = (np.linalg.norm(pts[pip_i] - pts[mcp_i]) +
                                np.linalg.norm(pts[dip_i] - pts[pip_i]) +
                                np.linalg.norm(pts[tip_i] - pts[dip_i])) + 1e-6
                    tip_dist = np.linalg.norm(pts[tip_i] - pts[mcp_i])
                    extension = tip_dist / bone_len
                    curl_ratio = float(np.clip((0.92 - extension) / (0.92 - 0.38), 0.0, 1.0))
                    c1 = curl_ratio * 1.35
                    c2 = curl_ratio * 1.45
                    c3 = curl_ratio * 1.15
                    return c1, c2, c3

                idx_c1, idx_c2, idx_c3 = calc_curl(5, 6, 7, 8)
                mid_c1, mid_c2, mid_c3 = calc_curl(9, 10, 11, 12)
                rng_c1, rng_c2, rng_c3 = calc_curl(13, 14, 15, 16)
                pnk_c1, pnk_c2, pnk_c3 = calc_curl(17, 18, 19, 20)

                v_mid_f = pts[12] - pts[9]
                v_idx_f = pts[8] - pts[5]
                v_rng_f = pts[16] - pts[13]
                v_pnk_f = pts[20] - pts[17]

                ang_mid = math.atan2(v_mid_f[0], -v_mid_f[1])
                ang_idx = math.atan2(v_idx_f[0], -v_idx_f[1])
                ang_rng = math.atan2(v_rng_f[0], -v_rng_f[1])
                ang_pnk = math.atan2(v_pnk_f[0], -v_pnk_f[1])

                raw_idx_sp = float(np.clip(ang_idx - ang_mid, -0.6, 0.2))
                raw_rng_sp = float(np.clip(ang_rng - ang_mid, -0.2, 0.5))
                raw_pnk_sp = float(np.clip(ang_pnk - ang_mid, -0.2, 0.7))

                # --- 3. TRUE ANATOMICAL THUMB BIOMECHANICS ---
                w_wrist = w_pts[0]
                w_mid_mcp = w_pts[9]
                w_idx_mcp = w_pts[5]
                w_pnk_mcp = w_pts[17]

                w_up = (w_mid_mcp - w_wrist) / (np.linalg.norm(w_mid_mcp - w_wrist) + 1e-6)
                w_across_raw = w_pnk_mcp - w_idx_mcp
                w_across = w_across_raw - np.dot(w_across_raw, w_up) * w_up
                w_across /= (np.linalg.norm(w_across) + 1e-6)
                w_normal = np.cross(w_up, w_across)
                w_normal /= (np.linalg.norm(w_normal) + 1e-6)

                w_cmc = w_pts[1]
                w_thb_mcp = w_pts[2]
                w_thb_ip = w_pts[3]
                w_thb_tip = w_pts[4]

                v_mc = w_thb_mcp - w_cmc
                v_pp = w_thb_ip - w_thb_mcp
                v_dp = w_thb_tip - w_thb_ip

                dir_mc = v_mc / (np.linalg.norm(v_mc) + 1e-6)

                proj_medial = np.dot(dir_mc, w_across)
                proj_up = np.dot(dir_mc, w_up)
                spread_angle = math.atan2(-proj_medial, max(proj_up, 0.05))
                raw_thb_spread = float(np.clip((spread_angle - 0.25) / (0.90 - 0.25), 0.0, 1.2))

                proj_normal = np.dot(dir_mc, w_normal)
                raw_thb_oppose = float(np.clip((proj_normal + 0.10) / 0.50, 0.0, 1.0))

                angle_mcp = angle_between_vectors(v_mc, v_pp)
                raw_thb_mcp = float(np.clip((angle_mcp - 0.10) / (0.95 - 0.10), 0.0, 1.0))

                angle_ip = angle_between_vectors(v_pp, v_dp)
                raw_thb_ip = float(np.clip((angle_ip - 0.12) / (1.35 - 0.12), 0.0, 1.0))

                # EMA Filters
                f["idx_c1"] = ema(f["idx_c1"], idx_c1)
                f["idx_c2"] = ema(f["idx_c2"], idx_c2)
                f["idx_c3"] = ema(f["idx_c3"], idx_c3)
                f["idx_sp"] = ema(f["idx_sp"], raw_idx_sp)

                f["mid_c1"] = ema(f["mid_c1"], mid_c1)
                f["mid_c2"] = ema(f["mid_c2"], mid_c2)
                f["mid_c3"] = ema(f["mid_c3"], mid_c3)

                f["rng_c1"] = ema(f["rng_c1"], rng_c1)
                f["rng_c2"] = ema(f["rng_c2"], rng_c2)
                f["rng_c3"] = ema(f["rng_c3"], rng_c3)
                f["rng_sp"] = ema(f["rng_sp"], raw_rng_sp)

                f["pnk_c1"] = ema(f["pnk_c1"], pnk_c1)
                f["pnk_c2"] = ema(f["pnk_c2"], pnk_c2)
                f["pnk_c3"] = ema(f["pnk_c3"], pnk_c3)
                f["pnk_sp"] = ema(f["pnk_sp"], raw_pnk_sp)

                f["thb_spread"] = ema(f["thb_spread"], raw_thb_spread)
                f["thb_oppose"] = ema(f["thb_oppose"], raw_thb_oppose)
                f["thb_mcp"] = ema(f["thb_mcp"], raw_thb_mcp)
                f["thb_ip"] = ema(f["thb_ip"], raw_thb_ip)

                tracking_state["detected"] = True
                tracking_state["wrist"] = {
                    "pitch": round(f["pitch"], 3),
                    "yaw": round(f["yaw"], 3),
                    "roll": round(f["roll"], 3)
                }
                tracking_state["thumb"] = {
                    "cmc_spread": round(f["thb_spread"], 3),
                    "cmc_oppose": round(f["thb_oppose"], 3),
                    "mcp_flex": round(f["thb_mcp"], 3),
                    "ip_flex": round(f["thb_ip"], 3),
                    "spread": round(f["thb_spread"], 3),
                    "curl1": round(f["thb_mcp"], 3),
                    "curl2": round(f["thb_ip"], 3)
                }
                tracking_state["index"] = {
                    "curl1": round(f["idx_c1"], 3),
                    "curl2": round(f["idx_c2"], 3),
                    "curl3": round(f["idx_c3"], 3),
                    "spread": round(f["idx_sp"], 3)
                }
                tracking_state["middle"] = {
                    "curl1": round(f["mid_c1"], 3),
                    "curl2": round(f["mid_c2"], 3),
                    "curl3": round(f["mid_c3"], 3)
                }
                tracking_state["ring"] = {
                    "curl1": round(f["rng_c1"], 3),
                    "curl2": round(f["rng_c2"], 3),
                    "curl3": round(f["rng_c3"], 3),
                    "spread": round(f["rng_sp"], 3)
                }
                tracking_state["pinky"] = {
                    "curl1": round(f["pnk_c1"], 3),
                    "curl2": round(f["pnk_c2"], 3),
                    "curl3": round(f["pnk_c3"], 3),
                    "spread": round(f["pnk_sp"], 3)
                }
                tracking_state["fps"] = round(fps, 1)
                tracking_state["timestamp"] = time.time()

                # --- DRAW THE ROBLOX ROBOTIC HAND REPLICA ON CAMERA ---
                draw_robotic_hand_overlay(frame, pts, tracking_state)
            else:
                tracking_state["detected"] = False
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
