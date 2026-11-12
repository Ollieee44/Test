"""The SELFTAC halves for v4, after the PROTAC in XVIVO's animation: a translucent space-filling surface round each half
(every atom, hydrogens included, a soft sphere at about its van der Waals size, contoured: lumpy, not blurred) and the
heavy atoms and bonds inside, for a ball-and-stick skeleton seen through it. From the journey's own invented halves
(reps/reps_atoms.json, in the molecule's crystal frame), so it is never a real ligand.
Usage: python selftac_glass.py ../reps/reps_atoms.json ../selftac_glass.json"""
import base64, json, sys
import numpy as np
from skimage import measure
src, dst = sys.argv[1:3]
A = json.load(open(src)); VDW = {'C': 1.7, 'N': 1.55, 'O': 1.52, 'S': 1.8, 'H': 1.1}
def pack(v, f):
    a, b, c = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    if np.einsum('ij,ij->i', a, np.cross(b, c)).sum() < 0: f = f[:, [0, 2, 1]]
    return {'pos': base64.b64encode(np.round(v * 100).astype(np.int16).tobytes()).decode(), 'idx': base64.b64encode(f.astype(np.uint16).tobytes()).decode(), 'idx32': False, 'nv': len(v), 'nf': len(f)}
import os
R_ = json.load(open(sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(src), 'reps_data.json')))
L = np.array(R_['linker']['curve']); ENDS = {'warhead': (L[0], L[-1]), 'e3lig': (L[-1], L[0])}   # (this half's attachment, the other's)
def rot_between(a, b):
    a = a / np.linalg.norm(a); b = b / np.linalg.norm(b); v = np.cross(a, b); c = a @ b
    K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]]); return np.eye(3) + K + K @ K / (1 + c)
out = {}
for k, a in A.items():
    xyz = np.array(a['xyz']); here, there = ENDS[k]
    hv0 = [i for i, e in enumerate(a['el']) if e != 'H']
    Rm = rot_between(xyz[hv0].mean(0) - here, here - there)      # the half's bulk, turned to point away from the other half
    xyz = (xyz - here) @ Rm.T + here
    rad = np.array([VDW[e] for e in a['el']]); SP = .32
    lo = xyz.min(0) - 3.5; n = np.ceil((xyz.max(0) + 3.5 - lo) / SP).astype(int) + 1
    G = np.stack(np.meshgrid(*[lo[j] + SP * np.arange(n[j]) for j in range(3)], indexing='ij'), -1)
    d = np.zeros(n)
    for p, r in zip(xyz, rad): d += np.exp(-np.sum((G - p) ** 2, -1) / (2 * (r * .6) ** 2))
    v, f, _, _ = measure.marching_cubes(d, .5); v = v * SP + lo
    hv = [i for i, e in enumerate(a['el']) if e != 'H']; at = {j: i for i, j in enumerate(hv)}
    out[k] = {'turn': {'pivot': np.round(here, 3).tolist(), 'm': np.round(Rm, 5).tolist()}, 'surface': pack(v, f), 'atoms': np.round(xyz[hv], 3).tolist(),
              'bonds': [[at[i], at[j]] for i, j in a['bonds'] if i in at and j in at]}
    print(k, len(v), 'surface verts', len(hv), 'heavy atoms', len(out[k]['bonds']), 'bonds')
json.dump(out, open(dst, 'w'), separators=(',', ':'))
