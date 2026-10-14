"""Recover the marker coordinates of the archived v5 parity grid.

Source: COMA/scatter_grid_desc_vs_emb_modified.png, the full-resolution original of the
raster used as manuscript Figure 4 (5370x3570; the manuscript copy is a 1280px JPEG with
row and column labels added around it). The underlying predictions are not in the
repository and the v18 reconstruction reports different metrics and has no descriptor arm,
so the raster is the only surviving record of these points.

Panels are located from their black spines, the data transform from the tick marks, and
markers from their fill colour (#629fca). Overlapping markers are split by blob area.
Extraction is accepted only if the recomputed R2, RMSE and MAE reproduce the values
printed inside each panel.
"""
from pathlib import Path
import json, hashlib
import numpy as np, pandas as pd
from PIL import Image
from scipy import ndimage
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

Image.MAX_IMAGE_PIXELS = None
ROOT = Path(__file__).resolve().parent
SRC = ROOT.parent.parent / 'scatter_grid_desc_vs_emb_modified.png'
OUT = ROOT / 'figure4_marker_coordinates.csv'

ROWS = ['Descriptors', 'Embeddings']
COLS = ['No labels', 'One-hot encoded labels', 'OpenAI embeddings labels']
# values printed inside each panel of the archived raster
PRINTED = {('Descriptors', 'No labels'): (0.476, 1.58, 1.18),
           ('Descriptors', 'One-hot encoded labels'): (0.559, 1.55, 1.14),
           ('Descriptors', 'OpenAI embeddings labels'): (0.616, 1.45, 1.06),
           ('Embeddings', 'No labels'): (0.384, 1.48, 1.09),
           ('Embeddings', 'One-hot encoded labels'): (0.719, 1.06, 0.84),
           ('Embeddings', 'OpenAI embeddings labels'): (0.767, 0.97, 0.73)}

a = np.array(Image.open(SRC).convert('RGB')).astype(int)
H, W, _ = a.shape
black = (a.sum(2) < 200)


def runs(idx, gap=10):
    out, s, p = [], idx[0], idx[0]
    for v in idx[1:]:
        if v - p > gap:
            out.append((s, p)); s = v
        p = v
    out.append((s, p)); return out


def longest_run(col):
    best = cur = 0
    for v in col:
        cur = cur + 1 if v else 0
        best = max(best, cur)
    return best


# a spine is one continuous dark line across a whole panel; axis labels and tick text are
# dark too but never continuous for that long
vlen = np.array([longest_run(black[:, x]) for x in range(W)])
hlen = np.array([longest_run(black[y, :]) for y in range(H)])
vx = [int(round((s + e) / 2)) for s, e in runs(np.where(vlen > 1000)[0])]
hy = [int(round((s + e) / 2)) for s, e in runs(np.where(hlen > 1000)[0])]
assert len(vx) == 6 and len(hy) == 4, (vx, hy)
XCOL = [(vx[0], vx[1]), (vx[2], vx[3]), (vx[4], vx[5])]
YROW = [(hy[0], hy[1]), (hy[2], hy[3])]
print('panel x edges', XCOL)
print('panel y edges', YROW)


def ticks(axis, lo, hi, const, depth=22):
    """Tick marks sit just outside the spine; return their pixel centres along the axis."""
    if axis == 'x':
        band = black[const + 4:const + depth, lo + 2:hi - 2]
        idx = np.where(band.sum(0) >= (depth - 4) * .6)[0]
        off = lo + 2
    else:
        band = black[lo + 2:hi - 2, const - depth:const - 4]
        idx = np.where(band.sum(1) >= (depth - 4) * .6)[0]
        off = lo + 2
    return [off + int(round((s + e) / 2)) for s, e in runs(idx, gap=6)]


def affine(pix, vals):
    """Least-squares pixel -> data mapping from tick positions."""
    A = np.vstack([pix, np.ones(len(pix))]).T
    m, c = np.linalg.lstsq(A, np.asarray(vals, float), rcond=None)[0]
    return m, c


# tick label values, read from the rendered figure
XTICKS = {('Descriptors', 0): [0, 2, 4, 6, 8], ('Descriptors', 1): [0, 2, 4, 6, 8],
          ('Descriptors', 2): [0, 2, 4, 6, 8],
          ('Embeddings', 0): [-2, 0, 2, 4, 6, 8], ('Embeddings', 1): [-2, 0, 2, 4, 6],
          ('Embeddings', 2): [-2, 0, 2, 4, 6]}
YTICKS = {('Descriptors', 0): [0, 2, 4, 6, 8], ('Descriptors', 1): [0, 2, 4, 6, 8],
          ('Descriptors', 2): [0, 2, 4, 6, 8],
          ('Embeddings', 0): [-2, 0, 2, 4, 6], ('Embeddings', 1): [-2, 0, 2, 4, 6],
          ('Embeddings', 2): [-2, 0, 2, 4, 6]}

MARKER = np.array([0x62, 0x9f, 0xca])
rows, report = [], []
for ri, row in enumerate(ROWS):
    y0, y1 = YROW[ri]
    for ci, col in enumerate(COLS):
        x0, x1 = XCOL[ci]
        sub = a[y0 + 3:y1 - 2, x0 + 3:x1 - 2]
        d = np.abs(sub - MARKER).sum(2)
        mask = d < 90
        lab, n = ndimage.label(mask, structure=np.ones((3, 3)))
        sizes = ndimage.sum(mask, lab, range(1, n + 1))
        keep = [i for i in range(n) if sizes[i] >= 60]
        unit = float(np.median([sizes[i] for i in keep]))
        pts = []
        for i in keep:
            k = max(1, int(round(sizes[i] / unit)))
            cells = np.argwhere(lab == i + 1)
            if k == 1:
                pts.append(cells.mean(0))
            else:                                    # split a merged blob into k markers
                from scipy.cluster.vq import kmeans2
                cen, _ = kmeans2(cells.astype(float), k, minit='++', seed=0)
                pts.extend(cen)
        pts = np.array(pts)
        px = pts[:, 1] + x0 + 3
        py = pts[:, 0] + y0 + 3
        xt = ticks('x', x0, x1, y1); yt = ticks('y', y0, y1, x0)
        xv, yv = XTICKS[(row, ci)], YTICKS[(row, ci)]
        assert len(xt) == len(xv), (row, col, 'x ticks', len(xt), len(xv))
        assert len(yt) == len(yv), (row, col, 'y ticks', len(yt), len(yv))
        mx, cx = affine(xt, xv); my, cy = affine(yt, yv)
        X = mx * px + cx; Y = my * py + cy
        r2 = r2_score(X, Y); rmse = float(np.sqrt(mean_squared_error(X, Y))); mae = mean_absolute_error(X, Y)
        pr = PRINTED[(row, col)]
        report.append(dict(row=row, col=col, n=len(X), blobs=len(keep), unit_px=unit,
                           R2=round(r2, 3), RMSE=round(rmse, 2), MAE=round(mae, 2),
                           printed_R2=pr[0], printed_RMSE=pr[1], printed_MAE=pr[2]))
        for xx, yy in zip(X, Y):
            rows.append(dict(row=row, col=col, experimental=xx, predicted=yy))

rep = pd.DataFrame(report)
print('\n', rep.to_string(index=False))
rep['dR2'] = (rep.R2 - rep.printed_R2).abs()
rep['dRMSE'] = (rep.RMSE - rep.printed_RMSE).abs()
rep['dMAE'] = (rep.MAE - rep.printed_MAE).abs()
print('\nworst deviation  R2 %.3f  RMSE %.3f  MAE %.3f' % (rep.dR2.max(), rep.dRMSE.max(), rep.dMAE.max()))
ok = bool((rep.dR2 < .02).all() and (rep.dRMSE < .03).all() and (rep.dMAE < .03).all())
print('extraction validated against the printed values:', ok)

df = pd.DataFrame(rows)
df.to_csv(OUT, index=False)
(ROOT / 'figure4_extraction_report.json').write_text(json.dumps(dict(
    source=str(SRC.name), source_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),
    method='panel spines, tick-mark affine calibration, marker-colour blobs split by area',
    validated=ok, panels=report), indent=2))
print('wrote', OUT.name, len(df), 'points')
