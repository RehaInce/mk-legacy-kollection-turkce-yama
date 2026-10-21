# Build the Turkish arcade MK1 ROMs: mk1_tr.json {"0xOFFSET": "TEXT, | = line break"} -> mkr4_tr.maincpu + mk_tr.gfxrom.
# Text that fits is written in place; longer text with a pointer moves to free ROM space.
# Inline strings (no pointer) sit inside text records and must keep their length.
import json, os, re, struct, sys
here = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, here)
import mk1_font

# Turkish letters -> the unused ASCII slots mk1_font draws them into
GLYPH = str.maketrans({**mk1_font.SLOT, 'Â': 'A', 'Û': 'U'})

ROM_BASE = 0xFF800000          # TMS34010 bit address of ROM byte 0
FREE, FREE_END = 0xf7950, mk1_font.HDR_FREE   # 0xFF-filled gap; glyph headers sit at its end

def ptr(off):
    return struct.pack('<I', ROM_BASE + off * 8)

def build(rom, tr):
    rom = bytearray(rom)
    errors, free = [], FREE
    for k, text in tr.items():
        off = int(k, 16)
        end = rom.index(0, off)
        old = rom[off:end].decode('ascii')
        # uppercase everything except printf specifiers (%d, %p, %,ld): the game's printf hangs on %D
        new = ''.join(p if p.startswith('%') else p.upper()
                      for p in re.split(r'(%[^a-zA-Z%]*[a-zA-Z])', text)).translate(GLYPH).replace('|', '\\n')
        try:
            nb = new.encode('ascii')
        except UnicodeEncodeError as ex:
            errors.append(f'{k}: unmapped char {ex.object[ex.start]!r}'); continue
        # ponytail: fixed slack over the original line width; tune per screen if text clips
        width = max(len(l) for l in old.split('\\n')) + (3 if '\\n' in old else 6)
        if max(len(l) for l in new.split('\\n')) > width:
            errors.append(f'{k}: line wider than {width}: {text}')
        elif len(nb) <= len(old) and rom.count(ptr(off)):
            rom[off:end] = nb + b'\0' * (len(old) - len(nb))
        elif len(nb) <= len(old):
            # inline string inside a text record: the next record starts after its null,
            # so the null must stay put -> pad with invisible spaces instead
            pad = len(old) - len(nb)
            if '\\n' in old and pad >= 2:
                nb += b'\\n' + b' ' * (pad - 2)          # extra blank line keeps centring
            else:
                nb = b' ' * (pad // 2) + nb + b' ' * (pad - pad // 2)
            rom[off:end] = nb
        elif rom.count(ptr(off)):
            # too long: move it to free space and repoint every reference
            assert free + len(nb) + 2 <= FREE_END, 'free space exhausted'
            rom[free:free + len(nb) + 1] = nb + b'\0'
            rom[:] = rom.replace(ptr(off), ptr(free))
            free = (free + len(nb) + 2) & ~1
        else:
            errors.append(f'{k}: inline string, {len(nb)} > {len(old)} bytes: {text}')
    return bytes(rom), errors

if __name__ == '__main__':
    rom = open(os.path.join(here, 'mkr4.maincpu'), 'rb').read()
    gfx = open(os.path.join(here, 'mk.gfxrom'), 'rb').read()
    out, errors = build(rom, json.load(open(os.path.join(here, 'mk1_tr.json'), encoding='utf-8')))
    for e in errors: print(e)
    if errors: sys.exit(f'{len(errors)} errors')
    out, gfx, _ = mk1_font.install(out, gfx)
    open(os.path.join(here, 'mkr4_tr.maincpu'), 'wb').write(out)
    open(os.path.join(here, 'mk_tr.gfxrom'), 'wb').write(gfx)
    print('ok')
