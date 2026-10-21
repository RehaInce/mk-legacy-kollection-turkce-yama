# Draw Turkish letters for the arcade MK1 fonts from existing glyphs and install them
# into unused character slots. Glyph = 12-byte header (w, h, anix, aniy, gfx bit address)
# pointing at 6bpp pixels in the graphics ROM. Fonts are 4-byte pointer tables indexed from ' '.
import struct

ROM_BASE = 0xFF800000      # TMS34010 bit address of program ROM byte 0
GFX_BASE = 0x02000000      # bit address of graphics ROM byte 0
# name: (table entry of ' ', header unused slots point to, rows squashed for top marks / for cedilla, small marks)
# text records point at the '!' entry; the 8px bio font has real '_' '`' glyphs, which bios never use
FONTS = {'16px': (0x9b570, 0xc7d6c, 3, 3, False),
         '11px': (0x9b3fc, 0xc7d6c, 2, 2, True),
         '8px':  (0x9b288, 0xc7838, 2, 0, True)}
OVERRIDE = {('8px', '_'), ('8px', '`')}
GFX_FREE = 0x5f0000        # byte offset in the 0xFF-filled tail of the graphics ROM
HDR_FREE = 0xff800         # byte offset in the 0xFF-filled gap of the program ROM
SLOT = {'Ç': '[', 'Ğ': ']', 'İ': '^', 'Ö': '_', 'Ş': '`', 'Ü': '{'}
BASE = {'Ç': 'C', 'Ğ': 'G', 'İ': 'I', 'Ö': 'O', 'Ş': 'S', 'Ü': 'U'}

def ptr(off):
    return struct.pack('<I', ROM_BASE + off * 8)

def entry(table, ch):
    return table + 4 * (ord(ch) - 32)

def read_glyph(rom, gfx, table, ch):
    p = (struct.unpack_from('<I', rom, entry(table, ch))[0] - ROM_BASE) // 8
    w, h, _, _, sag = struct.unpack_from('<HHhhI', rom, p)
    bit = sag - GFX_BASE
    n = int.from_bytes(gfx[bit // 8: bit // 8 + w * h + 2], 'little') >> (bit % 8)
    return [[(n >> ((y * w + x) * 6)) & 63 for x in range(w)] for y in range(h)]

def squash(px, k):
    # k times: drop one row from the longest run of identical rows (the letter's straight middle)
    px = list(px)
    for _ in range(k):
        best, start = (1, None), 0
        for i in range(1, len(px) + 1):
            if i == len(px) or px[i] != px[start]:
                if i - start > best[0] and start > 0:
                    best = (i - start, start)
                start = i
        if best[1] is None:   # no repeated rows (S, G): drop the middle row most like its neighbour
            diff = lambda i: sum(a != b for a, b in zip(px[i], px[i - 1]))
            best = (0, min(range(2, len(px) - 2), key=diff))
        del px[best[1]]
    return px

def span(row):
    xs = [x for x, v in enumerate(row) if v]
    return (xs[0] + xs[-1]) / 2

def mark(w, kind, cx, c, small):
    # small font: 2 rows, no gap; 16px: 2 rows + 1 gap row (cedilla 3 rows)
    rows = [[0] * w for _ in range(2 if small else 3)]
    put = lambda y, x: 0 <= x < w and rows[y].__setitem__(x, c)
    cx = int(round(cx))
    if kind == 'dots':
        xs = (cx - 2, cx + 1) if small else (cx - 3, cx - 2, cx + 2, cx + 3)
        for y in ((0,) if small else (0, 1)):
            for x in xs: put(y, x)
    elif kind == 'dot':
        for y in ((0,) if small else (0, 1)):
            for x in range(w): put(y, x)
    elif kind == 'breve':
        lo, hi = (cx - 2, cx + 1) if small else (cx - 3, cx + 3)   # U shape: tips, then bowl
        put(0, lo); put(0, hi)
        for x in range(lo + 1, hi): put(1, x)
    elif kind == 'cedilla':
        if small:
            put(0, cx); put(1, cx - 1); put(1, cx)
        else:
            put(0, cx); put(0, cx + 1); put(1, cx + 1); put(1, cx + 2)
            for x in range(cx - 1, cx + 2): put(2, x)
    return rows

def make(rom, gfx, font, letter):
    table, _, k_top, k_ced, small = font
    px = squash(read_glyph(rom, gfx, table, BASE[letter]), k_ced if letter in 'ÇŞ' else k_top)
    c = max(v for r in px for v in r)
    w = len(px[0])
    if letter in 'ÇŞ':                       # mark below; italic font leans right, so shift left
        return px + mark(w, 'cedilla', span(px[-1]) - (0 if small else 1), c, small)
    kind = {'Ö': 'dots', 'Ü': 'dots', 'İ': 'dot', 'Ğ': 'breve'}[letter]
    # marks centred on the glyph, nudged right for the italic lean
    return mark(w, kind, (w - 1) / 2 + (0 if small else 1), c, small) + px

def install(rom, gfx):
    rom, gfx = bytearray(rom), bytearray(gfx)
    bitpos, hdr = GFX_FREE * 8, HDR_FREE
    glyphs = {}
    for name, font in FONTS.items():
        table, fallback = font[:2]
        for letter, slot in SLOT.items():
            px = make(rom, gfx, font, letter)
            h, w = len(px), len(px[0])
            val = 0
            for i, v in enumerate(v for row in px for v in row):
                val |= v << (i * 6)
            nbytes = (w * h * 6 + 7) // 8
            gfx[bitpos // 8: bitpos // 8 + nbytes] = val.to_bytes(nbytes, 'little')
            rom[hdr:hdr + 12] = struct.pack('<HHhhI', w, h, 0, 0, GFX_BASE + bitpos)
            e = entry(table, slot)
            assert rom[e:e + 4] == ptr(fallback) or (name, slot) in OVERRIDE, f'{name} slot {slot} is in use'
            rom[e:e + 4] = ptr(hdr)
            glyphs[name + letter] = px
            bitpos = (bitpos + nbytes * 8 + 63) & ~63
            hdr += 12
    assert hdr <= 0xfff80, 'glyph headers reach the vector table'
    return bytes(rom), bytes(gfx), glyphs

def preview(glyphs, path):
    from PIL import Image
    im = Image.new('L', (len(glyphs) * 20, 20), 40)
    for k, px in enumerate(glyphs.values()):
        for y, row in enumerate(px):
            for x, v in enumerate(row):
                if v: im.putpixel((k * 20 + 2 + x, 2 + y), 255)
    im.resize((im.width * 6, im.height * 6), Image.NEAREST).save(path)
