"""Correct two numbers in Figure 1 (manuscript raster), matching font, size and colour.

  "based on 1500 example"  ->  "based on 1,103 examples"
      the expert annotation set contains 1103 labelled compounds
  "R²:0.53-0.86"           ->  "R²:0.60-0.77"
      per-endpoint R² range of the expert-guided embeddings in their strongest
      configuration (Table 2, multitask + encoded classes), parallel to panel A's
      "0.25-0.68", which is the per-endpoint range of the descriptor row of Table 1.
      No number in the manuscript supports 0.53 or 0.86.

Everything else in the image is left byte-for-byte untouched outside the two patches.
"""
from pathlib import Path
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
SRC = Path(sys.argv[1])
OUT = ROOT / 'figures' / 'figure1_numbers_corrected.png'
FONT = str(ROOT / 'FuturaMedium.ttf')

im = Image.open(SRC).convert('RGB')
a = np.array(im).astype(int)


def ink_color(y0, y1, x0, x1, pred):
    r = a[y0:y1, x0:x1].reshape(-1, 3)
    sel = r[pred(r)]
    lum = sel.sum(1)
    c = np.median(sel[lum <= np.percentile(lum, 30)], 0).astype(int)
    return tuple(int(v) for v in c)


def extent(y0, y1, x0, x1, pred):
    m = pred(a[y0:y1, x0:x1])
    ys, xs = np.where(m)
    return x0 + xs.min(), x0 + xs.max(), y0 + ys.min(), y0 + ys.max()


def font_for_height(text_probe, target_px):
    best = None
    for s in np.arange(10, 40, 0.25):
        f = ImageFont.truetype(FONT, size=float(s))
        l, t, r, b = f.getbbox(text_probe)
        if best is None or abs((b - t) - target_px) < abs(best[1] - target_px):
            best = (f, b - t, s)
    return best


dark = lambda r: r.sum(-1) < 380
purple = lambda r: (r[..., 2] > r[..., 1] + 25) & (r.sum(-1) < 450)
draw = ImageDraw.Draw(im)

# ---------- 1) R² range in panel B property box: replace only the digits ----------
x0, x1, y0, y1 = extent(731, 753, 1078, 1290, purple)          # "0.53-0.86"
col_p = ink_color(731, 753, 1078, 1290, purple)
f, h, s = font_for_height('0', y1 - y0 + 1)
l, t, r, b = f.getbbox('0.53-0.86')
print(f'R2 digits: box x{x0}-{x1} y{y0}-{y1}; font {s:.2f}px; width old {x1-x0+1} vs rendered {r-l}')
draw.rectangle([x0 - 2, y0 - 3, x1 + 3, y1 + 3], fill=(255, 255, 255))
new = '0.60-0.77'
nl, nt, nr, nb = f.getbbox(new)
draw.text((x0 - nl, y1 + 1 - nb), new, font=f, fill=col_p)

# ---------- 2) caption under the expert icon in panel B: re-centre the whole line ----------
cx0, cx1, cy0, cy1 = extent(783, 804, 400, 680, dark)          # "based on 1500 example"
col_d = ink_color(783, 804, 400, 680, dark)
# baseline = bottom of the 'b' (no descender); find it from the first glyph column block
first = a[783:804, cx0:cx0 + 8]
bx = np.where(dark(first).any(1))[0]
baseline = 783 + bx.max()
fc, hc, sc = font_for_height('b', baseline - cy0 + 1)
old = 'based on 1500 example'
ol, ot, orr, ob = fc.getbbox(old)
print(f'caption: x{cx0}-{cx1} y{cy0}-{cy1} baseline {baseline}; font {sc:.2f}px; width old {cx1-cx0+1} vs rendered {orr-ol}')
centre = (cx0 + cx1) / 2
draw.rectangle([cx0 - 3, cy0 - 1, cx1 + 3, cy1 + 3], fill=(255, 255, 255))   # line above ends at cy0 - 3
new2 = 'based on 1,103 examples'
l2, t2, r2, b2 = fc.getbbox(new2)
asc = fc.getbbox('b')[3]                                         # baseline offset of 'b'
draw.text((centre - (r2 - l2) / 2 - l2, baseline - asc), new2, font=fc, fill=col_d)

OUT.parent.mkdir(exist_ok=True)
im.save(OUT, optimize=True)
print('ink colours', col_p, col_d, '| saved', OUT)
