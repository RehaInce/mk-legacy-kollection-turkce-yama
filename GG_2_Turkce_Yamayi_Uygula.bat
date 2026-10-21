@echo off
cd /d "%~dp0"
python -I gg\patch_gg.py "..\assets.pie"
pause
