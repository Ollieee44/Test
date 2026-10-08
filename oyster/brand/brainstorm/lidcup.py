"""Round six: variations on round five's 02, Lid and cup. One drawing, lid_cup(), with every choice exposed,
and a list of variants that each change one or two things from 02: the angle the molecule runs at, where
the ligands leave the shell, how far the lid is open, the linker's form, the pearl's size, how much shell
texture there is, and the pearl's colour. Each drawing is fitted into the 0-100 box.
"""
import math
import numpy as np
from bifunctional import valve, pearl, ligand_bicyclic, ligand_branched, PT, f

def _on(c, rx, ry, deg):
    a = math.radians(deg); return np.array([c[0] + rx * math.cos(a), c[1] + ry * math.sin(a)])

def _rot(p, about, deg):
    a = math.radians(deg); p = np.array(p) - about
    return about + np.array([p[0] * math.cos(a) - p[1] * math.sin(a), p[0] * math.sin(a) + p[1] * math.cos(a)])

def lid_cup(ns, split=False, ang=45, lid=(31, 25), cup=(33, 31), r_in=13.5, pr=10, tilt=0, bond=5, zig=False,
            frill=1.1, growth=True, ring=1.0, colour='var(--pearl)'):
    c = np.array([50.0, 50.0]); g = 6 if split else 0
    L0, L1, C0, C1 = 196, 344, 16, 164
    la = min(max(ang + 180, L0 + 8), L1 - 8); ca = min(max(ang, C0 + 8), C1 - 8)
    hinge = c + [-lid[0], 0]
    # the lid, its attachment point and its ligand all turn together about the hinge when the shell is ajar
    lid_svg = valve(c + [0, -g], r_in, lid[0], lid[1], math.radians(L0), math.radians(L1), frill=frill, seed=.8, growth=growth, ns=ns + 'a')
    cup_svg = valve(c + [0, g], r_in, cup[0], cup[1], math.radians(C0), math.radians(C1), frill=frill, seed=2.2, growth=growth, ns=ns + 'b')
    pa = _on(c + [0, -g], lid[0], lid[1], la); pb = _on(c + [0, g], cup[0], cup[1], ca)
    da, db = math.radians(la), math.radians(ca)

    def arm(p, d, lig, r):
        u = np.array([math.cos(d), math.sin(d)])
        if zig:      # a short skeletal chain: three bonds with alternating kinks
            pts = [p]; k = 1
            for _ in range(3):
                kd = d + k * math.radians(32); pts.append(pts[-1] + np.array([math.cos(kd), math.sin(kd)]) * bond * .62); k = -k
            end = pts[-1]
            line = f'<polyline points="{PT(pts)}" fill="none" stroke="currentColor" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>'
        else:
            end = p + u * bond
            line = f'<line x1="{f(p[0])}" y1="{f(p[1])}" x2="{f(end[0])}" y2="{f(end[1])}" stroke="currentColor" stroke-width="2.8" stroke-linecap="round"/>'
        return line + lig(end, d, r=r), end + u * r * 2.4

    arm_a, tip_a = arm(pa, da, ligand_bicyclic, 4.6 * ring)
    arm_b, tip_b = arm(pb, db, ligand_branched, 4.8 * ring)
    top = f'<g transform="rotate({-tilt} {f(hinge[0])} {f(hinge[1])})">{lid_svg}{arm_a}</g>'
    tip_a = _rot(tip_a, hinge, -tilt)
    p_svg = pearl(c, pr, split, math.pi / 2, 6).replace('var(--pearl)', colour)
    body = top + cup_svg + arm_b + p_svg
    # fit: the shell and both ligand tips inside 5-95
    pts = np.array([tip_a, tip_b, c + [-cup[0], 0], c + [cup[0], 0], c + [0, -lid[1] - g - 2], c + [0, cup[1] + g + 2],
                    _rot(c + [lid[0], -lid[1] * .4], hinge, -tilt)])
    lo, hi = pts.min(0), pts.max(0); s = min(1.0, 90 / max(hi - lo)); mid = (lo + hi) / 2
    return f'<g transform="translate({f(50 - mid[0] * s)} {f(50 - mid[1] * s)}) scale({f(s)})">{body}</g>'

def V(**kw):
    fn = lambda ns, split=False: lid_cup(ns, split, **kw); return fn

CONCEPTS = [
    ('ref', '02', 'Lid and cup, as it was', V(),
     'Round five&rsquo;s 02, for reference: ligands leaving on the diagonal from the lid&rsquo;s back and the cup&rsquo;s belly.', ''),
    ('steep', 'A', 'Steeper', V(ang=62),
     'The molecule runs steeper, closer to upright: the ligands leave nearer the crown of the lid and the base of the cup.',
     'More compact and closer to a letter O.'),
    ('shallow', 'B', 'Shallower', V(ang=24),
     'The molecule runs flatter, the ligands leaving low on the lid and high on the cup, near the hinge and the mouth.',
     'Reads as a molecule laid on its side, passing through the shell.'),
    ('vertical', 'C', 'Upright', V(ang=90, bond=4),
     'The ligands leave straight up from the lid and straight down from the cup: the molecule stands on its end with the oyster at its middle.',
     'Symmetrical and calm; the tallest version.'),
    ('ajar', 'D', 'Ajar', V(tilt=14),
     'The lid lifted about the hinge, as an oyster opens, its ligand swinging with it: the pearl on show in the cup.',
     'The most oyster: an open oyster with its pearl is the image everyone knows.'),
    ('chain', 'E', 'Chain linkers', V(zig=True, bond=9),
     'The bonds to the ligands drawn as short zigzag chains, as a chemist draws a linker.',
     'More molecule; the oyster still reads at the middle.'),
    ('pearl', 'F', 'Bigger pearl', V(pr=12.5, r_in=16, lid=(30, 25), cup=(32, 30)),
     'A larger pearl in slimmer valves: the clasp is the hero.',
     'Puts the reversible clasp, the secret sauce, front and centre.'),
    ('smooth', 'G', 'Smooth', V(frill=0, growth=False),
     'No frill and no growth line: the same shapes, clean.',
     'The most iconic and the best at small sizes, though less obviously an oyster.'),
    ('ajarchain', 'H', 'Ajar, with chains', V(tilt=12, zig=True, bond=9, ang=40),
     'D and E together: the oyster open on its pearl, with chain linkers to the ligands.',
     'The fullest story in one mark, for large uses.'),
    ('gold', 'I', 'Gold pearl', V(colour='var(--clasp)'),
     '02 with the pearl in the clasp colour, gold in Nacre and coral in Tidepool, so the pearl reads as the clasp.',
     'Ties the mark to the clasp used across the site; the pearl colour leaves the logo.'),
]
