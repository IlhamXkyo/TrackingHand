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
    echo Silakan install Python dari https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [*] Memulai TrackingHand Controller...
echo [INFO] Tekan 'SPACE' atau 'ENTER' untuk mulai dari layar tutorial.
echo [INFO] Tekan 'M' untuk ganti mode Windows Air Mouse / Game Roblox.
echo [INFO] Tekan 'T' untuk membuka tutorial panduan gestur.
echo [INFO] Tekan 'Q' untuk keluar.
echo.

python main.py

if %errorlevel% neq 0 (
    echo.
    echo [*] Mencoba menginstall/memperbarui dependensi jika ada yang kurang...
    pip install -r requirements.txt
    python main.py
)
