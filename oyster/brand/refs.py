"""Marks drawn closely from the client's two reference images, each on its own (no hybrids).

A: the painting. One half shell, seen three-quarter: the hinge's beak at the left, the broad end up
   at the right, a deep cup with a thick rim at the front and a thin one at the back, and the pearl low
   in the cup. Outlines are traced from the painting (its coordinates, 960 x 1200) and fitted to 00's box.
B: the second image. Front-on and symmetric: the upper valve stands up as a fan behind, a shallow dish
   lies in front, and a big pearl rests in the dish, overlapping the fan.

Same conventions as refine.py. Running this file writes refs_defs.svg and oyster-refs-<name>-<palette>.svg.
"""
import math, os
from refine import P1, PALETTES
from frontal import build as _frontal_build
from threequarter import P, mask

D = os.path.dirname(os.path.abspath(__file__)) + '/'
INK = (8, 9.5, 92, 93.5)

def smooth(pts, steps=10):
    """A closed Catmull-Rom curve through the points."""
    out, n = [], len(pts)
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        for s in range(steps):
            t = s / steps; t2, t3 = t * t, t * t * t
            out.append(tuple(.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                   + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    return out

def rough(pts, amp, n=23, seed=.7):
    """Roughen an outline along its normals, like the chipped rim in the painting."""
    out, N = [], len(pts)
    for i, (x, y) in enumerate(pts):
        (ax, ay), (bx, by) = pts[i - 1], pts[(i + 1) % N]
        dx, dy = bx - ax, by - ay; L = math.hypot(dx, dy) or 1
        t = 2 * math.pi * i / N
        d = amp * (math.sin(n * t + seed) + .5 * math.sin(2.3 * n * t + 3 * seed) + .3 * math.sin(4.1 * n * t))
        out.append((x + dy / L * d, y - dx / L * d))
    return out

def fit(shapes, circles, box=INK):
    """Scale and centre point lists and circles (x, y, r) together so their ink fills the box."""
    xs = [x for p in shapes for x, _ in p] + [c[0] + s * c[2] for c in circles for s in (-1, 1)]
    ys = [y for p in shapes for _, y in p] + [c[1] + s * c[2] for c in circles for s in (-1, 1)]
    k = min((box[2] - box[0]) / (max(xs) - min(xs)), (box[3] - box[1]) / (max(ys) - min(ys)))
    ox = (box[0] + box[2]) / 2 - k * (min(xs) + max(xs)) / 2; oy = (box[1] + box[3]) / 2 - k * (min(ys) + max(ys)) / 2
    return [[(ox + k * x, oy + k * y) for x, y in p] for p in shapes], [(ox + k * c[0], oy + k * c[1], k * c[2]) for c in circles], k

# --- A: the painting (traced in its own pixel coordinates)
A_OUT = [(115, 590), (190, 505), (330, 468), (470, 420), (565, 362), (655, 336), (722, 348), (775, 410), (808, 520),
         (805, 640), (772, 742), (690, 815), (560, 868), (420, 880), (300, 830), (200, 745), (138, 668)]
A_OUT[0] = (100, 600)   # the beak, pointed
A_IN = [(250, 548), (340, 492), (470, 446), (580, 384), (662, 362), (735, 400), (778, 500), (775, 600), (735, 685),
        (640, 740), (505, 760), (380, 730), (290, 650)]   # thin at the back, thick at the front and the beak
A_PEARL = (520, 676, 74)   # low in the cup, against the front rim

# --- B: the second image (traced in its own pixel coordinates, 1000 x 500, mirrored to be symmetric)
def _fan(cx=500, cy=215, rx=190, ry=158, hinge=405, n=48):
    """The upright upper valve: a rounded top on a fan that tapers to the hinge, hidden behind the pearl.
    Drawn from the lower right, up and over the top, down to the lower left."""
    top = [(cx + rx * math.cos(math.radians(20 - 220 * i / n)), cy + ry * math.sin(math.radians(20 - 220 * i / n))) for i in range(n + 1)]
    return [(cx + 40, hinge)] + top + [(cx - 40, hinge)]

def _dish(cx=500, cy=412, rx=208, ry=30, depth=34):
    """The lower valve, a shallow dish seen from just above: its outline, and the inside of its rim."""
    out = [(cx + rx * math.cos(t), cy + (ry if math.sin(t) < 0 else ry + depth) * math.sin(t))
           for t in (2 * math.pi * i / 120 for i in range(120))]
    inner = [(cx + (rx - 22) * math.cos(t), cy - 4 + (ry - 12) * math.sin(t)) for t in (2 * math.pi * i / 120 for i in range(120))]
    return out, inner
B_PEARL = (500, 352, 74)

def build(ns=''):
    masks, sym = {}, {}
    fm, fs = _frontal_build(ns + 'f-'); masks['inside'] = fm['inside']; sym['inside'] = fs['inside']

    def half(name, rim=0.0, shadow=False):
        out = smooth(A_OUT); inn = smooth(A_IN)
        if rim: out = rough(out, rim)
        shapes = [out, inn]; circles = [A_PEARL]
        if shadow:   # the painting's cast shadow, a flat ellipse under the shell's left side
            sh = [(300 + 270 * math.cos(t), 850 + 58 * math.sin(t)) for t in (2 * math.pi * i / 90 for i in range(90))]
            shapes.append(sh)
        shapes, (pearl,), k = fit(shapes, circles)
        out, inn = shapes[0], shapes[1]; px, py, pr = pearl; mid = f'{ns}mA-{name}'
        sep = P(out, 'fill="#000" stroke="#000" stroke-width="4"') if shadow else ''
        masks[name] = mask(mid, P(inn, 'fill="#000"') + f'<circle cx="{px:.2f}" cy="{py:.2f}" r="{pr + 3:.2f}" fill="#000"/>')
        body = ''
        if shadow:
            m2 = f'{ns}mA-{name}-sh'; masks[name] += mask(m2, sep)
            body += P(shapes[2], f'mask="url(#{m2})" opacity=".35"')
        # the cup's inner wall: the opening tinted, except for its floor (the opening shifted down and
        # left), so a darker crescent runs round the back and right, as in the painting
        cx_ = sum(x for x, _ in inn) / len(inn); cy_ = sum(y for _, y in inn) / len(inn)
        floor = [(cx_ + .86 * (x - cx_) - 4, cy_ + .8 * (y - cy_) + 5) for x, y in inn]
        m3 = f'{ns}mA-{name}-wall'
        masks[name] += mask(m3, P(floor, 'fill="#000"') + f'<circle cx="{px:.2f}" cy="{py:.2f}" r="{pr + 3:.2f}" fill="#000"/>')
        body += P(inn, f'mask="url(#{m3})" opacity=".3"')
        sym[name] = body + P(out, f'mask="url(#{mid})"') + f'<circle cx="{px:.2f}" cy="{py:.2f}" r="{pr:.2f}" {P1}/>'

    # A1 the half shell, as painted: deep cup, thick front rim, the pearl low in the cup
    half('half')
    # A2 the same with the painting's chipped, rough rim
    half('rough', rim=7)
    # A3 the same, resting on its cast shadow, as in the painting
    half('shadow', rim=7, shadow=True)

    def front(name, ribs=0, scallop=0.0):
        fan = _fan()
        if scallop:   # the fan's edge bumped by its ribs, as the reference's shell is
            hx0, hy0 = 500, 405; f2 = []
            for x, y in fan:
                a = math.atan2(y - hy0, x - hx0); r = math.hypot(x - hx0, y - hy0)
                u = (math.degrees(a) + 180) / 180            # 0 at the left, 1 at the right
                bump = -scallop * (1 - abs(math.cos(math.pi * ribs * u))) if y < 330 else 0
                f2.append((hx0 + (r + bump) * math.cos(a), hy0 + (r + bump) * math.sin(a)))
            fan = f2
        dish, dish_in = _dish()
        shapes, (pearl,), k = fit([fan, dish, dish_in], [B_PEARL])
        fan, dish, dish_in = shapes; px, py, pr = pearl
        hx, hy = (fan[0][0] + fan[-1][0]) / 2, (fan[0][1] + fan[-1][1]) / 2   # the hinge, where the ribs meet
        cr = f'<circle cx="{px:.2f}" cy="{py:.2f}" r="{pr + 3:.2f}" fill="#000"/>'
        rib = ''
        if ribs and not scallop:
            top = min(y for _, y in fan)
            for i in range(ribs):
                a = math.radians(-163 + 146 * (i + .5) / ribs); L = (hy - top) * 1.3
                rib += f'<line x1="{hx:.2f}" y1="{hy:.2f}" x2="{hx + L * math.cos(a):.2f}" y2="{hy + L * math.sin(a):.2f}" stroke="#000" stroke-width="1.8"/>'
            rib = f'<g>{rib}</g><circle cx="{hx:.2f}" cy="{hy:.2f}" r="{(hy - top) * .2:.2f}" fill="#fff"/>'
        a, b = f'{ns}mB-{name}-fan', f'{ns}mB-{name}-dish'
        masks[name] = (mask(a, rib + P(dish, 'fill="#000" stroke="#000" stroke-width="4.5"') + cr)
                       + mask(b, P(dish_in, 'fill="#000"') + cr))
        sym[name] = P(fan, f'mask="url(#{a})"') + P(dish, f'mask="url(#{b})"') + f'<circle cx="{px:.2f}" cy="{py:.2f}" r="{pr:.2f}" {P1}/>'

    # B1 as in the reference: the fan with its ribs, the dish, the big pearl
    front('ribbed', ribs=9)
    # B2 the fan's ribs carried only by its scalloped edge, a cleaner icon
    front('scalloped', ribs=9, scallop=22)
    # B3 the fan smooth, no ribs: the composition without the scallop
    front('smooth')
    return masks, sym

def standalone(name, ink, pearl, clasp, ns='x-'):
    masks, sym = build(ns)
    body = sym[name].replace(P1, f'fill="{pearl}"')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs>{masks[name]}</defs>'
            f'<g fill="{ink}"><g transform="translate(-1.5 1.5)">{body}</g></g></svg>')

def defs():
    masks, sym = build()
    return ('<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>' + ''.join(masks.values()) + '</defs>'
            + ''.join(f'<symbol id="r-{k}" viewBox="0 0 100 100"><g transform="translate(-1.5 1.5)">{v}</g></symbol>' for k, v in sym.items())
            + '</svg>')

if __name__ == '__main__':
    open(D + 'refs_defs.svg', 'w').write(defs())
    names = [n for n in build()[1] if n != 'inside']
    for name in names:
        for pal, cols in PALETTES.items():
            open(D + f'oyster-refs-{name}-{pal}.svg', 'w').write(standalone(name, *cols))
    print('wrote refs_defs.svg and', len(names) * len(PALETTES), 'SVG exports')
