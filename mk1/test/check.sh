#!/bin/sh
# Crash check: check.sh MAINCPU [GFXROM]. Runs ~90 s of attract mode in headless MAME ($MAME = MAME 0.264 dir;
# newer builds crash under a Turkish Windows locale) and prints one START per boot: more than one = crash + watchdog reset.
here=$(cd "$(dirname "$0")" && pwd)
python -I "$here/mame_roms.py" "$1" "${2:-$here/../mk.gfxrom}" "$here/roms/mkr4" || exit 1
rm -f "$here/reset.txt"
# -str < 300 also skips MAME's "wrong checksum" warning screen
cd "$MAME" && MK_LOG="$(cygpath -m "$here")/reset.txt" timeout 300 ./mame.exe mkr4 -rompath "$(cygpath -m "$here/roms")" \
  -skip_gameinfo -video none -sound none -nothrottle -str 250 -autoboot_script "$(cygpath -m "$here/reset.lua")" >/dev/null 2>&1
cat "$here/reset.txt"
