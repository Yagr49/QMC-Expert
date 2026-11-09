#!/usr/bin/env python3
"""Figure: six adaptation strategies for the pretrained MolFormer-XL encoder.

Layout: 2 rows x 3 columns of strategy panels + a full-width joint CatBoost
decoder band underneath. Single fixed-coordinate Axes (0..130 x 0..90),
13 x 8.5 in canvas. Text is English only.

Outputs (next to this script):
  fig_architectures_adapters_finetuning.pdf / .svg / .png (300 dpi)
"""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon
from matplotlib.path import Path
from matplotlib.patches import PathPatch

plt.rcParams.update(
    {
        "font.family": "Arial",
        "font.size": 7,
        "text.color": "#1A1A1A",
        "pdf.fonttype": 42,
        "svg.fonttype": "none",
    }
)

# ---------------------------------------------------------------- palette ---
FROZEN, FROZEN_E = "#35618C", "#24425F"   # frozen backbone
EXT, EXT_E = "#D5753B", "#9C5226"         # trainable external modules
BB, BB_E = "#63A653", "#3F7034"           # trainable backbone weights
HEAD, HEAD_E = "#7E2F8E", "#571F63"       # task head wedge
PANEL_BG, PANEL_E = "#FAFAFA", "#D9D9D9"
HI_BG = "#FBF1E8"                          # highlighted panel (feature adapter)
FLOW = "#4D4D4D"                           # data-flow arrows
ROUTE = "#9E9E9E"                          # decoder collector lines
INK = "#1A1A1A"
GRAY = "#595959"

EDGE_OF = {FROZEN: FROZEN_E, EXT: EXT_E, BB: BB_E, HEAD: HEAD_E}

# ---------------------------------------------------------------- canvas ----
FIG_W, FIG_H = 13.0, 8.5
XMAX, YMAX = 130.0, 90.0

fig = plt.figure(figsize=(FIG_W, FIG_H))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, XMAX)
ax.set_ylim(0, YMAX)
ax.axis("off")
MUT = (FIG_H / YMAX) / (FIG_W / XMAX)  # corner-rounding aspect compensation


# ------------------------------------------------------------- primitives ---
def box(x, y, w, h, fc, ec, lw=1.1, rs=0.45, z=3, ls="-"):
    p = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0,rounding_size={rs}",
        mutation_aspect=MUT,
        fc=fc,
        ec=ec,
        lw=lw,
        zorder=z,
        linestyle=ls,
    )
    ax.add_patch(p)
    return p


def txt(x, y, s, size=7, weight="normal", color=INK, ha="center", va="center",
        rot=0, style="normal", z=6):
    return ax.text(
        x, y, s,
        fontsize=size, fontweight=weight, color=color,
        ha=ha, va=va, rotation=rot, fontstyle=style, zorder=z,
        linespacing=1.3,
    )


def arrow(p1, p2, color=FLOW, lw=1.15, ms=8, z=4):
    a = FancyArrowPatch(
        p1, p2, arrowstyle="-|>", mutation_scale=ms,
        lw=lw, color=color, zorder=z, shrinkA=0, shrinkB=0,
    )
    ax.add_patch(a)


def route(points, color=ROUTE, lw=1.05, z=2.4):
    """Polyline elbow connector with an arrowhead on the final segment."""
    pts = [tuple(p) for p in points]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, zorder=z,
            solid_capstyle="round", solid_joinstyle="round")
    arrow(pts[-2], pts[-1], color=color, lw=lw, ms=7, z=z)


def snowflake(x, y, r=0.75, color="white", lw=1.0, z=8):
    """Six-armed snowflake drawn with lines (3 axes + V-shaped branch tips)."""
    for th in (0.0, np.pi / 3, 2 * np.pi / 3):
        dx, dy = np.cos(th), np.sin(th)
        ax.plot([x - r * dx, x + r * dx], [y - r * dy, y + r * dy],
                color=color, lw=lw, zorder=z, solid_capstyle="round")
        for tip in (1, -1):
            phi = th if tip == 1 else th + np.pi
            tx, ty = x + tip * r * dx, y + tip * r * dy
            for dev in (0.68, -0.68):
                a = phi + np.pi + dev
                ax.plot([tx, tx + 0.42 * r * np.cos(a)],
                        [ty, ty + 0.42 * r * np.sin(a)],
                        color=color, lw=lw * 0.9, zorder=z,
                        solid_capstyle="round")


def rbrace(x, y0, y1, w=1.7, color=EXT_E, lw=1.3, z=5):
    """Right-pointing curly brace '}' spanning [y0, y1], tip to the right."""
    ym = 0.5 * (y0 + y1)
    hh = 0.5 * (y1 - y0)

    def cub(p0, p1, p2, p3, n=26):
        t = np.linspace(0, 1, n)[:, None]
        return ((1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1
                + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3)

    top = cub(np.array([x, y1]), np.array([x + 0.85 * w, y1 - 0.03 * hh]),
              np.array([x + w, ym + 0.34 * hh]), np.array([x + 0.10 * w, ym + 0.05 * hh]))
    bot = cub(np.array([x + 0.10 * w, ym - 0.05 * hh]),
              np.array([x + w, ym - 0.34 * hh]), np.array([x + 0.85 * w, y0 + 0.03 * hh]),
              np.array([x, y0]))
    pts = np.vstack([top, bot])
    ax.plot(pts[:, 0], pts[:, 1], color=color, lw=lw, zorder=z,
            solid_capstyle="round")


def wedge_right(x, y, w, h, label="4"):
    ax.add_patch(Polygon([(x, y), (x, y + h), (x + w, y + h / 2)],
                         closed=True, fc=HEAD, ec=HEAD_E, lw=1.2, zorder=5))
    txt(x + 0.34 * w, y + h / 2, label, size=7.5, weight="bold", color="white", z=6)


def wedge_down(x, y, w, h, label="4"):
    ax.add_patch(Polygon([(x, y + h), (x + w, y + h), (x + w / 2, y)],
                         closed=True, fc=HEAD, ec=HEAD_E, lw=1.2, zorder=5))
    txt(x + w / 2, y + 0.62 * h, label, size=7.5, weight="bold", color="white", z=6)


# ----------------------------------------------------- MolFormer stack ------
def molformer_stack(x0, w, emb_y, emb_h, blk_h, blk_gap, blk_colors, ln_color):
    """Compact MolFormer-XL stack, embeddings at the bottom, LN on top.

    Returns dict of anchor coordinates (data units).
    """
    box(x0, emb_y, w, emb_h, FROZEN, FROZEN_E, rs=0.18)
    txt(x0 + w / 2, emb_y + emb_h / 2, "emb", size=6, weight="bold",
        color="white")
    y = emb_y + emb_h + blk_gap
    for i in range(12):
        c = blk_colors[i]
        box(x0, y, w, blk_h, c, EDGE_OF[c], rs=0.14)
        y += blk_h + blk_gap
    box(x0, y, w, 1.4, ln_color, EDGE_OF[ln_color], rs=0.14)
    txt(x0 + w / 2, y + 0.7, "LN", size=5.5, weight="bold", color="white")
    return {
        "x0": x0, "x1": x0 + w, "xm": x0 + w / 2,
        "emb_mid": (x0, emb_y + emb_h / 2),
        "ln_y0": y, "ln_y1": y + 1.4, "ln_mid_right": (x0 + w, y + 0.7),
        "ln_center": (x0 + w, y + 0.7),
        "blk_top_y": y - blk_gap,
    }


def smiles_box(x, y, w=5.5, h=3.0):
    box(x, y, w, h, "white", "#8A8A8A", lw=1.0)
    txt(x + w / 2, y + h / 2, "SMILES", size=6.8, weight="bold")


MF_LABEL = "MolFormer-XL \u00B7 768-d \u00B7 44.4M"


def molformer_label(xm, y):
    txt(xm, y, MF_LABEL, size=6.2, color=GRAY)


# ------------------------------------------------------------- panel base ---
COL_X0 = [3.0, 47.0, 91.0]
COL_C = [22.0, 66.0, 110.0]
PAN_W = 38.0
A_Y0, A_Y1 = 57.0, 79.0
B_Y0, B_Y1 = 18.7, 48.5


def panel(x0, y0, w, h, highlight=False):
    if highlight:
        box(x0, y0, w, h, HI_BG, EXT, lw=1.6, rs=0.9, z=1)
    else:
        box(x0, y0, w, h, PANEL_BG, PANEL_E, lw=1.0, rs=0.9, z=1)


def num_circle(cx, cy, n, color, r=1.3):
    ax.add_patch(Circle((cx, cy), r, fc=color, ec="white", lw=1.2, zorder=8))
    txt(cx, cy - 0.05, str(n), size=9, weight="bold", color="white", z=9)


def captions(cx, lines, ys):
    for s, y in zip(lines, ys):
        txt(cx, y, s, size=7, color=INK)


CAP2 = [55.7, 54.5]
CAP3 = [56.1, 54.9, 53.7]

# ============================================================== ROW A =======
A_BLK_H, A_BLK_GAP, A_EMB_Y = 0.85, 0.12, 59.7
A_TITLE_Y, A_LAB_Y = 77.2, 75.6

# ---------------------------------------------------------- panel 1 ---------
x0 = COL_X0[0]
panel(x0, A_Y0, PAN_W, A_Y1 - A_Y0)
num_circle(COL_C[0], 80.9, 1, FROZEN)
txt(COL_C[0], A_TITLE_Y, "LINEAR PROBE", size=9, weight="bold")
smiles_box(x0 + 2, 58.1)
st = molformer_stack(x0 + 12, 6.5, A_EMB_Y, 1.8, A_BLK_H, A_BLK_GAP,
                     [FROZEN] * 12, FROZEN)
arrow((x0 + 7.5, 60.6), (st["x0"], 60.6))
snowflake(st["x1"] - 0.9, 60.6, r=0.7)
molformer_label(st["xm"], A_LAB_Y)
ln_y = st["ln_center"][1]
box(x0 + 23, 73.4, 7.5, 1.5, EXT, EXT_E)
txt(x0 + 26.75, 74.15, "LayerNorm", size=6.4, weight="bold", color="white")
arrow(st["ln_center"], (x0 + 23, ln_y))
txt(x0 + 21.6, 73.35, "768", size=6.2, color=GRAY, ha="right")
wedge_right(x0 + 32.5, 72.15, 5.2, 4.0)
arrow((x0 + 30.5, 74.15), (x0 + 32.5, 74.15))
captions(COL_C[0], ["LN + Linear(4)", "4,612 params"], CAP2)

# ---------------------------------------------------------- panel 2 ---------
x0 = COL_X0[1]
panel(x0, A_Y0, PAN_W, A_Y1 - A_Y0)
num_circle(COL_C[1], 80.9, 2, EXT)
txt(COL_C[1], A_TITLE_Y, "COMPACT MLP HEAD", size=9, weight="bold")
smiles_box(x0 + 2, 58.1)
st = molformer_stack(x0 + 12, 6.5, A_EMB_Y, 1.8, A_BLK_H, A_BLK_GAP,
                     [FROZEN] * 12, FROZEN)
arrow((x0 + 7.5, 60.6), (st["x0"], 60.6))
snowflake(st["x1"] - 0.9, 60.6, r=0.7)
molformer_label(st["xm"], A_LAB_Y)
box(x0 + 23, 73.1, 7.5, 1.4, EXT, EXT_E)
txt(x0 + 26.75, 73.8, "LayerNorm", size=6.4, weight="bold", color="white")
arrow(st["ln_center"], (x0 + 23, st["ln_center"][1]))
txt(x0 + 21.9, 73.5, "768", size=6.2, color=GRAY, ha="right")
box(x0 + 23, 70.6, 7.5, 1.9, EXT, EXT_E)
txt(x0 + 26.75, 71.55, "Linear 256\nGELU + Dropout", size=5.8, color="white")
box(x0 + 23, 68.1, 7.5, 1.9, EXT, EXT_E)
txt(x0 + 26.75, 69.05, "Linear 128\nGELU + Dropout", size=5.8, color="white")
arrow((x0 + 26.75, 73.1), (x0 + 26.75, 72.55))
arrow((x0 + 26.75, 70.6), (x0 + 26.75, 70.05))
arrow((x0 + 26.75, 68.1), (x0 + 26.75, 67.4))
wedge_down(x0 + 24.15, 64.3, 5.2, 3.0)
captions(COL_C[1], ["LN \u2192 256 \u2192 128 \u2192 4", "231,812 params"], CAP2)

# ---------------------------------------------------------- panel 3 ---------
x0 = COL_X0[2]
panel(x0, A_Y0, PAN_W, A_Y1 - A_Y0, highlight=True)
num_circle(COL_C[2], 80.9, 3, EXT)
txt(COL_C[2], A_TITLE_Y, "FEATURE ADAPTER (contrastive)", size=9, weight="bold")
smiles_box(x0 + 2, 58.1)
st = molformer_stack(x0 + 12, 6.5, A_EMB_Y, 1.8, A_BLK_H, A_BLK_GAP,
                     [FROZEN] * 12, FROZEN)
arrow((x0 + 7.5, 60.6), (st["x0"], 60.6))
snowflake(st["x1"] - 0.9, 60.6, r=0.7)
molformer_label(st["xm"], A_LAB_Y)
ad_x, ad_y, ad_w, ad_h = x0 + 22.5, 62.8, 8.0, 10.6
box(ad_x, ad_y, ad_w, ad_h, EXT, EXT_E)
txt(ad_x + ad_w / 2, ad_y + ad_h - 1.3, "Adapter MLP", size=7, weight="bold",
    color="white")
txt(ad_x + ad_w / 2, ad_y + ad_h - 3.1, "768 \u2192 512", size=6.4, color="white")
txt(ad_x + ad_w / 2, ad_y + ad_h - 4.3, "\u2192 384 \u2192 256", size=6.4,
    color="white")
txt(ad_x + ad_w / 2, ad_y + 1.7, "guided embedding\n256-d", size=5.9,
    color="white")
elbow = [st["ln_center"], (st["x1"] + 1.7, st["ln_center"][1]),
         (st["x1"] + 1.7, 68.3), (ad_x, 68.3)]
for p, q in zip(elbow[:-1], elbow[1:]):
    arrow(p, q) if q == elbow[-1] else ax.plot(
        [p[0], q[0]], [p[1], q[1]], color=FLOW, lw=1.15, zorder=4,
        solid_capstyle="round")
txt(st["x1"] + 2.05, 70.2, "768", size=6.2, color=GRAY, ha="left")
rbrace(ad_x + ad_w + 0.8, ad_y, ad_y + ad_h)
txt(ad_x + ad_w + 2.65, ad_y + ad_h / 2, "supervised contrastive", size=6.3,
    rot=90, color=EXT_E)
txt(ad_x + ad_w + 4.35, ad_y + ad_h / 2, "+ Borderline SMOTE", size=6.3,
    rot=90, color=EXT_E)
wedge_down(ad_x + ad_w / 2 - 2.6, 58.9, 5.2, 2.7)
arrow((ad_x + ad_w / 2, ad_y), (ad_x + ad_w / 2, 61.75))
txt(ad_x + ad_w / 2 + 1.1, 62.3, "256", size=6.2, color=GRAY, ha="left")
captions(COL_C[2],
         ["MLP 768\u2192512\u2192384\u2192256",
          "sup. contrastive + Borderline SMOTE",
          "691,584 params (contrastive: 741,504)"],
         CAP3)

# ============================================================== ROW B =======
B_BLK_H, B_BLK_GAP, B_EMB_Y = 0.74, 0.12, 32.7
B_TITLE_Y, B_LAB_Y = 47.7, 31.3
WEDGE_Y, WEDGE_H = 44.0, 2.4

# ---------------------------------------------------------- panel 4 ---------
x0 = COL_X0[0]
panel(x0, B_Y0, PAN_W, B_Y1 - B_Y0)
num_circle(COL_C[0], 49.9, 4, BB, r=1.2)
txt(COL_C[0], B_TITLE_Y, "LoRA", size=9, weight="bold")
smiles_box(x0 + 2, 32.1)
st = molformer_stack(x0 + 12, 6.5, B_EMB_Y, 1.8, B_BLK_H, B_BLK_GAP,
                     [FROZEN] * 12, FROZEN)
arrow((x0 + 7.5, 33.6), (st["x0"], 33.6))
snowflake(st["x0"] + 0.85, st["ln_center"][1], r=0.7)
molformer_label(st["xm"], B_LAB_Y)
for cy in (43.55, 40.30, 36.70):
    box(x0 + 16.6, cy - 0.5, 2.8, 1.0, BB, BB_E, lw=0.9, rs=0.2, z=5)
ax.plot([x0 + 19.4, x0 + 22.2], [40.30, 40.30], color=BB_E, lw=1.0,
        ls=(0, (3, 2)), zorder=4)
txt(x0 + 22.5, 41.15, "LoRA \u00D724 (Q/V)", size=6.6, ha="left")
txt(x0 + 22.5, 39.45, "rank 8, \u03B1 = 16", size=6.4, ha="left")
wy = WEDGE_Y + WEDGE_H / 2
arrow((st["x1"], 45.2), (x0 + 23, 45.2))
txt(st["x1"] + 0.9, 44.45, "768", size=6.2, color=GRAY,
    ha="left")
wedge_right(x0 + 23, WEDGE_Y, 5.6, WEDGE_H)
captions(COL_C[0], ["LoRA rank 8, \u03B1 = 16", "Q/V of all 12 blocks",
                    "299,524 params"], [18.0, 16.8, 15.6])

# ---------------------------------------------------------- panel 5 ---------
x0 = COL_X0[1]
panel(x0, B_Y0, PAN_W, B_Y1 - B_Y0)
num_circle(COL_C[1], 49.9, 5, BB, r=1.2)
txt(COL_C[1], B_TITLE_Y, "PARTIAL FINE-TUNING", size=9, weight="bold")
smiles_box(x0 + 2, 32.1)
blk5 = [FROZEN] * 4 + [BB] * 8
st = molformer_stack(x0 + 12, 6.5, B_EMB_Y, 1.8, B_BLK_H, B_BLK_GAP,
                     blk5, BB)
arrow((x0 + 7.5, 33.6), (st["x0"], 33.6))
snowflake(st["x0"] + 0.85, 35.7, r=0.7)
molformer_label(st["xm"], B_LAB_Y)
arrow((st["x1"], 45.2), (x0 + 23, 45.2))
txt(st["x1"] + 0.9, 44.45, "768", size=6.2, color=GRAY,
    ha="left")
wedge_right(x0 + 23, WEDGE_Y, 5.6, WEDGE_H)
captions(COL_C[1], ["freeze emb + blocks 0\u20133", "train blocks 4\u201311 + LN",
                    "28.4M params"], [18.0, 16.8, 15.6])

# ---------------------------------------------------------- panel 6 ---------
x0 = COL_X0[2]
panel(x0, B_Y0, PAN_W, B_Y1 - B_Y0)
num_circle(COL_C[2], 49.9, 6, BB, r=1.2)
txt(COL_C[2], B_TITLE_Y, "FULL FINE-TUNING", size=9, weight="bold")
smiles_box(x0 + 2, 32.1)
st = molformer_stack(x0 + 12, 6.5, B_EMB_Y, 1.8, B_BLK_H, B_BLK_GAP,
                     [BB] * 12, BB)
arrow((x0 + 7.5, 33.6), (st["x0"], 33.6))
molformer_label(st["xm"], B_LAB_Y)
arrow((st["x1"], 45.2), (x0 + 23, 45.2))
txt(st["x1"] + 0.9, 44.45, "768", size=6.2, color=GRAY,
    ha="left")
wedge_right(x0 + 23, WEDGE_Y, 5.6, WEDGE_H)
captions(COL_C[2], ["all backbone layers", "44.4M params"], [17.7, 16.5])

# ==================================================== decoder collector =====
ENTRIES = [40.0, 52.0, 64.0, 74.0, 84.0, 94.0]
# row A exits -> short stubs below the panels, then elbow routes through the
# two inter-column corridors (x ~ 44 and 87/89) down to the decoder top edge
route([(39.0, 57.2), (44.0, 57.2), (44.0, 12.2),
       (ENTRIES[0], 12.2), (ENTRIES[0], 10.55)])
route([(80.0, 57.5), (89.0, 57.5), (89.0, 12.2),
       (ENTRIES[1], 12.2), (ENTRIES[1], 10.55)])
route([(100.0, 57.2), (87.0, 57.2), (87.0, 12.2),
       (ENTRIES[2], 12.2), (ENTRIES[2], 10.55)])
# row B exits -> short drops onto the decoder top edge
route([(5.8, B_Y0), (5.8, 13.5), (ENTRIES[3], 13.5), (ENTRIES[3], 10.55)])
route([(49.8, B_Y0), (49.8, 14.5), (ENTRIES[4], 14.5), (ENTRIES[4], 10.55)])
route([(94.2, B_Y0), (94.2, 10.55)])

box(32.0, 4.0, 70.0, 6.5, "#FFFFFF", INK, lw=1.3, rs=0.7, z=3)
txt(67.0, 8.5, "JOINT CATBOOST DECODER", size=8.5, weight="bold")
txt(67.0, 7.0, "gradient boosting \u00B7 300 iterations \u00B7 depth 5", size=6.8)
txt(67.0, 5.6, "pooled representations from all six strategies", size=6.3,
    color=GRAY)

box(6.0, 6.0, 24.0, 3.2, "#FFFFFF", "#8A8A8A", lw=1.0)
txt(18.0, 8.25, "task metadata", size=7, weight="bold")
txt(18.0, 6.95, "(one-hot / text embeddings)", size=6.2, color=GRAY)
arrow((30.0, 7.6), (32.0, 7.6))

box(104.0, 5.8, 24.0, 3.4, "#FFFFFF", "#8A8A8A", lw=1.0)
txt(116.0, 8.3, "pMIC \u2014 4 endpoints", size=7.5, weight="bold")
txt(116.0, 6.9, "S. aureus / E. coli \u00D7 MIC / MBC", size=6.2, color=GRAY)
arrow((102.0, 7.5), (104.0, 7.5))

txt(67.0, 2.4, "task heads also allow zero-shot direct inference",
    size=6.5, style="italic", color=GRAY)

# ============================================================ headers =======
txt(3.0, 83.4, "A \u2014 Adapter-based adaptation (backbone frozen)",
    size=11, weight="bold", ha="left")
txt(3.0, 52.2, "B \u2014 Fine-tuning (backbone weights updated)",
    size=11, weight="bold", ha="left")

txt(3.0, 88.4, "Adaptation strategies for the pretrained MolFormer-XL encoder",
    size=13, weight="bold", ha="left")
txt(3.0, 86.2,
    "Shared: SMILES \u2192 MolFormer-XL (44.4M, 768-d) \u2192 adaptation "
    "\u2192 task head \u2192 joint decoder",
    size=8, ha="left", color=GRAY)

# ============================================================= legend =======
def legend_swatch(x, y, fc, ec):
    box(x, y - 0.65, 2.0, 1.3, fc, ec, lw=1.0, rs=0.25, z=6)


ly1, ly2 = 88.4, 86.0
legend_swatch(64.0, ly1, FROZEN, FROZEN_E)
txt(66.8, ly1, "frozen", size=7.5, ha="left")
legend_swatch(73.5, ly1, EXT, EXT_E)
txt(76.3, ly1, "trainable (external)", size=7.5, ha="left")
legend_swatch(89.5, ly1, BB, BB_E)
txt(92.3, ly1, "trainable (backbone)", size=7.5, ha="left")
legend_swatch(64.0, ly2, HEAD, HEAD_E)
txt(66.8, ly2, "task head", size=7.5, ha="left")
ax.add_patch(Circle((76.6, ly2), 1.0, fc=FROZEN, ec=FROZEN_E, lw=1.0, zorder=6))
snowflake(76.6, ly2, r=0.62, z=7)
txt(78.4, ly2, "frozen weights", size=7.5, ha="left")

# --------------------------------------------------------------- save -------
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "fig_architectures_adapters_finetuning")
fig.savefig(OUT + ".pdf")
fig.savefig(OUT + ".svg")
fig.savefig(OUT + ".png", dpi=300)
print("saved:", OUT + ".pdf", OUT + ".svg", OUT + ".png")
