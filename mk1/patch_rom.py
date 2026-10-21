# Write the Turkish arcade MK1 ROMs into assets.pie (same size, keystream reuse like ../patch_pie.py).
#   python patch_rom.py PIE          -> patch (first run backs up the original bytes next to the pie)
#   python patch_rom.py PIE --restore
import os, struct, sys, zlib
here = os.path.dirname(os.path.abspath(__file__))

CD_START, CD_FIRST = 11911977206, 0x3064   # central directory offset in the pie / in the decrypted CD buffer
D = 'roms/moo/Midway/MortalKombat_T/'
# archive name: central directory entry (cd), local header offset (lho), name length, size, original CRC
ENTRIES = {D + 'mkr4.maincpu': dict(cd=416524, lho=4241859819, nl=43, usz=1048576, crc=0xec1d9e34),
           D + 'mk.gfxrom':    dict(cd=416402, lho=4235568293, nl=40, usz=6291456, crc=0xab6407f2)}
NEW = {'mkr4.maincpu': 'mkr4_tr.maincpu', 'mk.gfxrom': 'mk_tr.gfxrom'}

def patch(pie, name, e, restore):
    data, size = e['lho'] + 30 + e['nl'], e['usz']
    ranges = [(data, size), (e['lho'] + 14, 4), (CD_START + e['cd'] - CD_FIRST + 16, 4)]
    backup = os.path.join(os.path.dirname(os.path.abspath(pie)), 'assets.pie.' + os.path.basename(name) + '.bak')
    with open(pie, 'r+b') as f:
        if restore:
            if not os.path.exists(backup):
                print('yedek yok, atlandi:', name); return
            b, p = open(backup, 'rb').read(), 0
            for off, n in ranges:
                f.seek(off); f.write(b[p:p + n]); p += n
            print('geri yuklendi:', name); return
        base = os.path.basename(name)
        old, new = open(os.path.join(here, base), 'rb').read(), open(os.path.join(here, NEW[base]), 'rb').read()
        assert zlib.crc32(old) == e['crc'] and len(new) == size, f'{base}: orijinal dosya hatali'
        if not os.path.exists(backup):
            with open(backup, 'wb') as bk:
                for off, n in ranges:
                    f.seek(off); bk.write(f.read(n))
        b = open(backup, 'rb').read()
        f.seek(data); f.write(bytes(c ^ o ^ n for c, o, n in zip(b[:size], old, new)))
        delta = struct.pack('<I', e['crc'] ^ zlib.crc32(new))
        for (off, _), cb in zip(ranges[1:], (b[size:size + 4], b[size + 4:size + 8])):
            f.seek(off); f.write(bytes(x ^ y for x, y in zip(cb, delta)))
        print('yamalandi:', name)

if __name__ == '__main__':
    for name, e in ENTRIES.items():
        patch(sys.argv[1], name, e, sys.argv[2:] == ['--restore'])
