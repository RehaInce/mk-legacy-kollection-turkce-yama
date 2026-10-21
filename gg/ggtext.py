# Text runs of Game Gear Mortal Kombat: FF-terminated uppercase lines, consecutive lines form a run.
import re, sys
LINE = rb'[ -Z]+\xff'

def runs(d, lo=0, hi=None):
    hi = hi or len(d)
    out, cur = [], None
    for m in re.finditer(rb'(?:' + LINE + rb')+', d[lo:hi]):
        lines = m.group().split(b'\xff')[:-1]
        if sum(len(l) for l in lines) >= 4 and any(re.search(rb'[A-Z]{3}', l) for l in lines):
            out.append((lo + m.start(), lines))
    return out

if __name__ == '__main__':
    d = open(sys.argv[1], 'rb').read()
    for s, lines in runs(d):
        print(hex(s), len(lines), [l.decode() for l in lines])
