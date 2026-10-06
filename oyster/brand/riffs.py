"""Riffs on B1 and B3 from refs.py: the front-on fan, dish and big pearl from the second reference.

All share B's geometry (the fan, the dish and the pearl, in the reference's own pixel coordinates,
fitted to 00's box) and change one idea each: what the ribs are made of, the fan's edge, the pearl,
or how the whole sits as the o of the logotype. Same conventions as refine.py: currentColor for the
shell, var(--p1) for the pearl and var(--p2) for the clasp.
Running this file writes riffs_defs.svg and oyster-riffs-<name>-<palette>.svg.
"""
import math, os
from refine import P1, P2, PALETTES
from refs import _fan, _dish, fit, rough, build as _refs_build
from threequarter import P, mask

D = os.path.dirname(os.path.abspath(__file__)) + '/'
HINGE = (500, 405); PEARL = (500, 352, 74)
SPAN = (-163, -17)   # the fan's angles, seen from the hinge

def L(pts, attrs=''):
    """An open polyline."""
    return '<path d="M' + 'L'.join(f'{x:.2f} {y:.2f}' for x, y in pts) + f'" {attrs}/>'

def edge(a, fan=None):
    """Distance from the hinge to the fan's edge in direction a."""
    fan = fan or _fan(); dense = []
    for (x0, y0), (x1, y1) in zip(fan, fan[1:]):   # densify, so the straight sides are measured too
        dense += [(x0 + (x1 - x0) * t / 12, y0 + (y1 - y0) * t / 12) for t in range(12)]
    best = min(dense[12:], key=lambda p: abs((math.atan2(p[1] - HINGE[1], p[0] - HINGE[0]) - a + math.pi) % (2 * math.pi) - math.pi))
    return math.hypot(best[0] - HINGE[0], best[1] - HINGE[1])

def rays(n):
    return [math.radians(SPAN[0] + (SPAN[1] - SPAN[0]) * (i + .5) / n) for i in range(n)]

def build(ns=''):
    masks, sym = {}, {}
    rm, rs = _refs_build(ns + 'b-')
    for k in ('ribbed', 'smooth'): masks[k], sym[k] = rm[k], rs[k]

    def compose(name, fan=None, cut=lambda T, k: '', extra=lambda T, k: '', pearl='plain', line=False, disc=False, gap=3.0):
        """Fan behind, dish in front, pearl on top. cut(T, k) adds black to the fan's mask and extra(T, k)
        adds ink, both given T (reference coordinates to the 0-100 box) and k (its scale)."""
        fan = fan or _fan(); dish, dish_in = _dish()
        shapes, circles, k = fit([fan, dish, dish_in], [PEARL], (22, 22, 81, 81) if disc else (8, 9.5, 92, 93.5))
        fan, dish, dish_in = shapes; (px, py, pr), = circles
        ox, oy = fan[0][0] - k * _fan()[0][0], fan[0][1] - k * _fan()[0][1]
        T = lambda x, y: (ox + k * x, oy + k * y)
        cr = f'<circle cx="{px:.2f}" cy="{py:.2f}" r="{pr + gap:.2f}" fill="#000"/>'
        a, b = f'{ns}mR-{name}-fan', f'{ns}mR-{name}-dish'
        if line:   # monoline: everything drawn as a stroke, the pearl solid
            w = 3.0; st = f'fill="none" stroke="currentColor" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"'
            cp = f'{ns}cR-{name}'   # the ribs are clipped to the inside of the fan
            masks[name] = (mask(a, P(dish, f'fill="#000" stroke="#000" stroke-width="{w + 3}"') + cr) + mask(b, cr)
                           + f'<clipPath id="{cp}">{P(fan)}</clipPath>')
            body = f'<g mask="url(#{a})">{P(fan, st)}<g clip-path="url(#{cp})">{cut(T, k)}</g></g><g mask="url(#{b})">{P(dish, st)}{P(dish_in, st)}</g>'
        else:
            masks[name] = (mask(a, cut(T, k) + P(dish, 'fill="#000" stroke="#000" stroke-width="4.5"') + cr)
                           + mask(b, P(dish_in, 'fill="#000"') + cr))
            body = P(fan, f'mask="url(#{a})"') + P(dish, f'mask="url(#{b})"') + extra(T, k)
        if disc:   # Inside Out: the disc is solid and the whole shell is cut out of it
            c = f'{ns}mR-{name}-disc'
            masks[name] += mask(c, P(fan, 'fill="#000" stroke="#000" stroke-width="3"') + P(dish, 'fill="#000" stroke="#000" stroke-width="3"') + cr)
            body = f'<circle cx="51.5" cy="50" r="42" mask="url(#{c})"/>' + body
        if pearl == 'clasp':   # two halves held by the clasp, the house's hero motif
            g, band = 1.1, 2.4; h = math.sqrt(pr * pr - g * g)
            body += (f'<path d="M{px - g:.2f} {py - h:.2f}A{pr:.2f} {pr:.2f} 0 0 0 {px - g:.2f} {py + h:.2f}Z" {P1}/>'
                     f'<path d="M{px + g:.2f} {py - h:.2f}A{pr:.2f} {pr:.2f} 0 0 1 {px + g:.2f} {py + h:.2f}Z" {P1}/>'
                     f'<rect x="{px - band / 2:.2f}" y="{py - pr - 1.2:.2f}" width="{band}" height="{2 * pr + 2.4:.2f}" rx="{band / 2}" {P2}/>')
        else:
            body += f'<circle cx="{px:.2f}" cy="{py:.2f}" r="{pr:.2f}" {P1}/>'
        sym[name] = body

    def rib_lines(n, w, r0=0, r1=1.35, cap='butt'):
        def f(T, k):
            out = ''
            for a in rays(n):
                R = edge(a)
                p0 = T(HINGE[0] + R * r0 * math.cos(a), HINGE[1] + R * r0 * math.sin(a))
                p1 = T(HINGE[0] + R * r1 * math.cos(a), HINGE[1] + R * r1 * math.sin(a))
                out += f'<line x1="{p0[0]:.2f}" y1="{p0[1]:.2f}" x2="{p1[0]:.2f}" y2="{p1[1]:.2f}" stroke="#000" stroke-width="{w}" stroke-linecap="{cap}"/>'
            return out
        return f

    # R1 bold ribs: five deep grooves instead of nine fine ones, for clarity at small sizes
    compose('bold', cut=rib_lines(5, 3.6, 0, 1.2))

    # R2 pearl strands: each rib is a string of pearls growing from the pearl to the rim, the house's
    # linker motif; the fan is literally built from strands of pearls
    def strands(T, k):
        out = ''
        for a in rays(9):
            R = edge(a)
            for t, r in ((.5, 5.5), (.6, 6.5), (.7, 7.5), (.8, 8.5)):
                x, y = T(HINGE[0] + R * t * math.cos(a), HINGE[1] + R * t * math.sin(a))
                out += f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r * k:.2f}" fill="#000"/>'
        return out
    compose('strands', cut=strands)

    # R3 growth lines: the fan's texture as an oyster's concentric growth lines rather than a
    # scallop's ribs, which also steps away from the Shell logo
    def growth(T, k):
        out = ''
        for s in (.8, .6):
            arc = [(HINGE[0] + s * (x - HINGE[0]), HINGE[1] + s * (y - HINGE[1])) for x, y in _fan()[1:-1]]
            out += L([T(x, y) for x, y in arc], 'fill="none" stroke="#000" stroke-width="2.2"')
        return out
    compose('growth', cut=growth)

    # R4 oyster lip: B3 with a frilled, uneven edge, as an oyster's is, not a scallop's even curve
    f = _fan(); top = rough(f[1:-1], 3.2, n=5, seed=1.3)
    compose('frilled', fan=[f[0]] + top + [f[-1]])

    # R5 the clasp: B3's pearl as two halves held by a band in the clasp colour
    compose('clasped', pearl='clasp')

    # R6 rays: B1's ribs start just outside the pearl and stop short of the rim, so they read as
    # light coming off the pearl as much as the ribs of a shell
    compose('rays', cut=rib_lines(9, 1.8, .5, .86, 'round'))

    # R7 line: B1 drawn as one even line, for an engraved, lighter feel
    compose('line', cut=lambda T, k: rib_lines(9, 3.0, .5, 1.0, 'round')(T, k).replace('stroke="#000"', 'stroke="currentColor"'), line=True)

    # R8 inside out: B3 cut out of 00's disc, so the shell keeps a round o for the logotype
    compose('disc', disc=True)
    return masks, sym

def standalone(name, ink, pearl, clasp, ns='x-'):
    masks, sym = build(ns)
    body = sym[name].replace(P1, f'fill="{pearl}"').replace(P2, f'fill="{clasp}"')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs>{masks[name]}</defs>'
            f'<g fill="{ink}"><g transform="translate(-1.5 1.5)">{body}</g></g></svg>')

def defs():
    masks, sym = build()
    return ('<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>' + ''.join(masks.values()) + '</defs>'
            + ''.join(f'<symbol id="r-{k}" viewBox="0 0 100 100"><g transform="translate(-1.5 1.5)">{v}</g></symbol>' for k, v in sym.items())
            + '</svg>')

if __name__ == '__main__':
    open(D + 'riffs_defs.svg', 'w').write(defs())
    names = [n for n in build()[1] if n not in ('ribbed', 'smooth')]
    for name in names:
        for pal, cols in PALETTES.items():
            open(D + f'oyster-riffs-{name}-{pal}.svg', 'w').write(standalone(name, *cols))
    print('wrote riffs_defs.svg and', len(names) * len(PALETTES), 'SVG exports')
