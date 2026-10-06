"""Three-quarter, open: the oyster seen a little from above and to the front, open, built from Inside
Out (00). What stops it reading as a makeup compact is depth: we look into both valves (their insides
are cut out, as 00's shells are), the rims are ellipses rather than flat lids, and the edges are frilled
and uneven. The pearl rests in the lower valve's cup, in 00's cradle.

Same conventions as refine.py: a 0-100 viewBox, currentColor for the shell, var(--p1) for the pearl.
Running this file writes threequarter_defs.svg and oyster-threequarter-<name>-<palette>.svg.
"""
import math, os
from refine import P1, PALETTES
from frontal import build as _frontal_build

D = os.path.dirname(os.path.abspath(__file__)) + '/'

def oval(cx, cy, rx, ry, rot=0.0, frill=0.0, n=9, seed=0.0, arc=None, steps=160):
    """Points on a rotated ellipse; frill adds an uneven ruffle to the edge (only on arc=(a0, a1), degrees, if given)."""
    pts, c, s = [], math.cos(math.radians(rot)), math.sin(math.radians(rot))
    for i in range(steps):
        t = 2 * math.pi * i / steps; k = 1.0
        if frill:
            a = math.degrees(t) % 360; on = 1.0
            if arc:
                a0, a1 = arc; span = (a1 - a0) % 360; d = (a - a0) % 360
                on = math.sin(math.pi * d / span) if d <= span else 0.0
            k += on * frill * (math.sin(n * t + seed) + .3 * math.sin(1.9 * n * t + 2 * seed)) / max(rx, ry) * 1.6
        x, y = rx * k * math.cos(t), ry * k * math.sin(t)
        pts.append((cx + x * c - y * s, cy + x * s + y * c))
    return pts

def P(pts, attrs=''):
    return '<path d="M' + 'L'.join(f'{x:.2f} {y:.2f}' for x, y in pts) + f'Z" {attrs}/>'

def mask(id, black):
    return (f'<mask id="{id}" maskUnits="userSpaceOnUse" x="-10" y="-10" width="120" height="120">'
            f'<rect x="-10" y="-10" width="120" height="120" fill="#fff"/>{black}</mask>')

def shell(ns, name, lower, upper, pearl, ring, extra_up='', extra_lo=''):
    """lower, upper: (outer, opening) point lists for each valve. The lower valve sits in front, so a
    sliver of clear space is cut from the upper valve all round it; the pearl's cradle is cut from both."""
    (lo_out, lo_in), (up_out, up_in) = lower, upper
    px, py, pr = pearl
    cradle = f'<circle cx="{px}" cy="{py}" r="{pr + ring}" fill="#000"/>'
    a, b = f'{ns}mT-{name}-up', f'{ns}mT-{name}-lo'
    sep = P(lo_out, 'fill="#000" stroke="#000" stroke-width="5" stroke-linejoin="round"')
    m = (mask(a, (P(up_in, 'fill="#000"') if up_in else '') + sep + cradle + extra_up)
         + mask(b, P(lo_in, 'fill="#000"') + cradle + extra_lo))
    body = f'{P(up_out, f"mask=\"url(#{a})\"")}{P(lo_out, f"mask=\"url(#{b})\"")}<circle cx="{px}" cy="{py}" r="{pr}" {P1}/>'
    return m, body

def pair(depth=1.0, frill=0.0, lean=0.0):
    """The two valves, (outer, opening) each. depth scales how far we look down into the bowl (1 is
    three-quarter, less is a lower angle); lean tips the upper valve further back. The upper valve's
    left end rests on the lower valve's rim: that is the hinge."""
    f = lambda a: a * frill
    lower = (oval(52, 66, 40, 21 * depth + 3, 4, f(1.6), 7, .4, (300, 240)),
             oval(54, 66 - 6.5 * depth, 32, 10.5 * depth, 4, f(1.0), 8, 1.1))
    upper = (oval(56, 37 - 3 * lean, 40, 22 + 4 * lean, -24 + 10 * lean, f(1.9), 6, 2.2, (110, 60)),
             oval(58, 39.5 - 3 * lean, 32, 15 + 4 * lean, -24 + 10 * lean, f(1.1), 7, .7))
    return lower, upper

def build(ns=''):
    masks, sym = {}, {}
    fm, fs = _frontal_build(ns + 't-'); masks['inside'] = fm['inside']; sym['inside'] = fs['inside']

    # 01 three-quarter open: the lower valve a bowl seen from above, the upper valve tipped back from
    # the hinge on the left so we see its hollow inside
    masks['open'], sym['open'] = shell(ns, 'open', *pair(), (56, 57, 8.6), 3.2)

    # 02 frilled: the same view with ruffled, uneven lips on both valves
    masks['frilled'], sym['frilled'] = shell(ns, 'frilled', *pair(frill=1), (56, 57, 8.6), 3.2)

    # 03 the outside of the upper valve: it stands up behind, solid, with growth lines; only the
    # lower valve's cup is open, holding the pearl
    lower, upper = pair(frill=1)
    growth = ''.join(P(oval(56 - 14 * (1 - k), 37 + 6 * (1 - k), 40 * k, 22 * k, -24), 'fill="none" stroke="#000" stroke-width="2.2"') for k in (.72, .46))
    masks['backed'], sym['backed'] = shell(ns, 'backed', lower, (upper[0], []), (56, 57, 8.6), 3.2, extra_up=growth)

    # 04 in the disc: 00's idea kept, the disc as the o, with the frilled open shell cut into it
    k = .78; T = lambda pts: [(51.5 + k * (x - 53), 50 + k * (y - 52)) for x, y in pts]
    (lo_out, lo_in), (up_out, up_in) = [(T(o), T(i)) for o, i in pair(frill=1)]
    px, py, pr = 51.5 + k * 3, 50 + k * 5, 8.6 * k; cr = f'<circle cx="{px:.2f}" cy="{py:.2f}" r="{pr + 2.6:.2f}" fill="#000"/>'
    m1, m2 = f'{ns}mT-disc', f'{ns}mT-disc-lo'
    masks['disc'] = (mask(m1, P(up_out, 'fill="none" stroke="#000" stroke-width="3"') + P(lo_out, 'fill="#000" stroke="#000" stroke-width="3"') + P(up_in, 'fill="#000"') + cr)
                     + mask(m2, P(lo_in, 'fill="#000"') + cr))
    sym['disc'] = f'<circle cx="51.5" cy="50" r="42" mask="url(#{m1})"/>' + P(lo_out, f'mask="url(#{m2})"') + f'<circle cx="{px:.2f}" cy="{py:.2f}" r="{pr:.2f}" {P1}/>'

    # 05 a lower angle: closer to front-on, the bowl's opening a thin ellipse, the upper valve
    # leaning back further so more of its inside shows
    masks['low'], sym['low'] = shell(ns, 'low', *pair(depth=.65, frill=1, lean=1), (56, 59, 9), 3.2)
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
    open(D + 'threequarter_defs.svg', 'w').write(defs())
    names = list(build()[1])[1:]
    for name in names:
        for pal, cols in PALETTES.items():
            open(D + f'oyster-threequarter-{name}-{pal}.svg', 'w').write(standalone(name, *cols))
    print('wrote threequarter_defs.svg and', len(names) * len(PALETTES), 'SVG exports')
