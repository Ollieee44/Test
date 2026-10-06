"""Two valves, one hinge: open-oyster marks drawn from two references the client shared.

From the painting: the oyster's own shape, a teardrop tapering to a beak at the hinge, a deep cup and
a thick, uneven rim. From the second image: the composition, an upper valve standing up behind like a
backdrop and a big pearl at the front in a shallow lower dish. A single half shell loses the two shells
coming together, which is the SELFTAC story, so every option keeps both valves, meeting at one hinge.
No scallop ribs: they read as a scallop.

Each valve is frontal.py's front-on valve (the teardrop with its beak), turned, squashed for
perspective and placed with its beak on the shared hinge. The insides are cut out, as in 00, and the
pearl breaks the dish's outline (from the eye-read fix) rather than sitting in the middle of it.
Same conventions as refine.py. Running this file writes hinged_defs.svg and oyster-hinged-<name>-<palette>.svg.
"""
import math, os
from refine import P1, PALETTES
from frontal import _valve_pts, build as _frontal_build
from threequarter import P, mask, shell, build as _tq_build

D = os.path.dirname(os.path.abspath(__file__)) + '/'
BEAK = round(228 / 360 * 180)   # index of the beak in _valve_pts' outline

def valve(hinge, rot, length, squash=1.0, ruffle=0.0):
    """One valve's outline, beak on the hinge. rot turns it (0 points the lip straight right), length
    scales it, squash flattens it across its length for perspective."""
    pts = _valve_pts(1.0, ruffle); bx, by = pts[BEAK]
    base = math.atan2(54 - by, 52 - bx)   # the valve's own axis, beak to centre
    r, s = math.radians(rot), length / 80; out = []
    for x, y in pts:
        x, y = x - bx, y - by
        u, v = x * math.cos(-base) - y * math.sin(-base), x * math.sin(-base) + y * math.cos(-base)
        u, v = u * s, v * s * squash
        out.append((hinge[0] + u * math.cos(r) - v * math.sin(r), hinge[1] + u * math.sin(r) + v * math.cos(r)))
    return out

def opening(pts, k=.78, dx=0.0, dy=-2.0):
    """The inside of a valve: its outline shrunk towards its centre and nudged back (up), so the rim
    is thicker at the front, where we see the shell's depth."""
    cx = sum(x for x, _ in pts) / len(pts); cy = sum(y for _, y in pts) / len(pts)
    return [(cx + k * (x - cx) + dx, cy + k * (y - cy) + dy) for x, y in pts]

INK = (8, 9.5, 92, 93.5)   # 00's ink box: every mark is fitted to it, so all sit alike in the logotype

def fit(shapes, pearl):
    """Scale and centre point lists and the pearl together so their ink fills INK."""
    xs = [x for p in shapes for x, _ in p] + [pearl[0] - pearl[2], pearl[0] + pearl[2]]
    ys = [y for p in shapes for _, y in p] + [pearl[1] - pearl[2], pearl[1] + pearl[2]]
    k = min((INK[2] - INK[0]) / (max(xs) - min(xs)), (INK[3] - INK[1]) / (max(ys) - min(ys)))
    ox = (INK[0] + INK[2]) / 2 - k * (min(xs) + max(xs)) / 2; oy = (INK[1] + INK[3]) / 2 - k * (min(ys) + max(ys)) / 2
    T = lambda p: [(ox + k * x, oy + k * y) for x, y in p]
    return [T(p) for p in shapes], (ox + k * pearl[0], oy + k * pearl[1], k * pearl[2]), k

def build(ns=''):
    masks, sym = {}, {}
    fm, fs = _frontal_build(ns + 'h-'); masks['inside'] = fm['inside']; sym['inside'] = fs['inside']
    tm, ts = _tq_build(ns + 'q-'); masks['frilled2'] = tm['frilled2']; sym['frilled2'] = ts['frilled2']   # the last pick, to compare
    def add(name, lo, up, pearl, ring=3.4, rings=(), solid_up=False, lo_rim=(.68, -3.5), up_rim=(.7, 2.5)):
        shapes = [lo, opening(lo, lo_rim[0], 0, lo_rim[1]), up, opening(up, up_rim[0], 0, up_rim[1])]
        shapes += [opening(up, kk, 0, 0) for kk in rings]
        (lo, lo_in, up, up_in, *gr), pearl, k = fit(shapes, pearl)
        growth = ''.join(P(g, 'fill="none" stroke="#000" stroke-width="2.3"') for g in gr)
        masks[name], sym[name] = shell(ns, name, (lo, lo_in), (up, [] if solid_up else up_in), pearl, ring, extra_up=growth)

    # 01 upright: the upper valve stands up behind like a backdrop (the second image), the lower valve a
    # shallow teardrop dish (the painting); the big pearl sits at the front, breaking the dish's rim
    H = (0, 0)
    add('upright', valve(H, 6, 80, .44, .9), valve(H, -62, 76, .8, .9), (48, 9, 11.5), lo_rim=(.62, -4.5))

    # 02 open book: the two valves near mirror images, opening from one beak; the pearl between them
    # is the moment they come together
    add('book', valve(H, 12, 80, .5, .9), valve(H, -36, 80, .56, .9), (44, -6, 10.5), up_rim=(.7, 3.5))

    # 03 the painting's cup: the lower valve deep and seen from above, with a thick rim at the front;
    # the upper valve smaller and further back, still joined at the hinge; the pearl rests on the
    # front lip, off-centre, so the cup does not read as an eye
    add('cup', valve(H, 8, 88, .66, 1.1), valve(H, -52, 64, .72, .8), (64, 14, 11), lo_rim=(.64, -5.5))

    # 04 big pearl: the second image's proportions, the pearl as big as it can be, the upper valve a
    # solid backdrop with growth lines, the dish a thin sliver in front
    add('bigpearl', valve(H, 3, 82, .36, .8), valve(H, -64, 80, .82, .9), (46, 6, 14.5), rings=(.62,), solid_up=True, lo_rim=(.6, -4))
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
    open(D + 'hinged_defs.svg', 'w').write(defs())
    names = [n for n in build()[1] if n not in ('inside', 'frilled2')]
    for name in names:
        for pal, cols in PALETTES.items():
            open(D + f'oyster-hinged-{name}-{pal}.svg', 'w').write(standalone(name, *cols))
    print('wrote hinged_defs.svg and', len(names) * len(PALETTES), 'SVG exports')
