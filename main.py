"""
PROGRAM DETEKSI GERAKAN TANGAN
Versi: Kompatibel dengan MediaPipe 0.10.13 ke atas
"""

import cv2
import mediapipe as mp
import numpy as np

class HandGestureRecognition:
    def __init__(self):
        """
        Inisialisasi semua komponen yang diperlukan
        """
        print("🚀 Memulai program deteksi gerakan tangan...")
        print(f"📌 MediaPipe version: {mp.__version__}")
        
        # Cara import yang benar untuk MediaPipe versi 0.10.13+
        try:
            # Coba import dengan cara pertama
            self.mp_hands = mp.solutions.hands
            self.mp_draw = mp.solutions.drawing_utils
            self.mp_styles = mp.solutions.drawing_styles
            print("✅ Import cara 1 berhasil")
        except AttributeError:
            try:
                # Coba import dengan cara kedua
                from mediapipe.python.solutions import hands as mp_hands
                from mediapipe.python.solutions import drawing_utils as mp_draw
                from mediapipe.python.solutions import drawing_styles as mp_styles
                self.mp_hands = mp_hands
                self.mp_draw = mp_draw
                self.mp_styles = mp_styles
                print("✅ Import cara 2 berhasil")
            except Exception as e:
                print(f"❌ Error import: {e}")
                raise
        
        # Konfigurasi deteksi tangan dengan parameter optimal
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            model_complexity=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        # Warna untuk UI
        self.colors = {
            'text': (255, 255, 255),      # Putih
            'success': (0, 255, 0),        # Hijau
            'warning': (0, 255, 255),       # Kuning
            'error': (0, 0, 255),          # Merah
            'info': (255, 0, 0)            # Biru
        }
        
        # Database gestur
        self.gestures = {
            0: {'name': 'KEPALAN', 'icon': '👊', 'color': self.colors['error']},
            1: {'name': 'TUNJUK', 'icon': '☝️', 'color': self.colors['info']},
            2: {'name': 'VICTORY', 'icon': '✌️', 'color': self.colors['success']},
            3: {'name': 'TIGA JARI', 'icon': '🖖', 'color': (255, 165, 0)},
            4: {'name': 'EMPAT JARI', 'icon': '🖐️', 'color': (255, 192, 203)},
            5: {'name': 'TELAPAK TERBUKA', 'icon': '✋', 'color': self.colors['warning']}
        }
        
        print("✅ Inisialisasi berhasil!")
        print("📋 Panduan: Tunjukkan gestur tangan di depan kamera")
        print("❌ Tekan 'q' untuk keluar\n")
        
    def get_finger_status(self, hand_landmarks):
        """Mengecek jari mana yang terbuka"""
        fingers = []
        tips = [4, 8, 12, 16, 20]
        pips = [2, 5, 9, 13, 17]
        
        # Ibu jari
        if hand_landmarks.landmark[tips[0]].x < hand_landmarks.landmark[tips[0] - 1].x:
            fingers.append(1)
        else:
            fingers.append(0)
        
        # 4 jari lainnya
        for i in range(1, 5):
            if hand_landmarks.landmark[tips[i]].y < hand_landmarks.landmark[pips[i]].y:
                fingers.append(1)
            else:
                fingers.append(0)
        
        return fingers
    
    def draw_landmarks_with_fallback(self, frame, hand_landmarks):
        """Menggambar landmark dengan fallback jika style tidak tersedia"""
        try:
            # Coba dengan style default
            self.mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_styles.get_default_hand_landmarks_style(),
                self.mp_styles.get_default_hand_connections_style()
            )
        except:
            # Fallback: gambar tanpa style
            self.mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS
            )
    
    def run(self):
        """Fungsi utama menjalankan program"""
        # Buka webcam
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ ERROR: Tidak dapat membuka webcam!")
            print("💡 Solusi: Pastikan webcam terhubung")
            return
        
        # Set resolusi
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        print("✅ Webcam siap!")
        print("💡 Tips: Letakkan tangan di depan kamera dengan pencahayaan cukup\n")
        
        # Variabel FPS
        fps_start_time = cv2.getTickCount()
        fps_frame_count = 0
        fps = 0
        
        while True:
            success, frame = cap.read()
            if not success:
                break
            
            # Flip horizontal
            frame = cv2.flip(frame, 1)
            
            # Hitung FPS
            fps_frame_count += 1
            if fps_frame_count >= 30:
                fps_end_time = cv2.getTickCount()
                time_diff = (fps_end_time - fps_start_time) / cv2.getTickFrequency()
                fps = fps_frame_count / time_diff
                fps_frame_count = 0
                fps_start_time = fps_end_time
            
            # Konversi BGR ke RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Proses deteksi
            results = self.hands.process(frame_rgb)
            
            # Panel informasi atas
            h, w, _ = frame.shape
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (w, 70), (0, 0, 0), -1)
            frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)
            
            # Tampilkan info umum
            if results.multi_hand_landmarks:
                hand_count = len(results.multi_hand_landmarks)
                cv2.putText(frame, f"👥 Tangan: {hand_count}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.colors['text'], 2)
                
                # Proses setiap tangan
                for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    # Gambar landmark
                    self.draw_landmarks_with_fallback(frame, hand_landmarks)
                    
                    # Dapatkan label tangan
                    if results.multi_handedness:
                        hand_label = results.multi_handedness[hand_idx].classification[0].label
                    else:
                        hand_label = "Unknown"
                    
                    # Hitung jari
                    finger_status = self.get_finger_status(hand_landmarks)
                    finger_count = sum(finger_status)
                    
                    # Dapatkan gestur
                    if finger_count in self.gestures:
                        gesture = self.gestures[finger_count]
                    else:
                        gesture = {'name': f'{finger_count} JARI', 'icon': '👆', 
                                  'color': self.colors['info']}
                    
                    # Tampilkan info per tangan
                    y_pos = 100 + hand_idx * 80
                    
                    # Background untuk teks
                    if hand_label == "Left":
                        x_pos = 10
                    else:
                        x_pos = w - 300
                    
                    cv2.rectangle(frame, (x_pos - 5, y_pos - 20), 
                                 (x_pos + 250, y_pos + 40), (0, 0, 0), -1)
                    
                    # Tampilkan teks
                    cv2.putText(frame, f"{hand_label}: {gesture['icon']} {gesture['name']}", 
                               (x_pos, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 
                               0.6, gesture['color'], 2)
                    
                    # Tampilkan detail jari
                    jari_list = []
                    jari_names = ["Ibu", "Telu", "Tengah", "Manis", "Keling"]
                    for i, status in enumerate(finger_status):
                        if status == 1:
                            jari_list.append(jari_names[i])
                    
                    if jari_list:
                        cv2.putText(frame, f"Jari: {', '.join(jari_list)}", 
                                   (x_pos, y_pos + 25), cv2.FONT_HERSHEY_SIMPLEX, 
                                   0.4, self.colors['text'], 1)
            else:
                cv2.putText(frame, "👋 Tidak ada tangan terdeteksi", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.colors['warning'], 2)
            
            # Tampilkan FPS dan panduan
            cv2.putText(frame, f"FPS: {int(fps)}", (w - 100, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.colors['info'], 1)
            cv2.putText(frame, "Tekan 'q' untuk keluar", (w - 200, 55),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors['warning'], 1)
            
            # Tampilkan frame
            cv2.imshow('Hand Gesture Recognition', frame)
            
            # Keluar jika tekan 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        print("\n👋 Program selesai. Terima kasih telah menggunakan!")

def main():
    print("=" * 60)
    print("      PROGRAM DETEKSI GERAKAN TANGAN")
    print("=" * 60)
    print()
    
    try:
        app = HandGestureRecognition()
        app.run()
    except Exception as e:
        print(f"❌ Terjadi error: {e}")
        print("\n💡 Solusi:")
        print("1. Hapus file main.py yang lama")
        print("2. Copy paste kode baru ini ke main.py")
        print("3. Install MediaPipe versi 0.10.13:")
        print("   pip install mediapipe==0.10.13")
        print("4. Jalankan lagi: python main.py")

if __name__ == "__main__":
    main()