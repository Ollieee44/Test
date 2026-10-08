"""Round four: the SELFTAC as an O. Start from the molecule, two halves (a ligand ring system on a linker)
joined by the clasp, curl it into an O, and shape the O as an oyster seen side on: hinge to the left, a flat
upper valve, a deep lower valve, the mouth on the right. The molecule's two halves are the shell's two valves.

Generic, per the house style: ring systems are invented hexagons traced as open tubes, never real ligands.
Same contract as concepts.py: fn(ns, split) -> SVG in a 0-100 box; ink currentColor, clasp var(--clasp).
"""
import math
import numpy as np

f = lambda v: f'{v:.2f}'
PT = lambda q: ' '.join(f'{f(x)},{f(y)}' for x, y in q)

def bez(p0, p1, p2, p3, n=80):
    t = np.linspace(0, 1, n)[:, None]; p0, p1, p2, p3 = map(np.array, (p0, p1, p2, p3))
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3

def resample(p, step):
    s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))]; t = np.arange(0, s[-1] + 1e-9, step)
    return np.stack([np.interp(t, s, p[:, 0]), np.interp(t, s, p[:, 1])], 1), s[-1]

# The oyster O, side on: the upper (flat) and lower (deep) valve as curves from the hinge to the mouth.
H = (9, 51)
UP = bez(H, (20, 28), (58, 18), (90, 34))
LO = bez(H, (16, 80), (62, 92), (90, 66))

def hexagon(c, r, ang):
    return [(c[0] + r * math.cos(ang + k * math.pi / 3), c[1] + r * math.sin(ang + k * math.pi / 3)) for k in range(6)]

def ring_at_end(curve, r, back=0.0):
    """A hexagon hung off the end of a curve, along its tangent, one vertex touching the end."""
    e = curve[-1]; t = curve[-1] - curve[-4]; t = t / np.linalg.norm(t)
    c = e + t * r; ang = math.atan2(-t[1], -t[0])
    return hexagon(c, r, ang)

def tube(curve, w):
    return f'<polyline points="{PT(curve)}" fill="none" stroke="currentColor" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>'

def hinge_clasp(gap):
    """The clasp at the hinge: two gold heads, one on each valve, and the bond between them."""
    a, b = np.array(UP[3]), np.array(LO[3])
    return (f'<g style="fill:var(--clasp);stroke:var(--clasp)"><line x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}" stroke-width="3.6" stroke-linecap="round"/>'
            f'<circle cx="{f(a[0])}" cy="{f(a[1])}" r="4.6" stroke="none"/><circle cx="{f(b[0])}" cy="{f(b[1])}" r="4.6" stroke="none"/></g>')

def molecule_o(ns, split=False):
    """01. The molecule, curled. Each valve is one half of the SELFTAC: a linker running from the hinge to the
    mouth, ending in an open ring, its ligand. At the hinge the two halves meet in the gold clasp; at the
    mouth the two rings sit apart, the oyster ajar. Split, the clasp lets go and the valves part."""
    dy = 5 if split else 0
    up = UP[4:] + [0, -dy]; lo = LO[4:] + [0, dy]
    w = 6.4
    rings = (f'<g fill="none" stroke="currentColor" stroke-width="{w * .8}" stroke-linejoin="round">'
             f'<polygon points="{PT(ring_at_end(up, 7.5))}"/><polygon points="{PT(ring_at_end(lo, 7.5))}"/></g>')
    clasp = '' if split else hinge_clasp(0)
    return f'<g transform="translate(4 6) scale(.86)">' + tube(up, w) + tube(lo, w) + rings + clasp + '</g>'

def kekulene(ns, split=False):
    """02. A ring of rings. The O as a macrocycle of fused hexagons, like the molecule kekulene, laid out on the
    oyster's outline: the zigzag of the rings' outer edges is the oyster's frilled lip. Broken in two at the
    hinge, where the gold clasp bonds the halves, and parted a hair at the mouth."""
    outline = np.concatenate([UP, LO[::-1][1:]])
    pts, L = resample(outline, 1.0)
    r = 6.2; step = r * math.sqrt(3) * .98
    n = int(L // step); s0 = (L - n * step) / 2
    hexes, ends = '', []
    dy = 4 if split else 0
    # skip a slot at the hinge (both ends of the closed path) and one at the mouth
    mouth_s = len(UP) and np.argmin(np.linalg.norm(pts - np.array(UP[-1]), axis=1))
    for k in range(n + 1):
        s = s0 + k * step
        if s < step * .9 or s > L - step * .9: continue
        i = int(round(s)); i = min(i, len(pts) - 2)
        if abs(i - mouth_s) < step * .6: continue
        c = pts[i]; t = pts[i + 1] - pts[i - 1]; ang = math.atan2(t[1], t[0])
        upper = i < mouth_s
        c = c + ([0, -dy] if upper else [0, dy])
        hexes += f'<polygon points="{PT(hexagon(c, r, ang + math.pi / 6))}"/>'
    clasp = '' if split else hinge_clasp(0)
    return f'<g fill="none" stroke="currentColor" stroke-width="3.6" stroke-linejoin="round">{hexes}</g>' + clasp

def crescents(ns, split=False):
    """03. Two crescents. Each half of the SELFTAC as a solid crescent, a thin lid and a deep cup, its ligand
    ring cut out at the mouth end as negative space. They meet only at the hinge, in the gold clasp, and
    together make an O with an oyster's lopsided profile."""
    dy = 5 if split else 0
    up_in = bez((14, 47), (26, 33), (56, 27), (86, 39))
    lo_in = bez((14, 55), (22, 74), (60, 83), (86, 62))
    up = np.concatenate([UP[3:], up_in[::-1]]) + [0, -dy]
    lo = np.concatenate([LO[3:], lo_in[::-1]]) + [0, dy]
    hu = hexagon((74, 30 - dy), 5.4, math.pi / 6 + .3); hl = hexagon((72, 74 + dy), 6.0, math.pi / 6 - .2)
    m = (f'<mask id="{ns}m" maskUnits="userSpaceOnUse" x="-10" y="-10" width="120" height="120"><rect x="-10" y="-10" width="120" height="120" fill="#fff"/>'
         f'<g fill="none" stroke="#000" stroke-width="2.8" stroke-linejoin="round"><polygon points="{PT(hu)}"/><polygon points="{PT(hl)}"/></g></mask>')
    clasp = '' if split else hinge_clasp(0)
    return (f'<defs>{m}</defs><g mask="url(#{ns}m)"><polygon points="{PT(up)}" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>'
            f'<polygon points="{PT(lo)}" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></g>' + clasp)

def rings_o(ns, split=False):
    """04. The growth-ring O. Round three's growth rings, the one you kept, made into the molecule: the outer
    ring is the SELFTAC curled into an O, its two halves the two valves, an open ligand ring where each ends
    at the mouth, the gold clasp at the hinge; inside it, the growth rings."""
    import geo
    H2 = (16, 76); ax = -36
    rings = geo._rings(H2, ax, (12, 21, 30), squash=.8)
    el = ''.join(f'<ellipse cx="{f(c[0])}" cy="{f(c[1])}" rx="{f(rx)}" ry="{f(ry)}" transform="rotate({ax} {f(c[0])} {f(c[1])})"/>' for c, rx, ry in rings)
    # the outer ring as two half-arcs from the hinge, ending short of the far end in rings
    c, rx, ry = geo._rings(H2, ax, (39,), squash=.8)[0]
    a = math.radians(ax)
    def pt(th):
        x, y = rx * math.cos(th), ry * math.sin(th)
        return (c[0] + x * math.cos(a) - y * math.sin(a), c[1] + x * math.sin(a) + y * math.cos(a))
    dy = 4 if split else 0
    n = (math.sin(a), -math.cos(a))
    upper = np.array([pt(th) for th in np.linspace(math.pi - .12, .42, 60)]) + np.array(n) * dy
    lower = np.array([pt(th) for th in np.linspace(math.pi + .12, 2 * math.pi - .42, 60)]) - np.array(n) * dy
    rr = (f'<g fill="none" stroke="currentColor" stroke-width="4" stroke-linejoin="round"><polygon points="{PT(ring_at_end(upper, 6.5))}"/>'
          f'<polygon points="{PT(ring_at_end(lower, 6.5))}"/></g>')
    hc = '' if split else (f'<g style="fill:var(--clasp);stroke:var(--clasp)"><line x1="{f(upper[0][0])}" y1="{f(upper[0][1])}" x2="{f(lower[0][0])}" y2="{f(lower[0][1])}" stroke-width="3.6"/>'
                           f'<circle cx="{f(upper[0][0])}" cy="{f(upper[0][1])}" r="4.2" stroke="none"/><circle cx="{f(lower[0][0])}" cy="{f(lower[0][1])}" r="4.2" stroke="none"/></g>')
    return (f'<g fill="none" stroke="currentColor" stroke-width="5">{el}</g>' + tube(upper, 5) + tube(lower, 5) + rr + hc)

# The bold O: a serif o's stress put to work. Thin at the top (the flat lid), heavy at the bottom (the deep cup),
# the counter set high, like an oyster side on. Split along the line from the hinge (left) to the mouth (right).
OUT = dict(cx=52, cy=51, rx=43, ry=39)
CTR = dict(cx=55, cy=45, rx=29, ry=23)
HG, MO = np.array([7.0, 50.0]), np.array([97.0, 47.0])

def _ell(e, extra=''):
    return f'<ellipse cx="{e["cx"]}" cy="{e["cy"]}" rx="{e["rx"]}" ry="{e["ry"]}"{extra}/>'

def _ept(e, phi):
    return np.array([e['cx'] + e['rx'] * math.cos(phi), e['cy'] + e['ry'] * math.sin(phi)])

def _outer_path(frill=1.0):
    """The O's outside edge, frilled like a shell's lip: strongest round the cup, faint on the lid."""
    pts = []
    for phi in np.linspace(0, 2 * math.pi, 360, endpoint=False):
        p = _ept(OUT, phi); c = np.array([OUT['cx'], OUT['cy']])
        amp = frill * (1 if math.sin(phi) > 0 else .5)
        w = .7 * math.sin(7 * phi + .6) + .55 * math.sin(12 * phi + 2.1) + .4 * math.sin(23 * phi + .3) + .25 * math.sin(41 * phi + 1.3)
        # quiet at the hinge and the mouth, where the seam is
        quiet = min(1, abs(math.sin(phi)) * 3)
        pts.append(p + (p - c) / np.linalg.norm(p - c) * amp * w * quiet)
    return 'M' + ' L'.join(f'{f(x)} {f(y)}' for x, y in pts) + ' Z'

def _mid(phi):
    """A point midway through the O's stroke at angle phi, and the stroke's thickness there."""
    a, b = _ept(OUT, phi), _ept(CTR, phi)
    return (a + b) / 2, np.linalg.norm(a - b)

def _bold(ns, split, inner, open_deg=-5, growth=True):
    """The bold O cut into two valves; inner(ns, which) adds knockouts in each valve's own coordinates."""
    d = MO - HG; nrm = np.array([d[1], -d[0]]) / np.linalg.norm(d)      # points up
    far = 300
    up = [HG - d * 2, MO + d * 2, MO + d * 2 + nrm * far, HG - d * 2 + nrm * far]
    lo = [HG - d * 2, MO + d * 2, MO + d * 2 - nrm * far, HG - d * 2 - nrm * far]
    seam = f'<line x1="{f(HG[0] - 9)}" y1="{f(HG[1] + .3)}" x2="{f(MO[0] + 9)}" y2="{f(MO[1] - .3)}" stroke="#000" stroke-width="3.2"/>'
    grow = (f'<g fill="none" stroke="#000" stroke-width="2.2">{_ell(dict(cx=52, cy=51, rx=37.5, ry=33.5))}</g>' if growth else '')
    def valve(which):
        m = (f'<mask id="{ns}{which}" maskUnits="userSpaceOnUse" x="-20" y="-20" width="140" height="140"><rect x="-20" y="-20" width="140" height="140" fill="#fff"/>'
             f'<g fill="#000">{_ell(CTR)}</g>{seam}' + (grow if which == "l" else '') + inner(which) + '</mask>')
        return (f'<clipPath id="{ns}c{which}"><polygon points="{PT(up if which == "u" else lo)}"/></clipPath>{m}'
                f'<g clip-path="url(#{ns}c{which})"><g mask="url(#{ns}{which})"><path d="{_outer_path()}"/></g></g>')
    dy = 4 if split else 0
    rot = open_deg - (5 if split else 0)
    out = (f'<g transform="translate(0 {-dy}) rotate({rot} {f(HG[0] + 6)} {f(HG[1])})">{valve("u")}</g>'
           f'<g transform="translate(0 {dy})">{valve("l")}</g>')
    if not split:   # the clasp: a gold bond across the seam at the hinge, one gold head on each valve
        a, b = (12.5, 46.6), (12.5, 53.6)
        out += (f'<g style="fill:var(--clasp);stroke:var(--clasp)"><line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke-width="3.4"/>'
                f'<circle cx="{a[0]}" cy="{a[1]}" r="3.6" stroke="none"/><circle cx="{b[0]}" cy="{b[1]}" r="3.6" stroke="none"/></g>')
    return out

def bold_rings(ns, split=False):
    """01. The bold O. A serif o, thin lid over a heavy cup, cut into the SELFTAC's two halves. Each valve
    carries its ligand as an open ring cut out near the mouth; the halves meet in the gold clasp at the
    hinge; the mouth sits a little open. A growth line on the cup makes it shell, not doughnut."""
    def inner(w):
        c, th = _mid(math.radians(326 if w == 'u' else 34))
        return f'<polygon points="{PT(hexagon(c, th * .3, math.pi / 6))}" fill="none" stroke="#000" stroke-width="2.2" stroke-linejoin="round"/>'
    return _bold(ns, split, inner)

def bold_engraved(ns, split=False):
    """02. The engraved molecule. The same bold O with the whole SELFTAC engraved into it: in each valve a
    linker runs from the clasp at the hinge to its ligand ring at the mouth, cut as a hairline."""
    def inner(w):
        span = np.radians(np.linspace(190, 318, 60)) if w == 'u' else np.radians(np.linspace(170, 42, 60))
        line = np.array([_mid(a)[0] for a in span])
        c, th = _mid(math.radians(330 if w == 'u' else 31))
        r = th * .3
        t = c - line[-1]; t = t / np.linalg.norm(t); cc = c
        return (f'<polyline points="{PT(np.vstack([line, c - t * r]))}" fill="none" stroke="#000" stroke-width="1.8" stroke-linecap="round"/>'
                f'<polygon points="{PT(hexagon(cc, r, math.atan2(-t[1], -t[0])))}" fill="none" stroke="#000" stroke-width="1.8" stroke-linejoin="round"/>')
    return _bold(ns, split, inner, growth=False)

CONCEPTS = [
    ('bold', '01', 'The bold O', bold_rings,
     'A serif o&rsquo;s thick and thin, put to work: a thin lid over a heavy cup, which is how an oyster sits. Cut along the seam into the SELFTAC&rsquo;s two halves, each carrying its ligand as an open ring near the mouth, joined by the gold clasp at the hinge.',
     'An O first, an oyster second, a molecule third: the order a logotype needs. It can be the o of &ldquo;oyster&rdquo;.'),
    ('engr', '02', 'The engraved molecule', bold_engraved,
     'The same bold O with the whole SELFTAC engraved into it as a hairline: in each valve a linker runs from the clasp at the hinge to its ligand ring at the mouth.',
     'The full molecule for close up (print, the intro&rsquo;s end card); from a distance it is just the bold O.'),
    ('mol', '03', 'The molecule, curled', molecule_o,
     'The molecule itself as a line: each valve is a linker from the hinge to the mouth, ending in its ligand ring. The halves meet in the gold clasp at the hinge; at the mouth the rings sit apart, the oyster ajar.',
     'The most literal, and the lightest. Thin as it is, it reads more bracelet than oyster: shown for comparison.'),
    ('rings', '04', 'The growth-ring O', rings_o,
     'Round three&rsquo;s growth rings, the one you kept, with the outer ring made into the molecule: its two halves are the valves, each ending in an open ring at the mouth, and the clasp is at the hinge.',
     'Joins the two directions: the oyster&rsquo;s growth and the SELFTAC in one mark.'),
]
