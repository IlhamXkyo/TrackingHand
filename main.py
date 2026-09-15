"""
TrackingHand v2.0 // Dual-Mode Air Controller & Roblox Driver
Control your Windows Desktop or Roblox / 3D Games using natural hand gestures.
Featuring an animated visual tutorial, EMA cursor smoothing, and DirectInput game keys.

Author: IlhamXkyo
License: MIT
"""

import cv2
import math
import time
import numpy as np

# MediaPipe
try:
    import mediapipe as mp
except ImportError:
    print("[ERROR] MediaPipe not installed! Run: pip install -r requirements.txt")
    exit(1)

# PyAutoGUI & PyDirectInput
try:
    import pyautogui
    pyautogui.FAILSAFE = False  # Prevent corner crash during fast air movement
    SCREEN_W, SCREEN_H = pyautogui.size()
except ImportError:
    pyautogui = None
    SCREEN_W, SCREEN_H = 1920, 1080

try:
    import pydirectinput
    pydirectinput.PAUSE = 0.01  # Ultra fast game responsiveness
except ImportError:
    pydirectinput = pyautogui  # Fallback to pyautogui if pydirectinput not available


class HandControllerApp:
    def __init__(self):
        # MediaPipe Setup
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_styles = mp.solutions.drawing_styles

        # Operating Modes: 'WINDOWS' or 'GAME'
        self.mode = 'WINDOWS'

        # State: 'TUTORIAL' or 'ACTIVE'
        self.state = 'TUTORIAL'
        self.tutorial_page = 0
        self.tutorial_hold_time = 0

        # Cursor Smoothing (Exponential Moving Average)
        self.prev_x = SCREEN_W // 2
        self.prev_y = SCREEN_H // 2
        self.smooth_factor = 0.45  # Higher = faster, lower = smoother

        # Gesture & Key states
        self.is_left_clicked = False
        self.is_right_clicked = False
        self.last_click_time = 0
        self.active_keys = set()  # Currently held keys in game mode

        # Camera calibration boundaries (active tracking box)
        self.box_margin_x = 100
        self.box_margin_y = 80

        # Animation ticker
        self.anim_tick = 0

    def calculate_distance(self, p1, p2):
        """Euclidean distance between two landmarks in pixel space"""
        return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

    def get_landmark_coords(self, landmark, w, h):
        """Converts normalized landmark to integer pixel coordinates"""
        return int(landmark.x * w), int(landmark.y * h)

    def draw_rounded_rect(self, img, top_left, bottom_right, color, thickness=1, corner_radius=10):
        """Draws clean rounded rectangles for UI HUD"""
        x1, y1 = top_left
        x2, y2 = bottom_right
        cv2.rectangle(img, (x1 + corner_radius, y1), (x2 - corner_radius, y2), color, thickness)
        cv2.rectangle(img, (x1, y1 + corner_radius), (x2, y2 - corner_radius), color, thickness)
        cv2.circle(img, (x1 + corner_radius, y1 + corner_radius), corner_radius, color, thickness)
        cv2.circle(img, (x2 - corner_radius, y1 + corner_radius), corner_radius, color, thickness)
        cv2.circle(img, (x1 + corner_radius, y2 - corner_radius), corner_radius, color, thickness)
        cv2.circle(img, (x2 - corner_radius, y2 - corner_radius), corner_radius, color, thickness)

    def draw_tutorial_overlay(self, frame, hand_detected):
        """Draws an animated visual guide on top of camera before starting"""
        h, w, _ = frame.shape
        self.anim_tick += 1

        # Darkened blur backdrop
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, h), (10, 15, 25), -1)
        frame[:] = cv2.addWeighted(overlay, 0.78, frame, 0.22, 0)

        # Card container
        cx, cy = w // 2, h // 2
        card_w, card_h = 560, 400
        x1, y1 = cx - card_w // 2, cy - card_h // 2
        x2, y2 = cx + card_w // 2, cy + card_h // 2

        cv2.rectangle(frame, (x1, y1), (x2, y2), (22, 28, 40), -1)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 240, 255), 2)

        # Title
        cv2.putText(frame, "TRACKING HAND v2.0 // ONBOARDING", (x1 + 30, y1 + 45),
                    cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 240, 255), 2)
        cv2.line(frame, (x1 + 30, y1 + 60), (x2 - 30, y1 + 60), (60, 70, 90), 1)

        # Tutorial Step Content
        if self.tutorial_page == 0:
            # Page 1: Windows Air Mouse Mode Guide
            cv2.putText(frame, "MODE 1: WINDOWS AIR MOUSE", (x1 + 30, y1 + 95),
                        cv2.FONT_HERSHEY_DUPLEX, 0.65, (255, 215, 0), 2)

            # Gesture Items
            items = [
                ("1. POINT INDEX FINGER", "Move Cursor across the screen smoothly"),
                ("2. PINCH (Thumb + Index)", "Left Click & Drag (touch tips < 30px)"),
                ("3. TWO-FINGER V-SIGN", "Right Click (peace sign)"),
                ("4. OPEN PALM VERTICAL", "Scroll pages up and down")
            ]
            for idx, (title, desc) in enumerate(items):
                iy = y1 + 140 + idx * 50
                cv2.circle(frame, (x1 + 45, iy - 6), 6, (0, 240, 255), -1)
                cv2.putText(frame, title, (x1 + 65, iy), cv2.FONT_HERSHEY_DUPLEX, 0.55, (255, 255, 255), 1)
                cv2.putText(frame, desc, (x1 + 65, iy + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (160, 175, 200), 1)

        else:
            # Page 2: Roblox & Game Controller Mode Guide
            cv2.putText(frame, "MODE 2: ROBLOX / 3D GAME CONTROLLER", (x1 + 30, y1 + 95),
                        cv2.FONT_HERSHEY_DUPLEX, 0.65, (56, 189, 248), 2)

            items = [
                ("LEFT HAND (WASD D-Pad)", "Point Up: [W] | Down: [S] | Left: [A] | Right: [D]"),
                ("JUMP ACTION", "Raise Thumb or Open Palm to press [SPACE]"),
                ("RIGHT HAND (Aim/Camera)", "Move index to look around; Pinch to Attack/Click"),
                ("HOTKEY TOGGLE", "Press [M] to instantly switch Windows <-> Game Mode")
            ]
            for idx, (title, desc) in enumerate(items):
                iy = y1 + 140 + idx * 50
                cv2.circle(frame, (x1 + 45, iy - 6), 6, (56, 189, 248), -1)
                cv2.putText(frame, title, (x1 + 65, iy), cv2.FONT_HERSHEY_DUPLEX, 0.55, (255, 255, 255), 1)
                cv2.putText(frame, desc, (x1 + 65, iy + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (160, 175, 200), 1)

        # Pulsing Start Prompt at Bottom
        pulse_alpha = 0.5 + 0.5 * math.sin(self.anim_tick * 0.15)
        pulse_color = (int(0 * pulse_alpha), int(240 * pulse_alpha), int(255 * pulse_alpha))

        cv2.putText(frame, "[TAB] Switch Guide Page  |  [SPACE / ENTER] Start Controller",
                    (x1 + 35, y2 - 25), cv2.FONT_HERSHEY_DUPLEX, 0.5, pulse_color, 1)

    def handle_windows_mode(self, frame, hand_landmarks, w, h):
        """Mode 1: Windows Air Mouse Control"""
        # Get Key Landmarks
        thumb_tip = self.get_landmark_coords(hand_landmarks.landmark[4], w, h)
        index_tip = self.get_landmark_coords(hand_landmarks.landmark[8], w, h)
        middle_tip = self.get_landmark_coords(hand_landmarks.landmark[12], w, h)
        ring_tip = self.get_landmark_coords(hand_landmarks.landmark[16], w, h)
        pinky_tip = self.get_landmark_coords(hand_landmarks.landmark[20], w, h)

        # 1. Cursor Movement with Smoothing & Calibration Box
        # Map (box_margin_x ... w - box_margin_x) to (0 ... SCREEN_W)
        clamped_x = np.clip(index_tip[0], self.box_margin_x, w - self.box_margin_x)
        clamped_y = np.clip(index_tip[1], self.box_margin_y, h - self.box_margin_y)

        target_x = np.interp(clamped_x, (self.box_margin_x, w - self.box_margin_x), (0, SCREEN_W))
        target_y = np.interp(clamped_y, (self.box_margin_y, h - self.box_margin_y), (0, SCREEN_H))

        # Exponential Moving Average smoothing
        curr_x = self.prev_x + (target_x - self.prev_x) * self.smooth_factor
        curr_y = self.prev_y + (target_y - self.prev_y) * self.smooth_factor
        self.prev_x, self.prev_y = curr_x, curr_y

        if pyautogui:
            pyautogui.moveTo(curr_x, curr_y)

        # Visual indicator at index tip
        cv2.circle(frame, index_tip, 8, (0, 240, 255), -1)

        # 2. Left Click (Pinch: Thumb + Index < 32px)
        pinch_dist = self.calculate_distance(thumb_tip, index_tip)
        now = time.time()

        if pinch_dist < 32:
            cv2.line(frame, thumb_tip, index_tip, (0, 255, 0), 3)
            cv2.circle(frame, index_tip, 12, (0, 255, 0), -1)
            if not self.is_left_clicked and (now - self.last_click_time) > 0.25:
                if pyautogui:
                    pyautogui.mouseDown()
                self.is_left_clicked = True
                self.last_click_time = now
        else:
            if self.is_left_clicked:
                if pyautogui:
                    pyautogui.mouseUp()
                self.is_left_clicked = False

        # 3. Right Click (V-Sign: Index & Middle close together < 35px, ring & pinky down)
        mid_index_dist = self.calculate_distance(index_tip, middle_tip)
        is_ring_down = ring_tip[1] > hand_landmarks.landmark[14].y * h
        is_pinky_down = pinky_tip[1] > hand_landmarks.landmark[18].y * h

        if mid_index_dist < 35 and is_ring_down and is_pinky_down and pinch_dist > 40:
            cv2.circle(frame, middle_tip, 12, (255, 0, 128), -1)
            if not self.is_right_clicked and (now - self.last_click_time) > 0.4:
                if pyautogui:
                    pyautogui.rightClick()
                self.is_right_clicked = True
                self.last_click_time = now
        else:
            self.is_right_clicked = False

        # 4. Scroll (Open Palm: all 5 fingers up, track wrist Y delta)
        # Hand wrist
        wrist = self.get_landmark_coords(hand_landmarks.landmark[0], w, h)
        is_palm_open = (index_tip[1] < wrist[1] - 80 and
                        middle_tip[1] < wrist[1] - 80 and
                        ring_tip[1] < wrist[1] - 80 and
                        pinky_tip[1] < wrist[1] - 80)

        if is_palm_open and pinch_dist > 50:
            cv2.putText(frame, "[SCROLL MODE]", (w - 220, h - 30),
                        cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 215, 0), 2)
            # Scroll based on vertical position
            if index_tip[1] < h * 0.35:
                if pyautogui:
                    pyautogui.scroll(60)
            elif index_tip[1] > h * 0.65:
                if pyautogui:
                    pyautogui.scroll(-60)

    def handle_game_mode(self, frame, hand_landmarks, handedness_label, w, h):
        """Mode 2: Roblox / 3D Game DirectInput Controller"""
        wrist = self.get_landmark_coords(hand_landmarks.landmark[0], w, h)
        thumb_tip = self.get_landmark_coords(hand_landmarks.landmark[4], w, h)
        index_tip = self.get_landmark_coords(hand_landmarks.landmark[8], w, h)
        middle_tip = self.get_landmark_coords(hand_landmarks.landmark[12], w, h)

        # LEFT HAND = D-PAD MOVEMENT (WASD & Jump)
        if handedness_label == "Left":
            dx = index_tip[0] - wrist[0]
            dy = index_tip[1] - wrist[1]

            desired_keys = set()

            # Directional threshold
            deadzone = 40
            if dy < -deadzone and abs(dx) < abs(dy) * 1.5:
                desired_keys.add('w')  # Forward
                cv2.arrowedLine(frame, wrist, (wrist[0], wrist[1] - 60), (0, 255, 0), 3)
            elif dy > deadzone and abs(dx) < abs(dy) * 1.5:
                desired_keys.add('s')  # Backward
                cv2.arrowedLine(frame, wrist, (wrist[0], wrist[1] + 60), (0, 100, 255), 3)

            if dx < -deadzone and abs(dy) < abs(dx) * 1.5:
                desired_keys.add('a')  # Left
                cv2.arrowedLine(frame, wrist, (wrist[0] - 60, wrist[1]), (255, 215, 0), 3)
            elif dx > deadzone and abs(dy) < abs(dx) * 1.5:
                desired_keys.add('d')  # Right
                cv2.arrowedLine(frame, wrist, (wrist[0] + 60, wrist[1]), (255, 215, 0), 3)

            # Jump: Thumb Pointing Upwards or Open Palm
            if thumb_tip[1] < wrist[1] - 90:
                desired_keys.add('space')
                cv2.putText(frame, "[JUMP!]", (wrist[0] - 30, wrist[1] - 70),
                            cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 240, 255), 2)

            # Update pressed keys in DirectInput
            if pydirectinput:
                for key in desired_keys - self.active_keys:
                    pydirectinput.keyDown(key)
                for key in self.active_keys - desired_keys:
                    pydirectinput.keyUp(key)
            self.active_keys = desired_keys

        # RIGHT HAND = CAMERA AIM & ACTION
        elif handedness_label == "Right":
            # Pinch = Attack / Use Tool (Left Click)
            pinch_dist = self.calculate_distance(thumb_tip, index_tip)
            if pinch_dist < 32:
                cv2.circle(frame, index_tip, 12, (0, 255, 0), -1)
                cv2.putText(frame, "[ACTION CLICK]", (index_tip[0] + 15, index_tip[1]),
                            cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 255, 0), 2)
                if pydirectinput and not self.is_left_clicked:
                    pydirectinput.mouseDown()
                    self.is_left_clicked = True
            else:
                if pydirectinput and self.is_left_clicked:
                    pydirectinput.mouseUp()
                    self.is_left_clicked = False

            # Relative Camera Look
            cx, cy = w * 3 // 4, h // 2
            cv2.circle(frame, (cx, cy), 45, (255, 255, 255), 1)
            rel_dx = (index_tip[0] - cx)
            rel_dy = (index_tip[1] - cy)

            if math.hypot(rel_dx, rel_dy) > 25 and pydirectinput:
                move_x = int(rel_dx * 0.15)
                move_y = int(rel_dy * 0.15)
                pydirectinput.moveRel(move_x, move_y)
                cv2.line(frame, (cx, cy), (cx + move_x * 3, cy + move_y * 3), (56, 189, 248), 2)

    def draw_hud(self, frame, fps, hands_count):
        """Renders the in-game cyberpunk telemetry HUD"""
        h, w, _ = frame.shape

        # Top Bar
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 65), (10, 15, 25), -1)
        frame[:] = cv2.addWeighted(overlay, 0.8, frame, 0.2, 0)

        # Mode Badge
        mode_color = (0, 240, 255) if self.mode == 'WINDOWS' else (56, 189, 248)
        mode_name = "WINDOWS AIR MOUSE" if self.mode == 'WINDOWS' else "ROBLOX / GAME CONTROLLER"

        cv2.rectangle(frame, (15, 12), (320, 52), (20, 28, 42), -1)
        cv2.rectangle(frame, (15, 12), (320, 52), mode_color, 2)
        cv2.putText(frame, mode_name, (28, 38), cv2.FONT_HERSHEY_DUPLEX, 0.55, mode_color, 2)

        # Active Keys Display in Game Mode
        if self.mode == 'GAME' and self.active_keys:
            keys_str = " ".join([f"[{k.upper()}]" for k in self.active_keys])
            cv2.putText(frame, f"KEYS: {keys_str}", (340, 38),
                        cv2.FONT_HERSHEY_DUPLEX, 0.65, (0, 255, 0), 2)

        # Stats & Hotkeys
        cv2.putText(frame, f"FPS: {int(fps)} | HANDS: {hands_count}", (w - 240, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (160, 175, 200), 1)
        cv2.putText(frame, "[M] Mode  [T] Guide  [Q] Exit", (w - 240, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 215, 0), 1)

        # Calibration Bounds (Subtle corner lines)
        bx, by = self.box_margin_x, self.box_margin_y
        cv2.rectangle(frame, (bx, by), (w - bx, h - by), (255, 255, 255), 1, cv2.LINE_AA)

    def release_all_keys(self):
        """Safety cleanup: release any held game keys"""
        if pydirectinput:
            for k in list(self.active_keys):
                pydirectinput.keyUp(k)
        self.active_keys.clear()

    def run(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("[ERROR] Cannot access webcam! Please connect a camera.")
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        print("[OK] TrackingHand initialized!")
        print("     Press 'M' to toggle Windows <-> Game mode.")
        print("     Press 'T' to open tutorial.")
        print("     Press 'Q' to quit.\n")

        fps_timer = time.time()
        fps_frames = 0
        fps = 30

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Mirror view for natural interaction
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape

            # FPS calculation
            fps_frames += 1
            if time.time() - fps_timer >= 1.0:
                fps = fps_frames / (time.time() - fps_timer)
                fps_frames = 0
                fps_timer = time.time()

            # MediaPipe Detection
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(frame_rgb)

            hands_count = len(results.multi_hand_landmarks) if results.multi_hand_landmarks else 0

            # 1. State Machine: Tutorial or Active Control
            if self.state == 'TUTORIAL':
                self.draw_tutorial_overlay(frame, hands_count > 0)
            else:
                # Active Control State
                if results.multi_hand_landmarks:
                    for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                        # Draw Landmarks
                        self.mp_draw.draw_landmarks(
                            frame,
                            hand_landmarks,
                            self.mp_hands.HAND_CONNECTIONS,
                            self.mp_styles.get_default_hand_landmarks_style(),
                            self.mp_styles.get_default_hand_connections_style()
                        )

                        # Determine Handedness
                        handedness_label = "Right"
                        if results.multi_handedness and idx < len(results.multi_handedness):
                            handedness_label = results.multi_handedness[idx].classification[0].label

                        # Route to active mode handler
                        if self.mode == 'WINDOWS':
                            self.handle_windows_mode(frame, hand_landmarks, w, h)
                        elif self.mode == 'GAME':
                            self.handle_game_mode(frame, hand_landmarks, handedness_label, w, h)
                else:
                    self.release_all_keys()

                self.draw_hud(frame, fps, hands_count)

            # Show Frame
            cv2.imshow("TrackingHand // Dual-Mode Air Controller", frame)

            # Keyboard Hotkeys
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('m'):
                self.release_all_keys()
                self.mode = 'GAME' if self.mode == 'WINDOWS' else 'WINDOWS'
            elif key == ord('t'):
                self.release_all_keys()
                self.state = 'TUTORIAL'
            elif key == ord('\t'):  # Tab
                if self.state == 'TUTORIAL':
                    self.tutorial_page = (self.tutorial_page + 1) % 2
            elif key == 32 or key == 13:  # Space or Enter
                if self.state == 'TUTORIAL':
                    self.state = 'ACTIVE'

        self.release_all_keys()
        cap.release()
        cv2.destroyAllWindows()
        print("\n[OK] TrackingHand closed cleanly.")


if __name__ == "__main__":
    app = HandControllerApp()
    app.run()