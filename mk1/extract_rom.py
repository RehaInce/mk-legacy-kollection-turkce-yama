# Copy the arcade MK1 ROMs out of the running game's memory (they are decrypted there).
# Run as administrator while arcade Mortal Kombat is open in the collection.
import ctypes, os, sys, subprocess, zlib
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(here))
from extract_strings import MBI, enable_debug_priv, k32
from patch_rom import ENTRIES

def main():
    out = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq mk_legacy_kollection.exe', '/FO', 'CSV', '/NH'],
                         capture_output=True, text=True).stdout
    if '","' not in out:
        sys.exit('Oyun calismiyor. Oyunu acip arcade Mortal Kombat\'i baslatin.')
    enable_debug_priv()
    h = k32.OpenProcess(0x0410, False, int(out.split('","')[1]))
    if not h:
        sys.exit('Oyun bellegine erisilemedi. Bu betigi yonetici olarak calistirin.')
    todo = {os.path.basename(n): e for n, e in ENTRIES.items()}
    addr, m = 0, MBI()
    while todo and k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(m), ctypes.sizeof(m)):
        fits = [(n, e) for n, e in todo.items() if e['usz'] <= m.RegionSize]
        if m.State == 0x1000 and m.Protect & 0xEE and not m.Protect & 0x100 and fits:
            buf, rd = ctypes.create_string_buffer(m.RegionSize), ctypes.c_size_t()
            if k32.ReadProcessMemory(h, ctypes.c_void_p(m.BaseAddress), buf, m.RegionSize, ctypes.byref(rd)):
                data = buf.raw[:rd.value]
                # the emulator keeps each ROM file in its own heap block, a few bytes past the block start
                for off in range(0, 0x400, 0x10):
                    for n, e in fits:
                        if n in todo and zlib.crc32(data[off:off + e['usz']]) == e['crc']:
                            open(os.path.join(here, n), 'wb').write(data[off:off + e['usz']])
                            print('Tamam:', n); del todo[n]
        addr = (m.BaseAddress or 0) + m.RegionSize
    if todo:
        sys.exit('Bulunamadi: ' + ', '.join(todo) + '. Oyun zaten yamaliysa once MK1_Orijinale_Geri_Don.bat '
                 'calistirin; degilse arcade Mortal Kombat acikken tekrar deneyin.')

if __name__ == '__main__':
    main()
