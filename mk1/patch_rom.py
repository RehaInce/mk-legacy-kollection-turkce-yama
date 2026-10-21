# Write the Turkish arcade MK1 ROMs into assets.pie:  python patch_rom.py PIE [--restore]
import os, sys
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(here))
import romlib

D = 'roms/moo/Midway/MortalKombat_T/'
FILES = {D + 'mkr4.maincpu': 'mkr4_tr.maincpu', D + 'mk.gfxrom': 'mk_tr.gfxrom'}

if __name__ == '__main__':
    for name, new in FILES.items():
        romlib.patch(sys.argv[1], name, os.path.join(here, os.path.basename(name)), os.path.join(here, new),
                     restore=sys.argv[2:] == ['--restore'])
