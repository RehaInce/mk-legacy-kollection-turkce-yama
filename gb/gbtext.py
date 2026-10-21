# Inline text blocks of Game Boy Mortal Kombat: after CALL 4D94 / CALL 20BC comes a run of
# 01 row col TEXT... entries (4D94 also has 02 b c d e = box), ended by 00; code resumes after the 00.
import re

PRINTERS = (b'\xcd\x94\x4d', b'\xcd\xbc\x20')

def parse(d, start):
    """-> (offset of the closing 00, [['text', row, col, bytes] | ['box', 5 bytes]] or None)"""
    i, items = start, []
    while i < len(d):
        b = d[i]
        if b == 0:
            return i, items
        if b == 1:
            items.append(['text', d[i + 1], d[i + 2], b'']); i += 3
        elif b == 2:
            items.append(['box', d[i:i + 5]]); i += 5
        elif items and items[-1][0] == 'text' and 0x20 <= b:
            items[-1][3] += bytes([b]); i += 1
        else:
            return i, None
    return i, None

def blocks(d):
    for p in PRINTERS:
        for m in re.finditer(re.escape(p), d):
            end, items = parse(d, m.end())
            if items and any(it[0] == 'text' and re.search(rb'[A-Z]{2}', it[3]) for it in items):
                yield m.end(), end, items

if __name__ == '__main__':
    import sys
    d = open(sys.argv[1], 'rb').read()
    for s, e, items in sorted(blocks(d)):
        print(hex(s), e - s, [(it[1], it[2], it[3].decode('latin1')) for it in items if it[0] == 'text'])
