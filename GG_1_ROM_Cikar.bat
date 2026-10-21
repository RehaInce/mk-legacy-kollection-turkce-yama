@echo off
net session >nul 2>&1 || (powershell -Command "Start-Process '%~f0' -Verb RunAs" & exit /b)
cd /d "%~dp0"
python -I gg\patch_gg.py extract
pause
