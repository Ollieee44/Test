"""Contour-line wallpaper for the site: the 5T35 ternary complex (BRD4, VHL, Elongin B and C) seen face
on, as the landing story turns it, flattened to a blurred density and traced as nested contour lines,
the same line language as the 3D proteins. Writes contours.svg (paths only, stroke set by the page)."""
import os
import numpy as np
from scipy.ndimage import gaussian_filter
from skimage import measure

D = os.path.dirname(os.path.abspath(__file__)) + '/'
lines = open(D + '../landing/data/5t35.pdb').read().splitlines()
xyz = {c: np.array([[float(l[30:38]), float(l[38:46]), float(l[46:54])] for l in lines
                    if l.startswith('ATOM') and l[21] == c and l[76:78].strip() != 'H']) for c in 'ABCD'}

def rot_between(a, b):
    a = a / np.linalg.norm(a); b = b / np.linalg.norm(b); v = np.cross(a, b); c = a @ b
    K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + K + K @ K / (1 + c)

# the same turn the landing story uses: BRD4 on the left, VHL on the right
R = rot_between(xyz['A'].mean(0) - xyz['D'].mean(0), np.array([-1., 0, 0]))
P = np.concatenate(list(xyz.values())); P = (P - P.mean(0)) @ R.T
xy = P[:, :2] * [1, -1]                         # screen y points down
S = 4.0                                         # grid cells per angstrom
lo = xy.min(0) - 30; hi = xy.max(0) + 30
shape = np.ceil((hi - lo) * S).astype(int) + 1
g = np.zeros(shape[::-1])
ij = np.round((xy - lo) * S).astype(int)
np.add.at(g, (ij[:, 1], ij[:, 0]), 1.0)
g = gaussian_filter(g, 2.4 * S)
paths = []
for lev in np.linspace(.03, .95, 24) * g.max():
    for c in measure.find_contours(g, lev):
        if len(c) < 30: continue
        c = measure.approximate_polygon(c, .6)
        pts = c[:, ::-1] / S
        paths.append('M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + 'Z')
w, h = (hi - lo)
svg = f'<svg class="contours" viewBox="0 0 {w:.0f} {h:.0f}" aria-hidden="true" focusable="false"><path d="{" ".join(paths)}"/></svg>'
open(D + 'contours.svg', 'w').write(svg)
print('contours.svg', len(paths), 'lines', len(svg) // 1024, 'KB')
