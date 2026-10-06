"""R7 (the line fan and pearl, from riffs.py) at different pearl sizes, and inside out.

The pearl always rests in the dish: its bottom stays on the dish's floor and it grows upwards over
the fan. The ribs radiate from the hinge and stop at the fan's edge; the ring of clear space round the
pearl hides them where they meet it. Inside out, the drawing is cut out of 00's disc as lines.
Same conventions as refine.py. Running this file writes linepearl_defs.svg and oyster-linepearl-<name>-<palette>.svg.
"""
import math, os
from refine import P1, PALETTES
from refs import _fan, _dish, fit
from riffs import edge, HINGE
from threequarter import P, mask

D = os.path.dirname(os.path.abspath(__file__)) + '/'
FLOOR, PR = 426, 74          # the dish floor the pearl rests on, and R7's pearl radius (reference units)
SIZES = {'xs': .6, 's': .8, 'm': 1.0, 'l': 1.25, 'xl': 1.5}
W = 3.0                      # line weight, in the 0-100 box

def drawing(scale, box):
    """The fan, dish, ribs and pearl fitted to the box, for a pearl scaled by scale."""
    r = PR * scale; pearl = (500, FLOOR - r, r)
    fan = _fan(); dish, dish_in = _dish()
    shapes, (pearl,), k = fit([fan, dish, dish_in], [pearl], box)
    ox, oy = shapes[0][0][0] - k * fan[0][0], shapes[0][0][1] - k * fan[0][1]
    T = lambda x, y: (ox + k * x, oy + k * y)
    ribs = []
    # the fan's straight lower sides already run out from the hinge like ribs, so they are the outer
    # two; seven more are spaced evenly between them, starting a little out from the hinge so they do
    # not crowd together below a small pearl
    side = math.degrees(math.atan2(fan[1][1] - HINGE[1], fan[1][0] - HINGE[0]))   # the right side's angle
    for i in range(7):
        a = math.radians(-180 - side + (2 * side + 180) * (i + 1) / 8); R = edge(a)
        ribs.append((T(HINGE[0] + R * .34 * math.cos(a), HINGE[1] + R * .34 * math.sin(a)), T(HINGE[0] + R * math.cos(a), HINGE[1] + R * math.sin(a))))
    return shapes, ribs, pearl

def _ribs(ribs, color):
    return ''.join(f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" stroke="{color}" stroke-width="{W}" stroke-linecap="round"/>' for a, b in ribs)

def build(ns=''):
    masks, sym = {}, {}
    def line(name, scale, gap=3.0):
        (fan, dish, dish_in), ribs, (px, py, pr) = drawing(scale, (8, 9.5, 92, 93.5))
        st = f'fill="none" stroke="currentColor" stroke-width="{W}" stroke-linejoin="round" stroke-linecap="round"'
        a, b, cp = f'{ns}mL-{name}-fan', f'{ns}mL-{name}-dish', f'{ns}cL-{name}'
        cr = f'<circle cx="{px:.2f}" cy="{py:.2f}" r="{pr + gap:.2f}" fill="#000"/>'
        masks[name] = (mask(a, P(dish, f'fill="#000" stroke="#000" stroke-width="{W + 3}"') + cr) + mask(b, cr)
                       + f'<clipPath id="{cp}">{P(fan)}</clipPath>')
        sym[name] = (f'<g mask="url(#{a})">{P(fan, st)}<g clip-path="url(#{cp})">{_ribs(ribs, "currentColor")}</g></g>'
                     f'<g mask="url(#{b})">{P(dish, st)}{P(dish_in, st)}</g><circle cx="{px:.2f}" cy="{py:.2f}" r="{pr:.2f}" {P1}/>')

    def inside(name, scale, gap=2.6):
        # the disc is solid; the drawing's lines are cut through it. Mask order matters: the fan's lines,
        # then the dish filled white (so the fan does not show through it), then the dish's lines
        (fan, dish, dish_in), ribs, (px, py, pr) = drawing(scale, (21, 23, 82, 80))
        st = f'fill="none" stroke="#000" stroke-width="{W}" stroke-linejoin="round" stroke-linecap="round"'
        a, cp = f'{ns}mL-{name}', f'{ns}cL-{name}'
        masks[name] = (mask(a, P(fan, st) + f'<g clip-path="url(#{cp})">{_ribs(ribs, "#000")}</g>'
                            + P(dish, f'fill="#fff" stroke="#fff" stroke-width="{W + 3}"') + P(dish, st) + P(dish_in, st)
                            + f'<circle cx="{px:.2f}" cy="{py:.2f}" r="{pr + gap:.2f}" fill="#000"/>')
                       + f'<clipPath id="{cp}">{P(fan)}</clipPath>')
        sym[name] = f'<circle cx="51.5" cy="50" r="42" mask="url(#{a})"/><circle cx="{px:.2f}" cy="{py:.2f}" r="{pr:.2f}" {P1}/>'

    for key, s in SIZES.items(): line(f'line-{key}', s)
    for key in ('s', 'm', 'l'): inside(f'io-{key}', SIZES[key])
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
    open(D + 'linepearl_defs.svg', 'w').write(defs())
    names = list(build()[1])
    for name in names:
        for pal, cols in PALETTES.items():
            open(D + f'oyster-linepearl-{name}-{pal}.svg', 'w').write(standalone(name, *cols))
    print('wrote linepearl_defs.svg and', len(names) * len(PALETTES), 'SVG exports')
