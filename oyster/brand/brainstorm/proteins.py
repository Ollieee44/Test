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
                flip_lid=True, flip_cup=False, hinge=4, balance=None):
    """balance (a number): place each protein so it reaches that far past the pearl's centre line before docking
    (lid downward, cup upward), so the seam runs through the pearl and each protein takes half of it."""
    pc = np.array([54.0, 52.0]); lk, lw, lh, lt = lid; ck, cw, ch, ct = cup
    def place(key, box, rot, flip):
        v = POSES[pose][key]; tf = _frame(v['outer'], box[2], box[3], rot, np.array(box[:2]), flip)
        return tf(smooth(v['outer'])), tf
    L0, tl = place(lk, (pc[0] - hinge, pc[1] - lh * .5 - pr * .35 + overlap / 2, lw, lh), lt, flip_lid)
    C0, tc = place(ck, (pc[0] - hinge, pc[1] + ch * .5 + pr * .2 - overlap / 2, cw, ch), ct, flip_cup)
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

def pearl_linker(c, r, angle, split, link=(.62, .34), seam=.09, ns='p'):
    """The pearl split along the shell's seam into two halves, one by each protein, held by a short, thick linker
    cut out of it as negative space across the split. link = (length, thickness) as fractions of the radius."""
    ll, lw = link[0] * r, link[1] * r; hg = seam * r; g = 4 if split else 0
    m = (f'<mask id="{ns}" maskUnits="userSpaceOnUse" x="{f(c[0] - 2 * r)}" y="{f(c[1] - 2 * r)}" width="{f(4 * r)}" height="{f(4 * r)}">'
         f'<rect x="{f(c[0] - 2 * r)}" y="{f(c[1] - 2 * r)}" width="{f(4 * r)}" height="{f(4 * r)}" fill="#fff"/>'
         f'<rect x="{f(c[0] - 2 * r)}" y="{f(c[1] - hg / 2)}" width="{f(4 * r)}" height="{f(hg)}" fill="#000"/>'
         f'<rect x="{f(c[0] - lw / 2)}" y="{f(c[1] - ll / 2)}" width="{f(lw)}" height="{f(ll)}" rx="{f(lw / 2)}" fill="#000"/></mask>')
    halves = (f'<g transform="translate(0 {-g})"><path d="M{f(c[0] - r)} {f(c[1])} A {f(r)} {f(r)} 0 0 1 {f(c[0] + r)} {f(c[1])} Z" style="fill:var(--pearl)" mask="url(#{ns})"/></g>'
              f'<g transform="translate(0 {g})"><path d="M{f(c[0] - r)} {f(c[1])} A {f(r)} {f(r)} 0 0 0 {f(c[0] + r)} {f(c[1])} Z" style="fill:var(--pearl)" mask="url(#{ns})"/></g>')
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

def molecular(P, r=3.2, seed=0, vary=.28, res=.2):
    """The outline redrawn as a molecular surface: the shape filled in, with round bumps of radius ~r set along
    its edge, and the silhouette of the lot traced back out (scalloped, as space-filling surfaces are)."""
    from matplotlib.path import Path as _MP
    from skimage import measure
    rng = np.random.default_rng(seed)
    lo = P.min(0) - 2 * r; hi = P.max(0) + 2 * r
    xs = np.arange(lo[0], hi[0], res); ys = np.arange(lo[1], hi[1], res); X, Y = np.meshgrid(xs, ys)
    pts = np.stack([X.ravel(), Y.ravel()], 1)
    core = inset(P, r * .9)
    field = _MP(core if core is not None else P).contains_points(pts).reshape(X.shape).astype(float)
    ring = _resample(P if core is None else core, r * 1.15)
    for c in ring:
        rr = r * (1 + vary * (rng.random() - .5) * 2)
        field = np.maximum(field, ((X - c[0]) ** 2 + (Y - c[1]) ** 2 <= rr * rr).astype(float))
    cs = measure.find_contours(field, .5); cc = max(cs, key=len)
    Q = np.stack([lo[0] + cc[:, 1] * res, lo[1] + cc[:, 0] * res], 1)
    return _resample(Q, .6)

def two_proteins(ns, split=False, angle=-32, bump=3.2, overlap=14, gap=1.8, w=2.8, pose=0, reach=16.0,
                 link=(.7, .44), seam=.09, contour=False, pr=11.0, lid=('target', 66, 28, -9), cup=('e3', 72, 36, 6), balance=None):
    L, C, pc, tl, tc = docked_geom(pose, overlap, gap, w=w, lid=lid, cup=cup, balance=balance)
    if reach > 0: L, C = close_mouth(L, C, reach, gap=gap, w=w, pc=pc, pr=pr)
    if bump > 0:
        L, C = molecular(L, bump, 1), molecular(C, bump, 2)
        if reach > 0: L, C = close_mouth(L, C, max(8.0, bump * 3), 30, gap=gap, w=w, pc=pc, pr=pr, relax=False)   # re-dock after the bumps
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
    seam_n = Rm @ np.array([0, 1.0]); g = 5 if split else 0
    body = ''
    for P, key, tf, s, nm in ((L, 'target', tl, -1, 'a'), (C, 'e3', tc, 1, 'b')):
        inner = ''
        if contour:   # one real surface contour from the trace, as a quiet interior line
            q = fit((tf(smooth(POSES[pose][key]['inner'][0])) - pc) @ Rm.T)
            inner = (f'<clipPath id="{ns}{nm}"><path d="{_d(inset(P, 3) if inset(P, 3) is not None else P)}"/></clipPath>'
                     f'<g clip-path="url(#{ns}{nm})"><path d="{_d(q)}" fill="none" stroke="currentColor" stroke-width="{w * .45:.2f}" stroke-linejoin="round"/></g>')
        off = seam_n * g * s
        body += (f'<g transform="translate({f(off[0])} {f(off[1])})"><path d="{_d(P)}" fill="none" stroke="currentColor" stroke-width="{w}" stroke-linejoin="round"/>{inner}</g>')
    return body + pearl_linker(c0, pr_, angle, split, link, seam, ns + 'p')

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
