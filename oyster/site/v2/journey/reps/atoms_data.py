"""Atoms of the journey's two generic degrader halves, for the atom-based representation mock-ups (space-filling and
ball-and-stick). Rebuilds the halves exactly as landing/build_meshes.py places them (MZ1's pose in PDB 5T35 sets
where each half sits; each half is an invented ring system, so no real ligand is shown), in the same centred frame as
the meshes, then checks them against the traced outlines in reps_data.json.
  python3 atoms_data.py <5t35.pdb> reps_atoms.json"""
import base64, json, os, sys
import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem
D = os.path.dirname(os.path.abspath(__file__)) + '/'
pdb, dst = sys.argv[1:3]
lines = open(pdb).read().splitlines()
CHAINS = {'brd4': 'A', 'elob': 'B', 'eloc': 'C', 'vhl': 'D'}
SMI = 'Cc1sc2n3c(C)nnc3[C@H](CC(=O)NCCOCCOCCOCC(=O)N[C@H](C(=O)N4C[C@H](O)C[C@H]4C(=O)NCc5ccc(cc5)c6scnc6C)C(C)(C)C)N=C(c7ccc(Cl)cc7)c2c1C'
GENERIC = {'warhead': 'CC1CCN(CC1)c1nc2ccccc2s1', 'e3lig': 'CNC(=O)c1ccc(cc1)-c1ccc2cccnc2c1'}
atoms = lambda ch: np.array([[float(l[30:38]), float(l[38:46]), float(l[46:54])] for l in lines if l.startswith('ATOM') and l[21] == ch and l[76:78].strip() != 'H'])
prot = {k: atoms(c) for k, c in CHAINS.items()}
origin = np.concatenate(list(prot.values())).mean(0)
lig = '\n'.join(l for l in lines if l.startswith('HETATM') and l[17:20] == '759' and l[21] == 'D')
pm = Chem.MolFromPDBBlock(lig, removeHs=False, sanitize=False); tmpl = Chem.MolFromSmiles(SMI)
pm = AllChem.AssignBondOrdersFromTemplate(tmpl, pm); match = pm.GetSubstructMatch(tmpl); conf = pm.GetConformer()
X = np.array([list(conf.GetAtomPosition(match[i])) for i in range(tmpl.GetNumAtoms())])
m = tmpl.GetSubstructMatch(Chem.MolFromSmarts('[CH2]C(=O)N[CH2][CH2]O[CH2][CH2]O[CH2][CH2]O[CH2]C(=O)N')); linker = set(m[1:-1])
sub = Chem.RWMol(tmpl)
for b in list(tmpl.GetBonds()):
    if (b.GetBeginAtomIdx() in linker) != (b.GetEndAtomIdx() in linker): sub.RemoveBond(b.GetBeginAtomIdx(), b.GetEndAtomIdx())
cl = [a.GetIdx() for a in tmpl.GetAtoms() if a.GetSymbol() == 'Cl'][0]; part = {}
for fr in Chem.GetMolFrags(sub.GetMol()):
    lab = 'linker' if set(fr) <= linker else ('warhead' if cl in fr else 'e3lig')
    for i in fr: part[i] = lab
def rot_between(a, b):
    a = a / np.linalg.norm(a); b = b / np.linalg.norm(b); v = np.cross(a, b); c = a @ b
    K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]]); return np.eye(3) + K + K @ K / (1 + c)
def rot_about(k, th):
    k = k / np.linalg.norm(k); K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]]); return np.eye(3) + np.sin(th) * K + (1 - np.cos(th)) * K @ K
toScreen = rot_between(prot['brd4'].mean(0) - prot['vhl'].mean(0), np.array([-1., 0, 0]))
REPS = json.load(open(D + 'reps_data.json'))
dec = lambda p: np.frombuffer(base64.b64decode(p['pos']), np.int16).reshape(-1, 3) / 100.0
out = {}
for name, attach in (('warhead', X[m[0]]), ('e3lig', X[m[-1]])):
    V = dec(REPS['parts'][name])[::5]
    def place(seed):
        mol = Chem.AddHs(Chem.MolFromSmiles(GENERIC[name])); AllChem.EmbedMolecule(mol, randomSeed=seed); AllChem.MMFFOptimizeMolecule(mol)
        heavy = [a.GetIdx() for a in mol.GetAtoms() if a.GetSymbol() != 'H']
        Yall = mol.GetConformer().GetPositions(); Y = Yall[heavy]
        Yc = Y.mean(0); Cc = X[[i for i in part if part[i] == name]].mean(0)
        R1 = rot_between(Y[0] - Yc, attach - Cc); Z = (Y - Yc) @ R1.T
        n = np.linalg.svd(Z - Z.mean(0))[2][2]
        ax = attach - Cc; best = max(np.linspace(0, 2 * np.pi, 72, endpoint=False), key=lambda th: abs((toScreen @ rot_about(ax, th) @ n)[2]))
        return mol, heavy, ((Yall - Yc) @ R1.T) @ rot_about(ax, best).T + Cc - origin
    def dist(P, hb):   # each outline vertex to its nearest heavy-atom bond
        d = np.full(len(V), 9.)
        for a, b in hb:
            A, B = P[a], P[b]; e = B - A; t = np.clip((V - A) @ e / (e @ e), 0, 1)[:, None]; d = np.minimum(d, np.linalg.norm(V - (A + t * e), axis=1))
        return d
    # the original build's conformer came from another RDKit version: take the seed whose conformer, placed the same
    # way, sits best in the traced outline
    cands = []
    for seed in [7] + list(range(1, 40)):
        mol, heavy, P = place(seed); hv = set(heavy)
        bonds = [(b.GetBeginAtomIdx(), b.GetEndAtomIdx()) for b in mol.GetBonds()]; hb = [(a, b) for a, b in bonds if a in hv and b in hv]
        cands.append((np.mean((dist(P, hb) - .42) ** 2), seed, mol, heavy, P, bonds, hb))
    err, seed, mol, heavy, P, bonds, hb = min(cands, key=lambda c: c[0])
    ds = dist(P, hb); print(name, 'seed', seed)
    print(name, len(heavy), 'heavy atoms', mol.GetNumAtoms(), 'with H · outline to bonds: median %.2f, 95%% %.2f (tube radius .42)' % (np.median(ds), np.percentile(ds, 95)))
    out[name] = {'el': [a.GetSymbol() for a in mol.GetAtoms()], 'xyz': np.round(P, 3).tolist(), 'bonds': bonds,
                 'order': [b.GetBondTypeAsDouble() for b in mol.GetBonds()], 'attach': 0,
                 'rings': [list(r) for r in mol.GetRingInfo().AtomRings()]}
json.dump(out, open(dst, 'w'))
