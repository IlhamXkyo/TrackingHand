@echo off
title TrackingHand Controller Launcher
color 0B

echo ========================================================
echo       TRACKING HAND v2.0 // AIR CONTROLLER
echo ========================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak ditemukan di sistem ini!
    echo Silakan install Python 3.10+ dari https://www.python.org/downloads/
    echo dan pastikan centang 'Add Python to PATH'.
    pause
    exit /b 1
)

echo [*] Memeriksa dependensi library Python...
pip install -r requirements.txt --quiet --disable-pip-version-check

echo.
echo [*] Memulai TrackingHand Controller...
echo [TIPS] Tekan 'M' di jendela aplikasi untuk ganti mode Windows / Game.
echo [TIPS] Tekan 'T' untuk membuka tutorial panduan gestur.
echo [TIPS] Tekan 'Q' untuk keluar.
echo.

python main.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Aplikasi berhenti dengan kode error.
    pause
)
