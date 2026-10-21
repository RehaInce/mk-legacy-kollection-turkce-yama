# Contact sheet of MAME snapshots:  python sheet.py SNAPDIR OUT.png
import sys, os
from PIL import Image
fs = sorted(os.listdir(sys.argv[1]), key=lambda f: os.path.getmtime(os.path.join(sys.argv[1], f)))
ims = [Image.open(os.path.join(sys.argv[1], f)).convert('RGB').resize((256, 200)) for f in fs]
cols = 6
sheet = Image.new('RGB', (256 * cols, 200 * ((len(ims) + cols - 1) // cols)))
for i, im in enumerate(ims): sheet.paste(im, (256 * (i % cols), 200 * (i // cols)))
sheet.save(sys.argv[2])
