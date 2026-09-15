"""
Shrink a photo for the website (JustGuide originals are ~6 MB; the site wants ~100-250 KB).

Usage (from the repo folder):
    python shrink_image.py "C:\\Downloads\\photo.jpg" assets/images/food-tour/wine.jpg
    python shrink_image.py photo.jpg out.jpg --max 900          # smaller long side (default 1200 px)
    python shrink_image.py photo.jpg out.jpg --aspect 4:5       # centre-crop to a ratio first (e.g. 1:1, 4:5, 3:2)

Requires Pillow (already installed):  pip install pillow
"""
import argparse
import os
from PIL import Image, ImageOps

ap = argparse.ArgumentParser()
ap.add_argument('src')
ap.add_argument('out')
ap.add_argument('--max', type=int, default=1200, help='longest side in px (default 1200)')
ap.add_argument('--aspect', default=None, help='centre-crop to W:H before resizing, e.g. 4:5')
ap.add_argument('--quality', type=int, default=80)
a = ap.parse_args()

im = ImageOps.exif_transpose(Image.open(a.src)).convert('RGB')
if a.aspect:
    aw, ah = (int(x) for x in a.aspect.split(':'))
    w, h = im.size
    if w / h > aw / ah:
        nw = int(h * aw / ah); x = (w - nw) // 2; im = im.crop((x, 0, x + nw, h))
    else:
        nh = int(w * ah / aw); y = (h - nh) // 2; im = im.crop((0, y, w, y + nh))
im.thumbnail((a.max, a.max), Image.LANCZOS)
os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
im.save(a.out, 'JPEG', quality=a.quality, optimize=True, progressive=True)
print(f'{a.out}: {im.size[0]}x{im.size[1]} px, {os.path.getsize(a.out) // 1024} KB')
