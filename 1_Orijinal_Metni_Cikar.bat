@echo off
net session >nul 2>&1 || (powershell -Command "Start-Process '%~f0' -Verb RunAs" & exit /b)
cd /d "%~dp0"
python -I extract_strings.py
pause
