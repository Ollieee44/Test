#!/usr/bin/env python3
"""Build meshes.json, the 3D shapes of the Oyster scroll story, from protein structures.

    python3 tools/build_meshes.py                       # uses tools/meshes.config.json, writes meshes.json
    python3 tools/build_meshes.py --config my.json --out meshes.json
    python3 tools/build_meshes.py --only brd4,vhl       # rebuild some parts, keep the rest from --base

Needs: numpy, scipy, scikit-image and, for the drawn degrader halves, rdkit
    pip install numpy scipy scikit-image rdkit

What it makes (the keys the story script reads; keep them):
    parts.brd4, parts.vhl, parts.elob, parts.eloc  protein surfaces, from chains of the complex structure
    parts.ub                                       ubiquitin, from its own structure, centred on its atoms
    parts.warhead, parts.e3lig                     the two halves of the degrader, as soft outlines of their bonds
    centres.<part>                                 the centroid of each part's atoms (the story turns and places parts by these)
    linker.curve                                   the linker: its attachment atom on each half and the chain between

Frame: the complex's own coordinates (Angstrom), moved so the centroid of the chains listed in
"origin_chains" sits at 0,0,0. Ubiquitin is centred on its own atoms. The story turns everything so the
target sits left of the ligase, so the structure's orientation does not matter.

Format, per part: pos = base64 of little-endian int16 x,y,z in Angstrom/100 (so +-327 A at most);
idx = base64 of the triangle indices (uint16, or uint32 when idx32 is true); nv, nf = counts.
"""
import argparse, base64, json, math, os, sys, urllib.request
from collections import defaultdict
import numpy as np
from scipy import sparse
from skimage.measure import marching_cubes

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, 'cache')


# ---------- input ----------
def fetch(url, name):
    """Download once into tools/cache, then read from there."""
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, name)
    if not os.path.exists(path):
        print('  downloading', url)
        urllib.request.urlretrieve(url, path)
    return path


def structure_path(src):
    """A local .pdb path, or a 4-character PDB id fetched from RCSB."""
    if os.path.exists(src):
        return src
    if os.path.exists(os.path.join(HERE, src)):
        return os.path.join(HERE, src)
    return fetch(f'https://files.rcsb.org/download/{src.upper()}.pdb', f'{src.upper()}.pdb')


def read_pdb(path):
    """Heavy atoms as dicts: record, name, res, chain, resseq, xyz, element. First model only, no water."""
    atoms = []
    for line in open(path):
        if line.startswith('ENDMDL'):
            break
        if not line.startswith(('ATOM', 'HETATM')):
            continue
        res = line[17:20].strip()
        el = (line[76:78].strip() or line[12:14].strip()).upper()
        if res == 'HOH' or el in ('H', 'D'):
            continue
        if line[16] not in (' ', 'A'):          # alternate locations: keep the first
            continue
        atoms.append(dict(record=line[:6].strip(), name=line[12:16].strip(), res=res, chain=line[21],
                          resseq=line[22:26].strip(),
                          xyz=np.array([float(line[30:38]), float(line[38:46]), float(line[46:54])]), element=el))
    return atoms


def ligand_bonds(code):
    """Bonds (atom name pairs and orders) of a ligand, from the PDB Chemical Component Dictionary."""
    path = fetch(f'https://files.rcsb.org/ligands/download/{code}.cif', f'{code}.cif')
    bonds, in_bonds, cols = [], False, []
    for line in open(path):
        s = line.strip()
        if s.startswith('_chem_comp_bond.'):
            in_bonds = True; cols.append(s.split('.')[1]); continue
        if in_bonds:
            if not s or s.startswith(('#', 'loop_', '_')):
                if bonds: break
                continue
            f = s.split()
            row = dict(zip(cols, f))
            bonds.append((row['atom_id_1'].strip('"'), row['atom_id_2'].strip('"'), row['value_order'], row.get('pdbx_aromatic_flag', 'N')))
    return bonds


# ---------- surfaces ----------
def taubin(v, f, iterations, lam=.5, mu=-.53):
    """Smooth without shrinking (Taubin's lambda/mu filter)."""
    n = len(v)
    e = np.concatenate([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]])
    a = sparse.coo_matrix((np.ones(len(e)), (e[:, 0], e[:, 1])), shape=(n, n)).tocsr()
    a = ((a + a.T) > 0).astype(float)
    deg = np.asarray(a.sum(1)).ravel(); deg[deg == 0] = 1
    w = sparse.diags(1 / deg) @ a
    for _ in range(iterations):
        v = v + lam * (w @ v - v)
        v = v + mu * (w @ v - v)
    return v


def outward(v, f):
    """Flip the winding if the surface faces inward (three.js lights and outlines by the winding)."""
    vol = np.einsum('ij,ij->i', v[f[:, 0]], np.cross(v[f[:, 1]], v[f[:, 2]])).sum()
    return f[:, ::-1].copy() if vol < 0 else f


def largest_piece(v, f):
    """Keep the largest connected piece (drops stray bubbles inside the surface)."""
    n = len(v)
    e = np.concatenate([f[:, [0, 1]], f[:, [1, 2]]])
    a = sparse.coo_matrix((np.ones(len(e)), (e[:, 0], e[:, 1])), shape=(n, n))
    k, lab = sparse.csgraph.connected_components(a, directed=False)
    if k == 1:
        return v, f
    keep = np.argmax(np.bincount(lab[f[:, 0]]))
    used = lab == keep
    remap = -np.ones(n, int); remap[used] = np.arange(used.sum())
    f = f[used[f[:, 0]]]
    return v[used], remap[f]


def grid_mesh(field, lo, step, level):
    v, f, _, _ = marching_cubes(field, level=level, spacing=(step, step, step))
    return v + lo, f.astype(np.int64)


def protein_surface(xyz, o):
    """A soft surface round the atoms: a sum of Gaussians, one per atom, cut at a density level, then smoothed."""
    step, sigma, level = o['grid'], o['sigma'], o['level']
    pad = 3 * sigma + 4
    lo = xyz.min(0) - pad
    shape = np.ceil((xyz.max(0) + pad - lo) / step).astype(int) + 1
    field = np.zeros(shape)
    r = int(math.ceil(3 * sigma / step))
    ax = np.arange(-r, r + 1)
    for p in xyz:
        c = np.round((p - lo) / step).astype(int)
        g = [(c[i] + ax) * step + lo[i] - p[i] for i in range(3)]
        blob = np.exp(-(g[0][:, None, None] ** 2 + g[1][None, :, None] ** 2 + g[2][None, None, :] ** 2) / (2 * sigma * sigma))
        field[c[0] - r:c[0] + r + 1, c[1] - r:c[1] + r + 1, c[2] - r:c[2] + r + 1] += blob
    v, f = grid_mesh(field, lo, step, level)
    v, f = largest_piece(v, f)
    v = taubin(v, f, o['smooth'])
    return v, outward(v, f)


def tube_outline(points, bonds, o):
    """A soft outline of a molecule: a tube along every bond, joined smoothly, ring holes left open."""
    step, rad, k = o['grid'], o['tube_radius'], o['blend']
    pad = rad + k + 1
    lo = points.min(0) - pad
    shape = np.ceil((points.max(0) + pad - lo) / step).astype(int) + 1
    gx, gy, gz = [lo[i] + step * np.arange(shape[i]) for i in range(3)]
    P = np.stack(np.meshgrid(gx, gy, gz, indexing='ij'), -1).reshape(-1, 3)
    # smooth union of capsule distances (exponential smooth-min), so joins are rounded
    acc = np.zeros(len(P))
    for a, b in bonds:
        A, B = points[a], points[b]; ab = B - A
        t = np.clip(((P - A) @ ab) / (ab @ ab), 0, 1)
        d = np.linalg.norm(P - (A + t[:, None] * ab), axis=1) - rad
        acc += np.exp(-d / k)
    sdf = (-k * np.log(np.maximum(acc, 1e-300))).reshape(shape)
    v, f = grid_mesh(-sdf, lo, step, 0.0)
    v = taubin(v, f, o['smooth'])
    return v, outward(v, f)


# ---------- the degrader halves ----------
def kabsch(src, dst):
    """Rotation and shift that best lay src onto dst (rows are points)."""
    cs, cd = src.mean(0), dst.mean(0)
    u, _, vt = np.linalg.svd((src - cs).T @ (dst - cd))
    dsign = np.sign(np.linalg.det(vt.T @ u.T))
    R = vt.T @ np.diag([1, 1, dsign]) @ u.T
    return R, cd - cs @ R.T


def story_turn(centres, target, ligase):
    """The turn the story applies: the target-to-ligase axis onto -x (as three.js setFromUnitVectors does)."""
    a = np.asarray(centres[target]) - np.asarray(centres[ligase]); a = a / np.linalg.norm(a)
    v = np.cross(a, [-1.0, 0, 0]); c = -a[0]
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + vx + vx @ vx / (1 + c)


def drawn_layout(names, crystal, bonds, scale=1.0, normal=None):
    """A flat, textbook drawing of a fragment (RDKit's 2D depiction). It lies in the plane facing `normal` (the
    crystal frame), turned within that plane to match its atoms' crystal pose, and centred where they bind."""
    from rdkit import Chem
    from rdkit.Chem import AllChem
    m = Chem.RWMol()
    idx = {}
    for n in names:
        idx[n] = m.AddAtom(Chem.Atom(crystal[n]['element'].capitalize()))
    order = {'SING': Chem.BondType.SINGLE, 'DOUB': Chem.BondType.DOUBLE, 'TRIP': Chem.BondType.TRIPLE}
    for a, b, o, arom in bonds:
        m.AddBond(idx[a], idx[b], Chem.BondType.AROMATIC if arom == 'Y' else order.get(o, Chem.BondType.SINGLE))
    mol = m.GetMol()
    try:
        Chem.SanitizeMol(mol, Chem.SanitizeFlags.SANITIZE_ALL ^ Chem.SanitizeFlags.SANITIZE_PROPERTIES)
    except Exception:
        pass
    AllChem.Compute2DCoords(mol)
    conf = mol.GetConformer()
    flat = np.array([[conf.GetAtomPosition(i).x, conf.GetAtomPosition(i).y, 0.0] for i in range(mol.GetNumAtoms())])
    X = np.array([crystal[n]['xyz'] for n in names])
    flat *= scale                              # RDKit draws bonds 1.5 A long; scale the drawing as a whole
    flat -= flat.mean(0)
    if normal is None:                         # free: the best fit to the crystal atoms in 3D
        R, t = kabsch(flat, X)
        out = flat @ R.T + t
        return out - out.mean(0) + X.mean(0)
    n = normal / np.linalg.norm(normal)
    e1 = np.cross(n, [0, 0, 1.0]) if abs(n[2]) < .9 else np.cross(n, [1.0, 0, 0]); e1 /= np.linalg.norm(e1); e2 = np.cross(n, e1)
    Y = (X - X.mean(0)) @ np.stack([e1, e2]).T   # the crystal atoms seen face-on in that plane
    F = flat[:, :2]
    u, _, vt = np.linalg.svd(F.T @ Y)            # best in-plane turn (a flip allowed: a flat drawing has no back)
    M = u @ vt
    return X.mean(0) + (F @ M) @ np.stack([e1, e2])


def degrader(atoms, origin, cfg, turn):
    d = cfg['degrader']
    lig = {a['name']: a for a in atoms if a['res'] == d['residue'] and a['chain'] == d['chain']}
    if not lig:
        sys.exit(f"no atoms of ligand {d['residue']} in chain {d['chain']}")
    for a in lig.values():
        a['xyz'] = a['xyz'] - origin
    bonds = [(a, b, o, ar) for a, b, o, ar in ligand_bonds(d['residue']) if a in lig and b in lig]
    linker = d['linker_atoms']
    adj = defaultdict(set)
    for a, b, *_ in bonds:
        adj[a].add(b); adj[b].add(a)
    parts, centres, ends = {}, {}, {}
    for key, half in d['halves'].items():
        # the half: everything joined to its attachment atom once the linker is cut out
        seen, todo = set(), [half['attach']]
        while todo:
            x = todo.pop()
            if x in seen or x in linker:
                continue
            seen.add(x); todo += adj[x]
        full = set(seen)                         # the centre is always that of the whole half
        if d['outline'].get('trim_ends'):        # drop end atoms (methyls, halogens, =O, -OH) for a cleaner outline
            seen = {x for x in seen if x == half['attach'] or len([y for y in adj[x] if y in seen]) > 1}
        names = sorted(seen, key=list(lig).index)
        hb = [b for b in bonds if b[0] in seen and b[1] in seen]
        centres[key] = np.mean([lig[n]['xyz'] for n in sorted(full)], 0)
        if d['layout'] == 'drawn':
            facing = d['outline'].get('facing')
            normal = None if facing is None else np.linalg.inv(turn) @ np.asarray(facing, float)
            pts = drawn_layout(names, lig, hb, d['outline'].get('scale', 1.0), normal)
        else:
            pts = np.array([lig[n]['xyz'] for n in names])
        pos = {n: pts[i] for i, n in enumerate(names)}
        ends[key] = pos[half['attach']]
        ib = [(names.index(a), names.index(b)) for a, b, *_ in hb]
        print(f'  {key}: {len(names)} atoms, {len(hb)} bonds ({d["layout"]})')
        parts[key] = tube_outline(pts, ib, d['outline'])
    keys = list(d['halves'])
    curve = [ends[keys[0]]] + [lig[n]['xyz'] for n in linker] + [ends[keys[1]]]
    return parts, centres, curve


# ---------- output ----------
def encode(v, f):
    q = np.round(v * 100)
    if np.abs(q).max() > 32767:
        sys.exit('a part reaches past +-327 A from the origin; move the origin closer')
    big = len(v) > 65535
    return {'pos': base64.b64encode(q.astype('<i2').tobytes()).decode(),
            'idx': base64.b64encode(f.astype('<u4' if big else '<u2').tobytes()).decode(),
            'idx32': big, 'nv': int(len(v)), 'nf': int(len(f))}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--config', default=os.path.join(HERE, 'meshes.config.json'))
    ap.add_argument('--out', default=os.path.join(HERE, '..', 'meshes.json'))
    ap.add_argument('--only', help='comma-separated parts to rebuild; the rest are copied from --base')
    ap.add_argument('--base', default=os.path.join(HERE, '..', 'meshes.json'), help='meshes.json to copy unrebuilt parts from')
    args = ap.parse_args()
    cfg = json.load(open(args.config))
    only = set(args.only.split(',')) if args.only else None
    want = lambda k: only is None or k in only

    out = json.load(open(args.base)) if only and os.path.exists(args.base) else {'units': 'angstrom/100', 'parts': {}, 'linker': {}, 'centres': {}}
    s = cfg['complex']
    print('complex', s['structure'])
    atoms = read_pdb(structure_path(s['structure']))
    prot = [a for a in atoms if a['record'] == 'ATOM']
    origin = np.mean([a['xyz'] for a in prot if a['chain'] in s['origin_chains']], 0)
    print('  origin (centroid of chains %s):' % s['origin_chains'], origin.round(3))
    for key, chain in s['chains'].items():
        if not want(key):
            continue
        xyz = np.array([a['xyz'] for a in prot if a['chain'] == chain]) - origin
        if not len(xyz):
            sys.exit(f'no protein atoms in chain {chain} for {key}')
        v, f = protein_surface(xyz, cfg['surface'])
        out['parts'][key] = encode(v, f); out['centres'][key] = xyz.mean(0).round(3).tolist()
        print(f'  {key}: chain {chain}, {len(xyz)} atoms -> {len(v)} vertices')

    if want('warhead') or want('e3lig') or want('linker'):
        turn = story_turn(out['centres'], 'brd4', 'vhl') if 'brd4' in out['centres'] else np.eye(3)
        parts, centres, curve = degrader(atoms, origin, cfg, turn)
        for k, (v, f) in parts.items():
            out['parts'][k] = encode(v, f); out['centres'][k] = centres[k].round(3).tolist()
            print(f'  {k}: {len(v)} vertices')
        out['linker'] = {'curve': [p.round(3).tolist() for p in curve]}

    for key, t in cfg.get('tags', {}).items():
        if not want(key):
            continue
        print(key, t['structure'])
        xyz = np.array([a['xyz'] for a in read_pdb(structure_path(t['structure'])) if a['record'] == 'ATOM' and a['chain'] in t['chains']])
        xyz = xyz - xyz.mean(0)
        v, f = protein_surface(xyz, cfg['surface'])
        out['parts'][key] = encode(v, f)
        print(f'  {key}: {len(xyz)} atoms -> {len(v)} vertices')

    with open(args.out, 'w') as fh:
        json.dump(out, fh, separators=(',', ':'))
    print('wrote', os.path.relpath(args.out), f'({os.path.getsize(args.out) // 1024} KB)')


if __name__ == '__main__':
    main()
