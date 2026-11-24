"""Crops the exporter's pictures for the deck: each element to its visible extent, each background to a JPEG. The SELFTAC
hero is always cut into its two halves (the perpendicular bisector of its two heads, so a dimer is cut at its clasp),
so Morph carries each half from the dimer into its monomer. Writes out/c/ and out/prep.json (rectangles in page px).
Usage: python prep.py"""
import json, os
import numpy as np
from PIL import Image
from scipy import ndimage
D = os.path.dirname(os.path.abspath(__file__)) + '/out/'
K = json.load(open(D + 'keys.json')); PR = 2
K['keys'].sort(key=lambda q: q['k'])   # story order (the in-between moments were captured last)
os.makedirs(D + 'c', exist_ok=True)
out = []
for n, k in enumerate(K['keys']):
    els = {}
    bg = Image.open(f"{D}{k['dir']}/bg.png").convert('RGB').resize((2880, 1620), Image.LANCZOS)
    bg.save(f'{D}c/k{n}_bg.jpg', quality=90, optimize=True, progressive=True)
    for name in k['names']:
        im = Image.open(f"{D}{k['dir']}/{name}.png").convert('RGBA'); a = np.array(im)[:, :, 3]
        mask = a > 6
        if not mask.any(): continue
        parts = [(name, mask)]
        if name == 'mol':   # the two halves: each pixel to the nearer head (head 0 is always half A)
            (ax, ay), (bx, by) = [(x * PR, y * PR) for x, y in k['heads']]
            # cut between the two gold clasp pearls (each half keeps its own), across the line joining them
            rgb = np.array(im)[:, :, :3].astype(int)
            gold = (a > 200) & (rgb[:, :, 0] > 170) & (rgb[:, :, 1] > 110) & (rgb[:, :, 1] < 200) & (rgb[:, :, 2] < 120) & (rgb[:, :, 0] - rgb[:, :, 2] > 90)
            lab, m = ndimage.label(gold)
            if m:
                sz = ndimage.sum(gold, lab, range(1, m + 1)); top = np.argsort(sz)[::-1] + 1
                if m == 1 or sz[top[1] - 1] < .3 * sz[top[0] - 1]:   # joined: pearl, bond, pearl in one piece; cut at its middle
                    ys, xs = np.where(lab == top[0]); ux, uy = bx - ax, by - ay; L = (ux * ux + uy * uy) ** .5; ux, uy = ux / L, uy / L
                    t = (xs - ax) * ux + (ys - ay) * uy; mid = (t.min() + t.max()) / 2
                    cx, cy = ax + ux * mid, ay + uy * mid
                    ax, ay, bx, by = cx - ux, cy - uy, cx + ux, cy + uy
            yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
            side = (xx - (ax + bx) / 2) * (bx - ax) + (yy - (ay + by) / 2) * (by - ay) < 0
            parts = [('molA', mask & side), ('molB', mask & ~side)]
            parts = [q for q in parts if q[1].sum() > 200]
        if name == 'debris' and k['k'] < .7: parts = [('flash', mask)]   # before the degradation, the only loose mesh is the split's flash ring
        for nm, mk in parts:
            ys, xs = np.where(mk); pad = 8
            x0, y0, x1, y1 = max(0, xs.min() - pad), max(0, ys.min() - pad), min(a.shape[1], xs.max() + pad + 1), min(a.shape[0], ys.max() + pad + 1)
            arr = np.array(im)[y0:y1, x0:x1].copy()
            if nm != name: arr[:, :, 3] = arr[:, :, 3] * mk[y0:y1, x0:x1]
            Image.fromarray(arr).save(f'{D}c/k{n}_{nm}.png', optimize=True)
            els[nm] = [x0 / PR, y0 / PR, (x1 - x0) / PR, (y1 - y0) / PR]
    out.append({'els': els, 'k': k['k'], 'jump': k['jump']})
    print(n, ' '.join(f'{e}' for e in els))
json.dump({'W': K['W'], 'H': K['H'], 'keys': out}, open(D + 'prep.json', 'w'), indent=1)
