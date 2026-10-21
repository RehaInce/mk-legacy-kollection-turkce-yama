@echo off
cd /d "%~dp0"
python -I mk1\build_mk1.py && python -I mk1\patch_rom.py "..\assets.pie"
pause
