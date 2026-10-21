# Merge tr/*.json (unique English string id -> Turkish) into the es-mx slot and write tr.strings.
# Ids index the unique en-us strings of locale.strings.orig in file order.
import sys, os, json, glob, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lstr import load, save

# ponytail: game fonts lack these glyphs (renders '?'); drop this map if fonts get patched
FALLBACK = str.maketrans('ğĞşŞıİ', 'gGsSiI')

here = os.path.dirname(os.path.abspath(__file__))
orig = open(os.path.join(here, 'locale.strings.orig'), 'rb').read()
prefix, langs = load(orig)
unique = list(dict.fromkeys(langs['en-us']))

tr = {}
for f in sorted(glob.glob(os.path.join(here, 'tr', '*.json'))):
    tr.update({int(k): v for k, v in json.load(open(f, encoding='utf-8-sig')).items()})
# Placeholders ({menu_accept}, %s, %%, newlines) must survive translation unchanged.
PH = re.compile(r'\{[^}]*\}|%%|%[sdi]|\n')
bad = [i for i, v in tr.items() if sorted(PH.findall(unique[i])) != sorted(PH.findall(v))]
assert not bad, f'placeholder mismatch in ids: {bad}'
en_to_tr = {unique[i]: v.translate(FALLBACK) for i, v in tr.items()}

# Turkish takes over the Latin-American Spanish slot; English stays untouched.
langs['es-mx'] = [en_to_tr.get(s, s) for s in langs['en-us']]
for name in langs:
    langs[name] = ['TÜRKÇE' if s == 'ESPAÑOL (AM)' else s for s in langs[name]]
out = save(prefix, langs)
assert load(out)[1] == langs
open(os.path.join(here, 'tr.strings'), 'wb').write(out)
print(f'translated {len(tr)}/{len(unique)} unique strings, size {len(out)}, headroom {len(orig) - len(out)}')
