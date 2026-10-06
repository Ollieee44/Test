"""Inside Out, refined: five refinements of the adopted mark (the disc with the open shell cut out of
it and the pearl in its cradle), each built from the same parts as marks.py.

Every mark is SVG in a 0-100 viewBox: currentColor for the disc, var(--p1) for the pearl and var(--p2)
for the clasp. The disc is the same in all of them (centre 50, 51.5 after the -1.5 1.5 nudge, radius
42), so they share Inside Out's ink bounds and sit in the logotype exactly where it does.
Running this file writes refine_defs.svg and the SVG exports oyster-refine-<name>-<palette>.svg.
"""
import math, os
from marks import LOW, UP

D = os.path.dirname(os.path.abspath(__file__)) + '/'
DISC = (51.5, 50, 42)

def _pt(x, y, s, up):
    """A point in shell coordinates, through the upper shell's rotation if up is set, into the disc."""
    if up is not None:
        a = math.radians(up); dx, dy = x - 12, y - 53
        x, y = 12 + dx * math.cos(a) - dy * math.sin(a), 53 + dx * math.sin(a) + dy * math.cos(a)
    return DISC[0] + s * (x - 50.5), DISC[1] + s * (y - 47.5)

def _shell(s, up):
    return (f'<g fill="#000" transform="translate({DISC[0]} {DISC[1]}) scale({s}) translate(-50.5 -47.5)">'
            f'<path d="{LOW}"/><path transform="rotate({up} 12 53)" d="{UP}"/></g>')

def _mask(id, black):
    return (f'<mask id="{id}" maskUnits="userSpaceOnUse" x="0" y="0" width="100" height="100">'
            f'<rect width="100" height="100" fill="#fff"/>{black}</mask>')

def _disc(mask):
    return f'<circle cx="{DISC[0]}" cy="{DISC[1]}" r="{DISC[2]}" mask="url(#{mask})"/>'

P1, P2 = 'style="fill:var(--p1)"', 'style="fill:var(--p2)"'

def build(ns=''):
    """Returns (masks, symbols) keyed by option name; ns prefixes the mask ids."""
    masks, sym = {}, {}
    def add(name, black, body):
        mid = f'{ns}mR-{name}'; masks[name] = _mask(mid, black); sym[name] = _disc(mid) + body

    # 00 the adopted mark, unchanged
    s, up = .76, -24; cx, cy = _pt(62, 52, s, None)
    add('inside', _shell(s, up) + f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{13.5 * s:.2f}" fill="#000"/>',
        f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{9.5 * s:.2f}" {P1}/>')

    # 01 the pearl is two halves held by a clasp-coloured band: one pearl from afar, the clasp up close
    r = 9.5 * s; g = .9; band = 1.5
    add('seam', _shell(s, up) + f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{13.5 * s:.2f}" fill="#000"/>',
        f'<path d="M{cx - g:.2f} {cy - math.sqrt(r * r - g * g):.2f}A{r:.2f} {r:.2f} 0 0 0 {cx - g:.2f} {cy + math.sqrt(r * r - g * g):.2f}Z" {P1}/>'
        f'<path d="M{cx + g:.2f} {cy - math.sqrt(r * r - g * g):.2f}A{r:.2f} {r:.2f} 0 0 1 {cx + g:.2f} {cy + math.sqrt(r * r - g * g):.2f}Z" {P1}/>'
        f'<rect x="{cx - band / 2:.2f}" y="{cy - r - .9:.2f}" width="{band}" height="{2 * r + 1.8:.2f}" rx="{band / 2}" {P2}/>')

    # 02 the clasp itself in the cradle: two clasp pearls and their bond, in a long cradle that follows the lower shell
    s2 = .78; ax, ay = _pt(54.5, 53.5, s2, None); bx, by = _pt(73.5, 53.5, s2, None); pr = 5.6; pad = 2.9
    add('clasp', _shell(s2, up) + f'<line x1="{ax:.2f}" y1="{ay:.2f}" x2="{bx:.2f}" y2="{by:.2f}" stroke="#000" stroke-width="{2 * (pr + pad):.2f}" stroke-linecap="round"/>',
        f'<line x1="{ax:.2f}" y1="{ay:.2f}" x2="{bx:.2f}" y2="{by:.2f}" stroke-width="3.8" style="stroke:var(--p2)"/>'
        f'<circle cx="{ax:.2f}" cy="{ay:.2f}" r="{pr}" {P2}/><circle cx="{bx:.2f}" cy="{by:.2f}" r="{pr}" {P2}/>')

    # 03 a larger shell in a thinner rim, so the oyster reads before the disc does
    s3 = .82; cx3, cy3 = _pt(62, 52.5, s3, None)
    add('large', _shell(s3, up) + f'<circle cx="{cx3:.2f}" cy="{cy3:.2f}" r="{13 * s3:.2f}" fill="#000"/>',
        f'<circle cx="{cx3:.2f}" cy="{cy3:.2f}" r="{9.3 * s3:.2f}" {P1}/>')

    # 04 the shell opens wider and the pearl grows into the opening
    s4, up4 = .74, -31; cx4, cy4 = _pt(63, 50, s4, None)
    add('wide', _shell(s4, up4) + f'<circle cx="{cx4:.2f}" cy="{cy4:.2f}" r="{15 * s4:.2f}" fill="#000"/>',
        f'<circle cx="{cx4:.2f}" cy="{cy4:.2f}" r="{11 * s4:.2f}" {P1}/>')

    # 05 the small-size cut, for 16-32px: no cradle ring, a wider mouth and a big pearl
    s5, up5 = .78, -32; cx5, cy5 = _pt(64, 49, s5, None)
    add('small', _shell(s5, up5) + f'<circle cx="{cx5:.2f}" cy="{cy5:.2f}" r="{12.5 * s5:.2f}" fill="#000"/>',
        f'<circle cx="{cx5:.2f}" cy="{cy5:.2f}" r="{12.5 * s5:.2f}" {P1}/>')
    return masks, sym

def standalone(name, ink, pearl, clasp, ns='x-'):
    """One mark as a file, in literal colours."""
    masks, sym = build(ns)
    body = (sym[name].replace(P1, f'fill="{pearl}"').replace(P2, f'fill="{clasp}"')
            .replace('style="stroke:var(--p2)"', f'stroke="{clasp}"'))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs>{masks[name]}</defs>'
            f'<g fill="{ink}"><g transform="translate(-1.5 1.5)">{body}</g></g></svg>')

def defs():
    masks, sym = build()
    return ('<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>' + ''.join(masks.values()) + '</defs>'
            + ''.join(f'<symbol id="r-{k}" viewBox="0 0 100 100"><g transform="translate(-1.5 1.5)">{v}</g></symbol>' for k, v in sym.items())
            + '</svg>')

# ink, pearl, clasp (house style: one accent for one meaning, the clasp)
PALETTES = {'nacre': ('#2B2230', '#C99BB0', '#D9A443'), 'tidepool': ('#0F4C4A', '#F2B84B', '#F27D62')}

if __name__ == '__main__':
    open(D + 'refine_defs.svg', 'w').write(defs())
    names = list(build()[1])[1:]
    for name in names:
        for pal, cols in PALETTES.items():
            open(D + f'oyster-refine-{name}-{pal}.svg', 'w').write(standalone(name, *cols))
    print('wrote refine_defs.svg and', len(names) * len(PALETTES), 'SVG exports')
