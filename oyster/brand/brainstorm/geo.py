"""Round three: constructed marks. Where round two drew the oyster's anatomy, these are built from simple
geometry only (circles, arcs, bars and dots on a strict system), the way a modernist symbol is made. They
keep the two clasp devices chosen from round two: the gold hinge (01, the ligament) and the gold seam
(05, kintsugi).

Same contract as concepts.py: fn(ns, split) -> SVG in a 0-100 box; ink is currentColor, the clasp
var(--clasp); split=True draws the halves apart.
"""
import math
import numpy as np

f = lambda v: f'{v:.2f}'

def _rings(H, axis_deg, radii, squash=.78):
    """Growth rings as ellipses all touching at the hinge H: each grows from the hinge along the axis, as an
    oyster's shell does. Returns (centre, rx, ry) for each."""
    a = math.radians(axis_deg)
    return [((H[0] + r * math.cos(a), H[1] + r * math.sin(a)), r, r * squash) for r in radii]

def growth(ns, split=False, kintsugi=False):
    """01. Growth rings. Four rings, each touching the others at one point: the hinge, from which a real
    oyster grows. The axis from the hinge splits them into two valves; the hinge is the gold clasp.
    Split, the upper valve swings open about the hinge, as an oyster opens."""
    H = (16, 76); ax = -36
    rings = _rings(H, ax, (12, 21, 30, 39), squash=.8)
    el = ''.join(f'<ellipse cx="{f(c[0])}" cy="{f(c[1])}" rx="{f(rx)}" ry="{f(ry)}" transform="rotate({ax} {f(c[0])} {f(c[1])})"/>' for c, rx, ry in rings)
    a = math.radians(ax); far = (H[0] + 140 * math.cos(a), H[1] + 140 * math.sin(a)); back = (H[0] - 40 * math.cos(a), H[1] - 40 * math.sin(a))
    up = f'{f(back[0])},{f(back[1])} {f(far[0])},{f(far[1])} {f(far[0] - 200 * math.sin(a))},{f(far[1] + 200 * math.cos(a)) if False else f(far[1] - 200)} -100,-100'
    # the two half-planes either side of the axis through the hinge
    n = (math.sin(a), -math.cos(a))           # normal pointing up-left of the axis
    big = 300
    upper = [back, far, (far[0] + n[0] * big, far[1] + n[1] * big), (back[0] + n[0] * big, back[1] + n[1] * big)]
    lower = [back, far, (far[0] - n[0] * big, far[1] - n[1] * big), (back[0] - n[0] * big, back[1] - n[1] * big)]
    P = lambda q: ' '.join(f'{f(x)},{f(y)}' for x, y in q)
    rot = -22 if split else 0
    rings_g = f'<g fill="none" stroke="currentColor" stroke-width="5">{el}</g>'
    seam = ''
    if kintsugi and not split:
        seam = (f'<line x1="{f(H[0])}" y1="{f(H[1])}" x2="{f(H[0] + 2 * rings[-1][1] * math.cos(a))}" y2="{f(H[1] + 2 * rings[-1][1] * math.sin(a))}" '
                f'style="stroke:var(--clasp)" stroke-width="2.6"/>')
    hinge = '' if (split or kintsugi) else f'<circle cx="{f(H[0])}" cy="{f(H[1])}" r="5.2" style="fill:var(--clasp)"/>'
    gap = 3.4 if kintsugi else 0
    off = (n[0] * gap / 2, n[1] * gap / 2)
    return (f'<defs><clipPath id="{ns}u"><polygon points="{P(upper)}"/></clipPath><clipPath id="{ns}l"><polygon points="{P(lower)}"/></clipPath></defs>'
            f'<g transform="rotate({rot} {f(H[0])} {f(H[1])}) translate({f(off[0])} {f(off[1])})"><g clip-path="url(#{ns}u)">{rings_g}</g></g>'
            f'<g transform="translate({f(-off[0])} {f(-off[1])})"><g clip-path="url(#{ns}l)">{rings_g}</g></g>' + seam + hinge)

def growth_seam(ns, split=False):
    """02. Growth rings, rejoined. The same rings, the two valves parted by a hair and rejoined along the
    axis by a gold seam: the kintsugi of round two, drawn with a compass."""
    return growth(ns, split, kintsugi=True)

def strata(ns, split=False):
    """03. Strata. An oyster shell is built in layers. The closed oyster, side on, as a stack of rounded bars:
    a short flat stack for the lid, a deeper one for the cup. Every bar starts further from the hinge the
    further it is from the seam, so together they taper to the hinge on the left, and their ragged right
    ends make the mouth. Between the stacks, one gold bar: the seam where the halves clasp."""
    h, g = 6.0, 2.4
    lid = [(26, 84), (11, 93)]                                # top to bottom, ending at the seam
    cup = [(11, 96), (17, 92), (25, 86), (35, 78), (47, 66)]  # seam downwards
    y = 26; out = ''; dy = 6 if split else 0
    for x0, x1 in lid:
        out += f'<rect x="{x0}" y="{f(y - dy)}" width="{x1 - x0}" height="{h}" rx="{h / 2}"/>'; y += h + g
    if not split:
        out += f'<rect x="5" y="{f(y)}" width="90" height="3.6" rx="1.8" style="fill:var(--clasp)"/>'
    y += 3.6 + g
    for x0, x1 in cup:
        out += f'<rect x="{x0}" y="{f(y + dy)}" width="{x1 - x0}" height="{h}" rx="{h / 2}"/>'; y += h + g
    return out

def halftone(ns, split=False):
    """04. Small pieces. The oyster from above, set in dots on a grid: a SELFTAC is made of small molecules
    that build something bigger. The row of dots along the seam between the two halves is gold."""
    import shell as S
    from matplotlib.path import Path as _P  # noqa: F401  (not available everywhere; fallback below)
    return ''

def _inside(poly, x, y):
    c = False; n = len(poly)
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1): c = not c
    return c

def dots(ns, split=False):
    """04. Small pieces. The oyster from above, set in dots on a grid: a SELFTAC is built from small molecules
    that make something bigger. Dots shrink toward the frilled edge; the column along the seam, where
    the two halves meet, is gold."""
    import shell as S
    o = S.transform(S.outline(2.2, 9, 1.0), 0, about=(50, 50), scale=(1.12, 1.02), move=(-2, 0))
    step = 6.6; out = ''
    xs = np.arange(8.4, 97, step); ys = np.arange(5, 99, step)
    mid = xs[len(xs) // 2]
    for x in xs:
        for y in ys:
            if not _inside(o, x, y): continue
            # distance to the edge, for size
            dmin = np.min(np.linalg.norm(o - [x, y], axis=1))
            r = min(2.9, .8 + dmin * .3)
            dx = (-4 if x < mid else 4 if x > mid else 0) if split else 0
            if x == mid:
                if split: continue
                out += f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" style="fill:var(--clasp)"/>'
            else:
                out += f'<circle cx="{f(x + dx)}" cy="{f(y)}" r="{f(r)}"/>'
    return out

def venn(ns, split=False):
    """05. Overlap. Two egg-shaped valves, the lid tilted a little off the cup, overlap at the hinge end; the
    overlap, the only place the two halves are one, is gold. Read together they are a closed oyster."""
    rot = -26 if split else -9
    cup = '<ellipse cx="52" cy="58" rx="40" ry="27"/>'
    lid = f'<ellipse cx="50" cy="44" rx="38" ry="22" transform="rotate({rot} 14 52)"/>'
    return (f'<defs><clipPath id="{ns}c"><ellipse cx="52" cy="58" rx="40" ry="27"/></clipPath>'
            f'<mask id="{ns}m" maskUnits="userSpaceOnUse" x="-10" y="-10" width="120" height="120"><rect x="-10" y="-10" width="120" height="120" fill="#fff"/>'
            f'<g fill="#000" stroke="#000" stroke-width="5">{lid.replace("/>", " />")}</g></mask></defs>'
            f'<g mask="url(#{ns}m)">{cup}</g>{lid}'
            + ('' if split else f'<g clip-path="url(#{ns}c)"><g style="fill:var(--clasp)">{lid}</g></g>'))

CONCEPTS = [
    ('growth', '01', 'Growth rings', growth,
     'Four rings that all touch at one point, the hinge, which is where a real oyster grows from. The axis from the hinge splits them into two valves, and the hinge is the gold clasp.',
     'Built with a compass, so it holds at any size, and it moves: the upper valve swings open about the hinge and clasps shut.'),
    ('seam', '02', 'Growth rings, rejoined', growth_seam,
     'The same rings, the two valves parted by a hair and rejoined along the axis by a gold seam: round two&rsquo;s kintsugi, drawn with a compass.',
     'The calmest kintsugi: one straight gold line, so the story is in the cut, not in decoration.'),
    ('strata', '03', 'Strata', strata,
     'An oyster shell is built in layers. The closed oyster, side on, as a stack of rounded bars: a flat lid, a deep cup, every bar starting from the hinge. Between them, one gold bar where the halves clasp.',
     'Pixel-perfect at favicon sizes, and unlike any other biotech mark; the layers say oyster, the gold bar says clasp.'),
    ('dots', '04', 'Small pieces', dots,
     'The oyster from above, set in dots on a grid, shrinking toward the frilled edge: a SELFTAC is small molecules that build something bigger. The column along the seam is gold.',
     'Scientific in feel, and the dots animate well: the halves can assemble dot by dot in the intro.'),
]
