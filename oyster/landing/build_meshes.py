"""Cartoon 3D meshes of the 5T35 ternary complex for the landing page.

Each protein (BRD4 BD2, VHL, Elongin B, Elongin C) becomes a smooth, blobby molecular surface: atoms
are splatted onto a grid, blurred with a wide Gaussian and contoured, so the real shape survives but
the atomic detail does not. The degrader is deliberately generic: MZ1's crystal pose
sets where its two halves and linker sit, but each half is drawn as an invented ring system traced
along its bonds, so it reads as a PROTAC without being identifiable. Everything is centred on the complex and written to data/meshes.json with positions
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

# the degrader, drawn generically. A chemist should read it as a PROTAC (two ligands joined by a linker)
# without being able to tell which one, so each half is an invented, unremarkable ring system rather
# than MZ1's real warhead and E3 ligand: no JQ1, no hydroxyproline, no glutarimide. Each half is
# embedded in 3D, placed where the real half sits in the crystal (same centre, attachment end facing the
# linker, ring plane turned toward the viewer) and drawn as an outline traced along its bonds: a smooth
# tube, so the rings show as open loops and no atoms or elements are shown. The linker is a curve
# between the two attachment atoms, which the page dresses as a string of beads.
GENERIC = {'warhead': 'CC1CCN(CC1)c1nc2ccccc2s1',          # piperidine on a benzothiazole; attach at the methyl
           'e3lig': 'CNC(=O)c1ccc(cc1)-c1ccc2cccnc2c1'}    # biaryl amide; attach at the N-methyl

def rot_between(a, b):
    a = a / np.linalg.norm(a); b = b / np.linalg.norm(b); v = np.cross(a, b); c = a @ b
    K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + K + K @ K / (1 + c)

def rot_about(k, th):
    k = k / np.linalg.norm(k); K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + np.sin(th) * K + (1 - np.cos(th)) * K @ K

# the page turns the crystal by the shortest rotation taking the VHL-to-BRD4 axis onto -x; "toward the
# viewer" is +z after that turn
toScreen = rot_between(prot['brd4'].mean(0) - prot['vhl'].mean(0), np.array([-1., 0, 0]))

def generic_half(name, attach):
    mol = Chem.AddHs(Chem.MolFromSmiles(GENERIC[name]))
    AllChem.EmbedMolecule(mol, randomSeed=7); AllChem.MMFFOptimizeMolecule(mol)
    mol = Chem.RemoveHs(mol); Y = mol.GetConformer().GetPositions()
    Yc = Y.mean(0); Cc = X[[i for i in part if part[i] == name]].mean(0)
    R1 = rot_between(Y[0] - Yc, attach - Cc); Z = (Y - Yc) @ R1.T
    n = np.linalg.svd(Z - Z.mean(0))[2][2]                # ring-plane normal
    ax = attach - Cc; best = max(np.linspace(0, 2 * np.pi, 72, endpoint=False), key=lambda th: abs((toScreen @ rot_about(ax, th) @ n)[2]))
    P = Z @ rot_about(ax, best).T + Cc
    return P, [(b.GetBeginAtomIdx(), b.GetEndAtomIdx()) for b in mol.GetBonds()]

def skeleton(P, bonds, r=.42, k=.3, spacing=.12):
    """A tube of radius r along every bond: the signed distance to each bond segment, blended with a
    smooth minimum (k) so joints are filleted, contoured at zero."""
    pad = r + 1; lo = P.min(0) - pad; hi = P.max(0) + pad
    axes = [np.arange(lo[j], hi[j] + spacing, spacing) for j in range(3)]
    G = np.stack(np.meshgrid(*axes, indexing='ij'), -1)
    d = None
    for i, j in bonds:
        A, B = P[i], P[j]; e = B - A; t = np.clip(((G - A) @ e) / (e @ e), 0, 1)
        di = np.linalg.norm(G - (A + t[..., None] * e), axis=-1) - r
        if d is None: d = di
        else:                                    # polynomial smooth minimum
            h = np.clip(.5 + .5 * (di - d) / k, 0, 1); d = di * (1 - h) + d * h - k * h * (1 - h)
    v, fc, _, _ = measure.marching_cubes(-d, 0)
    v = v * spacing + lo
    nb = [set() for _ in range(len(v))]
    for a_, b_, c_ in fc:
        nb[a_] |= {b_, c_}; nb[b_] |= {a_, c_}; nb[c_] |= {a_, b_}
    nb = [np.fromiter(x, int) for x in nb]
    for it in range(6):
        lam = .5 if it % 2 == 0 else -.53
        v = v + lam * (np.array([v[n].mean(0) for n in nb]) - v)
    return v, fc

ends = {}
for name, attach in (('warhead', X[m[0]]), ('e3lig', X[m[-1]])):
    P, bonds = generic_half(name, attach)
    v, f = skeleton(P, bonds)
    out['parts'][name] = pack(v, f, origin); ends[name] = P[0]
    print(name, GENERIC[name], '->', len(v), 'verts')
# the linker keeps the real chain's length (the page lays it out as an arc between the two ends)
out['linker'] = {'curve': ([ends['warhead']] + list(X[path]) + [ends['e3lig']])}
out['linker']['curve'] = (np.array(out['linker']['curve']) - origin).round(3).tolist()
out['centres'] = {k: (prot[k].mean(0) - origin).round(2).tolist() for k in prot}
out['centres'].update({k: (X[[i for i in part if part[i] == k]].mean(0) - origin).round(2).tolist() for k in ('warhead', 'e3lig')})
# ubiquitin (PDB 1UBQ), centred on itself, for the tags the E2 hands to the target
ub = np.array([[float(l[30:38]), float(l[38:46]), float(l[46:54])] for l in open(D + 'data/1ubq.pdb') if l.startswith('ATOM')])
v, f = surface(ub, sigma=2.2, level=.18, spacing=1.2)
out['parts']['ub'] = pack(v, f, ub.mean(0))
print('ub', len(ub), 'atoms ->', len(v), 'verts')
json.dump(out, open(D + 'data/meshes.json', 'w'), separators=(',', ':'))
print('meshes.json', os.path.getsize(D + 'data/meshes.json') // 1024, 'KB')
