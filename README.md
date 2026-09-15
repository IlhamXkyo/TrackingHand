# 🖐️ TrackingHand v2.0 // Dual-Mode Air Controller & Roblox Driver

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![MediaPipe](https://img.shields.io/badge/Vision-MediaPipe_0.10-00f0ff.svg)](https://developers.google.com/mediapipe)
[![DirectInput](https://img.shields.io/badge/DirectInput-Roblox_Ready-38bdf8.svg)](https://pypi.org/project/PyDirectInput/)
[![License: MIT](https://img.shields.io/badge/License-MIT-gold.svg)](LICENSE)

> **TrackingHand v2.0** turns your standard webcam into an interactive AI gesture controller for your **Windows Desktop** (Air Mouse) and **3D Games like Roblox & Minecraft** (DirectInput WASD + Camera Aim). Comes with an interactive animated onboarding tutorial HUD and one-click executable builder.

---

## 🌟 Dual Operating Modes

Press **`M`** at any time to toggle between the two modes:

### 🖥️ Mode 1: Windows Air Mouse ("Iron Man" Mode)
Control your desktop and applications without touching a physical mouse:
* **Cursor Movement**: Point with your index finger. Exponential Moving Average (EMA) smoothing eliminates trembling and hand jitter.
* **Left Click & Drag**: Pinch thumb tip and index tip together ($< 32$ px). Hold pinch to drag windows or files.
* **Right Click**: Form a Two-Finger Peace / Victory sign (`V-Sign`).
* **Scroll Document/Browser**: Open palm moving up/down in the camera view.

---

### 🎮 Mode 2: Roblox / 3D Game Controller (DirectInput)
Compatible with **Roblox**, **Minecraft**, and other DirectX games that require raw keyboard/mouse scan codes:

| Hand | Gesture | Action in Game |
| :--- | :--- | :--- |
| **Left Hand** | Point Upwards | Move Forward (**`W`**) |
| **Left Hand** | Point Downwards | Move Backward (**`S`**) |
| **Left Hand** | Point Left / Right | Strafe Left (**`A`**) / Right (**`D`**) |
| **Left Hand** | Raise Thumb / Open Palm Up | Jump (**`Spacebar`**) |
| **Right Hand** | Index finger navigation | 360° Camera Look (Mouse Aim) |
| **Right Hand** | Pinch (Thumb + Index) | Action / Tool / Attack (**Left Click**) |

---

## 🎨 Interactive Animated Tutorial HUD

Upon startup, an animated onboarding guide is rendered directly over your camera feed:
* Displays step-by-step gesture illustrations.
* Real-time landmark skeleton tracking confirms that your hand is properly positioned.
* Press **`TAB`** to switch between Windows and Game mode tutorials.
* Press **`SPACE`** or **`ENTER`** to dismiss the tutorial and engage active control.
* Press **`T`** at any time during gameplay to bring back the tutorial.

---

## 🚀 Quick Run (One-Click)

### Cara 1: Menggunakan Launcher Batch (Paling Praktis)
Cukup klik ganda berkas:
```
run_controller.bat
```
Script ini akan otomatis memeriksa Python, menginstall dependensi yang diperlukan (`opencv`, `mediapipe`, `pydirectinput`, `pyautogui`), dan langsung membuka controller.

---

### Cara 2: Menjalankan via Terminal / CMD
```bash
# 1. Clone repository
git clone https://github.com/IlhamXkyo/TrackingHand.git
cd TrackingHand

# 2. Install dependensi
pip install -r requirements.txt

# 3. Jalankan
python main.py
```

---

## 📦 Compile ke Standalone Windows `.EXE`

Ingin menjalankan aplikasi tanpa perlu membuka terminal atau menginstall Python di komputer lain?

1. Jalankan berkas:
   ```
   build_exe.bat
   ```
2. Tunggu proses PyInstaller selesai (sekitar 1-2 menit).
3. File executable akan tersedia di folder:
   ```
   dist/TrackingHand/TrackingHand.exe
   ```

---

## ⌨️ Hotkeys

- **`M`**: Ganti mode (**WINDOWS AIR MOUSE** $\leftrightarrow$ **ROBLOX GAME CONTROLLER**).
- **`T`**: Buka/tutup kembali panduan tutorial visual.
- **`TAB`**: Ganti halaman tutorial (Halaman 1: Windows / Halaman 2: Roblox).
- **`SPACE` / `ENTER`**: Mulai kontrol dari layar tutorial.
- **`Q`**: Keluar dari aplikasi dengan aman (melepaskan semua tombol keyboard yang tertahan).

---

## 📜 Lisensi

Didistribusikan di bawah lisensi MIT. Lihat berkas `LICENSE` untuk detailnya.

Dibuat dengan ❤️ oleh [IlhamXkyo](https://github.com/IlhamXkyo).
