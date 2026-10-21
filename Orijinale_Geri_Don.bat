@echo off
cd /d "%~dp0"
python -I patch_pie.py "..\assets.pie" --restore
pause
