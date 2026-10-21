@echo off
cd /d "%~dp0"
python -I mk1\patch_rom.py "..\assets.pie" --restore
pause
