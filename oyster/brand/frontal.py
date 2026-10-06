"""Beyond the compact: directions from Inside Out (00) that stop it reading as a makeup compact.

00 is a perfect disc with straight-lipped shells and a lid hinged open like a mirror, which is what
makes it look like a compact. These options break that: a front-on view of an oyster valve, an
organic shell edge in place of the perfect circle, and ruffled lips in place of straight ones.

Same conventions as refine.py: a 0-100 viewBox, currentColor for the shell, var(--p1) for the pearl.
Running this file writes frontal_defs.svg and oyster-frontal-<name>-<palette>.svg.
"""
import math, os
from marks import LOW, UP
from refine import _shell, _pt, _mask, P1, P2, PALETTES

D = os.path.dirname(os.path.abspath(__file__)) + '/'

# --- the front-on valve: an oyster seen from above, the hinge (umbo) at top left, the lip at bottom right
UMBO = (25, 15)
def _valve_pts(k=1.0, ruffle=0.0, n=180):
    """Points on the valve outline, scaled by k towards the umbo. ruffle adds the frilled lip."""
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        # an egg leaning from the umbo to the lip: wide and round at the lip, narrow at the hinge
        r = 40 * (1 + .16 * math.cos(t - math.radians(48)))
        x, y = 52 + r * math.cos(t), 54 + r * .96 * math.sin(t)
        # pull the hinge end in to a beak at the umbo, so the growth lines can fan out from it
        w = max(0, math.cos(t - math.radians(228))) ** 4
        x, y = x + (UMBO[0] - x) * .9 * w, y + (UMBO[1] - y) * .9 * w
        if ruffle:   # frills grow towards the lip and vanish at the hinge
            f = ruffle * (1 - w) ** 2 * (math.sin(13 * t + .6) + .4 * math.sin(21 * t + 1.9))
            cx, cy = 52, 54; d = math.hypot(x - cx, y - cy)
            x, y = x + (x - cx) / d * f, y + (y - cy) / d * f
        pts.append((x, y))
    bx, by = pts[round(228 / 360 * n)]   # the beak: growth lines are smaller copies of the lip, all meeting here
    return [(bx + k * (x - bx), by + k * (y - by)) for x, y in pts]

def _path(pts):
    return 'M' + 'L'.join(f'{x:.2f} {y:.2f}' for x, y in pts) + 'Z'

def _rings(ks, w):
    return ''.join(f'<path d="{_path(_valve_pts(k))}" fill="none" stroke="#000" stroke-width="{w}"/>' for k in ks)

# --- organic edges for the disc and ruffled lips for the side view
def _rough_disc(cx=51.5, cy=50, r=42, n=200):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        rr = r * (1 + .015 * math.sin(5 * t + .7) + .009 * math.sin(9 * t + 2.1) + .03 * math.cos(t - .9) - .015)
        pts.append((cx + rr * math.cos(t), cy + rr * math.sin(t)))
    return _path(pts)

def _wavy(y, x0, x1, amp, n):
    """A wavy line from x0 to x1 at height y, as SVG path commands after a moveto/lineto at (x0, y)."""
    step = (x1 - x0) / n; out = f'Q{x0 + step / 2:.2f} {y - amp:.2f} {x0 + step:.2f} {y:.2f}'
    for i in range(2, n + 1): out += f'T{x0 + i * step:.2f} {y:.2f}'
    return out
LOW_R = LOW.replace('H84', _wavy(57, 14, 84, 2.6, 7))
UP_R = UP.replace('H84', _wavy(50, 15, 84, -2.2, 7))

def _shell_r(s, up):
    return (f'<g fill="#000" transform="translate(51.5 50) scale({s}) translate(-50.5 -47.5)">'
            f'<path d="{LOW_R}"/><path transform="rotate({up} 12 53)" d="{UP_R}"/></g>')

def build(ns=''):
    masks, sym = {}, {}
    def add(name, black, body):
        mid = f'{ns}mF-{name}'; masks[name] = _mask(mid, black)
        sym[name] = body.replace('MASK', f'url(#{mid})')
    s, up = .76, -24; cx, cy = _pt(62, 52, s, None)
    cradle = f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{13.5 * s:.2f}" fill="#000"/>'
    pearl = f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{9.5 * s:.2f}" {P1}/>'

    # 00 the adopted mark
    add('inside', _shell(s, up) + cradle, f'<circle cx="51.5" cy="50" r="42" mask="MASK"/>{pearl}')

    # 01 front-on: the valve seen from above, growth lines running round to the hinge, the pearl in the cup
    px, py, pr = 58, 62, 10.5
    add('valve', _rings((.78, .58, .38), 2.3) + f'<circle cx="{px}" cy="{py}" r="{pr + 3.6}" fill="#000"/>',
        f'<path d="{_path(_valve_pts(ruffle=.8))}" mask="MASK"/><circle cx="{px}" cy="{py}" r="{pr}" {P1}/>')

    # 02 front-on in the disc: the disc stays the o, and the valve is drawn into it as cut lines (its lip
    # and two growth lines), with the pearl in the cup
    k = .8; tf = lambda pts: [(51.5 + k * (x - 52), 50 + k * (y - 53)) for x, y in pts]
    qx, qy = 51.5 + k * (60 - 52), 50 + k * (63 - 53)
    lines = ''.join(f'<path d="{_path(tf(_valve_pts(kk, ruffle=.8 if kk == 1 else 0)))}" fill="none" stroke="#000" stroke-width="{w}"/>'
                    for kk, w in ((1, 3.2), (.72, 2.4), (.46, 2.4)))
    add('valvedisc', lines + f'<circle cx="{qx:.2f}" cy="{qy:.2f}" r="{13 * k:.2f}" fill="#000"/>',
        f'<circle cx="51.5" cy="50" r="42" mask="MASK"/><circle cx="{qx:.2f}" cy="{qy:.2f}" r="{9.6 * k:.2f}" {P1}/>')

    # 03 the same drawing in a shell-edged disc: a slightly lumpy, asymmetric rim, as a real shell has
    add('rough', _shell(s, up) + cradle, f'<path d="{_rough_disc()}" mask="MASK"/>{pearl}')

    # 04 ruffled lips: the straight edges of both shells become frilled, as an oyster's are
    add('ruffle', _shell_r(s, up) + cradle, f'<circle cx="51.5" cy="50" r="42" mask="MASK"/>{pearl}')

    # 05 both: a shell-edged disc and ruffled lips
    add('both', _shell_r(s, up) + cradle, f'<path d="{_rough_disc()}" mask="MASK"/>{pearl}')
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
    open(D + 'frontal_defs.svg', 'w').write(defs())
    names = list(build()[1])[1:]
    for name in names:
        for pal, cols in PALETTES.items():
            open(D + f'oyster-frontal-{name}-{pal}.svg', 'w').write(standalone(name, *cols))
    print('wrote frontal_defs.svg and', len(names) * len(PALETTES), 'SVG exports')
