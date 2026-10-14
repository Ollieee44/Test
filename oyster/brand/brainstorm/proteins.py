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
