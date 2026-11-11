"""A surface mesh of the human 26S proteasome for the click-through, from PDB 6MSB (Dong et al., Nature 2019).
The 20S core particle (entities 20-33) and the 19S regulatory particle (entities 1-18; the structure's own ubiquitin,
entity 19, is left out) are blurred from their C-alpha atoms and contoured, in the same way as the other proteins'
surfaces (landing/build_meshes.py). The core's long axis is turned onto +x with the cap on the +x side, centred on the
core, so the target goes into the middle of the core. Positions in 0.01 A steps, the format the page's geom() reads.
Usage: python proteasome_mesh.py 6MSB.cif.gz ../proteasome.json [grid step, default 4.6]   (from files.rcsb.org/download/6MSB.cif.gz)"""
import base64, gzip, json, sys
import numpy as np
from scipy.ndimage import gaussian_filter
from skimage import measure

src, dst = sys.argv[1:3]
SPACING = float(sys.argv[3]) if len(sys.argv) > 3 else 4.6   # grid step (A): coarser is lighter
cols, rows = [], []
for l in gzip.open(src, 'rt'):
    if l.startswith('_atom_site.'): cols.append(l.strip().split('.', 1)[1])
    elif l.startswith('ATOM') and cols: rows.append(l.split())
c = {k: i for i, k in enumerate(cols)}
ca = [(int(r[c['label_entity_id']]), [float(r[c['Cartn_x']]), float(r[c['Cartn_y']]), float(r[c['Cartn_z']])]) for r in rows if r[c['label_atom_id']] == 'CA']
CP = np.array([x for e, x in ca if 20 <= e <= 33]); RP = np.array([x for e, x in ca if 1 <= e <= 18])
print('core', len(CP), 'cap', len(RP), 'C-alphas')
# the frame: core's long axis on +x (cap that side), centred on the core
o = CP.mean(0); w, V = np.linalg.eigh(np.cov((CP - o).T)); ax = V[:, -1]
if (RP.mean(0) - o) @ ax < 0: ax = -ax
b = V[:, 0]; c2 = np.cross(ax, b); R = np.array([ax, b, c2])
f = lambda P: (P - o) @ R.T

def surface(xyz, sigma=None, level=.12, spacing=None, smooth=10):
    spacing = spacing or SPACING; sigma = sigma or max(5, SPACING * 1.05)
    pad = 3 * sigma + 2; lo = xyz.min(0) - pad; hi = xyz.max(0) + pad
    g = np.zeros((np.ceil((hi - lo) / spacing).astype(int) + 1))
    ijk = np.round((xyz - lo) / spacing).astype(int); np.add.at(g, tuple(ijk.T), 1.0)
    g = gaussian_filter(g, sigma / spacing)
    v, fc, _, _ = measure.marching_cubes(g, g.max() * level); v = v * spacing + lo
    nb = [set() for _ in range(len(v))]
    for a, bb, cc in fc: nb[a] |= {bb, cc}; nb[bb] |= {a, cc}; nb[cc] |= {a, bb}
    nb = [np.fromiter(s, int) for s in nb]
    for it in range(smooth):
        lam = .5 if it % 2 == 0 else -.53
        v = v + lam * (np.array([v[n].mean(0) if len(n) else v[i] for i, n in enumerate(nb)]) - v)
    return v, fc

def pack(v, fc):
    a, bb, cc = v[fc[:, 0]], v[fc[:, 1]], v[fc[:, 2]]
    if np.einsum('ij,ij->i', a, np.cross(bb, cc)).sum() < 0: fc = fc[:, [0, 2, 1]]
    q = np.round(v * 100).astype(np.int16); idx = fc.astype(np.uint16 if len(v) < 65536 else np.uint32)
    return {'pos': base64.b64encode(q.tobytes()).decode(), 'idx': base64.b64encode(idx.tobytes()).decode(),
            'idx32': bool(idx.dtype == np.uint32), 'nv': len(v), 'nf': len(fc)}

out = {}
for name, P in [('core', CP), ('cap', RP)]:
    v, fc = surface(f(P)); out[name] = pack(v, fc)
    print(name, len(v), 'verts', 'x %.0f..%.0f' % (v[:, 0].min(), v[:, 0].max()), 'r %.0f' % np.abs(v[:, 1:]).max())
json.dump(out, open(dst, 'w')); print(dst)
