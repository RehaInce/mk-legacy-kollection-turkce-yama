# Copy the decrypted strings/locale.strings out of the running game's memory.
# Run as administrator while the game is at the main menu. Output: locale.strings.orig
import ctypes, ctypes.wintypes as wt, os, subprocess, sys, zlib

SIZE, CRC = 2393861, 0x14bd6dbb          # values from the archive's central directory
HEADER = bytes.fromhex('1800000000200000108000000020000008000100')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'locale.strings.orig')

k32 = ctypes.WinDLL('kernel32', use_last_error=True)
a32 = ctypes.WinDLL('advapi32', use_last_error=True)

class MBI(ctypes.Structure):
    _fields_ = [('BaseAddress', ctypes.c_void_p), ('AllocationBase', ctypes.c_void_p), ('AllocationProtect', wt.DWORD),
                ('PartitionId', wt.WORD), ('RegionSize', ctypes.c_size_t), ('State', wt.DWORD), ('Protect', wt.DWORD), ('Type', wt.DWORD)]

def enable_debug_priv():
    class LUID(ctypes.Structure): _fields_ = [('Low', wt.DWORD), ('High', wt.LONG)]
    class TP(ctypes.Structure): _fields_ = [('Count', wt.DWORD), ('Luid', LUID), ('Attr', wt.DWORD)]
    tok, luid = wt.HANDLE(), LUID()
    a32.OpenProcessToken(k32.GetCurrentProcess(), 0x28, ctypes.byref(tok))
    a32.LookupPrivilegeValueW(None, 'SeDebugPrivilege', ctypes.byref(luid))
    a32.AdjustTokenPrivileges(tok, False, ctypes.byref(TP(1, luid, 2)), 0, None, None)

def main():
    out = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq mk_legacy_kollection.exe', '/FO', 'CSV', '/NH'],
                         capture_output=True, text=True).stdout
    if '","' not in out:
        sys.exit('Oyun calismiyor. Once oyunu acip ana menuye gelin.')
    enable_debug_priv()
    h = k32.OpenProcess(0x0410, False, int(out.split('","')[1]))
    if not h:
        sys.exit('Oyun bellegine erisilemedi. Bu betigi yonetici olarak calistirin.')
    addr, m = 0, MBI()
    while k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(m), ctypes.sizeof(m)):
        if m.State == 0x1000 and m.Protect & 0xEE and not m.Protect & 0x100 and m.RegionSize >= SIZE:
            buf, rd = ctypes.create_string_buffer(m.RegionSize), ctypes.c_size_t()
            if k32.ReadProcessMemory(h, ctypes.c_void_p(m.BaseAddress), buf, m.RegionSize, ctypes.byref(rd)):
                data, i = buf.raw[:rd.value], 0
                while (i := data.find(HEADER, i)) != -1:
                    if zlib.crc32(data[i:i + SIZE]) == CRC:
                        open(OUT, 'wb').write(data[i:i + SIZE])
                        print('Tamam:', OUT); return
                    i += 1
        addr = (m.BaseAddress or 0) + m.RegionSize
    sys.exit('Dosya bellekte bulunamadi. Oyun zaten yamaliysa once Orijinale_Geri_Don.bat calistirin; degilse ana menuye gelip tekrar deneyin.')

if __name__ == '__main__':
    main()
