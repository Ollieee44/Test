"""Round seven: the valves are the proteins. The oyster's two halves are drawn from the traced surfaces of PDB
5T35 (Gadd et al., Nat. Chem. Biol. 2017): BRD4, the target, is the lid, and VHL, the ligase, is the cup. The
SELFTAC between them is the pearl, as in the real complex, where it holds the two proteins together.

Outlines come from editorial/5t35/5t35_poses.json (traced from the PDB), smoothed into blobs. Where a protein
would overlap the pearl its edge is pushed out round it, so the two valves cup the pearl. The traced surface
contours inside each protein double as the shell's growth lines. Minimal outlines, one line weight.

Contract as before: fn(ns, split) -> SVG in a 0-100 box; ink currentColor, the pearl var(--pearl), the clasp
var(--clasp).
"""
import json, math, os
import numpy as np

f = lambda v: f'{v:.2f}'
PT = lambda q: ' '.join(f'{f(x)},{f(y)}' for x, y in q)
D = os.path.dirname(os.path.abspath(__file__)) + '/'
POSES = json.load(open(D + '../../editorial/5t35/5t35_poses.json'))['poses']

def smooth(p, n=10):
    """A closed Catmull-Rom spline through the traced points: the blob."""
    p = np.array(p, float); out = []
    for i in range(len(p)):
        p0, p1, p2, p3 = p[i - 1], p[i], p[(i + 1) % len(p)], p[(i + 2) % len(p)]
        for t in np.linspace(0, 1, n, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    return np.array(out)

def _frame(outer, width, height, rot, centre, flip=False):
    """Map a protein so its long axis lies along rot (degrees), fitted to width x height, centred."""
    o = np.array(outer, float); c = o.mean(0); q = o - c
    w, v = np.linalg.eigh(np.cov(q.T)); ax = v[:, np.argmax(w)]
    a = -math.atan2(ax[1], ax[0]); R = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
    q = q @ R.T
    if flip: q[:, 1] *= -1
    sx = width / (q[:, 0].max() - q[:, 0].min()); sy = height / (q[:, 1].max() - q[:, 1].min())
    b = math.radians(rot); R2 = np.array([[math.cos(b), -math.sin(b)], [math.sin(b), math.cos(b)]])
    def tf(pts):
        z = (np.array(pts, float) - c) @ R.T
        if flip: z[:, 1] *= -1
        return (z * [sx, sy]) @ R2.T + centre
    return tf

def push_out(p, c, r):
    """Points inside the circle (c, r) moved radially onto it: the blob's edge wraps round the pearl."""
    p = p.copy(); d = p - c; n = np.linalg.norm(d, axis=1); m = n < r
    p[m] = c + d[m] / np.maximum(n[m, None], 1e-6) * r
    return p

def protein(key, pose, box, rot, flip, pc, pr, ns, contours=1, w=3.0, solid=False):
    """One valve: the protein's smoothed outline (and its first few surface contours, clipped inside it)."""
    v = POSES[pose][key]; cx, cy, wd, ht = box
    tf = _frame(v['outer'], wd, ht, rot, np.array([cx, cy]), flip)
    out = push_out(tf(smooth(v['outer'])), pc, pr)
    path = 'M' + ' L'.join(f'{f(x)} {f(y)}' for x, y in out) + ' Z'
    inner = ''
    for ring in v['inner'][:contours]:
        q = push_out(tf(smooth(ring)), pc, pr + w)
        inner += f'<path d="M{" L".join(f"{f(x)} {f(y)}" for x, y in q)} Z" fill="none" stroke="currentColor" stroke-width="{w * .55:.2f}" stroke-linejoin="round"/>'
    clip = f'<clipPath id="{ns}c"><path d="{path}"/></clipPath>'
    if solid:   # a solid valve, its surface contours cut through it as lines
        cuts = inner.replace('stroke="currentColor"', 'stroke="#000"')
        m = (f'<mask id="{ns}m" maskUnits="userSpaceOnUse" x="-20" y="-20" width="140" height="140"><rect x="-20" y="-20" width="140" height="140" fill="#fff"/>{cuts}</mask>')
        return (f'<defs>{m}</defs><path d="{path}" stroke="currentColor" stroke-width="{w * .5}" stroke-linejoin="round" mask="url(#{ns}m)"/>'), out
    return (f'<defs>{clip}</defs><path d="{path}" fill="none" stroke="currentColor" stroke-width="{w}" stroke-linejoin="round"/>'
            + (f'<g clip-path="url(#{ns}c)">{inner}</g>' if inner else '')), out

def hexagon(c, r, ang=math.pi / 6):
    return [(c[0] + r * math.cos(ang + k * math.pi / 3), c[1] + r * math.sin(ang + k * math.pi / 3)) for k in range(6)]

def pearl_molecule(c, r, split, style):
    """The pearl as a styled SELFTAC.
    'mol': a pearl with the molecule knocked out of it: two open rings, each on half a linker, meeting at the clasp.
    'halves': the pearl as two halves with a hairline seam: the two halves of the SELFTAC, clasped.
    'ring': the molecule itself, curled into the pearl's circle: two arcs, each ending in a ring, meeting at a gold clasp.
    """
    c = np.array(c, float)
    if style == 'halves':
        if split:
            return (f'<path d="M{f(c[0] - 3)} {f(c[1] - r)} A {f(r)} {f(r)} 0 0 0 {f(c[0] - 3)} {f(c[1] + r)} Z" style="fill:var(--pearl)"/>'
                    f'<path d="M{f(c[0] + 3)} {f(c[1] - r)} A {f(r)} {f(r)} 0 0 1 {f(c[0] + 3)} {f(c[1] + r)} Z" style="fill:var(--pearl)"/>')
        return (f'<circle cx="{f(c[0])}" cy="{f(c[1])}" r="{f(r)}" style="fill:var(--pearl)"/>'
                f'<line x1="{f(c[0])}" y1="{f(c[1] - r)}" x2="{f(c[0])}" y2="{f(c[1] + r)}" style="stroke:var(--clasp)" stroke-width="{f(r * .22)}"/>')
    if style == 'ring':
        w = r * .2; out = ''
        for s in (-1, 1):
            dx = 3 * s if split else 0
            a0, a1 = (math.radians(100), math.radians(250)) if s < 0 else (math.radians(-70), math.radians(80))
            t = np.linspace(a0, a1, 40); arc = np.stack([c[0] + dx + r * .78 * np.cos(t), c[1] + r * .78 * np.sin(t)], 1)
            out += f'<polyline points="{PT(arc)}" fill="none" style="stroke:var(--pearl)" stroke-width="{f(w)}" stroke-linecap="round"/>'
            end = arc[-1] if s < 0 else arc[0]
            out += f'<polygon points="{PT(hexagon(end, r * .22))}" fill="none" style="stroke:var(--pearl)" stroke-width="{f(w * .8)}" stroke-linejoin="round"/>'
        if not split:
            out += (f'<g style="fill:var(--clasp);stroke:var(--clasp)"><line x1="{f(c[0] - r * .28)}" y1="{f(c[1] - r * .74)}" x2="{f(c[0] + r * .28)}" y2="{f(c[1] - r * .74)}" stroke-width="{f(w * .8)}"/>'
                    f'<circle cx="{f(c[0] - r * .28)}" cy="{f(c[1] - r * .74)}" r="{f(w * .75)}"/><circle cx="{f(c[0] + r * .28)}" cy="{f(c[1] - r * .74)}" r="{f(w * .75)}"/></g>')
        return out
    # 'mol': a solid pearl with the molecule cut out of it
    w = r * .13; hl = hexagon(c + [-r * .45, 0], r * .26); hr = hexagon(c + [r * .45, 0], r * .26)
    link = f'<line x1="{f(c[0] - r * .19)}" y1="{f(c[1])}" x2="{f(c[0] + r * .19)}" y2="{f(c[1])}"/>'
    if split:
        return ''.join(f'<g transform="translate({3 * s} 0)">' + _knock(c, r, s, hl if s < 0 else hr, w) + '</g>' for s in (-1, 1))
    return (f'<mask id="pm{int(c[0])}{int(r * 10)}" maskUnits="userSpaceOnUse" x="0" y="0" width="100" height="100"><rect width="100" height="100" fill="#fff"/>'
            f'<g fill="none" stroke="#000" stroke-width="{f(w)}" stroke-linejoin="round"><polygon points="{PT(hl)}"/><polygon points="{PT(hr)}"/>{link}</g></mask>'
            f'<circle cx="{f(c[0])}" cy="{f(c[1])}" r="{f(r)}" style="fill:var(--pearl)" mask="url(#pm{int(c[0])}{int(r * 10)})"/>'
            f'<circle cx="{f(c[0])}" cy="{f(c[1])}" r="{f(r * .16)}" style="fill:var(--clasp)"/>')

def _knock(c, r, s, hexa, w):
    a = 'M{0} {1} A {2} {2} 0 0 {3} {0} {4} Z'.format(f(c[0]), f(c[1] - r), f(r), 0 if s < 0 else 1, f(c[1] + r))
    return f'<path d="{a}" style="fill:var(--pearl)"/><polygon points="{PT(hexa)}" fill="none" style="stroke:var(--bg, #fff)" stroke-width="{f(w)}"/>'

def oyster(ns, split=False, pose=0, lid=('target', 64, 26, -12), cup=('e3', 70, 34, 7), pr=11, pearl='halves',
           contours=1, gap=2.2, w=3.0, flip_lid=True, flip_cup=False, solid=False, hinge=4):
    """Lid above, cup below, cupping the pearl. The lid tilts up at the right and both shift so their left ends
    nearly meet (the hinge) while the right side gapes (the mouth). lid / cup = (protein, width, height, tilt)."""
    pc = np.array([54.0, 52.0]); g = 5 if split else 0
    lk, lw, lh, lt = lid; ck, cw, ch, ct = cup
    top, _ = protein(lk, pose, (pc[0] - hinge, pc[1] - lh * .5 - pr * .35 - g, lw, lh), lt, flip_lid, pc + [0, -g], pr + gap, ns + 'a', contours, w, solid)
    bot, _ = protein(ck, pose, (pc[0] - hinge, pc[1] + ch * .5 + pr * .2 + g, cw, ch), ct, flip_cup, pc + [0, g], pr + gap, ns + 'b', contours, w, solid)
    if pearl == 'mol' and split: pearl = 'halves'
    return top + bot + pearl_molecule(pc, pr, split, pearl)

def V(**kw):
    fn = lambda ns, split=False: oyster(ns, split, **kw); fn.kw = kw; return fn

CONCEPTS = [
    ('line', '01', 'Line', V(),
     'BRD4 as the lid and VHL as the cup, each its traced surface from 5T35 smoothed into one line, with its first surface contour inside as a growth line. Between them, the pearl: the SELFTAC as two halves, clasped by a gold seam.',
     'The brief in one line weight: an open oyster with its pearl, drawn from the real complex.'),
    ('pure', '02', 'Pure outline', V(contours=0),
     'The same, with the outlines alone: no growth lines.',
     'The sleekest; the protein shapes do all the work.'),
    ('solid', '03', 'Solid', V(solid=True, contours=2),
     'The proteins filled, their surface contours cut through them as fine lines, which read as an oyster&rsquo;s growth rings.',
     'Strongest at small sizes, and the contours are a quiet nod to how proteins are drawn.'),
    ('mol', '04', 'Molecule pearl', V(pearl='mol'),
     'The pearl with the SELFTAC cut into it: two open rings on a linker, the gold clasp at its centre.',
     'The molecule is there for anyone who looks closely; from a distance it is a pearl.'),
    ('curl', '05', 'Curled pearl', V(pearl='ring', pr=12),
     'The pearl drawn as the molecule itself: two arcs, each ending in a ring, meeting at the gold clasp to close the circle.',
     'All outline, so it matches the shells exactly; the most diagrammatic.'),
    ('contours', '06', 'Contours', V(contours=3, w=2.6),
     'Three surface contours in each protein, like a topographic map, and like an oyster&rsquo;s layered shell.',
     'The most scientific in feel; busier at small sizes.'),
    ('pose2', '07', 'Another view', V(pose=2),
     'The same complex turned to another of the traced views, so the two proteins have different silhouettes.',
     'Shows how much the shapes can vary while staying true to the structure.'),
    ('ajar', '08', 'Hinged', V(lid=('target', 62, 25, -20), cup=('e3', 70, 34, 10), hinge=7),
     'The lid tilted further and the two proteins brought together on the left, so the hinge and the gaping mouth read clearly.',
     'The most oyster: the shape of a shell opening on its pearl.'),
]

# ---- Round eight: docked. 02's pure outlines brought together until their facing surfaces fit each other, a
# constant gap apart, as docked proteins do; the backs keep their traced shapes.

def _resample(p, step=.8):
    q = np.vstack([p, p[:1]]); s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(q, axis=0), axis=1))]
    t = np.arange(0, s[-1], step)
    return np.stack([np.interp(t, s, q[:, 0]), np.interp(t, s, q[:, 1])], 1)

def _inside(P, q):
    a, b = P, np.roll(P, -1, 0); x, y = q[:, :1], q[:, 1:]
    c = (a[None, :, 1] > y) != (b[None, :, 1] > y)
    xi = a[None, :, 0] + (y - a[None, :, 1]) * (b[None, :, 0] - a[None, :, 0]) / (b[None, :, 1] - a[None, :, 1] + 1e-12)
    return ((c & (x < xi)).sum(1) % 2) == 1

def _nearest(P, q):
    """Nearest point on polygon P's edge to each point of q."""
    a, b = P, np.roll(P, -1, 0); ab = b - a
    t = np.clip(((q[:, None] - a[None]) * ab[None]).sum(-1) / ((ab * ab).sum(-1)[None] + 1e-12), 0, 1)
    n = a[None] + t[..., None] * ab[None]; d = np.linalg.norm(q[:, None] - n, axis=-1); k = d.argmin(1)
    return n[np.arange(len(q)), k], d[np.arange(len(q)), k]

def _clear(p, other, gap, share=.5):
    """Move p's points that are inside `other` or nearer than gap to it out to exactly gap (by `share` of the way)."""
    n, d = _nearest(other, p); ins = _inside(other, p)
    bad = ins | (d < gap)
    if not bad.any(): return p, 0
    v = np.where(ins[:, None], n - p, p - n); v /= np.maximum(np.linalg.norm(v, axis=1, keepdims=True), 1e-9)
    target = n + v * gap
    p = p.copy(); p[bad] += (target[bad] - p[bad]) * share
    return p, bad.sum()

def _relax(p, k=.35, n=2):
    for _ in range(n): p = p + k * ((np.roll(p, 1, 0) + np.roll(p, -1, 0)) / 2 - p)
    return p

def dock(lid_pts, cup_pts, pc, pr, gap, iters=80, w=0.0):
    """Resolve the overlap: both proteins give way equally to each other, and fully to the pearl, until every
    point is at least `gap` from the other protein and from the pearl; lightly smoothed as it goes."""
    L, C = _resample(lid_pts), _resample(cup_pts)
    pg = gap + w / 2; gap = gap + w          # gaps measured between the drawn lines' edges
    for i in range(iters):
        L2, nl = _clear(L, C, gap, .5); C2, nc = _clear(C, L, gap, .5)
        L, C = push_out(L2, pc, pr + pg), push_out(C2, pc, pr + pg)
        if i % 4 == 3: L, C = _relax(L, .3, 1), _relax(C, .3, 1)
        if i > 20 and nl + nc == 0: break
    # a last pass so the gap holds exactly after smoothing
    for _ in range(6):
        L, _ = _clear(L, C, gap, .5); C, _ = _clear(C, L, gap, .5)
        L, C = push_out(L, pc, pr + pg), push_out(C, pc, pr + pg)
    return _resample(L, 1.0), _resample(C, 1.0)

def docked(ns, split=False, pose=0, overlap=8, gap=2.6, pr=11, lid=('target', 66, 28, -9), cup=('e3', 72, 36, 6),
           w=3.0, flip_lid=True, flip_cup=False, pearl='halves', hinge=4):
    """02 docked: the lid and cup placed `overlap` units into each other, then resolved to fit with a `gap`."""
    pc = np.array([54.0, 52.0])
    lk, lw, lh, lt = lid; ck, cw, ch, ct = cup
    def place(key, box, rot, flip):
        v = POSES[pose][key]; tf = _frame(v['outer'], box[2], box[3], rot, np.array(box[:2]), flip)
        return tf(smooth(v['outer']))
    L0 = place(lk, (pc[0] - hinge, pc[1] - lh * .5 - pr * .35 + overlap / 2, lw, lh), lt, flip_lid)
    C0 = place(ck, (pc[0] - hinge, pc[1] + ch * .5 + pr * .2 - overlap / 2, cw, ch), ct, flip_cup)
    L, C = dock(L0, C0, pc, pr, gap, w=w)
    g = 5 if split else 0
    path = lambda P, dy: f'<path d="M{" L".join(f"{f(x)} {f(y + dy)}" for x, y in P)} Z" fill="none" stroke="currentColor" stroke-width="{w}" stroke-linejoin="round"/>'
    return path(L, -g) + path(C, g) + pearl_molecule(pc, pr, split, pearl)

def DV(**kw):
    fn = lambda ns, split=False: docked(ns, split, **kw); fn.kw = kw; return fn

# ---- Round nine: 04 (docked, hairline gap) turned so the seam runs on a diagonal, with texture lines for depth.

def docked_geom(pose=0, overlap=14, gap=1.8, pr=11, lid=('target', 66, 28, -9), cup=('e3', 72, 36, 6), w=3.0,
                flip_lid=True, flip_cup=False, hinge=4, balance=None, blob=None):
    """blob: {'lid': exaggerate() settings, 'cup': ...} applied before docking.
    balance (a number): place each protein so it reaches that far past the pearl's centre line before docking
    (lid downward, cup upward), so the seam runs through the pearl and each protein takes half of it."""
    pc = np.array([54.0, 52.0]); lk, lw, lh, lt = lid; ck, cw, ch, ct = cup
    def place(key, box, rot, flip):
        v = POSES[pose][key]; tf = _frame(v['outer'], box[2], box[3], rot, np.array(box[:2]), flip)
        return tf(smooth(v['outer'])), tf
    L0, tl = place(lk, (pc[0] - hinge, pc[1] - lh * .5 - pr * .35 + overlap / 2, lw, lh), lt, flip_lid)
    C0, tc = place(ck, (pc[0] - hinge, pc[1] + ch * .5 + pr * .2 - overlap / 2, cw, ch), ct, flip_cup)
    if blob:
        L0 = exaggerate(L0, **blob.get('lid', {})); C0 = exaggerate(C0, **blob.get('cup', {}))
    if balance is not None:
        near = lambda P: P[np.abs(P[:, 0] - pc[0]) < pr * 1.6]
        dl = (pc[1] + balance) - near(L0)[:, 1].max(); dc = (pc[1] - balance) - near(C0)[:, 1].min()
        L0 = L0 + [0, dl]; C0 = C0 + [0, dc]
        tl0, tc0 = tl, tc; tl = lambda q, f=tl0, d=dl: f(q) + [0, d]; tc = lambda q, f=tc0, d=dc: f(q) + [0, d]
    L, C = dock(L0, C0, pc, pr, gap, w=w)
    return L, C, pc, tl, tc

def _normals(P):
    d = np.roll(P, -1, 0) - np.roll(P, 1, 0); n = np.stack([d[:, 1], -d[:, 0]], 1)
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-9)
    # outward: the side away from the centroid on average
    if ((P - P.mean(0)) * n).sum() < 0: n = -n
    return n

_SDF = {}
def _sdf(P, res=.25):
    """Distance from the outline, inside the shape, on a fine grid (cached per outline)."""
    key = (P.shape, float(P[0, 0]), float(P[0, 1]), float(P[:, 0].sum()))
    if key not in _SDF:
        from scipy.ndimage import distance_transform_edt
        from matplotlib.path import Path as _MP
        lo = P.min(0) - 2; hi = P.max(0) + 2
        xs = np.arange(lo[0], hi[0], res); ys = np.arange(lo[1], hi[1], res)
        X, Y = np.meshgrid(xs, ys); inside = _MP(P).contains_points(np.stack([X.ravel(), Y.ravel()], 1)).reshape(X.shape)
        _SDF[key] = (distance_transform_edt(inside) * res, lo, res)
    return _SDF[key]

def inset(P, d):
    """The line inside the shape at distance d from its outline: an iso-line of the distance field, so it never
    loops back on itself in tight curves. Returns the longest closed contour (or None if the shape is thinner)."""
    from skimage import measure
    dist, lo, res = _sdf(P)
    cs = measure.find_contours(dist, d)
    if not cs: return None
    c = max(cs, key=len)
    Q = np.stack([lo[0] + c[:, 1] * res, lo[1] + c[:, 0] * res], 1)
    Q = _resample(Q, .8)
    return _relax(Q, .4, 2)

def _runs(P, keep):
    """Split a closed outline into the polylines where keep is true."""
    out, cur = [], []
    idx = list(range(len(P)))
    start = int(np.argmin(keep)) if not keep.all() else 0
    for i in idx[start:] + idx[:start]:
        if keep[i]: cur.append(P[i])
        elif len(cur) > 3: out.append(np.array(cur)); cur = []
        else: cur = []
    if len(cur) > 3: out.append(np.array(cur))
    return out

def textured(ns, split=False, angle=-32, texture='layers', gap=1.8, overlap=14, pose=0, pearl='halves', w=3.0, light=(-1, -1)):
    """The docked pair turned by `angle` degrees about the pearl, so the seam runs on a diagonal, with texture:
    'layers': two inset outlines in each protein, like contours on a surface;
    'traced': the real surface contours from 5T35, clipped inside each protein;
    'shade':  inset contours only on the side turned away from the light (top left), so the form turns;
    'rim':    shading plus one highlight line on the lit side."""
    L, C, pc, tl, tc = docked_geom(pose, overlap, gap, w=w)
    a = math.radians(angle); R = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
    rot = lambda P: (np.asarray(P) - pc) @ R.T + [50, 50]
    L, C = rot(L), rot(C)
    # fit into the box by moving the geometry itself (so the drawn coordinates are the final ones)
    allp = np.vstack([L, C]); lo, hi = allp.min(0) - w, allp.max(0) + w
    sc = min(1.0, 92 / max(hi - lo)); mid = (lo + hi) / 2
    fit = lambda P: (np.asarray(P) - mid) * sc + 50
    L, C = fit(L), fit(C); c0 = fit(np.array([50.0, 50.0])); pr_ = 11 * sc
    rot0 = rot
    rot = lambda P: fit(rot0(P))
    seam_n = R @ np.array([0, 1.0])                      # from lid to cup, after turning
    g = 5 if split else 0
    lt = np.array(light, float); lt /= np.linalg.norm(lt)
    def tex(P, key, tf, ns2):
        out = ''
        if texture == 'layers':
            for k, d in enumerate((4.2, 8.6)):
                Q = inset(P, d)
                if Q is None: continue
                out += f'<path d="{_d(Q)}" fill="none" stroke="currentColor" stroke-width="{w * (.5 - .1 * k):.2f}" stroke-linejoin="round"/>'
        elif texture == 'traced':
            for ring in POSES[pose][key]['inner'][:3]:
                q = rot(tf(smooth(ring)))
                out += f'<path d="{_d(q)}" fill="none" stroke="currentColor" stroke-width="{w * .42:.2f}" stroke-linejoin="round"/>'
        else:
            for k, d in enumerate((3.8, 7.6, 11.4)):
                Q = inset(P, d)
                if Q is None: continue
                n = _normals(Q); dot = (n * lt).sum(1)
                for run in _runs(Q, dot < (-.15 + .25 * k)):
                    out += f'<polyline points="{PT(run)}" fill="none" stroke="currentColor" stroke-width="{w * (.5 - .09 * k):.2f}" stroke-linecap="round" stroke-linejoin="round"/>'
            if texture == 'rim':
                Q = inset(P, 3.6)
                if Q is None: Q = P
                n = _normals(Q); dot = (n * lt).sum(1)
                for run in _runs(Q, dot > .55):
                    out += f'<polyline points="{PT(run)}" fill="none" stroke="currentColor" stroke-width="{w * .38:.2f}" stroke-linecap="round" stroke-dasharray="0.1 2.4"/>'
        return f'<clipPath id="{ns2}"><path d="{_d(P)}"/></clipPath><g clip-path="url(#{ns2})">{out}</g>'
    body = ''
    for P, key, tf, s, nm in ((L, 'target', tl, -1, 'a'), (C, 'e3', tc, 1, 'b')):
        off = seam_n * g * s
        body += (f'<g transform="translate({f(off[0])} {f(off[1])})"><path d="{_d(P)}" fill="none" stroke="currentColor" stroke-width="{w}" stroke-linejoin="round"/>'
                 + tex(P, key, tf, ns + nm) + '</g>')
    pm = pearl_molecule(c0, pr_, split, pearl)
    pm = f'<g transform="rotate({angle} {f(c0[0])} {f(c0[1])})">{pm}</g>'
    return body + pm

def _d(P):
    return 'M' + ' L'.join(f'{f(x)} {f(y)}' for x, y in P) + ' Z'

def TV(**kw):
    fn = lambda ns, split=False: textured(ns, split, **kw); fn.kw = kw; return fn

CONCEPTS9 = [
    ('layers', '01', 'Diagonal, layered', TV(texture='layers'),
     '04 turned so the seam between the proteins runs on a diagonal, with two lines inside each protein at an even depth from its edge, like contours on a surface.',
     'The cleanest way to add depth: the lines follow each protein&rsquo;s own shape, so it stays a protein outline.'),
    ('shade', '02', 'Diagonal, shaded', TV(texture='shade'),
     'The same lines kept only on the side of each protein turned away from the light (top left), so the form turns away into shadow.',
     'The most 3D: light from one side, shade on the other, from line alone.'),
    ('rim', '03', 'Shaded, with highlight', TV(texture='rim'),
     'Shading as 02, plus a dotted highlight just inside the lit edge.',
     'Most like a rendered surface; the dots are a detail for large sizes.'),
    ('traced', '04', 'Traced contours', TV(texture='traced'),
     'The real surface contours from the 5T35 trace inside each protein, as in round seven.',
     'The most scientific; the contours are the proteins&rsquo; own.'),
    ('other', '05', 'Other diagonal', TV(texture='shade', angle=32),
     'Shaded, turned the other way, so the seam falls from top left to bottom right.',
     'Compare the two diagonals: this one reads more as a shell lying open.'),
    ('steep', '06', 'Steeper, layered', TV(texture='layers', angle=-48),
     'Layered, turned further, close to 45 degrees.',
     'The most dynamic angle; the pair reads as a single rounded form.'),
]

# ---- Round ten: round nine's 02, rounder at the right, with the pearl split along the seam and a short, thick
# linker cut out of it.

def round_right(L, C, amount, pc, pr, gap, w, start=.45):
    """Smooth the pair progressively more toward the right (the mouth), then restore the even gap."""
    if amount <= 0: return L, C
    allp = np.vstack([L, C]); x0, x1 = allp[:, 0].min(), allp[:, 0].max(); xs = x1 - start * (x1 - x0)
    def sm(P):
        wt = np.clip((P[:, 0] - xs) / (x1 - xs), 0, 1) ** 1.2 * amount
        for _ in range(int(60 * amount) + 10):
            P = P + .5 * wt[:, None] * ((np.roll(P, 1, 0) + np.roll(P, -1, 0)) / 2 - P)
        return _resample(P, 1.0)
    L, C = sm(L), sm(C)
    pg, g = gap + w / 2, gap + w
    for _ in range(30):
        L, _ = _clear(L, C, g, .5); C, _ = _clear(C, L, g, .5)
        L, C = push_out(L, pc, pr + pg), push_out(C, pc, pr + pg)
    return _resample(L, 1.0), _resample(C, 1.0)

def pearl_linker(c, r, angle, split, link=(.62, .34), seam=.09, ns='p', nacre=None):
    """The pearl split along the shell's seam into two halves, one by each protein, held by a short, thick linker
    cut out of it as negative space across the split. link = (length, thickness) as fractions of the radius."""
    ll, lw = link[0] * r, link[1] * r; hg = seam * r; g = 4 if split else 0
    m = (f'<mask id="{ns}" maskUnits="userSpaceOnUse" x="{f(c[0] - 2 * r)}" y="{f(c[1] - 2 * r)}" width="{f(4 * r)}" height="{f(4 * r)}">'
         f'<rect x="{f(c[0] - 2 * r)}" y="{f(c[1] - 2 * r)}" width="{f(4 * r)}" height="{f(4 * r)}" fill="#fff"/>'
         f'<rect x="{f(c[0] - 2 * r)}" y="{f(c[1] - hg / 2)}" width="{f(4 * r)}" height="{f(hg)}" fill="#000"/>'
         f'<rect x="{f(c[0] - lw / 2)}" y="{f(c[1] - ll / 2)}" width="{f(lw)}" height="{f(ll)}" rx="{f(lw / 2)}" fill="#000"/></mask>')
    halves = (f'<g transform="translate(0 {-g})"><path d="M{f(c[0] - r)} {f(c[1])} A {f(r)} {f(r)} 0 0 1 {f(c[0] + r)} {f(c[1])} Z" style="fill:var(--pearl)" mask="url(#{ns})"/></g>'
              f'<g transform="translate(0 {g})"><path d="M{f(c[0] - r)} {f(c[1])} A {f(r)} {f(r)} 0 0 0 {f(c[0] + r)} {f(c[1])} Z" style="fill:var(--pearl)" mask="url(#{ns})"/></g>')
    if nacre:   # a photographic pearl: body gradient, overtone, dark rim and a specular highlight, through the same split/linker mask
        P_ = NACRE[nacre]; gid = ns + 'pg'; oid = ns + 'po'
        defs = (f'<radialGradient id="{gid}" gradientUnits="userSpaceOnUse" cx="{f(c[0] - r * .3)}" cy="{f(c[1] - r * .35)}" r="{f(r * 1.25)}">'
                f'<stop offset="0" stop-color="#ffffff"/><stop offset=".22" stop-color="{P_["pearl"][0]}"/>'
                f'<stop offset=".7" stop-color="{P_["pearl"][1]}"/><stop offset="1" stop-color="{P_["pearl"][2]}"/></radialGradient>'
                f'<radialGradient id="{oid}" gradientUnits="userSpaceOnUse" cx="{f(c[0] + r * .35)}" cy="{f(c[1] + r * .4)}" r="{f(r * .9)}">'
                f'<stop offset="0" stop-color="{P_["overtone"]}" stop-opacity=".55"/><stop offset="1" stop-color="{P_["overtone"]}" stop-opacity="0"/></radialGradient>')
        halves = halves.replace('style="fill:var(--pearl)"', f'fill="url(#{gid})"')
        over = (f'<g transform="translate(0 {-g})"><path d="M{f(c[0] - r)} {f(c[1])} A {f(r)} {f(r)} 0 0 1 {f(c[0] + r)} {f(c[1])} Z" fill="url(#{oid})" mask="url(#{ns})"/></g>'
                f'<g transform="translate(0 {g})"><path d="M{f(c[0] - r)} {f(c[1])} A {f(r)} {f(r)} 0 0 0 {f(c[0] + r)} {f(c[1])} Z" fill="url(#{oid})" mask="url(#{ns})"/></g>')
        spec = f'<ellipse cx="{f(c[0] - r * .38)}" cy="{f(c[1] - r * .42)}" rx="{f(r * .2)}" ry="{f(r * .13)}" transform="rotate(-35 {f(c[0] - r * .38)} {f(c[1] - r * .42)})" fill="#fff" opacity=".85"/>'
        return f'<defs>{defs}</defs><g transform="rotate({angle} {f(c[0])} {f(c[1])})">{m}{halves}{over}</g>' + ('' if split else spec)
    return f'<g transform="rotate({angle} {f(c[0])} {f(c[1])})">{m}{halves}</g>'

def textured2(ns, split=False, angle=-32, rnd=.6, link=(.7, .44), seam=.09, gap=1.8, overlap=14, pose=0, w=3.0, light=(-1, -1)):
    """Round nine's 02 (diagonal, shaded) with a rounder right side and the linker pearl."""
    L, C, pc, tl, tc = docked_geom(pose, overlap, gap, w=w)
    a = math.radians(angle); R = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
    L, C = (L - pc) @ R.T + 50, (C - pc) @ R.T + 50
    L, C = round_right(L, C, rnd, np.array([50.0, 50.0]), 11, gap, w)     # the right as you see it
    allp = np.vstack([L, C]); lo, hi = allp.min(0) - w, allp.max(0) + w
    sc = min(1.0, 92 / max(hi - lo)); mid = (lo + hi) / 2
    fit = lambda P: (np.asarray(P) - mid) * sc + 50
    L, C = fit(L), fit(C); c0 = fit(np.array([50.0, 50.0])); pr_ = 11 * sc
    seam_n = R @ np.array([0, 1.0]); g = 5 if split else 0
    lt = np.array(light, float); lt /= np.linalg.norm(lt)
    body = ''
    for P, s, nm in ((L, -1, 'a'), (C, 1, 'b')):
        out = ''
        for k, d in enumerate((3.8, 7.6, 11.4)):
            Q = inset(P, d)
            if Q is None: continue
            n = _normals(Q); dot = (n * lt).sum(1)
            for run in _runs(Q, dot < (-.15 + .25 * k)):
                out += f'<polyline points="{PT(run)}" fill="none" stroke="currentColor" stroke-width="{w * (.5 - .09 * k):.2f}" stroke-linecap="round" stroke-linejoin="round"/>'
        off = seam_n * g * s
        body += (f'<g transform="translate({f(off[0])} {f(off[1])})"><path d="{_d(P)}" fill="none" stroke="currentColor" stroke-width="{w}" stroke-linejoin="round"/>'
                 f'<clipPath id="{ns}{nm}"><path d="{_d(P)}"/></clipPath><g clip-path="url(#{ns}{nm})">{out}</g></g>')
    return body + pearl_linker(c0, pr_, angle, split, link, seam, ns + 'p')

def TV2(**kw):
    fn = lambda ns, split=False: textured2(ns, split, **kw); fn.kw = kw; return fn

# ---- Round eleven: the pair as one round form. A circle split by a gentle S-shaped seam through the pearl; each
# half's outer edge carries the lumps of its own traced protein (BRD4 above, VHL below), so the halves differ and
# read as proteins while the whole reads as round. Hairline gap, shading, diagonal and linker pearl as before.

def _profile(key, pose, n=360, keep=8):
    """A protein's outline as a radial profile about its centroid: r(phi)/mean - 1, low-passed to its broad lobes."""
    o = smooth(POSES[pose][key]['outer'], 16); c = o.mean(0); d = o - c
    ang = np.mod(np.arctan2(d[:, 1], d[:, 0]), 2 * np.pi); r = np.linalg.norm(d, axis=1)
    k = np.argsort(ang); ang, r = ang[k], r[k]
    phi = np.linspace(0, 2 * np.pi, n, endpoint=False)
    rr = np.interp(phi, ang, r, period=2 * np.pi); rr = rr / rr.mean() - 1
    F = np.fft.rfft(rr); F[keep:] = 0
    return np.fft.irfft(F, n)

def circle_pair(ns, split=False, R=38.0, amp=.12, wave=4.0, angle=-32, pose=0, gap=1.8, w=3.0, pr=11.0,
                link=(.7, .44), seam=.09, lobes=8, phase=(.0, .0), light=(-1, -1), shade=True):
    """amp: how far the protein lumps push the outline in and out (fraction of R); wave: the seam's S (units);
    lobes: how many of each protein's broad lobes are kept; phase: turns each protein's profile (fraction of a turn)."""
    pu = np.roll(_profile('target', pose, keep=lobes), int(phase[0] * 360))
    pl = np.roll(_profile('e3', pose, keep=lobes), int(phase[1] * 360))
    def arc(t0, t1, prof):
        t = np.linspace(t0, t1, 200); u = (t - t0) / (t1 - t0)
        bump = np.interp(u * 2 * np.pi, np.linspace(0, 2 * np.pi, len(prof), endpoint=False), prof, period=2 * np.pi)
        taper = np.clip(np.sin(u * np.pi) * 2.2, 0, 1)            # back to the circle where the halves meet
        r = R * (1 + amp * bump * taper)
        return np.stack([r * np.cos(t), r * np.sin(t)], 1)
    xs = np.linspace(-R, R, 160); seam_pts = np.stack([xs, wave * np.sin(np.pi * xs / R)], 1)
    up = np.vstack([arc(np.pi, 2 * np.pi, pu), seam_pts[::-1]])       # y down: pi..2pi is the top
    lo = np.vstack([arc(0, np.pi, pl), seam_pts])
    up, lo = _resample(up, .8), _resample(lo, .8)
    c = np.zeros(2); pg, g2 = gap + w / 2, gap + w
    for i in range(40):
        up, lo = push_out(up, c, pr + pg), push_out(lo, c, pr + pg)
        up, _ = _clear(up, lo, g2, .5); lo, _ = _clear(lo, up, g2, .5)
        if i % 5 == 4: up, lo = _relax(up, .25, 1), _relax(lo, .25, 1)
    for _ in range(6):
        up, _ = _clear(up, lo, g2, .5); lo, _ = _clear(lo, up, g2, .5)
        up, lo = push_out(up, c, pr + pg), push_out(lo, c, pr + pg)
    a = math.radians(angle); Rm = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
    up, lo = up @ Rm.T, lo @ Rm.T
    allp = np.vstack([up, lo]); lo_, hi_ = allp.min(0) - w, allp.max(0) + w
    sc = min(1.0, 92 / max(hi_ - lo_)); mid = (lo_ + hi_) / 2
    fit = lambda P: (np.asarray(P) - mid) * sc + 50
    up, lo = fit(_resample(up, 1.0)), fit(_resample(lo, 1.0)); c0 = fit(np.zeros(2)); pr_ = pr * sc
    seam_n = Rm @ np.array([0, 1.0]); gsp = 5 if split else 0
    lt = np.array(light, float); lt /= np.linalg.norm(lt)
    body = ''
    for P, s, nm in ((up, -1, 'a'), (lo, 1, 'b')):
        out = ''
        if shade:
            for k, d in enumerate((3.8, 7.6, 11.4)):
                Q = inset(P, d)
                if Q is None: continue
                n = _normals(Q); dot = (n * lt).sum(1)
                rad = Q - c0; rad /= np.maximum(np.linalg.norm(rad, axis=1, keepdims=True), 1e-9)
                outer = (n * rad).sum(1) > .35                     # only along the outer surface, not the seam
                for run in _runs(Q, (dot < (-.1 + .25 * k)) & outer):
                    out += f'<polyline points="{PT(run)}" fill="none" stroke="currentColor" stroke-width="{w * (.5 - .09 * k):.2f}" stroke-linecap="round" stroke-linejoin="round"/>'
        off = seam_n * gsp * s
        body += (f'<g transform="translate({f(off[0])} {f(off[1])})"><path d="{_d(P)}" fill="none" stroke="currentColor" stroke-width="{w}" stroke-linejoin="round"/>'
                 f'<clipPath id="{ns}{nm}"><path d="{_d(P)}"/></clipPath><g clip-path="url(#{ns}{nm})">{out}</g></g>')
    tilt = angle + math.degrees(math.atan(wave * math.pi / R))         # the seam's direction at the pearl
    return body + pearl_linker(c0, pr_, tilt, split, link, seam, ns + 'p')

def CP(**kw):
    fn = lambda ns, split=False: circle_pair(ns, split, **kw); fn.kw = kw; return fn

# ---- Round twelve: two proteins first. Real traced outlines (no circle, no shell lines), drawn as molecular
# surfaces (overlapping round bumps), docked along their whole facing side round the pearl. The oyster is only in
# the silhouette the pair makes together.

def close_mouth(L, C, reach=16.0, iters=60, gap=1.8, w=3.0, pc=None, pr=11.0, relax=True):
    L, C = _resample(L, .8), _resample(C, .8)
    assert len(L) < 4000 and len(C) < 4000, 'outline exploded'
    """Pull each protein's facing surface toward the other wherever they are within `reach`, then clear back to
    the gap, so the open mouth closes and the two meet along their whole facing side."""
    g2, pg = gap + w, gap + w / 2
    for i in range(iters):
        for A, B, which in ((L, C, 0), (C, L, 1)):
            n, d = _nearest(B, A)
            wt = np.clip(1 - (d - g2) / (reach - g2), 0, 1) ** 1.5 * (d > g2)
            A = A + (n - A) * (wt * .12)[:, None]
            if which == 0: L = A
            else: C = A
        L, _ = _clear(L, C, g2, .5); C, _ = _clear(C, L, g2, .5)
        if pc is not None: L, C = push_out(L, pc, pr + pg), push_out(C, pc, pr + pg)
        if relax and i % 6 == 5: L, C = _relax(_resample(L, .8), .25, 1), _relax(_resample(C, .8), .25, 1)
    return _resample(L, .8) if relax else L, _resample(C, .8) if relax else C

def molecular(P, r=3.2, seed=0, vary=.28, res=.2, soften=0.0, spacing=1.15, sink=.9):
    """The outline redrawn as a molecular surface: the shape filled in, with round bumps of radius ~r set along
    its edge, and the silhouette of the lot traced back out (scalloped, as space-filling surfaces are)."""
    from matplotlib.path import Path as _MP
    from skimage import measure
    rng = np.random.default_rng(seed)
    lo = P.min(0) - 2 * r; hi = P.max(0) + 2 * r
    xs = np.arange(lo[0], hi[0], res); ys = np.arange(lo[1], hi[1], res); X, Y = np.meshgrid(xs, ys)
    pts = np.stack([X.ravel(), Y.ravel()], 1)
    core = inset(P, r * sink)
    field = _MP(core if core is not None else P).contains_points(pts).reshape(X.shape).astype(float)
    ring = _resample(P if core is None else core, r * spacing)
    for c in ring:
        rr = r * (1 + vary * (rng.random() - .5) * 2)
        field = np.maximum(field, ((X - c[0]) ** 2 + (Y - c[1]) ** 2 <= rr * rr).astype(float))
    if soften > 0:   # blur the union before tracing: the lobes stay, the notches between them round into waves
        from scipy.ndimage import gaussian_filter
        field = gaussian_filter(field, soften / res)
    cs = measure.find_contours(field, .5); cc = max(cs, key=len)
    Q = np.stack([lo[0] + cc[:, 1] * res, lo[1] + cc[:, 0] * res], 1)
    return _resample(Q, .6)

def two_proteins(ns, split=False, angle=-32, bump=3.2, overlap=14, gap=1.8, w=2.8, pose=0, reach=16.0,
                 link=(.7, .44), seam=.09, contour=False, pr=11.0, lid=('target', 66, 28, -9), cup=('e3', 72, 36, 6), balance=None, blob=None, fill=None, soften=0.0, lumps=0, tint=False, spacing=1.15, sink=.9, waves=None, island=None, pearl=None):
    gk = repr((angle, bump, overlap, gap, w, pose, reach, pr, lid, cup, balance, blob, soften, spacing, sink, waves))
    if gk in _GEOM_CACHE: L, C, c0, pr_, seam_n, tl, tc, pc, Rm, fit = _GEOM_CACHE[gk]
    else: L, C, c0, pr_, seam_n, tl, tc, pc, Rm, fit = _GEOM_CACHE.setdefault(gk, _two_geom(angle, bump, overlap, gap, w, pose, reach, pr, lid, cup, balance, blob, soften, spacing, sink, waves))
    return _two_draw(ns, split, L, C, c0, pr_, seam_n, tl, tc, pc, Rm, fit, w, pose, link, seam, contour, angle, fill, lumps, tint, island, pearl)

_GEOM_CACHE = {}
def _two_geom(angle, bump, overlap, gap, w, pose, reach, pr, lid, cup, balance, blob, soften, spacing, sink, waves):
    L, C, pc, tl, tc = docked_geom(pose, overlap, gap, w=w, lid=lid, cup=cup, balance=balance, blob=blob)
    if reach > 0: L, C = close_mouth(L, C, reach, gap=gap, w=w, pc=pc, pr=pr)
    if bump > 0:
        L, C = (molecular(L, bump, 1, soften=soften, spacing=spacing, sink=sink),
                molecular(C, bump, 2, soften=soften, spacing=spacing, sink=sink))
        if reach > 0: L, C = close_mouth(L, C, max(8.0, bump * 3), 30, gap=gap, w=w, pc=pc, pr=pr, relax=False)   # re-dock after the bumps
    if waves:     # (n, depth, phase, sharp) per protein: a few big undulations, then re-dock
        L0_, C0_ = L, C
        L = undulate(L0_, *waves[0], other=C0_, pc=pc, pr=pr); C = undulate(C0_, *waves[1], other=L0_, pc=pc, pr=pr)
        L, C = close_mouth(L, C, 10.0, 40, gap=gap, w=w, pc=pc, pr=pr, relax=False)
    g2, pg = gap + w, gap + w / 2
    for _ in range(14):                                         # keep the gap and the pocket exact after the bumps
        L, _ = _clear(L, C, g2, .5); C, _ = _clear(C, L, g2, .5)
        L, C = push_out(L, pc, pr + pg), push_out(C, pc, pr + pg)
    a = math.radians(angle); Rm = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
    L, C = (L - pc) @ Rm.T, (C - pc) @ Rm.T
    allp = np.vstack([L, C]); lo, hi = allp.min(0) - w, allp.max(0) + w
    sc = min(1.0, 92 / max(hi - lo)); mid = (lo + hi) / 2
    fit = lambda P: (np.asarray(P) - mid) * sc + 50
    L, C = fit(L), fit(C); c0 = fit(np.zeros(2)); pr_ = pr * sc
    seam_n = Rm @ np.array([0, 1.0])
    return L, C, c0, pr_, seam_n, tl, tc, pc, Rm, fit

def _two_draw(ns, split, L, C, c0, pr_, seam_n, tl, tc, pc, Rm, fit, w, pose, link, seam, contour, angle, fill, lumps, tint, island, pearl=None):
    g = 5 if split else 0
    body = ''
    if fill and fill.startswith('mono:'):   # one colour (currentColor), the pearl too: for overlays
        for P, key in ((L, 'target'), (C, 'e3')):
            body += _mono(P, key, fill[5:], ns + key[0], w, island)
        return f'<g style="--pearl:currentColor">{body}{pearl_linker(c0, pr_, angle, split, link, seam, ns + "p")}</g>'
    for P, key, tf, s, nm in ((L, 'target', tl, -1, 'a'), (C, 'e3', tc, 1, 'b')):
        inner = ''
        if contour:   # one real surface contour from the trace, as a quiet interior line
            q = fit((tf(smooth(POSES[pose][key]['inner'][0])) - pc) @ Rm.T)
            inner = (f'<clipPath id="{ns}{nm}"><path d="{_d(inset(P, 3) if inset(P, 3) is not None else P)}"/></clipPath>'
                     f'<g clip-path="url(#{ns}{nm})"><path d="{_d(q)}" fill="none" stroke="currentColor" stroke-width="{w * .45:.2f}" stroke-linejoin="round"/></g>')
        off = seam_n * g * s
        if fill and fill.startswith('nacre:'):
            body += f'<g transform="translate({f(off[0])} {f(off[1])})">' + _nacre_fill(P, key, fill[6:], ns + nm, w) + '</g>'
            continue
        if fill:
            body += f'<g transform="translate({f(off[0])} {f(off[1])})">' + _filled(P, key, fill, ns + nm, w, lumps=lumps, tint=tint, seed=3 if key == "target" else 7, island=island) + '</g>'
            continue
        body += (f'<g transform="translate({f(off[0])} {f(off[1])})"><path d="{_d(P)}" fill="none" stroke="currentColor" stroke-width="{w}" stroke-linejoin="round"/>{inner}</g>')
    nac = fill[6:] if fill and fill.startswith('nacre:') else None
    if pearl: return body + pearl_alt(c0, pr_, angle, pearl, ns + 'p')
    return body + pearl_linker(c0, pr_, angle, split, link, seam, ns + 'p', nacre=nac)

def _filled(P, key, style, ns, w, light=(-1, -1), lumps=0, tint=False, seed=0, island=None):
    """A protein filled in the 3D story's colours (var(--brd4) / var(--vhl)) with an ink outline (var(--outline)),
    and depth by style: 'flat'; 'rings' (contour rings at even depths, in var(--ring), as on the 3D models);
    'toon' (a lit band and a shade band, cut by the shape shifted toward and away from the light); 'soft' (a
    radial gradient lit from the top left); 'model' (toon plus rings: closest to the 3D story)."""
    col = 'var(--brd4)' if key == 'target' else 'var(--vhl)'
    shade = f'color-mix(in srgb, {col} 72%, var(--outline))'; lit = f'color-mix(in srgb, {col} 55%, #fff)'
    lt = np.array(light, float); lt /= np.linalg.norm(lt)
    d = _d(P); clip = f'<clipPath id="{ns}k"><path d="{d}"/></clipPath>'
    out = clip
    if style in ('toon', 'model'):
        a, b = -lt * 5.5, lt * 2.6            # shade on the far side, a thin lit band on the near side
        out += (f'<g clip-path="url(#{ns}k)"><path d="{d}" style="fill:{shade}"/>'
                f'<path d="{d}" transform="translate({f(a[0])} {f(a[1])})" style="fill:{col}"/>'
                f'<path d="{d}" transform="translate({f(b[0])} {f(b[1])})" style="fill:{col}" opacity="0"/></g>')
        # the lit band: the shape minus itself shifted away from the light
        out += (f'<mask id="{ns}m" maskUnits="userSpaceOnUse" x="-20" y="-20" width="140" height="140"><rect x="-20" y="-20" width="140" height="140" fill="#fff"/>'
                f'<path d="{d}" transform="translate({f(-lt[0] * 2.4)} {f(-lt[1] * 2.4)})" fill="#000"/></mask>'
                f'<g clip-path="url(#{ns}k)"><path d="{d}" style="fill:{lit}" mask="url(#{ns}m)" opacity=".85"/></g>')
    elif style in ('soft', 'softrings'):
        c = P.mean(0); r = np.ptp(P, 0).max() * .75; fx, fy = c + lt * r * .45
        out += (f'<radialGradient id="{ns}g" gradientUnits="userSpaceOnUse" cx="{f(fx)}" cy="{f(fy)}" r="{f(r)}">'
                f'<stop offset="0" style="stop-color:{lit}"/><stop offset=".55" style="stop-color:{col}"/><stop offset="1" style="stop-color:{shade}"/></radialGradient>'
                f'<path d="{d}" fill="url(#{ns}g)"/>')
    else:
        out += f'<path d="{d}" style="fill:{col}"/>'
    if style in ('rings', 'model', 'softrings'):
        rings = ''
        for k, dd in enumerate((3.6, 7.2, 10.8, 14.4)):
            Q = inset(P, dd)
            if Q is None: break
            rings += f'<path d="{_d(Q)}" fill="none" style="stroke:var(--ring)" stroke-width="{w * (.42 - .05 * k):.2f}" stroke-linejoin="round" opacity=".55"/>'
        if island and key == 'target':
            rings += _island(P, island, w)
        out += f'<g clip-path="url(#{ns}k)">{rings}</g>'
    if lumps:   # soft lumps inside, as in illustrated proteins: a few merged blobs traced as light lines
        out += f'<g clip-path="url(#{ns}k)">' + _lumps(P, lumps, seed, col, w) + '</g>'
    stroke = f'color-mix(in srgb, {col} 45%, var(--outline))' if tint else 'var(--outline)'
    return out + f'<path d="{d}" fill="none" style="stroke:{stroke}" stroke-width="{w}" stroke-linejoin="round"/>'

def _lumps(P, n, seed, col, w, res=.25):
    """n soft lumps inside the shape: a metaball field of random blobs, traced at one level, drawn as lighter lines."""
    from matplotlib.path import Path as _MP
    from scipy.ndimage import gaussian_filter
    from skimage import measure
    rng = np.random.default_rng(seed)
    core = inset(P, 5.0)
    if core is None: return ''
    lo = P.min(0) - 2; hi = P.max(0) + 2
    xs = np.arange(lo[0], hi[0], res); ys = np.arange(lo[1], hi[1], res); X, Y = np.meshgrid(xs, ys)
    path = _MP(core); pts = []
    while len(pts) < n * 6:
        q = lo + rng.random(2) * (hi - lo)
        if path.contains_point(q): pts.append(q)
    field = np.zeros_like(X)
    for q in pts:
        rr = 3.2 + rng.random() * 3.2
        field += np.exp(-((X - q[0]) ** 2 + (Y - q[1]) ** 2) / (2 * rr * rr))
    out = ''
    light = f'color-mix(in srgb, {col} 40%, #fff)'; dark = f'color-mix(in srgb, {col} 80%, var(--outline))'
    for lev, c_, op in ((.55, dark, .35), (1.05, light, .55)):
        for cc in measure.find_contours(field, lev):
            if len(cc) < 20: continue
            Q = np.stack([lo[0] + cc[:, 1] * res, lo[1] + cc[:, 0] * res], 1)
            out += f'<path d="{_d(_resample(Q, .8))}" style="fill:{c_}" opacity="{op}"/>'
    return out

_TP_CACHE = {}
def TP(**kw):
    """A concept function for two_proteins with its settings fixed. The geometry is heavy (rasterised surfaces,
    docking), so each (settings, split) is computed once and its ids renamed for each use."""
    key0 = repr(sorted((k, repr(v)) for k, v in kw.items()))
    def fn(ns, split=False):
        k = (key0, split)
        if k not in _TP_CACHE: _TP_CACHE[k] = two_proteins('NSX', split, **kw)
        return _TP_CACHE[k].replace('NSX', ns)
    fn.kw = kw; return fn

def aspect(key, pose=0):
    """A protein outline's natural height / width along its long axis (no squashing)."""
    o = smooth(POSES[pose][key]['outer']); q = o - o.mean(0)
    w_, v = np.linalg.eigh(np.cov(q.T)); ax = v[:, np.argmax(w_)]; a = -math.atan2(ax[1], ax[0])
    R = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]]); q = q @ R.T
    return (q[:, 1].max() - q[:, 1].min()) / (q[:, 0].max() - q[:, 0].min())

def natural(lw=58, cw=62, pose=0, lt=-9, ct=6, squash=1.0):
    """lid / cup boxes at each protein's own proportions (squash < 1 flattens them toward a shell)."""
    return dict(lid=('target', lw, lw * aspect('target', pose) * squash, lt), cup=('e3', cw, cw * aspect('e3', pose) * squash, ct))


# ---- Round thirteen: 02 of round twelve, blobbier. Each protein's own traced lobes amplified, with clefts pressed
# into its back and an optional wider domain, before docking (which keeps the facing side fitted).

def exaggerate(P, amp=1.2, keep=6, clefts=(), bulges=()):
    """Amplify an outline's own broad lobes (radially, about its centroid) and press in clefts / push out bulges.
    clefts / bulges: (angle in degrees, depth as a fraction of the radius, width in degrees)."""
    P = _resample(np.asarray(P, float), .6); c = P.mean(0); d = P - c
    th = np.arctan2(d[:, 1], d[:, 0]); r = np.linalg.norm(d, axis=1)
    # the shape's own oval (from its covariance), so only local lobes are amplified, not its length
    ev, V = np.linalg.eigh(np.cov(d.T)); q = d @ V
    sa, sb = np.sqrt(ev) * 2.0
    phi = np.arctan2(q[:, 1], q[:, 0])
    r_e = 1 / np.sqrt((np.cos(phi) / sa) ** 2 + (np.sin(phi) / sb) ** 2)
    rel = r / r_e; rel = rel / rel.mean() - 1
    F = np.fft.rfft(rel); F[keep:] = 0; lob = np.fft.irfft(F, len(rel))
    k = 1 + amp * lob
    for ang, depth, width in clefts:
        dt = np.angle(np.exp(1j * (th - math.radians(ang)))); k *= 1 - depth * np.exp(-(dt / math.radians(width)) ** 2)
    for ang, depth, width in bulges:
        dt = np.angle(np.exp(1j * (th - math.radians(ang)))); k *= 1 + depth * np.exp(-(dt / math.radians(width)) ** 2)
    Q = c + d * k[:, None]
    return _relax(_resample(Q, .8), .3, 3)


# ---- Round sixteen: a few big, deep undulations instead of many lobes.

def undulate(P, n=5, depth=3.5, phase=0.0, sharp=1.0, other=None, pc=None, pr=0.0, near=4.0, fade=10.0):
    """Push the outline in and out along its normal in exactly n smooth waves round its length.
    sharp > 1 makes the crests rounder and the troughs tighter, like lobes with clefts between. Where the outline
    is within `near` + `fade` of the other protein or the pearl, the waves fade out, so the seam and pocket stay put."""
    P = _resample(np.asarray(P, float), .6); L = len(P)
    t = np.arange(L) / L * 2 * np.pi * n + phase * 2 * np.pi
    wv = np.sin(t); wv = np.sign(wv) * np.abs(wv) ** (1 / sharp) if sharp != 1 else wv
    k = np.ones(L)
    if other is not None:
        _, d = _nearest(_resample(other, 1.0), P); k = np.minimum(k, np.clip((d - near) / fade, 0, 1))
    if pc is not None:
        d = np.linalg.norm(P - pc, axis=1) - pr; k = np.minimum(k, np.clip((d - near) / fade, 0, 1))
    k = np.convolve(np.r_[k[-15:], k, k[:15]], np.ones(31) / 31, 'valid')     # smooth the fade
    Q = P + _normals(P) * (depth * wv * k)[:, None]
    return _relax(_resample(Q, .8), .3, 2)


# ---- Round seventeen: mother-of-pearl colourways. The proteins as iridescent nacre, the pearl photographic.
NACRE = {
    'akoya':    dict(bands=['#F5EFF2', '#EADBE6', '#DDE8EE', '#F3EADF', '#E7DDEE', '#F7F1EE'], edge='#8E7C8C', shade='#B8A8BC',
                     pearl=['#FBF6F7', '#EDE3E8', '#C9B9C4'], overtone='#F4C6D8'),
    'rose':     dict(bands=['#F8E4E8', '#E9D2F0', '#D3EDE6', '#F6E7D2', '#EFD5E8', '#DDE6F4'], edge='#9A7A90', shade='#C3A6BC',
                     pearl=['#FBEFF2', '#F0D9E2', '#C9A9B9'], overtone='#C9E8DC'),
    'southsea': dict(bands=['#F6E4B2', '#EBCB8C', '#F8EDCF', '#DDBB7A', '#F3DCA9', '#E8D3A6'], edge='#8C6A30', shade='#C9A35E',
                     pearl=['#FBF0D2', '#EBCB86', '#B98F47'], overtone='#F6E7B8'),
    'tahitian': dict(bands=['#3E4C55', '#5E726C', '#6F5D7B', '#476E7C', '#808C68', '#525A6E'], edge='#151B1E', shade='#22292C',
                     pearl=['#A8B4B4', '#4E5C61', '#1F2629'], overtone='#7FAF92'),
    'abalone':  dict(bands=['#3F7F8F', '#5DA79C', '#6B61A3', '#3E70A0', '#8CC2AA', '#4F8FB6'], edge='#173640', shade='#24505C',
                     pearl=['#E9F3F2', '#B7D0D3', '#6F8F9A'], overtone='#9FD6C6'),
}

def _nacre_fill(P, key, name, ns, w, light=(-1, -1)):
    """A protein as mother-of-pearl: iridescent colour bands across it (each protein at its own angle), a fine
    fibrous nacre sheen from turbulence, a soft highlight toward the light and shade away from it, a thin rim."""
    N_ = NACRE[name]; d = _d(P); c = P.mean(0); r = np.ptp(P, 0).max() * .6
    lt = np.array(light, float); lt /= np.linalg.norm(lt)
    ang = 25 if key == 'target' else 115
    a = math.radians(ang); x1, y1 = c - r * np.array([math.cos(a), math.sin(a)]); x2, y2 = c + r * np.array([math.cos(a), math.sin(a)])
    stops = ''.join(f'<stop offset="{i / (len(N_["bands"]) - 1):.2f}" stop-color="{col}"/>' for i, col in enumerate(N_['bands']))
    hx, hy = c + lt * r * .45; sx, sy = c - lt * r * .55
    seed = 3 if key == 'target' else 9
    defs = (f'<linearGradient id="{ns}b" gradientUnits="userSpaceOnUse" x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}">{stops}</linearGradient>'
            f'<radialGradient id="{ns}h" gradientUnits="userSpaceOnUse" cx="{f(hx)}" cy="{f(hy)}" r="{f(r * .8)}">'
            f'<stop offset="0" stop-color="#fff" stop-opacity=".75"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
            f'<radialGradient id="{ns}s" gradientUnits="userSpaceOnUse" cx="{f(sx)}" cy="{f(sy)}" r="{f(r * .9)}">'
            f'<stop offset="0" stop-color="{N_["shade"]}" stop-opacity=".55"/><stop offset="1" stop-color="{N_["shade"]}" stop-opacity="0"/></radialGradient>'
            f'<filter id="{ns}f" x="-10%" y="-10%" width="120%" height="120%">'
            f'<feTurbulence type="fractalNoise" baseFrequency="0.035 0.18" numOctaves="3" seed="{seed}"/>'
            f'<feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 1.4 0 -0.55"/></filter>'
            f'<clipPath id="{ns}k"><path d="{d}"/></clipPath>')
    sheen = (f'<g clip-path="url(#{ns}k)"><rect x="{f(c[0] - r * 1.2)}" y="{f(c[1] - r * 1.2)}" width="{f(r * 2.4)}" height="{f(r * 2.4)}" '
             f'filter="url(#{ns}f)" opacity=".38" transform="rotate({ang + 60} {f(c[0])} {f(c[1])})"/></g>')
    return (f'<defs>{defs}</defs><path d="{d}" fill="url(#{ns}b)"/>{sheen}'
            f'<path d="{d}" fill="url(#{ns}s)"/><path d="{d}" fill="url(#{ns}h)"/>'
            f'<path d="{d}" fill="none" stroke="{N_["edge"]}" stroke-width="{w * .7:.2f}" stroke-linejoin="round" opacity=".9"/>')


def _island(P, spec, w):
    """Small closed contour rings round the deepest point of the protein's left-hand part, like a peak on a
    topographic map. spec = (size, count): the outer ring sits `size` below the peak, with `count` rings in all."""
    from skimage import measure
    if isinstance(spec, dict):   # a small round ring (or a few concentric ones) at the left-hand peak, gently wobbled
        dist, lo, res = _sdf(P); xs = lo[0] + np.arange(dist.shape[1]) * res
        left = dist.copy(); left[:, xs > P[:, 0].mean()] = 0
        j, i = np.unravel_index(np.argmax(left), left.shape); pt = np.array([lo[0] + i * res, lo[1] + j * res])
        pt = pt + np.array(spec.get('nudge', (0, 0)))
        out = ''
        for k in range(spec.get('count', 1)):
            r = spec['r'] * (k + 1)
            t = np.linspace(0, 2 * np.pi, 60, endpoint=False)
            rr = r * (1 + .08 * np.sin(3 * t + 1.1) + .05 * np.sin(5 * t))
            Q = np.stack([pt[0] + rr * np.cos(t), pt[1] + rr * .85 * np.sin(t)], 1)
            out += f'<path d="{_d(Q)}" fill="none" style="stroke:var(--ring)" stroke-width="{w * .36:.2f}" stroke-linejoin="round" opacity=".55"/>'
        return out
    size, count = spec if isinstance(spec, tuple) else (spec, 1)
    dist, lo, res = _sdf(P)
    xs = lo[0] + np.arange(dist.shape[1]) * res
    left = dist.copy(); left[:, xs > P[:, 0].mean()] = 0
    j, i = np.unravel_index(np.argmax(left), left.shape); peak = left[j, i]; pt = np.array([lo[0] + i * res, lo[1] + j * res])
    out = ''
    for k in range(count):
        lev = peak - size * (k + 1) / count
        if lev <= 0: continue
        best = None
        for cc in measure.find_contours(dist, lev):
            Q = np.stack([lo[0] + cc[:, 1] * res, lo[1] + cc[:, 0] * res], 1)
            from matplotlib.path import Path as _MP
            if _MP(Q).contains_point(pt) and (best is None or len(Q) < len(best)): best = Q
        if best is not None:
            out += f'<path d="{_d(_relax(_resample(best, .5), .4, 2))}" fill="none" style="stroke:var(--ring)" stroke-width="{w * .36:.2f}" stroke-linejoin="round" opacity=".55"/>'
    return out


# ---- Round twenty: one-colour versions for laying over photographs. Everything in currentColor on a clear ground.

def _mono(P, key, style, ns, w, island=None):
    """A protein in one colour. 'line': the outline alone. 'contour': the outline with the contour rings (and the
    island) as hairlines. 'solid': a silhouette, the island cut out of it. 'cut': a silhouette with the contour rings
    and island cut out of it. 'duo': BRD4 as 'solid', VHL as 'line', so the two proteins differ."""
    import re as _re
    if style == 'duo': style = 'solid' if key == 'target' else 'line'
    d = _d(P); rings = []
    for dd in (3.6, 7.2, 10.8, 14.4):
        Q = inset(P, dd)
        if Q is None: break
        rings.append(_d(Q))
    isl = _re.findall(r' d="([^"]+)"', _island(P, island, w)) if island and key == 'target' else []
    line = f'<path d="{d}" fill="none" stroke="currentColor" stroke-width="{w}" stroke-linejoin="round"/>'
    if style == 'line':
        return line
    if style == 'contour':
        hl = ''.join(f'<path d="{q}" fill="none" stroke="currentColor" stroke-width="{w * .3:.2f}" stroke-linejoin="round"/>' for q in rings + isl)
        return f'<clipPath id="{ns}k"><path d="{d}"/></clipPath><g clip-path="url(#{ns}k)">{hl}</g>' + line
    cuts = isl if style == 'solid' else rings + isl
    cw = w * .5 if style == 'solid' else w * .42
    m = (f'<mask id="{ns}m" maskUnits="userSpaceOnUse" x="-20" y="-20" width="140" height="140"><rect x="-20" y="-20" width="140" height="140" fill="#fff"/>'
         + ''.join(f'<path d="{q}" fill="none" stroke="#000" stroke-width="{cw:.2f}" stroke-linejoin="round"/>' for q in cuts) + '</mask>')
    return m + f'<path d="{d}" fill="currentColor" stroke="currentColor" stroke-width="{w}" stroke-linejoin="round" mask="url(#{ns}m)"/>'


# ---- Round twenty-one: other ways for the pearl to tell the SELFTAC story (two halves that clasp back together).

def pearl_alt(c, r, angle, style, ns):
    """The pearl in the pocket, drawn with the seam level and the BRD4 half on top, then turned to the shell's angle.
    'bridge': the two halves a little apart, held by a solid gold bond (the clasp) across the gap. 'glow': the same,
    the bond glowing as the site's clasp does when closed. 'twotone': as bridge, the halves in two tones, one per
    protein. 'clasp': the site's clasp glyph, two gold pearls joined by a thick bond. 'yinyang': two interlocking
    teardrop halves. 'jigsaw': halves joined by a knob and socket, which click together. 'venn': two overlapping
    pearls, the overlap gold. 'strand': the site's pearl strand running from one protein to the other through the
    pocket, the two gold clasp pearls at its middle."""
    c = np.asarray(c, float); P, G = 'var(--pearl)', 'var(--clasp)'; pale = 'color-mix(in srgb, var(--pearl) 45%, #fff)'
    gap = .1 * r
    M = lambda inner: (f'<mask id="{ns}" maskUnits="userSpaceOnUse" x="{f(c[0] - 3 * r)}" y="{f(c[1] - 3 * r)}" width="{f(6 * r)}" height="{f(6 * r)}">'
                       f'<rect x="{f(c[0] - 3 * r)}" y="{f(c[1] - 3 * r)}" width="{f(6 * r)}" height="{f(6 * r)}" fill="#fff"/>{inner}</mask>')
    at = lambda x, y: c + np.array([x, y]) * r

    def halves(seam_pts, up, lo, extra=''):
        sp = np.array([at(x, y) for x, y in seam_pts])
        t = np.linspace(0, -np.pi, 90); top = np.stack([c[0] + r * np.cos(t), c[1] + r * np.sin(t)], 1)
        t = np.linspace(0, np.pi, 90); bot = np.stack([c[0] + r * np.cos(t), c[1] + r * np.sin(t)], 1)
        mk = M(f'<path d="{_d(sp)[:-2]}" fill="none" stroke="#000" stroke-width="{f(gap)}" stroke-linejoin="round"/>{extra}')
        return (mk + f'<g mask="url(#{ns})"><path d="{_d(np.vstack([sp, top]))}" style="fill:{up}"/>'
                f'<path d="{_d(np.vstack([sp, bot]))}" style="fill:{lo}"/></g>')

    def bond(lw=.42, ll=.72, glow=False):
        x, y = c[0] - lw * r / 2, c[1] - ll * r / 2
        cut = f'<rect x="{f(x - gap)}" y="{f(y - gap)}" width="{f(lw * r + 2 * gap)}" height="{f(ll * r + 2 * gap)}" rx="{f(lw * r / 2 + gap)}" fill="#000"/>'
        g = (f'<filter id="{ns}gl" x="-1" y="-1" width="3" height="3"><feGaussianBlur stdDeviation="{f(r * .22)}"/></filter>'
             f'<ellipse cx="{f(c[0])}" cy="{f(c[1])}" rx="{f(r * .45)}" ry="{f(r * .6)}" style="fill:{G}" opacity=".7" filter="url(#{ns}gl)"/>') if glow else ''
        return cut, g + f'<rect x="{f(x)}" y="{f(y)}" width="{f(lw * r)}" height="{f(ll * r)}" rx="{f(lw * r / 2)}" style="fill:{G}"/>'

    line = [(-1.2, 0), (1.2, 0)]
    if style in ('bridge', 'glow', 'twotone'):
        cut, b = bond(glow=style == 'glow')
        body = halves(line, P, pale if style == 'twotone' else P, cut) + b
    elif style == 'clasp':
        k = .5; rr = .4
        body = (f'<rect x="{f(c[0] - .18 * r)}" y="{f(c[1] - k * r)}" width="{f(.36 * r)}" height="{f(2 * k * r)}" style="fill:{G}"/>'
                + ''.join(f'<circle cx="{f(c[0])}" cy="{f(c[1] + s * k * r)}" r="{f(rr * r)}" style="fill:{G}"/>'
                          f'<circle cx="{f(c[0] - .13 * r)}" cy="{f(c[1] + s * k * r - .13 * r)}" r="{f(.1 * r)}" fill="#fff" opacity=".55"/>' for s in (-1, 1)))
    elif style == 'yinyang':
        t1 = np.linspace(np.pi, 2 * np.pi, 40); t2 = np.linspace(np.pi, 0, 40)
        s_ = [(-1.2, 0)] + [(-.5 + .5 * math.cos(t), .5 * math.sin(t)) for t in t1] + [(.5 + .5 * math.cos(t), .5 * math.sin(t)) for t in t2] + [(1.2, 0)]
        body = halves(s_, P, pale)
    elif style == 'jigsaw':
        kc, kr, nk = .4, .28, .16                     # knob centre (below the seam), radius, half-width of its neck
        a0 = math.atan2(-math.sqrt(kr ** 2 - nk ** 2), -nk); a1 = math.atan2(-math.sqrt(kr ** 2 - nk ** 2), nk) - 2 * np.pi
        s_ = [(-1.2, 0), (-nk, 0)] + [(kr * math.cos(t), kc + kr * math.sin(t)) for t in np.linspace(a0, a1, 60)] + [(nk, 0), (1.2, 0)]
        body = halves(s_, P, pale)
    elif style == 'venn':
        k, rr = .36, .62; cu, cl = at(0, -k), at(0, k)
        lens = (f'<clipPath id="{ns}v"><circle cx="{f(cu[0])}" cy="{f(cu[1])}" r="{f(rr * r)}"/></clipPath>'
                f'<circle cx="{f(cl[0])}" cy="{f(cl[1])}" r="{f(rr * r)}" style="fill:{G}" clip-path="url(#{ns}v)"/>')
        rim = ''.join(f'<circle cx="{f(q[0])}" cy="{f(q[1])}" r="{f(rr * r)}" fill="none" stroke="#000" stroke-width="{f(gap)}"/>' for q in (cu, cl))
        body = (M(rim) + f'<g mask="url(#{ns})"><circle cx="{f(cu[0])}" cy="{f(cu[1])}" r="{f(rr * r)}" style="fill:{P}"/>'
                f'<circle cx="{f(cl[0])}" cy="{f(cl[1])}" r="{f(rr * r)}" style="fill:{pale}"/>{lens}</g>')
    elif style == 'strand':
        k, rr = .42, .34; white = 'color-mix(in srgb, var(--pearl) 20%, #fff)'
        body = f'<line x1="{f(c[0])}" y1="{f(c[1] - 1.75 * r)}" x2="{f(c[0])}" y2="{f(c[1] + 1.75 * r)}" style="stroke:var(--outline)" stroke-width="{f(.1 * r)}" stroke-linecap="round"/>'
        for s in (-1, 1):
            for y in (1.04, 1.5):
                body += f'<circle cx="{f(c[0])}" cy="{f(c[1] + s * y * r)}" r="{f(.17 * r)}" style="fill:{white};stroke:var(--outline)" stroke-width="{f(.06 * r)}"/>'
        body += f'<rect x="{f(c[0] - .16 * r)}" y="{f(c[1] - k * r)}" width="{f(.32 * r)}" height="{f(2 * k * r)}" style="fill:{G}"/>'
        body += ''.join(f'<circle cx="{f(c[0])}" cy="{f(c[1] + s * k * r)}" r="{f(rr * r)}" style="fill:{G}"/>' for s in (-1, 1))
    else:
        raise ValueError(style)
    return f'<g transform="rotate({angle} {f(c[0])} {f(c[1])})">{body}</g>'
