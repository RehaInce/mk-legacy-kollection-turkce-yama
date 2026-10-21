#!/bin/sh
# Visual run: run.sh MAINCPU GFXROM -> sheet.png (coin, start, pick a fighter, fight; snapshot every 4 s)
here=$(cd "$(dirname "$0")" && pwd)
python -I "$here/mame_roms.py" "$1" "$2" "$here/roms/mkr4" || exit 1
cd "$MAME" && rm -rf snap/mkr4
timeout 300 ./mame.exe mkr4 -rompath "$(cygpath -m "$here/roms")" -skip_gameinfo -video none -sound none -nothrottle -str 200 \
  -autoboot_script "$(cygpath -m "$here/fight.lua")" 2>&1 | tail -1
python -I "$here/sheet.py" snap/mkr4 "$here/sheet.png"
