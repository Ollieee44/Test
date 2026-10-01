"""Trace stylised outlines of several ternary-complex poses from PDB 5T35.

Pose 0 is the crystal structure (BRD4 BD2 : MZ1 : VHL : Elongin C : Elongin B).
Further poses rigidly rotate BRD4 about the MZ1 binding site by 18-40 degrees,
rejecting any pose where BRD4 clashes with VHL or the Elongins. Each pose is then
projected along the viewing direction that best separates the proteins, oriented
with BRD4 on the left, and traced as a smoothed outline with inner contour rings.
Put 5t35.pdb (https://files.rcsb.org/download/5T35.pdb) next to this script.
"""
import os, json
import numpy as np
from scipy.ndimage import gaussian_filter
from skimage import measure

D = os.path.dirname(os.path.abspath(__file__)) + '/'
atoms, lig = {}, []
for l in open(D + '5t35.pdb'):
    if l[:6] not in ('ATOM  ', 'HETATM'):
        continue
    el = l[76:78].strip()
    if el == 'H':
        continue
    xyz = [float(l[30:38]), float(l[38:46]), float(l[46:54])]
    if l[:4] == 'ATOM':
        atoms.setdefault(l[21], []).append(xyz)
    elif l[17:20] == '759' and l[21] == 'D':
        lig.append(xyz)
A = {k: np.array(v) for k, v in atoms.items()}
L = np.array(lig)
pivot = L.mean(0)
rng = np.random.default_rng(7)

def rotm(axis, ang):
    a = axis / np.linalg.norm(axis); x, y, z = a; c, s = np.cos(ang), np.sin(ang); C = 1 - c
    return np.array([[c + x*x*C, x*y*C - z*s, x*z*C + y*s], [y*x*C + z*s, c + y*y*C, y*z*C - x*s], [z*x*C - y*s, z*y*C + x*s, c + z*z*C]])

def qrot(q):
    q = q / np.linalg.norm(q); w, x, y, z = q
    return np.array([[1-2*(y*y+z*z), 2*(x*y-w*z), 2*(x*z+w*y)], [2*(x*y+w*z), 1-2*(x*x+z*z), 2*(y*z-w*x)], [2*(x*z-w*y), 2*(y*z+w*x), 1-2*(x*x+y*y)]])

rest = np.vstack([A['D'], A['B'], A['C']])
def clash(t):  # closest approach between moved BRD4 and the rest, on a subsample
    d = np.linalg.norm(t[::3, None, :] - rest[None, ::3, :], axis=2)
    return d.min() < 3.2

poses = [A['A']]
while len(poses) < 5:
    R = rotm(rng.normal(size=3), np.radians(rng.uniform(18, 40)))
    t = (A['A'] - pivot) @ R.T + pivot
    if not clash(t):
        poses.append(t)

def trace(target):
    groups = {'target': target, 'e3': A['D'], 'eloc': A['C'], 'elob': A['B']}
    cen = np.vstack(list(groups.values())).mean(0)
    def score(R, res=1.6):
        P = {k: ((v - cen) @ R.T)[:, :2] for k, v in groups.items()}
        allxy = np.vstack(list(P.values())); mn = allxy.min(0) - 4
        n = int((allxy.max(0) - mn).max() / res) + 6
        M = {}
        for k, p in P.items():
            g = np.zeros((n, n), bool); ij = ((p - mn) / res).astype(int)
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    g[np.clip(ij[:, 0] + di, 0, n - 1), np.clip(ij[:, 1] + dj, 0, n - 1)] = True
            M[k] = g
        ov = (M['target'] & M['e3']).sum() + 1.5 * (M['target'] & (M['eloc'] | M['elob'])).sum() + .4 * (M['e3'] & (M['eloc'] | M['elob'])).sum()
        return ov / sum(v.sum() for v in M.values())
    best = min((score(R), i, R) for i, R in enumerate(qrot(rng.normal(size=4)) for _ in range(900)))
    R = best[2]
    P = {k: ((v - cen) @ R.T)[:, :2] for k, v in groups.items()}
    v = P['e3'].mean(0) - P['target'].mean(0); a = -np.arctan2(v[1], v[0])
    R2 = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
    P = {k: p @ R2.T for k, p in P.items()}
    if np.vstack([P['eloc'], P['elob']])[:, 1].mean() < P['target'][:, 1].mean():
        P = {k: p * [1, -1] for k, p in P.items()}
    allxy = np.vstack(list(P.values())); mid = (allxy.min(0) + allxy.max(0)) / 2; span = (allxy.max(0) - allxy.min(0)).max()
    res = .5; mn = allxy.min(0) - 8; shape = np.ceil((allxy.max(0) - mn + 8) / res).astype(int)
    out = {}
    for k, p in P.items():
        g = np.zeros(shape[::-1]); ij = ((p - mn) / res).astype(int); np.add.at(g, (ij[:, 1], ij[:, 0]), 1)
        g = gaussian_filter(g, 2.2 / res)
        to = lambda c: [[round(float(x), 4), round(float(y), 4)] for x, y in (np.c_[c[:, 1] * res + mn[0], c[:, 0] * res + mn[1]] - mid) / span]
        outer = sorted(measure.find_contours(g, g.max() * .06), key=len, reverse=True)[0]
        inner = []
        for f in (.3, .52, .74):
            cc = sorted([c for c in measure.find_contours(g, g.max() * f) if len(c) > 30], key=len, reverse=True)[:2]
            inner += [to(measure.approximate_polygon(c, tolerance=.9 / res)[:-1]) for c in cc]
        out[k] = {'outer': to(measure.approximate_polygon(outer, tolerance=.9 / res)[:-1]), 'inner': inner}
    return out, best[0]

result = {'pdb': '5T35', 'poses': []}
for i, t in enumerate(poses):
    shapes, ov = trace(t)
    result['poses'].append(shapes)
    print('pose', i, 'overlap %.3f' % ov)
json.dump(result, open(D + '5t35_poses.json', 'w'), separators=(',', ':'))
