# Split collection MK1 ROMs into MAME's mkr4 file layout:  python mame_roms.py MAINCPU GFXROM OUTDIR
# Sound ROMs are optional (tests run with -sound none); missing ones are filled with 0xFF.
import os, sys
here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
main, gfx, out = open(sys.argv[1], 'rb').read(), open(sys.argv[2], 'rb').read(), sys.argv[3]
os.makedirs(out, exist_ok=True)
w = lambda n, b: open(os.path.join(out, n), 'wb').write(b)
w('l4_mortal_kombat_t-unit_ug12_game_rom.ug12', main[1::2])
w('l4_mortal_kombat_t-unit_uj12_game_rom.uj12', main[0::2])
for k, chips in enumerate((('ug14', 'uj14', 'ug19', 'uj19'), ('ug16', 'uj16', 'ug20', 'uj20'), ('ug17', 'uj17', 'ug22', 'uj22'))):
    s = gfx[k * 0x200000:(k + 1) * 0x200000]
    for i, c in enumerate(chips):
        w(f'l1_mortal_kombat_t-unit_{c}_game_rom.{c}', s[i::4])
oki_path = os.path.join(here, 'mk.adpcm_oki')
oki = open(oki_path, 'rb').read() if os.path.exists(oki_path) else b'\xff' * 0x100000
w('sl1_mortal_kombat_u12_sound_rom.u12', oki[:0x40000])
w('sl1_mortal_kombat_u13_sound_rom.u13', oki[0x80000:0xc0000])
cpu = os.path.join(here, 'mk.adpcm_cpu')
w('sl1_mortal_kombat_u3_sound_rom.u3', open(cpu, 'rb').read() if os.path.exists(cpu) else b'\xff' * 0x40000)
