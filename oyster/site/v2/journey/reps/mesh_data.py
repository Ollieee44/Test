"""Surfaces round the journey's generic halves for the translucent options: each half's van der Waals spheres splatted,
blurred and contoured, once smooth (the glass shell) and once coarse (the low-poly wire mesh), packed like the journey's
meshes, in the same frame as reps_atoms.json.   python3 mesh_data.py reps_atoms.json reps_mesh.json"""
import base64, json, sys
import numpy as np
from scipy.ndimage import gaussian_filter
from skimage import measure
src, dst = sys.argv[1:3]
A = json.load(open(src)); VDW = {'C': 1.7, 'N': 1.55, 'O': 1.52, 'S': 1.8, 'H': 1.1}
def pack(v, f):
    a, b, c = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    if np.einsum('ij,ij->i', a, np.cross(b, c)).sum() < 0: f = f[:, [0, 2, 1]]
    return {'pos': base64.b64encode(np.round(v * 100).astype(np.int16).tobytes()).decode(), 'idx': base64.b64encode(f.astype(np.uint16).tobytes()).decode(), 'idx32': False, 'nv': len(v), 'nf': len(f)}
def surf(xyz, rad, sp, blur, level):
    lo = xyz.min(0) - 4; n = np.ceil((xyz.max(0) + 4 - lo) / sp).astype(int) + 1
    G = np.stack(np.meshgrid(*[lo[j] + sp * np.arange(n[j]) for j in range(3)], indexing='ij'), -1)
    d = np.zeros(n)
    for p, r in zip(xyz, rad): d += np.exp(-np.sum((G - p) ** 2, -1) / (2 * (r * .62) ** 2))   # soft spheres
    d = gaussian_filter(d, blur / sp)
    v, f, _, _ = measure.marching_cubes(d, level); return v * sp + lo, f
out = {}
for k, a in A.items():
    xyz = np.array(a['xyz']); rad = np.array([VDW[e] for e in a['el']])
    hv = np.array([e != 'H' for e in a['el']])
    out[k] = {'smooth': pack(*surf(xyz[hv], rad[hv] * 1.25, .3, .5, .35)), 'coarse': pack(*surf(xyz[hv], rad[hv] * 1.25, 1.05, .5, .35))}
    print(k, {m: out[k][m]['nv'] for m in out[k]})
json.dump(out, open(dst, 'w'))
