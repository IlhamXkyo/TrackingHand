# 🖐️ TrackingHand v3.0 // AI Gesture Suite & Roblox 3D Bionic Hand MoCap

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![MediaPipe](https://img.shields.io/badge/Vision-MediaPipe_0.10-00f0ff.svg)](https://developers.google.com/mediapipe)
[![Roblox](https://img.shields.io/badge/Roblox-Studio_Ready-e11d48.svg)](https://create.roblox.com/)
[![DirectInput](https://img.shields.io/badge/DirectInput-Roblox_Ready-38bdf8.svg)](https://pypi.org/project/PyDirectInput/)
[![License: MIT](https://img.shields.io/badge/License-MIT-gold.svg)](LICENSE)

> **TrackingHand** mengubah webcam laptop standar Anda menjadi pengontrol gesture AI interaktif untuk **Windows Desktop**, **Game 3D**, dan **Sistem Motion Capture Real-time Tangan Robot Bionik di Roblox Studio**.

---

## 🌟 Fitur Utama

### 🤖 1. Roblox 3D Bionic Hand MoCap & Cyber HUD Replica (BARU!)
Koneksikan webcam Anda langsung ke model tangan robot bionik 107-komponen di dalam Roblox Studio:
* **Replika Visual Tangan Robot di Kamera:** Kerangka garis standar MediaPipe diubah menjadi **replika visual tangan robot Roblox** langsung di atas frame video Anda (pelat lapis baja karbon, lampu neon cyan bercahaya `#00E6FF`, aktuator knuckle krom, dan reaktor inti telapak tangan).
* **Kinematika Biomekanik Ibu Jari Manusia:** Model sendi pelana CMC (*Carpometacarpal*), MCP, dan IP terkalibrasi dengan rotasi pronasi internal $75^\circ$ dan basis ortonormal telapak tangan 3D. Menekuk jempol tidak akan mengacaukan sudut mekar jempol (*100% decoupled*).
* **Zero HTTP Rate-Limit Crashing:** Polling stream otomatis dioptimasi ke ~7.1 req/detik (di bawah kuota batas 500 req/menit Roblox HttpService). Visual di Roblox Studio tetap halus di **60 FPS** menggunakan interpolasi *exponential lerp*.

#### Cara Menjalankan Bionic Hand MoCap:
1. **Jalankan Tracker di Komputer:**
   Klik dua kali:
   ```cmd
   run_hand_tracker.bat
   ```
   *(Atau jalankan `python hand_tracker.py` di terminal)*
2. **Buka Roblox Studio:**
   Tekan **Play** (`F5`) atau **Run** (`F8`). Tangan robot di game akan bergerak 1:1 mengikuti gerakan tangan Anda di depan webcam!
3. *(Opsional)* Jika membuat map/place baru dari nol:
   - Salin isi berkas [`roblox/BuildRoboticHand.lua`](roblox/BuildRoboticHand.lua) dan jalankan di Command Bar Roblox Studio untuk membuat model tangan bionik seketika.
   - Pasang berkas [`roblox/RoboticHandController.lua`](roblox/RoboticHandController.lua) ke dalam `ServerScriptService`.

---

### 🖥️ 2. Windows Air Mouse ("Iron Man" Mode)
Kontrol desktop dan aplikasi Windows tanpa menyentuh mouse fisik:
* **Pergerakan Kursor:** Arahkan dengan jari telunjuk. Dilengkapi *Exponential Moving Average (EMA)* untuk memfilter getaran tangan.
* **Klik Kiri & Drag:** Cubitkan ujung jempol dan telunjuk ($< 32$ px). Tahan untuk drag file/jendela.
* **Klik Kanan:** Bentuk gestur dua jari *Peace / Victory* (`V-Sign`).
* **Scroll Dokumen/Browser:** Gerakkan telapak tangan terbuka naik/turun di depan kamera.

---

### 🎮 3. Roblox & 3D Game Controller (DirectInput)
Kompatibel dengan **Roblox**, **Minecraft**, dan game DirectX lainnya menggunakan raw keyboard scan codes:

| Tangan | Gestur | Aksi di Dalam Game |
| :--- | :--- | :--- |
| **Tangan Kiri** | Tunjuk ke Atas | Jalan Maju (**`W`**) |
| **Tangan Kiri** | Tunjuk ke Bawah | Jalan Mundur (**`S`**) |
| **Tangan Kiri** | Tunjuk ke Kiri / Kanan | Belok Kiri (**`A`**) / Kanan (**`D`**) |
| **Tangan Kiri** | Buka Telapak / Angkat Jempol | Melompat (**`Spacebar`**) |
| **Tangan Kanan** | Gerakan Telunjuk | Arah Kamera 360° (*Mouse Aim*) |
| **Tangan Kanan** | Cubit (Jempol + Telunjuk) | Pukul / Serang (**Klik Kiri**) |

---

## 🚀 Panduan Memulai Cepat

### Menggunakan Batch Launcher (Paling Praktis)
* Untuk **Roblox Bionic Hand MoCap**: Klik ganda `run_hand_tracker.bat`
* Untuk **Air Mouse & Game Controller**: Klik ganda `run_controller.bat`

### Menjalankan via Terminal / CMD
```bash
# 1. Clone repository
git clone https://github.com/IlhamXkyo/TrackingHand.git
cd TrackingHand

# 2. Install dependencies
pip install -r requirements.txt

# 3. Jalankan Bionic Hand MoCap
python hand_tracker.py

# Atau jalankan Air Mouse / Game Controller
python main.py
```

---

## 📁 Struktur Proyek

```
TrackingHand/
├── hand_tracker.py           # Engine MoCap 3D dengan visual Tangan Robot Roblox & Cyber HUD
├── run_hand_tracker.bat      # Launcher 1-klik untuk Bionic Hand MoCap
├── main.py                   # Engine Air Mouse & Roblox Game Controller
├── run_controller.bat        # Launcher 1-klik untuk Air Mouse Controller
├── build_exe.bat             # Skrip pembuat standalone .EXE Windows
├── requirements.txt          # Daftar dependensi Python
├── roblox/
│   ├── RoboticHandController.lua  # Script ServerScriptService untuk Roblox Studio
│   └── BuildRoboticHand.lua       # Generator standalone model tangan 107-part
└── README.md
```

---

## ⌨️ Hotkeys

- **Pada `hand_tracker.py`**:
  - **`Q`**: Menutup tracker kamera dengan aman.
- **Pada `main.py`**:
  - **`M`**: Ganti mode (**AIR MOUSE** $\leftrightarrow$ **GAME CONTROLLER**).
  - **`T`**: Buka/tutup panduan tutorial visual.
  - **`TAB`**: Ganti halaman tutorial.
  - **`SPACE` / `ENTER`**: Mulai kontrol dari layar tutorial.
  - **`Q`**: Keluar dari aplikasi.

---

## 📜 Lisensi
Didistribusikan di bawah lisensi MIT.

Dibuat dengan ❤️ oleh [IlhamXkyo](https://github.com/IlhamXkyo).
