# Game Gear Mortal Kombat: build the Turkish ROM and write it into assets.pie.
#   python patch_gg.py extract        (as administrator, Game Gear MK1 open in the collection)
#   python patch_gg.py PIE            build gg_mk1_tr.gg and patch it in
#   python patch_gg.py PIE --restore
import os, sys
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
sys.path.insert(0, os.path.dirname(here))
import romlib, gg_build, json

NAME = 'roms/moo/Sega/GameGear/Mortal Kombat (JUE) (V3.3).gg'
ORIG, NEW = os.path.join(here, os.path.basename(NAME)), os.path.join(here, 'gg_mk1_tr.gg')

if __name__ == '__main__':
    if sys.argv[1] == 'extract':
        romlib.extract([NAME], here)
    elif sys.argv[2:] == ['--restore']:
        romlib.patch(sys.argv[1], NAME, restore=True)
    else:
        tr = json.load(open(os.path.join(here, 'gg_mk1_tr.json'), encoding='utf-8'))
        open(NEW, 'wb').write(gg_build.build(open(ORIG, 'rb').read(), tr))
        romlib.patch(sys.argv[1], NAME, ORIG, NEW)
