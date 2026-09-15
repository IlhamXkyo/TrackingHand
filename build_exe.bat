@echo off
title Build TrackingHand.exe (PyInstaller)
color 0A

echo ========================================================
echo     COMPILER: MEMBUAT STANDALONE TrackingHand.exe
echo ========================================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak terdeteksi!
    pause
    exit /b 1
)

echo [*] Menginstall PyInstaller & dependensi...
pip install -r requirements.txt pyinstaller --quiet

echo.
echo [*] Memulai proses compile ke .exe (Single File)...
echo     Mohon tunggu sekitar 1-2 menit...
echo.

pyinstaller --noconfirm --onedir --windowed ^
    --name "TrackingHand" ^
    --add-data "README.md;." ^
    main.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================================
    echo  [SUKSES] Executable berhasil dibuat!
    echo  Folder output: dist\TrackingHand\TrackingHand.exe
    echo ========================================================
) else (
    echo.
    echo [ERROR] Terjadi kesalahan saat proses compile PyInstaller.
)

pause
