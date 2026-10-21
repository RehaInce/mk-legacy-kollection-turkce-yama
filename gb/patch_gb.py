# Game Boy Mortal Kombat: build the Turkish ROM and write it into assets.pie.
#   python patch_gb.py extract        (as administrator, Game Boy MK1 open in the collection)
#   python patch_gb.py PIE            build gb_mk1_tr.gb and patch it in
#   python patch_gb.py PIE --restore
import os, sys
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
sys.path.insert(0, os.path.dirname(here))
import romlib, gb_build, json

NAME = 'roms/gb/gb_mk1_us.gb'
ORIG, NEW = os.path.join(here, 'gb_mk1_us.gb'), os.path.join(here, 'gb_mk1_tr.gb')

if __name__ == '__main__':
    if sys.argv[1] == 'extract':
        romlib.extract([NAME], here)
    elif sys.argv[2:] == ['--restore']:
        romlib.patch(sys.argv[1], NAME, restore=True)
    else:
        tr = json.load(open(os.path.join(here, 'gb_mk1_tr.json'), encoding='utf-8'))
        open(NEW, 'wb').write(gb_build.build(open(ORIG, 'rb').read(), tr))
        romlib.patch(sys.argv[1], NAME, ORIG, NEW)
