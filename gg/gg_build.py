# Build the Turkish Game Gear Mortal Kombat ROM:  python gg_build.py ORIG.gg TR.json OUT.gg
# TR.json: {"0xADDR": ["line", ...]}  a page: the FF-terminated lines starting at ADDR are read one after
#                                      another, so lines can be re-flowed freely within the page's bytes;
#          {"0xADDR": "text"}          one string kept in place (at most its original length).
# Turkish letters go into the font's unused lowercase tiles (ç ğ ı ö ş ü).
import json, re, sys

W = 20                                    # visible tiles per row
FONTS = (0x6999A, 0x7D000)                # two copies of the 4bpp font in ROM; first tile = 0x144 (char ' ')
LOWER = {'Ç': 'c', 'Ğ': 'g', 'İ': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u'}
GLYPH = str.maketrans({**LOWER, '-': '+', 'Â': 'A', 'Û': 'U'})   # the font draws '+' as a dash
OK = set(b" !\"#$%&'()*+,.0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ") | set(map(ord, LOWER.values()))

# 8x8 glyphs (# = ink) in the style of the game's C G I O S U
TILES = {
    'c': ['...##...', '..####..', '.##..#..', '.##.....', '##......', '##..##..', '.####...', '...##...'],   # Ç
    'g': ['.#..#...', '..##....', '.####...', '##......', '##.###..', '##..##..', '.####...', '........'],   # Ğ
    'i': ['..##....', '........', '..##....', '..##....', '..##....', '..##....', '..##....', '........'],   # İ
    'o': ['..#..#..', '..####..', '.##..#..', '.##..#..', '##..##..', '##..##..', '.####...', '........'],   # Ö
    's': ['.####...', '##..##..', '##......', '.##.....', '..###...', '##..##..', '.####...', '..##....'],   # Ş
    'u': ['.#..#...', '........', '##..##..', '##..##..', '##..##..', '##..##..', '.####...', '........'],   # Ü
}

def tile_of(ch):
    c = ord(ch)
    return 0x124 + (c - 6 if c >= 0x5B else c)        # the print routine's mapping (char + 0x24, attr bit set)

def encode(s):
    b = s.upper().translate(GLYPH).encode('latin1')    # ç etc. are already mapped to lowercase bytes
    bad = set(b) - OK
    assert not bad, f'{s!r}: no glyph for {bytes(bad)!r}'
    return b

def page_lines(rom, at):
    """original FF-terminated lines from at until a byte that does not start a text line"""
    lines, i = [], at
    while True:
        m = re.match(rb'[ -Z]+\xff', rom[i:i + 64])
        if not m:
            return lines
        lines.append(m.group()[:-1]); i += m.end()

def build_one(rom, k, v):
    at = int(k, 16)
    if isinstance(v, str):
        end = rom.index(0xFF, at)
        nb = encode(v)
        assert len(nb) <= end - at, f'{k}: {len(nb)} > {end - at} chars: {v}'
        rom[at:end] = nb + b' ' * (end - at - len(nb))
        return
    old = page_lines(rom, at)
    size = sum(len(l) + 1 for l in old)
    new = [encode(l) for l in v]
    for l in new:
        assert len(l) <= W, f'{k}: line over {W}: {l!r}'
    spare = size - sum(len(l) + 1 for l in new)
    assert spare >= 0, f'{k}: page {-spare} bytes too long (budget {size})'
    while spare:                               # pad the shortest lines with (invisible) trailing spaces,
        i = min(range(len(new)), key=lambda j: len(new[j]))
        if len(new[i]) < W:
            new[i] += b' '; spare -= 1
        else:                                  # then with blank lines (a line costs 1 byte for its FF)
            assert len(new) < 14, f'{k}: cannot pad'
            if spare == 1:                     # give back one padding space to afford the FF
                j = next(j for j in range(len(new)) if new[j].endswith(b' '))
                new[j] = new[j][:-1]; spare += 1
            new.append(b' '); spare -= 2
    rom[at:at + size] = b''.join(l + b'\xff' for l in new)

def install_font(rom):
    for ch, rows in TILES.items():
        bits = [sum(1 << (7 - x) for x, c in enumerate(r) if c == '#') for r in rows]
        for font in FONTS:
            t = font + (tile_of(ch) - 0x144) * 32
            rom[t:t + 32] = bytes(b for row in bits for b in (row,) * 4)   # colour 15: all four planes set

def build(rom, tr):
    rom = bytearray(rom)
    errors = []
    for k, v in tr.items():
        try:
            build_one(rom, k, v)
        except AssertionError as e:
            errors.append(str(e))
    assert not errors, '\n'.join(errors)
    install_font(rom)
    return bytes(rom)

if __name__ == '__main__':
    rom = open(sys.argv[1], 'rb').read()
    if sys.argv[2] == '--budget':              # print each page's byte budget for translators
        for a in sys.argv[3:]:
            ls = page_lines(rom, int(a, 16))
            print(a, sum(len(l) + 1 for l in ls), [l.decode() for l in ls])
        sys.exit()
    tr = json.load(open(sys.argv[2], encoding='utf-8'))
    open(sys.argv[3], 'wb').write(build(rom, tr))
    print('ok')
