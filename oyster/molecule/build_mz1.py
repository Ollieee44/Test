"""Lay out MZ1 (JQ1 - PEG linker - VH032) in 2D and trace blobby outlines of its two halves.

MZ1 is the PROTAC in PDB 5T35 (SMILES from the RCSB ligand 759 definition). It stands in for
"a bifunctional degrader": the drawings are illustrative, not a SELFTAC compound.
Output: mz1_2d.json with atoms, bonds, part labels, the linker path, the break bond and outlines.
"""
import json, os
import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem, rdDepictor
from scipy.ndimage import gaussian_filter
from skimage import measure

D = os.path.dirname(os.path.abspath(__file__)) + '/'
SMI = 'Cc1sc2n3c(C)nnc3[C@H](CC(=O)NCCOCCOCCOCC(=O)N[C@H](C(=O)N4C[C@H](O)C[C@H]4C(=O)NCc5ccc(cc5)c6scnc6C)C(C)(C)C)N=C(c7ccc(Cl)cc7)c2c1C'
mol = Chem.MolFromSmiles(SMI)
rdDepictor.SetPreferCoordGen(True)
rdDepictor.Compute2DCoords(mol)
xy = np.array([[mol.GetConformer().GetAtomPosition(i).x, mol.GetConformer().GetAtomPosition(i).y] for i in range(mol.GetNumAtoms())])

# linker = the PEG chain with its two amide carbonyls: C(=O)NCCOCCOCCOCC(=O)N
patt = Chem.MolFromSmarts('[CH2]C(=O)N[CH2][CH2]O[CH2][CH2]O[CH2][CH2]O[CH2]C(=O)N')
m = mol.GetSubstructMatch(patt)
assert m, 'linker not found'
linker = set(m[1:-1])  # drop the CH2 on the JQ1 side and the N on the VH032 side, they belong to the heads
rest = [a.GetIdx() for a in mol.GetAtoms() if a.GetIdx() not in linker]
sub = Chem.RWMol(mol)
for b in list(mol.GetBonds()):
    if (b.GetBeginAtomIdx() in linker) != (b.GetEndAtomIdx() in linker):
        sub.RemoveBond(b.GetBeginAtomIdx(), b.GetEndAtomIdx())
frags = Chem.GetMolFrags(sub.GetMol())
cl = [a.GetIdx() for a in mol.GetAtoms() if a.GetSymbol() == 'Cl'][0]
part = {}
for f in frags:
    lab = 'linker' if set(f) <= linker else ('warhead' if cl in f else 'e3lig')
    for i in f: part[i] = lab

# orient: warhead on the left, E3 ligand on the right
cw = xy[[i for i in part if part[i] == 'warhead']].mean(0); ce = xy[[i for i in part if part[i] == 'e3lig']].mean(0)
v = ce - cw; a = -np.arctan2(v[1], v[0]); R = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
xy = (xy - (cw + ce) / 2) @ R.T
xy[:, 1] *= -1  # SVG y down

# linker path in order (backbone heavy atoms, no carbonyl O), and the break bond near its middle
path = [i for i in m[1:-1] if mol.GetAtomWithIdx(i).GetSymbol() != 'O' or mol.GetAtomWithIdx(i).GetDegree() == 2]
mid = len(path) // 2
brk = [path[mid - 1], path[mid]]

def outline(idx, sigma, level, res=.08, pad=6):
    p = xy[idx]; mn = p.min(0) - pad; mx = p.max(0) + pad
    shape = np.ceil((mx - mn) / res).astype(int)
    g = np.zeros(shape[::-1])
    for x, y in p:
        j, i = int((x - mn[0]) / res), int((y - mn[1]) / res); g[i, j] += 1
    g = gaussian_filter(g, sigma / res)
    c = sorted(measure.find_contours(g, g.max() * level), key=len, reverse=True)[0]
    c = measure.approximate_polygon(c, tolerance=.035 / res)[:-1]
    return [[round(float(cc[1] * res + mn[0]), 3), round(float(cc[0] * res + mn[1]), 3)] for cc in c]

# warhead/e3 blobs include their linker half up to the break, so each half reads as one small molecule
halfA = [i for i in part if part[i] == 'warhead']; halfB = [i for i in part if part[i] == 'e3lig']
out = {
  'atoms': [[round(float(x), 3), round(float(y), 3)] for x, y in xy],
  'el': [a.GetSymbol() for a in mol.GetAtoms()],
  'part': [part[i] for i in range(mol.GetNumAtoms())],
  'bonds': [[b.GetBeginAtomIdx(), b.GetEndAtomIdx(), 1.5 if b.GetIsAromatic() else b.GetBondTypeAsDouble()] for b in mol.GetBonds()],
  'linker_path': path, 'break': brk,
  'blob': {'warhead': outline(halfA, .95, .16), 'e3lig': outline(halfB, .95, .16)},
  'blob_soft': {'warhead': outline(halfA, 1.9, .22), 'e3lig': outline(halfB, 1.9, .22)},
  'blob_core': {'warhead': outline(halfA, .95, .42), 'e3lig': outline(halfB, .95, .42)},
  'rings': [[int(i) for i in r] for r in mol.GetRingInfo().AtomRings() if all(mol.GetAtomWithIdx(i).GetIsAromatic() for i in r)],
}
json.dump(out, open(D + 'mz1_2d.json', 'w'), separators=(',', ':'))
print('atoms', len(xy), 'parts', {k: list(part.values()).count(k) for k in set(part.values())}, 'linker path', len(path), 'break', brk)
print('extent', xy.min(0).round(1), xy.max(0).round(1))
