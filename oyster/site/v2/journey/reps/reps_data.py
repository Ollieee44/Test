"""Shapes for the SELFTAC representation mock-ups, from the journey's own degrader halves (landing/data/meshes.json),
in the same crystal frame, so every option keeps the geometry (both halves where they are, the same linker and length):
a smooth surface round each half, a few pearl centres per half, a fitted pebble (ellipsoid) and a sphere."""
import base64, json, sys
import numpy as np
from scipy.cluster.vq import kmeans2
from scipy.ndimage import gaussian_filter
from skimage import measure
src, dst = sys.argv[1:3]
d = json.load(open(src))
dec = lambda p: np.frombuffer(base64.b64decode(p['pos']), np.int16).reshape(-1, 3) / 100.0
def pack(v, f):
    a, b, c = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    if np.einsum('ij,ij->i', a, np.cross(b, c)).sum() < 0: f = f[:, [0, 2, 1]]
    return {'pos': base64.b64encode(np.round(v * 100).astype(np.int16).tobytes()).decode(), 'idx': base64.b64encode(f.astype(np.uint16).tobytes()).decode(), 'idx32': False, 'nv': len(v), 'nf': len(f)}
out = {'parts': {k: d['parts'][k] for k in ('warhead', 'e3lig')}, 'linker': d['linker'], 'centres': d['centres'], 'reps': {}}
for k, n in (('warhead', 6), ('e3lig', 7)):
    V = dec(d['parts'][k]); c = V.mean(0)
    # a smooth surface: the half's own shape, blurred and contoured
    sp, sg = .3, 1.0; lo = V.min(0) - 3; g = np.zeros(np.ceil((V.max(0) + 3 - lo) / sp).astype(int) + 1)
    ijk = np.round((V - lo) / sp).astype(int); np.add.at(g, tuple(ijk.T), 1); g = gaussian_filter(g, sg / sp)
    v, f, _, _ = measure.marching_cubes(g, g.max() * .1); v = v * sp + lo
    # pearls: centres of the half's mass, spread along it
    np.random.seed(3); cen, _ = kmeans2(V, n, minit='++', seed=3)
    # a pebble: the half's principal axes, sized to its spread
    w, U = np.linalg.eigh(np.cov((V - c).T)); rad = 2.1 * np.sqrt(w) + .5
    out['reps'][k] = {'surface': pack(v, f), 'pearls': np.round(cen, 2).tolist(), 'pebble': {'c': np.round(c, 2).tolist(), 'axes': np.round(U.T, 4).tolist(), 'r': np.round(rad, 2).tolist()},
                      'sphere': {'c': np.round(c, 2).tolist(), 'r': round(float(np.sqrt(((V - c) ** 2).sum(1)).mean() * 1.05), 2)}}
    print(k, len(v), 'surface verts', n, 'pearls', 'pebble radii', np.round(rad, 1), 'sphere r', out['reps'][k]['sphere']['r'])
json.dump(out, open(dst, 'w'))
