@echo off
cd /d "%~dp0"
python -I build_tr.py && python -I patch_pie.py "..\assets.pie" tr.strings
pause
