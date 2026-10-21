# Read/write Digital Eclipse locale.strings (MK Legacy Kollection).
# Layout: 24B header | u32 hash[8192] | u32 index[8192] | lang desc[n] (16B each:
# self-relative name ptr+len, self-relative table ptr+count) | per lang: name, (rel off,len)[count], utf-8 text.
import struct, sys, json

LANG_DESC = 0x10018

def load(data):
    n = struct.unpack_from('<I', data, 20)[0]
    langs = {}
    for k in range(n):
        a = LANG_DESC + 16 * k
        no, nl, to, tc = struct.unpack_from('<IIII', data, a)
        name = data[a + no:a + no + nl].decode()
        tb = a + 8 + to
        strs = []
        for i in range(tc):
            e = tb + 8 * i
            o, l = struct.unpack_from('<II', data, e)
            strs.append(data[e + o:e + o + l].decode('utf-8'))
        langs[name] = strs
    return data[:LANG_DESC], langs

def save(prefix, langs):
    names = list(langs)
    # Offsets are unsigned and self-relative, so all tables go first and one shared,
    # deduplicated string pool goes last: every pointer points forward.
    out = bytearray(prefix) + bytearray(16 * len(names))
    tables = []
    for k, name in enumerate(names):
        a = LANG_DESC + 16 * k
        nb = name.encode()
        name_at = len(out); out += nb + b'\0' * (8 - len(nb) % 8 or 8)
        tb = len(out); out += bytearray(8 * len(langs[name]))
        struct.pack_into('<IIII', out, a, name_at - a, len(nb), tb - (a + 8), len(langs[name]))
        tables.append(tb)
    seen = {}
    for tb, name in zip(tables, names):
        for i, s in enumerate(langs[name]):
            sb = s.encode('utf-8'); e = tb + 8 * i
            if sb not in seen:
                seen[sb] = len(out); out += sb + b'\0'
            struct.pack_into('<II', out, e, seen[sb] - e, len(sb))
    return bytes(out)

if __name__ == '__main__':
    orig = open(sys.argv[1], 'rb').read()
    prefix, langs = load(orig)
    re_prefix, re_langs = load(save(prefix, langs))
    assert re_prefix == prefix and re_langs == langs, 'roundtrip mismatch'
    print('roundtrip OK', {k: len(v) for k, v in langs.items()})
    json.dump(langs['en-us'], open('en-us.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
