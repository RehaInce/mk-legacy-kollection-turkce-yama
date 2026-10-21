# Copy the arcade MK1 ROMs out of the running game's memory (they are decrypted there).
# Run as administrator while arcade Mortal Kombat is open in the collection.
import os, sys
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
sys.path.insert(0, os.path.dirname(here))
import romlib
from patch_rom import FILES

if __name__ == '__main__':
    romlib.extract(FILES, here)
