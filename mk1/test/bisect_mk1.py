# Find translations that crash arcade MK1 under headless MAME (resets = watchdog after a crash).
import json, os, subprocess, sys
test = os.path.dirname(os.path.abspath(__file__))
here = os.path.dirname(test)
sys.path.insert(0, here)
import build_mk1
rom = open(os.path.join(here, 'mkr4.maincpu'), 'rb').read()
tr = json.load(open(os.path.join(here, 'mk1_tr.json'), encoding='utf-8'))
out = os.path.join(test, 'mkr4_bisect.maincpu')

def crashes(keys):
    data, err = build_mk1.build(rom, {k: tr[k] for k in keys})
    open(out, 'wb').write(data)
    log = subprocess.run(['sh', os.path.join(test, 'check.sh'), out], capture_output=True, text=True).stdout
    n = log.count('START')
    print(len(keys), keys[0], keys[-1], 'restarts', n - 1, flush=True)
    return n > 1

# repeat until the remaining set is clean; every culprit found is set aside
good, bad = list(tr), []
while crashes(good):
    keys = good
    while len(keys) > 1:
        half = keys[:len(keys) // 2]
        keys = half if crashes(half) else keys[len(keys) // 2:]
    print('CULPRIT', keys[0], tr[keys[0]], flush=True)
    bad.append(keys[0]); good.remove(keys[0])
print('BAD', bad)
