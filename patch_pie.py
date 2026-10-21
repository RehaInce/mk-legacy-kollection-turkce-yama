# Patch strings/locale.strings inside the encrypted assets.pie via known-plaintext keystream reuse.
# The archive is a ZIP under a position-keyed stream cipher, so new = old_cipher ^ old_plain ^ new_plain.
#   python patch_pie.py PIE new_locale.strings     -> patch (backs up original bytes first)
#   python patch_pie.py PIE --restore              -> put original bytes back
import sys, os, zlib, struct

ORIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'locale.strings.orig')
BACKUP_NAME = 'assets.pie.tr-backup'
LHO = 5083069333                    # local header of strings/locale.strings
DATA = LHO + 30 + 22                # stored, no extra field
CD_ENTRY = 11911977206 + (500367 - 0x3064)  # central-directory entry of the same file
ORIG_SIZE, ORIG_CRC = 2393861, 0x14bd6dbb
RANGES = [(DATA, ORIG_SIZE), (LHO + 14, 4), (CD_ENTRY + 16, 4)]

def main():
    pie = sys.argv[1]
    backup = os.path.join(os.path.dirname(os.path.abspath(pie)), BACKUP_NAME)
    with open(pie, 'r+b') as f:
        if sys.argv[2] == '--restore':
            b = open(backup, 'rb').read(); p = 0
            for off, n in RANGES:
                f.seek(off); f.write(b[p:p + n]); p += n
            print('restored'); return
        if not os.path.exists(backup):
            with open(backup, 'wb') as bk:
                for off, n in RANGES:
                    f.seek(off); bk.write(f.read(n))
        old_plain = open(ORIG, 'rb').read()
        assert zlib.crc32(old_plain) == ORIG_CRC, 'locale.strings.orig does not match this game version'
        new_plain = open(sys.argv[2], 'rb').read()
        assert len(new_plain) <= ORIG_SIZE, f'too big by {len(new_plain) - ORIG_SIZE} bytes'
        new_plain += b'\0' * (ORIG_SIZE - len(new_plain))
        b = open(backup, 'rb').read()
        cipher = b[:ORIG_SIZE]
        f.seek(DATA)
        f.write(bytes(c ^ o ^ n for c, o, n in zip(cipher, old_plain, new_plain)))
        crc_delta = struct.pack('<I', ORIG_CRC ^ zlib.crc32(new_plain))
        for (off, _), old in zip(RANGES[1:], (b[ORIG_SIZE:ORIG_SIZE + 4], b[ORIG_SIZE + 4:])):
            f.seek(off); f.write(bytes(x ^ y for x, y in zip(old, crc_delta)))
        print('patched', len(new_plain), 'crc', hex(zlib.crc32(new_plain)))

if __name__ == '__main__':
    main()
