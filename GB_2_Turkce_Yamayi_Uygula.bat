@echo off
cd /d "%~dp0"
python -I gb\patch_gb.py "..\assets.pie"
pause
