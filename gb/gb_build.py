# Build the Turkish Game Boy Mortal Kombat ROM:  python gb_build.py ORIG.gb TR.json OUT.gb
# TR.json: {"0xBLOCK": ["line", ...]} replaces the lines of an inline text block (same line count, same rows);
#          {"0xADDR": "text"} overwrites raw text of the same length.
# Blocks keep their byte length (code resumes after the block's 00), so shorter text is padded
# with cursor-only entries. Turkish letters are drawn over the unused Q X (c) (r) font tiles.
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gbtext

W = 20                                    # screen width in tiles
# Turkish letter -> byte whose font tile we redraw. Only 4 tiles are free: Q X (unused in Turkish) and
# (c) (r) (copyright screen only). W stays for MIDWAY / SOFTWARE, so Ğ and İ fall back to G and I.
GLYPH = str.maketrans({'Ç': '@', 'Ş': '\x9c', 'Ö': 'Q', 'Ü': 'X', 'Ğ': 'G', 'İ': 'I', 'Â': 'A', 'Û': 'U'})
OK = set(b'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,@\x9c#')   # '#' = the copyright screen's (tm)

# 8x8 glyphs (# = ink), drawn from the game's own C G O S U
TILES = {
    '@': ['...##...', '..####..', '.##..#..', '.##.....', '##......', '##..##..', '.####...', '...##...'],   # Ç
    '\x9c': ['.####...', '##..##..', '##......', '.##.....', '..###...', '##..##..', '.####...', '..##....'],  # Ş
    'Q': ['..#..#..', '..####..', '.##..#..', '.##..#..', '##..##..', '##..##..', '.####...', '........'],   # Ö
    'X': ['.#..#...', '........', '##..##..', '##..##..', '##..##..', '##..##..', '.####...', '........'],   # Ü
}
TILE_NO = {'@': 0x30, '\x9c': 0x31, 'Q': 0x11, 'X': 0x18}

HOOK = 0x68                               # free bank-0 space (0x68-0xFF, after the interrupt vectors)
FONT_LOADS = (0x4EEF, 0x20B8)             # 'call 0F77 ; ret' that decompress the font (to VRAM / RAM copy)

def tile_hi(rows):
    # font tiles: low plane 0, high plane = background bits (ink is 0); only the high plane is stored
    return bytes(sum(1 << (7 - x) for x, c in enumerate(r) if c != '#') for r in rows)

def asm(items):
    # bytes / 'label' / ('jr', opcode, 'label'): resolves relative jumps
    pos, labels = 0, {}
    for it in items:
        if isinstance(it, str): labels[it] = pos
        else: pos += 2 if isinstance(it, tuple) else len(it)
    out = b''
    for it in items:
        if isinstance(it, str): continue
        if isinstance(it, tuple):
            off = labels[it[2]] - (len(out) + 2)
            assert -128 <= off < 128
            out += bytes([it[1], off & 0xFF])
        else:
            out += it
    return out

JR, JRZ, JRNZ = 0x18, 0x28, 0x20

def hook_code(table):
    return asm([
        bytes([0xD5, 0xCD, 0x77, 0x0F, 0xE1]),          # push de; call 0F77; pop hl   hl = font destination
        bytes([0x11, table & 0xFF, table >> 8]),        # ld de,table
        'loop',
        bytes([0x1A, 0xFE, 0xFF, 0xC8, 0xE5]),          # ld a,(de); cp FF; ret z; push hl
        bytes([0x4F, 0x13, 0x1A, 0x47, 0x13]),          # bc = tile offset
        bytes([0xCD, 0xD0, 0x17]),                      # call 17D0: VRAM reads give FF while the LCD draws
        bytes([0x23, 0x7E, 0x2B, 0xA7, 0x09]),          # a = space tile byte 1 (FF plain, 00 shadow font); add hl,bc
        (JR, JRZ, 'shadow'),
        bytes([0x06, 0x08]),                            # ld b,8
        'plain',
        bytes([0xCD, 0xD0, 0x17]),                      # call 17D0: wait for VRAM access
        bytes([0xAF, 0x22, 0x1A, 0x22, 0x13, 0x05]),    # xor a; ld (hl+),a; ld a,(de); ld (hl+),a; inc de; dec b
        (JR, JRNZ, 'plain'),
        bytes([0xE1]), (JR, JR, 'loop'),                # pop hl
        'shadow',                                       # game's shadow font: lo = ink | prev_ink >> 1, hi = ink
        bytes([0x0E, 0x00, 0x06, 0x08]),                # ld c,0; ld b,8
        'srow',                                         # compute first: the VRAM window after 17D0 is short
        bytes([0x1A, 0x2F, 0x13, 0xF5]),                # ld a,(de); cpl; inc de; push af   a = ink
        bytes([0xCB, 0x39, 0xB1, 0xF5]),                # srl c; or c; push af              a = shadow
        bytes([0xCD, 0xD0, 0x17]),
        bytes([0xF1, 0x22, 0xF1, 0x22, 0x4F, 0x05]),    # pop af; ld (hl+),a; pop af; ld (hl+),a; ld c,a; dec b
        (JR, JRNZ, 'srow'),
        bytes([0xE1]), (JR, JR, 'loop'),
    ])

def build_hook(rom):
    table = b''.join((TILE_NO[c] * 16).to_bytes(2, 'little') + tile_hi(t) for c, t in TILES.items()) + b'\xff'
    code = hook_code(0)
    code = hook_code(HOOK + len(code))
    # dark screens also invert tiles 0x00-0x26 in place (routine at 4F14); Ç Ğ sit at 0x30-0x31, so wrap it:
    # ld hl,8000; ld bc,0138; call 4F1A; ld hl,8300; ld bc,0010; call 4F1A; ret
    inv = HOOK + len(code) + len(table)
    wrap = bytes([0x21, 0x00, 0x80, 0x01, 0x38, 0x01, 0xCD, 0x1A, 0x4F,
                  0x21, 0x00, 0x83, 0x01, 0x10, 0x00, 0xCD, 0x1A, 0x4F, 0xC9])
    blob = code + table + wrap
    assert HOOK + len(blob) <= 0x100 and set(rom[HOOK:HOOK + len(blob)]) == {0xFF}, 'hook space'
    rom[HOOK:HOOK + len(blob)] = blob
    assert rom[0x4F14:0x4F17] == bytes([0x21, 0x00, 0x80])
    rom[0x4F14:0x4F17] = bytes([0xC3, inv & 0xFF, inv >> 8])
    for at in FONT_LOADS:
        assert rom[at:at + 4] == bytes([0xCD, 0x77, 0x0F, 0xC9]), hex(at)
        rom[at:at + 3] = bytes([0xC3, HOOK & 0xFF, HOOK >> 8])     # call 0F77 -> jp hook (hook ends in ret)

def encode(s):
    b = s.upper().translate(GLYPH).encode('latin1')
    bad = set(b) - OK
    assert not bad, f'{s!r}: no glyph for {bytes(bad)!r}'
    return b

def layout(row, col, old, new):
    if old.endswith(b' '):                       # a number is printed right after: keep the position
        return col
    vis = col + len(old) - len(old.lstrip())
    stripped = old.strip()
    if abs(2 * vis + len(stripped) - W) <= 1:    # centred line stays centred
        return (W - len(new)) // 2
    return min(vis, W - len(new))

def build(rom, tr):
    rom = bytearray(rom)
    blocks = {s: (e, items) for s, e, items in gbtext.blocks(bytes(rom))}
    errors = []
    for k, v in tr.items():
        try:
            build_one(rom, blocks, k, list(v) if isinstance(v, list) else v)
        except AssertionError as e:
            errors.append(str(e))
    assert not errors, '; '.join(errors)
    build_hook(rom)
    return bytes(rom)

def build_one(rom, blocks, k, v):
    at = int(k, 16)
    if isinstance(v, str):
        old_end = rom.index(0, at)
        nb = encode(v)
        assert len(nb) == old_end - at, f'{k}: raw text must be {old_end - at} chars'
        rom[at:old_end] = nb
        return
    end, items = blocks[at]
    texts = [it for it in items if it[0] == 'text']
    assert len(v) == len(texts), f'{k}: {len(texts)} lines expected'
    new_items = []
    for it in items:
        if it[0] == 'box':
            new_items.append(it); continue
        _, row, col, old = it
        nb = encode(v.pop(0))
        assert len(nb) <= W, f'{k}: line too long: {nb!r}'
        c = layout(row, col, old, nb)
        new_items.append(['text', row, c, nb])
    size = end - at
    body = lambda: b''.join(it[1] if it[0] == 'box' else bytes([1, it[1], it[2]]) + it[3] for it in new_items)
    k_pad = size - len(body())
    assert k_pad >= 0, f'{k}: {-k_pad} bytes too long'
    if k_pad % 3:                            # 1-2 spare bytes: spaces on a line that has room
        r = k_pad % 3
        for t in reversed([it for it in new_items if it[0] == 'text' and it[3].strip()]):
            if t[2] + len(t[3]) + r <= W:
                t[3] += b' ' * r; break
            if t[2] >= r:
                t[2] -= r; t[3] = b' ' * r + t[3]; break
        else:
            raise AssertionError(f'{k}: cannot pad')
    t = [it for it in new_items if it[0] == 'text'][-1]
    # cursor-only entries; they leave the cursor at the end of the last line, where code may print a number
    blob = body() + bytes([1, t[1], t[2] + len(t[3])]) * ((size - len(body())) // 3)
    assert len(blob) == size
    rom[at:end] = blob

if __name__ == '__main__':
    rom = open(sys.argv[1], 'rb').read()
    tr = json.load(open(sys.argv[2], encoding='utf-8'))
    open(sys.argv[3], 'wb').write(build(rom, tr))
    print('ok')
