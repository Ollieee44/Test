"""Atom-detailed protein surfaces for the v4 restyle (after XVIVO's targeted-protein-degradation animation): each protein
as the bumpy envelope of its atoms (every heavy atom a soft sphere, contoured close to its van der Waals size, lightly
relaxed), not the blurred blob of the cartoon version, with a baked occlusion term per vertex (how buried it is: crevices
darker) for the shader. Same chains and frame as landing/build_meshes.py (PDB 5T35, centred on the four proteins;
ubiquitin from 1UBQ, centred on itself), so they drop in where the old surfaces were.
Usage: python bumpy_meshes.py 5t35.pdb 1ubq.pdb ../bumpy.json [grid step, default .7]"""
import base64, json, sys
import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.spatial import cKDTree
from skimage import measure
p5, p1, dst = sys.argv[1:4]; SP = float(sys.argv[4]) if len(sys.argv) > 4 else .7
VDW = {'C': 1.7, 'N': 1.55, 'O': 1.52, 'S': 1.8}
def atoms(path, chain=None):
    out = []
    for l in open(path):
        if l.startswith('ATOM') and (chain is None or l[21] == chain):
            e = l[76:78].strip() or l[12:14].strip()[0]
            if e != 'H': out.append(([float(l[30:38]), float(l[38:46]), float(l[46:54])], VDW.get(e, 1.7)))
    return np.array([a for a, _ in out]), np.array([r for _, r in out])
CH = {'brd4': 'A', 'elob': 'B', 'eloc': 'C', 'vhl': 'D'}
prot = {k: atoms(p5, c) for k, c in CH.items()}
origin = np.concatenate([x for x, _ in prot.values()]).mean(0)
def surface(xyz, rad):
    # each atom a gaussian of width ~ its radius; the contour sits a little outside the vdW spheres
    pad = 4; lo = xyz.min(0) - pad; n = np.ceil((xyz.max(0) + pad - lo) / SP).astype(int) + 1
    g = np.zeros(n); tree_pts = np.stack(np.meshgrid(*[lo[j] + SP * np.arange(n[j]) for j in range(3)], indexing='ij'), -1).reshape(-1, 3)
    t = cKDTree(tree_pts)
    flat = g.reshape(-1)
    for p, r in zip(xyz, rad):
        idx = t.query_ball_point(p, r * 2.2)
        d2 = np.sum((tree_pts[idx] - p) ** 2, 1); flat[idx] += np.exp(-d2 / (2 * (r * .62) ** 2))
    v, f, _, _ = measure.marching_cubes(g, .5); v = v * SP + lo
    # a light relax (Taubin), so the facets go but the atom bumps stay
    nb = [set() for _ in range(len(v))]
    for a, b, c in f: nb[a] |= {b, c}; nb[b] |= {a, c}; nb[c] |= {a, b}
    nb = [np.fromiter(s, int) for s in nb]
    for it in range(4):
        lam = .45 if it % 2 == 0 else -.47
        v = v + lam * (np.array([v[x].mean(0) if len(x) else v[i] for i, x in enumerate(nb)]) - v)
    return v, f
def occlusion(v, xyz):
    # buried-ness: atoms within 10 A of the vertex, mapped to 1 (open) .. 0 (deep in a crevice)
    c = np.array([len(x) for x in cKDTree(xyz).query_ball_point(v, 10.0)])
    lo, hi = np.percentile(c, 8), np.percentile(c, 97); return np.clip(1 - (c - lo) / (hi - lo), 0, 1)
def pack(v, f, ao, o):
    a, b, c = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    if np.einsum('ij,ij->i', a, np.cross(b, c)).sum() < 0: f = f[:, [0, 2, 1]]
    v = v - o; idx = f.astype(np.uint16 if len(v) < 65536 else np.uint32)
    return {'pos': base64.b64encode(np.round(v * 100).astype(np.int16).tobytes()).decode(), 'idx': base64.b64encode(idx.tobytes()).decode(),
            'idx32': idx.dtype == np.uint32, 'nv': len(v), 'nf': len(f), 'ao': base64.b64encode(np.round(ao * 255).astype(np.uint8).tobytes()).decode()}
out = {'parts': {}}
allxyz = np.concatenate([x for x, _ in prot.values()])
for k, (xyz, rad) in prot.items():
    v, f = surface(xyz, rad); out['parts'][k] = pack(v, f, occlusion(v, allxyz), origin)
    print(k, len(xyz), 'atoms ->', len(v), 'verts', len(f), 'tris')
ub, ur = atoms(p1)
v, f = surface(ub, ur); out['parts']['ub'] = pack(v, f, occlusion(v, ub), ub.mean(0)); print('ub', len(ub), 'atoms ->', len(v), 'verts')
json.dump(out, open(dst, 'w'), separators=(',', ':'))
import os; print(dst, os.path.getsize(dst) // 1024, 'KB')
