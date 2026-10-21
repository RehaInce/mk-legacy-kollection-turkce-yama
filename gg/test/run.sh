#!/bin/sh
# Visual run: run.sh ROM [PLAN] [SECONDS] -> sheet.png. $MAME = MAME 0.264 dir. PLAN = "t:Field,..." with
# MAME input names, e.g. "20:Start,29:P1 Button 1". MAME's Game Gear wants a BIOS: a stub that switches
# itself off (port 3E) from RAM and jumps to the cartridge is enough.
here=$(cd "$(dirname "$0")" && pwd); rom=$(cygpath -m "$(cd "$(dirname "$1")" && pwd)/$(basename "$1")")
mkdir -p "$here/roms/gamegear"
python -I -c "
b = bytearray(1024)
b[0:0x14] = bytes([0xF3, 0x31, 0xF0, 0xDF, 0x21, 0x20, 0x00, 0x11, 0x00, 0xC0, 0x01, 0x05, 0x00, 0xED, 0xB0,
                   0x3E, 0xA8, 0xC3, 0x00, 0xC0])      # di; ld sp; copy stub to C000; ld a,A8; jp C000
b[0x20:0x25] = bytes([0xD3, 0x3E, 0xC3, 0x00, 0x00])  # out (3E),a: BIOS off, cartridge on; jp 0
open(r'$(cygpath -m "$here")/roms/gamegear/majbios.rom', 'wb').write(b)"
cd "$MAME" && rm -rf snap/gamegear
MK_PLAN="$2" MK_END="${3:-120}" timeout 300 ./mame.exe gamegear -cart "$rom" -rompath "$(cygpath -m "$here/roms")" \
  -skip_gameinfo -video none -sound none -nothrottle -str 250 -autoboot_script "$(cygpath -m "$here/run.lua")" >/dev/null 2>&1
python -I "$here/sheet.py" snap/gamegear "$here/sheet.png"
