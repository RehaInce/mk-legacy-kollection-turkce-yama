#!/bin/sh
# Visual run: run.sh ROM [PLAN] [SECONDS] -> sheet.png. $MAME = MAME 0.264 dir (newer builds crash under a
# Turkish Windows locale). PLAN = "t:Button,..." e.g. "10:Start,13:Start,16:Start,19:Button A".
# MAME's Game Boy needs a boot ROM; a stub that just switches itself off and jumps to the cartridge is enough.
here=$(cd "$(dirname "$0")" && pwd); rom=$(cygpath -m "$(cd "$(dirname "$1")" && pwd)/$(basename "$1")")
mkdir -p "$here/roms/gameboy"
python -I -c "
b = bytearray(256)
b[0:6] = bytes([0x31, 0xFE, 0xFF, 0xC3, 0xFC, 0x00])   # ld sp,FFFE; jp 00FC
b[0xFC:] = bytes([0x3E, 0x01, 0xE0, 0x50])            # ld a,1; ldh (50),a: boot ROM off, falls into 0100
open(r'$(cygpath -m "$here")/roms/gameboy/dmg_boot.bin', 'wb').write(b)"
cd "$MAME" && rm -rf snap/gameboy
MK_PLAN="$2" MK_END="${3:-120}" timeout 300 ./mame.exe gameboy -cart "$rom" -rompath "$(cygpath -m "$here/roms")" \
  -skip_gameinfo -video none -sound none -nothrottle -str 250 -autoboot_script "$(cygpath -m "$here/gbrun.lua")" >/dev/null 2>&1
python -I "$here/sheet.py" snap/gameboy "$here/sheet.png"
