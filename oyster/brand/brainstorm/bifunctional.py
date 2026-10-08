"""Round five: the mark is the molecule. A stylised heterobifunctional degrader: two different ligands at the
ends, a linker between them whose middle is the two valves of an oyster, and the pearl cupped between the
valves as the clasp, the reversible secret sauce. Split, the valves part and the pearl parts with them,
each valve keeping half. The valves round the pearl make a loose O.

Generic, per the house style: invented ring systems traced as open tubes, never a real ligand; the two ends
differ (a fused bicyclic ring system and a single ring with a branch), as a heterobifunctional's do.
Contract as before: fn(ns, split) -> SVG in a 0-100 box; ink currentColor; the pearl var(--pearl).
"""
import math
import numpy as np

f = lambda v: f'{v:.2f}'
PT = lambda q: ' '.join(f'{f(x)},{f(y)}' for x, y in q)
BOX = 'maskUnits="userSpaceOnUse" x="-20" y="-20" width="140" height="140"'

def poly_ring(c, r, n, rot):
    return [(c[0] + r * math.cos(rot + 2 * math.pi * k / n), c[1] + r * math.sin(rot + 2 * math.pi * k / n)) for k in range(n)]

def ligand_bicyclic(attach, direction, r=5.2, w=2.6):
    """A fused six-five ring system hung off attach, pointing along direction (radians)."""
    d = np.array([math.cos(direction), math.sin(direction)])
    c6 = np.array(attach) + d * r * 1.0
    hexa = poly_ring(c6, r, 6, direction + math.pi)                      # a vertex at the attachment point
    # the five ring shares the hexagon's edge furthest from the attachment, on one side
    a, b = np.array(hexa[2]), np.array(hexa[3])
    mid = (a + b) / 2; out = mid - c6; out = out / np.linalg.norm(out)
    side = np.linalg.norm(a - b); rp = side / (2 * math.sin(math.pi / 5)); cp = mid + out * rp * math.cos(math.pi / 5)
    ang = math.atan2(a[1] - cp[1], a[0] - cp[0])
    pent = poly_ring(cp, rp, 5, ang)
    return (f'<g fill="none" stroke="currentColor" stroke-width="{w}" stroke-linejoin="round"><polygon points="{PT(hexa)}"/>'
            f'<polygon points="{PT(pent)}"/></g>')

def ligand_branched(attach, direction, r=5.6, w=2.6):
    """A single six ring with a short branch, hung off attach along direction."""
    d = np.array([math.cos(direction), math.sin(direction)])
    c6 = np.array(attach) + d * r
    hexa = poly_ring(c6, r, 6, direction + math.pi)
    far = np.array(hexa[3]); tip = far + d * r * .9
    kink = tip + np.array([math.cos(direction + 1.05), math.sin(direction + 1.05)]) * r * .8
    return (f'<g fill="none" stroke="currentColor" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"><polygon points="{PT(hexa)}"/>'
            f'<polyline points="{PT([far, tip, kink])}"/></g>')

def bond(a, b, w=2.8):
    return f'<line x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}" stroke="currentColor" stroke-width="{w}" stroke-linecap="round"/>'

def valve(c, r_in, rx, ry, a0, a1, frill=1.1, seed=0.0, growth=True, ns='v'):
    """A valve cupped round the pearl: between a smooth inner arc (radius r_in about c) and a frilled outer
    arc (ellipse rx, ry about c), from angle a0 to a1. A growth line runs between them."""
    t = np.linspace(a0, a1, 90)
    wob = .8 * np.sin(7 * t + seed) + .5 * np.sin(13 * t + 2 * seed + 1) + .3 * np.sin(23 * t + seed)
    fade = np.clip(np.sin((t - a0) / (a1 - a0) * math.pi) * 3, 0, 1)
    outer = np.stack([c[0] + (rx + frill * wob * fade) * np.cos(t), c[1] + (ry + frill * wob * fade) * np.sin(t)], 1)
    inner = np.stack([c[0] + r_in * np.cos(t[::-1]), c[1] + r_in * np.sin(t[::-1])], 1)
    body = f'<polygon points="{PT(np.vstack([outer, inner]))}" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>'
    if not growth:
        return body
    tm = np.linspace(a0 + .25, a1 - .25, 60); k = .58
    mid = np.stack([c[0] + (r_in + (rx - r_in) * k) * np.cos(tm), c[1] + (r_in + (ry - r_in) * k) * np.sin(tm)], 1)
    return (f'<mask id="{ns}" {BOX}><rect x="-20" y="-20" width="140" height="140" fill="#fff"/>'
            f'<polyline points="{PT(mid)}" fill="none" stroke="#000" stroke-width="1.8" stroke-linecap="round"/></mask>'
            f'<g mask="url(#{ns})">{body}</g>')

def pearl(c, r, split, axis=0.0, gap=0.0):
    """The pearl, or, split, its two halves pulled apart along axis (radians) by gap."""
    if not split:
        return (f'<circle cx="{f(c[0])}" cy="{f(c[1])}" r="{f(r)}" style="fill:var(--pearl)"/>'
                f'<circle cx="{f(c[0] - r * .35)}" cy="{f(c[1] - r * .38)}" r="{f(r * .26)}" fill="#fff" opacity=".55"/>')
    d = np.array([math.cos(axis), math.sin(axis)]); out = ''
    for sgn in (-1, 1):
        cc = np.array(c) + d * sgn * gap
        base = math.atan2(sgn * d[1], sgn * d[0])           # the half's outward direction
        t = np.linspace(base - math.pi / 2, base + math.pi / 2, 40)
        half = np.stack([cc[0] + r * np.cos(t), cc[1] + r * np.sin(t)], 1)
        out += f'<polygon points="{PT(half)}" style="fill:var(--pearl)"/>'
    return out

def side_by_side(ns, split=False):
    """01. Bracketed. The degrader laid straight: a ligand at each end, and in the middle of the linker the
    two valves facing each other like brackets round the pearl, ( o ). The valves and pearl are the O."""
    c = (50, 50); g = 7 if split else 0; r_in, rx, ry = 13.5, 25, 29
    left = valve((c[0] - g, c[1]), r_in, rx, ry, math.radians(112), math.radians(248), seed=.3, ns=ns + 'a')
    right = valve((c[0] + g, c[1]), r_in, rx * .92, ry * .92, math.radians(-68), math.radians(68), seed=1.7, ns=ns + 'b')
    la = (c[0] - g - rx, c[1]); lb = (c[0] + g + rx * .92, c[1])
    ends = (bond(la, (la[0] - 5, la[1])) + ligand_bicyclic((la[0] - 5, la[1]), math.pi, r=4.6)
            + bond(lb, (lb[0] + 5, lb[1])) + ligand_branched((lb[0] + 5, lb[1]), 0, r=4.8))
    return left + right + ends + pearl(c, 10, split, 0, 6)

def lid_and_cup(ns, split=False):
    """02. Lid and cup. The oyster side on, a flatter lid over a deeper cup with the pearl held between, and
    the two ligands leaving from opposite corners, so the molecule runs on the diagonal through the shell.
    Lid, pearl and cup make the O."""
    c = (50, 50); g = 6 if split else 0; r_in = 13.5
    lid = valve((c[0], c[1] - g), r_in, 31, 25, math.radians(196), math.radians(344), seed=.8, ns=ns + 'a')
    cup = valve((c[0], c[1] + g), r_in, 33, 31, math.radians(16), math.radians(164), seed=2.2, ns=ns + 'b')
    a = (c[0] - 27, c[1] - g - 13); b = (c[0] + 28, c[1] + g + 16)
    ends = (bond(a, (a[0] - 5, a[1] - 5)) + ligand_bicyclic((a[0] - 5, a[1] - 5), math.radians(225), r=4.6)
            + bond(b, (b[0] + 5, b[1] + 5)) + ligand_branched((b[0] + 5, b[1] + 5), math.radians(45), r=4.8))
    return lid + cup + ends + pearl(c, 10, split, math.pi / 2, 6)

def curled(ns, split=False):
    """03. Curled. The whole degrader bent into an O: from the bicyclic ligand at the top left, the linker
    runs round the right-hand side, where its middle is the oyster, two small valves cupped round the
    pearl, and on round to the branched ligand at the bottom left. The two ligands nearly meet, closing
    the O, as the two ends of a degrader meet their two proteins."""
    c = np.array([52.0, 50.0]); R = 33
    pc = c + [R, 0]                                 # the oyster sits at three o'clock
    g = 5 if split else 0
    th1 = np.radians(np.linspace(-150, -22, 60)); th2 = np.radians(np.linspace(22, 150, 60))
    arc1 = np.stack([c[0] + R * np.cos(th1), c[1] + R * np.sin(th1)], 1) + [0, -g]
    arc2 = np.stack([c[0] + R * np.cos(th2), c[1] + R * np.sin(th2)], 1) + [0, g]
    link = ''.join(f'<polyline points="{PT(a)}" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round"/>' for a in (arc1, arc2))
    up = valve((pc[0], pc[1] - g), 7.6, 15, 13, math.radians(185), math.radians(355), frill=.7, seed=.4, growth=False, ns=ns + 'a')
    lo = valve((pc[0], pc[1] + g), 7.6, 15, 15, math.radians(5), math.radians(175), frill=.8, seed=1.9, growth=False, ns=ns + 'b')
    e1, e2 = arc1[0], arc2[-1]
    t1 = math.atan2(arc1[0][1] - arc1[3][1], arc1[0][0] - arc1[3][0]); t2 = math.atan2(arc2[-1][1] - arc2[-4][1], arc2[-1][0] - arc2[-4][0])
    ends = ligand_bicyclic(e1, t1, r=5) + ligand_branched(e2, t2, r=5.2)
    return f'<g transform="translate(-6 0)">{link}{up}{lo}{ends}{pearl(pc, 6.2, split, math.pi / 2, 4)}</g>'

def ring_o(ns, split=False):
    """04. The O. The valves drawn large enough to be the O on their own, a near-complete ring split top and
    bottom into lid and cup, the pearl in the counter; the ligands sit on short bonds at the hinge side
    and the mouth side, so the molecule crosses the O from left to right."""
    c = (50, 50); g = 5 if split else 0; r_in = 17
    lid = valve((c[0], c[1] - g), r_in, 36, 33, math.radians(188), math.radians(352), seed=.5, ns=ns + 'a')
    cup = valve((c[0], c[1] + g), r_in, 37, 35, math.radians(8), math.radians(172), seed=2.6, ns=ns + 'b')
    return lid + cup + pearl(c, 12, split, math.pi / 2, 5)

CONCEPTS = [
    ('brackets', '01', 'Bracketed', side_by_side,
     'The degrader laid straight: a different ligand at each end, and in the middle of the linker the two valves facing each other round the pearl, like brackets: ( &bull; ). The valves and pearl make the O.',
     'The clearest read of a bifunctional, and the shell-and-pearl O sits right where the o goes.'),
    ('lidcup', '02', 'Lid and cup', lid_and_cup,
     'The oyster side on, a flat lid over a deep cup with the pearl held between them, and the two ligands leaving from opposite corners, so the molecule runs on the diagonal through the shell.',
     'More oyster than 01 (lid over cup is how an oyster sits), with a diagonal that gives it movement.'),
    ('curled', '03', 'Curled', curled,
     'The whole degrader bent into an O: the linker runs from one ligand round to the other, and at its middle is the oyster, two small valves cupping the pearl. The two ligands nearly meet, closing the O.',
     'The most like a letter O, with the oyster as the jewel in it.'),
    ('ring', '04', 'The O', ring_o,
     'The valves large enough to be the O on their own, lid over cup round the pearl, no ligands: the simple form for small sizes and the o of the logotype, with 01 to 03 as the full molecule.',
     'Pairs with any of the others as the small-size cut.'),
]
