"""Cartoon 3D meshes of the 5T35 ternary complex for the landing page.

Each protein (BRD4 BD2, VHL, Elongin B, Elongin C) becomes a smooth, blobby molecular surface: atoms
are splatted onto a grid, blurred with a wide Gaussian and contoured, so the real shape survives but
the atomic detail does not. MZ1, the degrader, is split the way the site draws it: two small blobby
heads (the JQ1 warhead and the VH032 E3 ligand) joined by a chain of linker beads, with the break
bond marked. Everything is centred on the complex and written to data/meshes.json with positions
quantised to int16 and base64 encoded.
"""
import base64, json, os
import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem
from scipy.ndimage import gaussian_filter
from skimage import measure

D = os.path.dirname(os.path.abspath(__file__)) + '/'
PDB = D + 'data/5t35.pdb'
CHAINS = {'brd4': 'A', 'elob': 'B', 'eloc': 'C', 'vhl': 'D'}
SMI = 'Cc1sc2n3c(C)nnc3[C@H](CC(=O)NCCOCCOCCOCC(=O)N[C@H](C(=O)N4C[C@H](O)C[C@H]4C(=O)NCc5ccc(cc5)c6scnc6C)C(C)(C)C)N=C(c7ccc(Cl)cc7)c2c1C'

lines = open(PDB).read().splitlines()
def atoms(chain):
    return np.array([[float(l[30:38]), float(l[38:46]), float(l[46:54])] for l in lines
                     if l.startswith('ATOM') and l[21] == chain and l[76:78].strip() != 'H'])

def surface(xyz, sigma, level, spacing, smooth=12):
    """Blurred atom density, contoured with marching cubes and Taubin-smoothed."""
    pad = 3 * sigma + 2; lo = xyz.min(0) - pad; hi = xyz.max(0) + pad
    shape = np.ceil((hi - lo) / spacing).astype(int) + 1
    g = np.zeros(shape)
    ijk = np.round((xyz - lo) / spacing).astype(int)
    np.add.at(g, (ijk[:, 0], ijk[:, 1], ijk[:, 2]), 1.0)
    g = gaussian_filter(g, sigma / spacing)
    v, f, _, _ = measure.marching_cubes(g, g.max() * level)
    v = v * spacing + lo
    # Taubin smoothing: shrink, then inflate, so the mesh relaxes without collapsing
    nb = [set() for _ in range(len(v))]
    for a, b, c in f:
        nb[a] |= {b, c}; nb[b] |= {a, c}; nb[c] |= {a, b}
    nb = [np.fromiter(s, int) for s in nb]
    for it in range(smooth):
        lam = .5 if it % 2 == 0 else -.53
        avg = np.array([v[n].mean(0) if len(n) else v[i] for i, n in enumerate(nb)])
        v = v + lam * (avg - v)
    return v, f

def pack(v, f, origin):
    # outward-facing triangles (counter-clockwise from outside) give a positive signed volume
    a, b, c = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    if np.einsum('ij,ij->i', a, np.cross(b, c)).sum() < 0:
        f = f[:, [0, 2, 1]]
    v = v - origin
    q = np.round(v * 100).astype(np.int16)        # 0.01 A steps
    idx = f.astype(np.uint16 if len(v) < 65536 else np.uint32)
    return {'pos': base64.b64encode(q.tobytes()).decode(), 'idx': base64.b64encode(idx.tobytes()).decode(),
            'idx32': idx.dtype == np.uint32, 'nv': len(v), 'nf': len(f)}

# ---------- proteins ----------
prot = {k: atoms(c) for k, c in CHAINS.items()}
origin = np.concatenate(list(prot.values())).mean(0)
out = {'units': 'angstrom/100', 'parts': {}}
for k, xyz in prot.items():
    v, f = surface(xyz, sigma=2.4, level=.16, spacing=1.5)
    out['parts'][k] = pack(v, f, origin)
    print(k, len(xyz), 'atoms ->', len(v), 'verts', len(f), 'tris')

# ---------- MZ1: coordinates from the crystal, atom roles from the 2D template ----------
lig = '\n'.join(l for l in lines if l.startswith('HETATM') and l[17:20] == '759' and l[21] == 'D')
pm = Chem.MolFromPDBBlock(lig, removeHs=False, sanitize=False)
tmpl = Chem.MolFromSmiles(SMI)
pm = AllChem.AssignBondOrdersFromTemplate(tmpl, pm)
match = pm.GetSubstructMatch(tmpl)
assert match, 'MZ1 template does not match the crystal ligand'
conf = pm.GetConformer()
X = np.array([list(conf.GetAtomPosition(match[i])) for i in range(tmpl.GetNumAtoms())])

patt = Chem.MolFromSmarts('[CH2]C(=O)N[CH2][CH2]O[CH2][CH2]O[CH2][CH2]O[CH2]C(=O)N')
m = tmpl.GetSubstructMatch(patt)
linker = set(m[1:-1])
sub = Chem.RWMol(tmpl)
for b in list(tmpl.GetBonds()):
    if (b.GetBeginAtomIdx() in linker) != (b.GetEndAtomIdx() in linker):
        sub.RemoveBond(b.GetBeginAtomIdx(), b.GetEndAtomIdx())
cl = [a.GetIdx() for a in tmpl.GetAtoms() if a.GetSymbol() == 'Cl'][0]
part = {}
for fr in Chem.GetMolFrags(sub.GetMol()):
    lab = 'linker' if set(fr) <= linker else ('warhead' if cl in fr else 'e3lig')
    for i in fr: part[i] = lab
path = [i for i in m[1:-1] if tmpl.GetAtomWithIdx(i).GetSymbol() != 'O' or tmpl.GetAtomWithIdx(i).GetDegree() == 2]
mid = len(path) // 2

for name in ('warhead', 'e3lig'):
    idx = [i for i in part if part[i] == name]
    v, f = surface(X[idx], sigma=1.25, level=.2, spacing=.5, smooth=10)
    out['parts'][name] = pack(v, f, origin)
    print(name, len(idx), 'atoms ->', len(v), 'verts')
out['linker'] = {'beads': (X[path] - origin).round(2).tolist(), 'oxygen': [tmpl.GetAtomWithIdx(i).GetSymbol() == 'O' for i in path],
                 'break': [mid - 1, mid],
                 'ends': {'warhead': (X[m[0]] - origin).round(2).tolist(), 'e3lig': (X[m[-1]] - origin).round(2).tolist()}}
out['centres'] = {k: (prot[k].mean(0) - origin).round(2).tolist() for k in prot}
out['centres'].update({k: (X[[i for i in part if part[i] == k]].mean(0) - origin).round(2).tolist() for k in ('warhead', 'e3lig')})
json.dump(out, open(D + 'data/meshes.json', 'w'), separators=(',', ':'))
print('meshes.json', os.path.getsize(D + 'data/meshes.json') // 1024, 'KB')
