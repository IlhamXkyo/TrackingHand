Tentu! Berikut adalah file README.md yang lengkap dan profesional untuk project hand gesture recognition Anda:

# 🖐️ Hand Gesture Recognition

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8%2B-green)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.13%2B-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

Program deteksi gerakan tangan secara real-time menggunakan **MediaPipe** dan **OpenCV**. Dapat mengenali berbagai gestur tangan seperti kepalan, victory, telapak terbuka, dan lainnya.

## 📋 Daftar Isi
- [Fitur](#fitur)
- [Demo](#demo)
- [Persyaratan Sistem](#persyaratan-sistem)
- [Instalasi](#instalasi)
- [Cara Penggunaan](#cara-penggunaan)
- [Gestur yang Didukung](#gestur-yang-didukung)
- [Struktur Project](#struktur-project)
- [Troubleshooting](#troubleshooting)
- [Kontribusi](#kontribusi)
- [Lisensi](#lisensi)

## ✨ Fitur

- ✅ Deteksi tangan secara real-time (30+ FPS)
- ✅ Support 2 tangan sekaligus (kiri dan kanan)
- ✅ Menghitung jumlah jari yang terbuka
- ✅ Mengenali 6 gestur dasar:
  - 👊 Kepalan (0 jari)
  - ☝️ Menunjuk (1 jari)
  - ✌️ Victory (2 jari)
  - 🖖 Tiga jari (3 jari)
  - 🖐️ Empat jari (4 jari)
  - ✋ Telapak terbuka (5 jari)
- ✅ Informasi detail jari yang terbuka
- ✅ Tampilan UI yang informatif
- ✅ Indikator FPS real-time
- ✅ Mudah dikembangkan untuk gestur kustom

## 🎥 Demo

![Demo Hand Gesture](demo.gif)
*Tampilan program saat mendeteksi gestur tangan*

## 💻 Persyaratan Sistem

- **Python**: 3.7 atau lebih baru
- **Webcam**: Kamera internal atau eksternal
- **RAM**: Minimal 4GB (rekomendasi 8GB)
- **OS**: Windows/Linux/MacOS

## 🔧 Instalasi

### 1. Clone Repository
```bash
git clone https://github.com/IlhamXkyo/TrackingHand
cd TrackingHand
```

### 2. Buat Virtual Environment (Opsional tapi direkomendasikan)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

Atau install manual:
```bash
pip install opencv-python mediapipe==0.10.13 numpy
```

### 4. Jalankan Program
```bash
python main.py
```

## 📖 Cara Penggunaan

1. **Jalankan program**:
   ```bash
   python main.py
   ```

2. **Posisikan tangan** Anda di depan webcam dengan jarak 30-70 cm

3. **Lakukan gestur** yang ingin dideteksi

4. **Lihat hasil** di layar:
   - Jumlah tangan terdeteksi
   - Label tangan (kiri/kanan)
   - Jumlah jari terbuka
   - Nama gestur dengan icon
   - Detail jari yang terbuka

5. **Keluar program**: Tekan tombol `q` atau `ESC`

## 🎯 Gestur yang Didukung

| Jumlah Jari | Nama Gestur | Icon | Deskripsi |
|------------|-------------|------|-----------|
| 0 | Kepalan | 👊 | Semua jari mengepal |
| 1 | Menunjuk | ☝️ | Hanya telunjuk terbuka |
| 2 | Victory | ✌️ | Telunjuk dan tengah terbuka |
| 3 | Tiga Jari | 🖖 | Telunjuk, tengah, manis terbuka |
| 4 | Empat Jari | 🖐️ | Empat jari terbuka (ibu jari tertutup) |
| 5 | Telapak Terbuka | ✋ | Semua jari terbuka |

## 📁 Struktur Project

```
hand-gesture-recognition/
│
├── main.py                 # Program utama
├── requirements.txt        # Daftar dependencies
├── README.md              # Dokumentasi
├── LICENSE                # File lisensi
│
├── src/                   # (Opsional) Untuk pengembangan lanjutan
│   ├── detector.py        # Modul deteksi tangan
│   ├── gesture_recognizer.py  # Modul pengenalan gestur
│   └── utils.py           # Fungsi utilitas
│
├── assets/                # Gambar dan aset
│   └── demo.gif          # GIF demo
│
└── tests/                 # Unit tests
    └── test_detector.py
```

## 🔍 Troubleshooting

### Error: "module 'mediapipe' has no attribute 'solutions'"
**Solusi**: Install versi MediaPipe yang kompatibel
```bash
pip uninstall mediapipe
pip install mediapipe==0.10.13
```

### Webcam tidak terdeteksi
**Solusi**: 
- Coba ganti index kamera dari 0 ke 1:
  ```python
  cap = cv2.VideoCapture(1)  # Ganti 0 dengan 1
  ```
- Pastikan webcam tidak digunakan program lain

### Program berjalan lambat
**Solusi**:
- Turunkan resolusi webcam
- Kurangi nilai `model_complexity` menjadi 0
- Tutup program lain yang berat

### Deteksi kurang akurat
**Solusi**:
- Perbaiki pencahayaan ruangan
- Jaga jarak tangan 30-70 cm dari kamera
- Hindari background yang terlalu ramai

## 🤝 Kontribusi

Kontribusi selalu diterima! Berikut cara berkontribusi:

1. **Fork** repository ini
2. **Buat branch** baru: `git checkout -b fitur-baru`
3. **Commit** perubahan: `git commit -m 'Menambah fitur X'`
4. **Push** ke branch: `git push origin fitur-baru`
5. Buat **Pull Request**

### Ide Pengembangan
- [ ] Tambahkan dukungan untuk lebih banyak gestur
- [ ] Integrasi dengan mouse virtual
- [ ] Kontrol presentasi dengan gestur
- [ ] Game controller dengan tangan
- [ ] GUI dengan PyQt/Tkinter

## 📄 Lisensi

Project ini dilisensikan di bawah **MIT License** - lihat file [LICENSE](LICENSE) untuk detail.

## 🙏 Credit

- [MediaPipe](https://mediapipe.dev/) oleh Google
- [OpenCV](https://opencv.org/) library
- Inspirasi dari berbagai tutorial dan dokumentasi

## 📞 Kontak

- **Nama**: muhammad ilham
- **Email**: xanderilham4@gmail.com
- **GitHub**: [github.com/username](https://github.com/IlhamXkyo)

---

## 📦 File requirements.txt

Buat file `requirements.txt` dengan isi:

```txt
opencv-python>=4.8.0
mediapipe==0.10.13
numpy>=1.24.0
```

## 🚀 Cara Upload ke GitHub

```bash
# Inisialisasi git
git init

# Tambahkan semua file
git add .

# Commit pertama
git commit -m "Initial commit: Hand Gesture Recognition"

# Tambahkan remote repository
git remote add origin https://github.com/username/hand-gesture-recognition.git

# Push ke GitHub
git branch -M main
git push -u origin main
```

## 📝 Catatan Tambahan

### Untuk pengembang yang ingin memodifikasi:

**Menambah gestur baru**:
Edit dictionary `self.gestures` di file `main.py`:
```python
self.gestures = {
    # ... gestur yang sudah ada
    6: {
        'name': 'GESTUR BARU',
        'icon': '🆕',
        'color': (255, 255, 255)
    }
}
```

**Mengubah logika deteksi jari**:
Modifikasi fungsi `get_finger_status()` sesuai kebutuhan.

---

**Selamat mencoba!** Jika ada pertanyaan atau masalah, silakan buat issue di repository ini. ⭐ Jangan lupa beri star jika project ini bermanfaat!
