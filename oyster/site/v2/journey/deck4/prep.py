"""Crops the exporter's pictures for the deck: each element to its visible extent (and the SELFTAC hero into its two
monomers when they are apart), each background to a JPEG. Writes out/c/ and out/prep.json (rectangles in page px).
Usage: python prep.py"""
import json, os
import numpy as np
from PIL import Image
from scipy import ndimage
D = os.path.dirname(os.path.abspath(__file__)) + '/out/'
K = json.load(open(D + 'keys.json')); PR = 2
os.makedirs(D + 'c', exist_ok=True)
out = []
for n, k in enumerate(K['keys']):
    els = {}
    bg = Image.open(f'{D}k{n}/bg.png').convert('RGB').resize((2880, 1620), Image.LANCZOS)
    bg.save(f'{D}c/k{n}_bg.jpg', quality=90, optimize=True, progressive=True)
    for name in k['names']:
        im = Image.open(f'{D}k{n}/{name}.png').convert('RGBA'); a = np.array(im)[:, :, 3]
        mask = a > 6
        if not mask.any(): continue
        parts = [(name, mask)]
        if name == 'mol':   # two monomers apart: one picture each, left to right
            lab, m = ndimage.label(ndimage.binary_dilation(mask, iterations=6))
            sizes = ndimage.sum(mask, lab, range(1, m + 1)); big = [i + 1 for i in np.argsort(sizes)[::-1][:2] if sizes[i] > .15 * sizes.max()]
            if len(big) == 2:
                cx = lambda i: ndimage.center_of_mass(lab == i)[1]
                big.sort(key=cx); parts = [('molA', mask & (lab == big[0])), ('molB', mask & (lab == big[1]))]
        for nm, mk in parts:
            ys, xs = np.where(mk); pad = 8
            x0, y0, x1, y1 = max(0, xs.min() - pad), max(0, ys.min() - pad), min(a.shape[1], xs.max() + pad + 1), min(a.shape[0], ys.max() + pad + 1)
            arr = np.array(im)[y0:y1, x0:x1].copy()
            if nm != name: arr[:, :, 3] = arr[:, :, 3] * ndimage.binary_dilation(mk[y0:y1, x0:x1], iterations=4)
            Image.fromarray(arr).save(f'{D}c/k{n}_{nm}.png', optimize=True)
            els[nm] = [x0 / PR, y0 / PR, (x1 - x0) / PR, (y1 - y0) / PR]
    out.append({'els': els})
    print(n, ' '.join(f'{e}' for e in els))
json.dump({'W': K['W'], 'H': K['H'], 'keys': out}, open(D + 'prep.json', 'w'), indent=1)
