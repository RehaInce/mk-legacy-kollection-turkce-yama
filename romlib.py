# Shared ROM helpers for the in-game translations.
# extract(): copy decrypted ROM files out of the running game's memory (run as administrator, game open).
# patch():   write a translated ROM into assets.pie at the same size (keystream reuse, like patch_pie.py);
#            the first run backs up the original bytes next to the pie, restore=True puts them back.
import ctypes, os, struct, subprocess, sys, zlib
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)

CD_START, CD_FIRST = 11911977206, 0x3064   # central directory offset in the pie / in the decrypted CD buffer
# archive name: central directory entry (cd), local header offset (lho), name length, size, original CRC
ENTRIES = {
    'roms/moo/Midway/MortalKombat_T/mkr4.maincpu': dict(cd=416524, lho=4241859819, nl=43, usz=1048576, crc=0xec1d9e34),
    'roms/moo/Midway/MortalKombat_T/mk.gfxrom':    dict(cd=416402, lho=4235568293, nl=40, usz=6291456, crc=0xab6407f2),
    'roms/gb/gb_mk1_us.gb':                        dict(cd=413455, lho=4112842294, nl=20, usz=262144, crc=0x64f5460c),
}
# small ROMs share heap blocks with other data: find them by header signature (Game Boy logo, SEGA string)
SIGS = ((bytes.fromhex('ceed6666cc0d000b'), 0x104), (b'TMR SEGA', 0x7ff0))

def extract(names, outdir):
    from extract_strings import MBI, enable_debug_priv, k32
    out = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq mk_legacy_kollection.exe', '/FO', 'CSV', '/NH'],
                         capture_output=True, text=True).stdout
    if '","' not in out:
        sys.exit('Oyun calismiyor. Oyunu acip ilgili oyunu baslatin.')
    enable_debug_priv()
    h = k32.OpenProcess(0x0410, False, int(out.split('","')[1]))
    if not h:
        sys.exit('Oyun bellegine erisilemedi. Bu betigi yonetici olarak calistirin.')
    todo = {os.path.basename(n): ENTRIES[n] for n in names}
    addr, m = 0, MBI()
    while todo and k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(m), ctypes.sizeof(m)):
        if m.State == 0x1000 and m.Protect & 0xEE and not m.Protect & 0x100 and m.RegionSize >= min(e['usz'] for e in todo.values()):
            buf, rd = ctypes.create_string_buffer(m.RegionSize), ctypes.c_size_t()
            if k32.ReadProcessMemory(h, ctypes.c_void_p(m.BaseAddress), buf, m.RegionSize, ctypes.byref(rd)):
                data = buf.raw[:rd.value]
                # big ROM files sit a few bytes past the start of their own heap block
                cands = [(off, n) for off in range(0, 0x400, 0x10) for n, e in todo.items() if e['usz'] <= len(data)]
                for sig, at in SIGS:
                    i = data.find(sig)
                    while i >= 0:
                        cands += [(i - at, n) for n in todo]
                        i = data.find(sig, i + 1)
                for off, n in cands:
                    e = todo.get(n)
                    if e and off >= 0 and zlib.crc32(data[off:off + e['usz']]) == e['crc']:
                        open(os.path.join(outdir, n), 'wb').write(data[off:off + e['usz']])
                        print('Tamam:', n); del todo[n]
        addr = (m.BaseAddress or 0) + m.RegionSize
    if todo:
        sys.exit('Bulunamadi: ' + ', '.join(todo) + '. Oyun zaten yamaliysa once geri alma betigini '
                 'calistirin; degilse ilgili oyun acikken tekrar deneyin.')

def patch(pie, name, orig=None, new=None, restore=False):
    e = ENTRIES[name]
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
        old, new = open(orig, 'rb').read(), open(new, 'rb').read()
        assert zlib.crc32(old) == e['crc'] and len(new) == size, f'{os.path.basename(name)}: orijinal dosya hatali'
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
