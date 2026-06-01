@echo off
title ControlPC Ultimate v2.0
cd /d "%~dp0"
echo Installing Python dependencies...
python -m pip install -q pyserial psutil pywin32 pycaw comtypes
echo.
echo Starting ControlPC Ultimate v2.0...
echo Edit this file to change the COM port (default COM3).
echo.
python pc_listener.py COM3
pause
