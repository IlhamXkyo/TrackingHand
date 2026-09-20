@echo off
title Roblox Robotic Hand Motion Capture Server
echo ========================================================
echo  ROBLOX ROBOTIC HAND TRACKER
echo ========================================================
echo  Memulai kamera laptop dan server MediaPipe...
echo.
cd /d "%~dp0"
python hand_tracker.py
pause
