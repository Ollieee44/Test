"""New brandmark concepts that build SELFTAC from the oyster's own anatomy instead of adding pearls.

An oyster is two separate valves joined at one reversible joint, the hinge ligament; a SELFTAC is two halves
that clasp back together. So in every concept the valves are the two halves, and the hinge, the lip or the
seam between them carries the clasp. Each valve is drawn from shell.py: a frilled teardrop with growth layers,
so it reads as an oyster first.

Each concept is a function (ns, split) -> SVG in a 0-100 box: ink is currentColor, the clasp is var(--clasp),
and split=True draws the halves apart (the story's split state, for motion). ns namespaces ids.
"""
import math
import numpy as np
import shell as S

f = lambda v: f'{v:.2f}'
PTS = lambda p: ' '.join(f'{f(x)},{f(y)}' for x, y in p)
FR, WV, SEED = 2.2, 9, 1.0
BOX = 'maskUnits="userSpaceOnUse" x="-20" y="-20" width="140" height="140"'
WHITE = '<rect x="-20" y="-20" width="140" height="140" fill="#fff"/>'

def valve(ns, tf=lambda p: p, layers=(.74, .5), cut=2.4, extra_cuts=''):
    """One frilled valve with its growth layers cut in, passed through a point transform tf."""
    o = tf(S.outline(FR, WV, SEED))
    ls = ''.join(f'<path d="{S.d(tf(S.layer(S.outline(FR * (.8 - .2 * i), WV, SEED + .5 + .5 * i), s)))}"/>' for i, s in enumerate(layers))
    return (f'<mask id="{ns}" {BOX}>{WHITE}<g fill="none" stroke="#000" stroke-width="{cut}" stroke-linejoin="round" stroke-linecap="round">{ls}{extra_cuts}</g></mask>'
            f'<path d="{S.d(o)}" mask="url(#{ns})"/>')

def gold_hinge(ns, split=False):
    """01. The ligament. The whole oyster, closed, from above; the ligament at the hinge, which is what opens
    and closes a real oyster, is the clasp, in gold. Split, the hinge lets go and the gold leaves."""
    lig = '' if split else '<path d="M36.5 13 C 40 9.5 48.5 9.5 52 13" fill="none" style="stroke:var(--clasp)" stroke-width="4.6" stroke-linecap="round"/>'
    tf = (lambda p: S.transform(p, 0, move=(0, 4))) if split else (lambda p: p)
    return valve(ns, tf) + lig

def butterfly(ns, split=False):
    """02. Two valves, one hinge. The oyster opened and laid flat, as on a plate: two valves, mirror images,
    joined at their hinges by the gold ligament. The deeper valve is a little larger, as in a real oyster."""
    gap = 6 if split else 0
    def tf(rot, mirror, sc, dx):
        return lambda p: S.transform(S.transform(p, 0, scale=(mirror * sc, sc)), rot, move=(50 - S.UMBO[0] + dx, 24 - S.UMBO[1]))
    left = valve(ns + 'a', tf(50, 1, .66, -1.5 - gap), cut=3.4)
    right = valve(ns + 'b', tf(-50, -1, .6, 1.5 + gap), cut=3.6)
    lig = '' if split else '<rect x="44.5" y="18.5" width="11" height="8" rx="4" style="fill:var(--clasp)"/>'
    return left + right + lig

def chain_seam(ns, split=False):
    """03. The seam is the linker. The oyster from above, split from hinge to lip, and the seam is drawn as a
    chain in a chemist's skeletal formula, a zigzag, with its middle bond in gold: the clasp. The growth
    layers run straight across, so it is plainly one shell in two halves."""
    n, amp = 4, 6.5
    a, b = np.array([44.0, 4]), np.array([50.0, 97])
    pts = [a + (b - a) * k / n + (np.array([amp if k % 2 else -amp, 0]) if 0 < k < n else 0) for k in range(n + 1)]
    seam = [a + [0, -8]] + pts + [b + [0, 8]]
    dx = 4 if split else 0
    left_poly = PTS(seam + [(-20, 120), (-20, -20)]); right_poly = PTS(seam + [(120, 120), (120, -20)])
    cut = f'<polyline points="{PTS(seam)}" fill="none" stroke="#000" stroke-width="3.6" stroke-linejoin="miter" stroke-miterlimit="8"/>'
    body = valve(ns + 'v', extra_cuts=cut)
    p, q = pts[2], pts[3]
    clasp = '' if split else f'<line x1="{f(p[0])}" y1="{f(p[1])}" x2="{f(q[0])}" y2="{f(q[1])}" style="stroke:var(--clasp)" stroke-width="4" stroke-linecap="round"/>'
    return (f'<clipPath id="{ns}l"><polygon points="{left_poly}"/></clipPath><clipPath id="{ns}r"><polygon points="{right_poly}"/></clipPath>'
            f'<g clip-path="url(#{ns}l)" transform="translate({-dx} 0)">{body}</g>'
            f'<g clip-path="url(#{ns}r)" transform="translate({dx} 0)">{body.replace(f"id=\"{ns}v\"", f"id=\"{ns}w\"").replace(f"url(#{ns}v)", f"url(#{ns}w)")}</g>' + clasp)

def side_lip(ns, split=False):
    """04. The lip is the linker, side on. A closed oyster seen from the side: a flat, layered upper valve on a
    deep cupped lower valve. Its lip, the line where they meet, is a zigzag chain with a gold middle bond."""
    base = np.concatenate([S._bez(*map(np.array, c)) for c in [
        ((6, 50), (16, 34), (42, 27), (68, 28)), ((68, 28), (86, 29), (96, 38), (95, 48)),
        ((95, 48), (94, 66), (72, 82), (46, 81)), ((46, 81), (24, 80), (10, 66), (6, 50))]])
    o = S.outline(1.6, 13, 2.0, base=base)
    n, amp = 6, 4.5
    pts = [np.array([6 + 89 * k / n, 50 - 2 * k / n + ((amp if k % 2 else -amp) if 0 < k < n else 0)]) for k in range(n + 1)]
    seam = [np.array([-10, 50])] + pts + [np.array([110, 48])]
    up = PTS(seam + [(120, -20), (-20, -20)]); lo = PTS(seam + [(120, 120), (-20, 120)])
    # growth layers on the upper valve: its edge stepped back toward the hinge
    lam = ''.join(f'<path d="{S.d(S.layer(o, s, toward=(4, 46)), close=False)}"/>' for s in (.8, .6))
    dy = 5 if split else 0
    m = (f'<mask id="{ns}m" {BOX}>{WHITE}<g fill="none" stroke="#000" stroke-width="3.6" stroke-linejoin="miter" stroke-miterlimit="8">'
         f'<polyline points="{PTS(seam)}"/></g><g clip-path="url(#{ns}u)" fill="none" stroke="#000" stroke-width="2.2">{lam}</g></mask>')
    p, q = pts[3], pts[4]
    clasp = '' if split else f'<line x1="{f(p[0])}" y1="{f(p[1])}" x2="{f(q[0])}" y2="{f(q[1])}" style="stroke:var(--clasp)" stroke-width="4" stroke-linecap="round"/>'
    return (f'<clipPath id="{ns}u"><polygon points="{up}"/></clipPath><clipPath id="{ns}l"><polygon points="{lo}"/></clipPath>{m}'
            f'<g mask="url(#{ns}m)"><path d="{S.d(o)}" clip-path="url(#{ns}u)" transform="translate(0 {-dy})"/>'
            f'<path d="{S.d(o)}" clip-path="url(#{ns}l)" transform="translate(0 {dy})"/></g>' + clasp)

def nested(ns, split=False):
    """05. Lid and cup. The flat upper valve lies on the cupped lower valve, a turn out of line, so the lower
    valve's frilled edge shows round it: two halves stacked into one oyster. They meet only at the hinge,
    in gold."""
    rot = 16 if split else 9
    lower = valve(ns + 'a', layers=(.6,))
    lid_o = S.transform(S.outline(FR, WV, SEED), rot, scale=(.72, .74), move=(3, 6))
    halo = f'<path d="{S.d(lid_o)}" fill="#000" stroke="#000" stroke-width="7"/>'
    lower = lower.replace('<g fill="none"', f'{halo}<g fill="none"', 1)
    lid = valve(ns + 'b', lambda p: S.transform(p, rot, scale=(.72, .74), move=(3, 6)), layers=(.6,))
    lig = '' if split else '<path d="M37 12 C 40 8.5 48 8.5 51 12" fill="none" style="stroke:var(--clasp)" stroke-width="4.6" stroke-linecap="round"/>'
    return lower + lid + lig

def kintsugi(ns, split=False):
    """06. Kintsugi. The Japanese craft of joining broken pieces with gold. The oyster from above in two halves,
    the whole seam between them a line of gold: halves rejoined, stronger and more beautiful for it. The
    seam keeps the chain's zigzag, so a chemist still sees the linker."""
    n, amp = 4, 6.5
    a, b = np.array([44.0, 4]), np.array([50.0, 97])
    pts = [a + (b - a) * k / n + (np.array([amp if k % 2 else -amp, 0]) if 0 < k < n else 0) for k in range(n + 1)]
    out = chain_seam(ns, split)
    if split: return out
    # keep the cut halves, replace the single gold bond with a gold line along the whole seam inside the shell
    out = out[:out.rindex('<line')]
    o = S.outline(FR, WV, SEED)
    return (out + f'<clipPath id="{ns}k"><path d="{S.d(o)}"/></clipPath>'
            f'<polyline points="{PTS(pts)}" fill="none" clip-path="url(#{ns}k)" style="stroke:var(--clasp)" stroke-width="2.4" stroke-linejoin="miter" stroke-miterlimit="8"/>')

def side_ajar(ns, split=False):
    """07. Ajar. The side-on oyster of 04, its lid lifted a little about the hinge: the zigzag lips part, and the
    ligament at the hinge, which springs the shell open and closed, is gold. Built to move: it opens and
    closes like the SELFTAC it stands for."""
    base = np.concatenate([S._bez(*map(np.array, c)) for c in [
        ((6, 54), (16, 38), (42, 31), (68, 32)), ((68, 32), (86, 33), (96, 42), (95, 52)),
        ((95, 52), (94, 70), (72, 86), (46, 85)), ((46, 85), (24, 84), (10, 70), (6, 54))]])
    o = S.outline(1.6, 13, 2.0, base=base)
    n, amp = 6, 4.5
    pts = [np.array([6 + 89 * k / n, 54 - 2 * k / n + ((amp if k % 2 else -amp) if 0 < k < n else 0)]) for k in range(n + 1)]
    seam = [np.array([-10, 54])] + pts + [np.array([110, 52])]
    up = PTS(seam + [(120, -20), (-20, -20)]); lo = PTS(seam + [(120, 120), (-20, 120)])
    lam = ''.join(f'<path d="{S.d(S.layer(o, s, toward=(4, 50)), close=False)}"/>' for s in (.8, .6))
    ang = -24 if split else -13
    m = (f'<mask id="{ns}m" {BOX}>{WHITE}<g clip-path="url(#{ns}u)" fill="none" stroke="#000" stroke-width="2.2">{lam}</g></mask>')
    lig = '' if split else '<path d="M2 50.5 C 2 45 9 44 11 49 L 11 58 C 9 62 2 61 2 56 Z" style="fill:var(--clasp)"/>'
    return (f'<clipPath id="{ns}u"><polygon points="{up}"/></clipPath><clipPath id="{ns}l"><polygon points="{lo}"/></clipPath>{m}'
            f'<g transform="translate(0 -4)"><g transform="rotate({ang} 8 54)"><path d="{S.d(o)}" clip-path="url(#{ns}u)" mask="url(#{ns}m)"/></g>'
            f'<path d="{S.d(o)}" clip-path="url(#{ns}l)"/></g>' + lig.replace('<path ', '<path transform="translate(0 -4)" '))

CONCEPTS = [
    ('hinge', '01', 'The ligament', gold_hinge,
     'The whole oyster, closed, from above. Its ligament, the joint at the hinge that opens and closes a real oyster, is the clasp, in gold.',
     'The least added: one gold detail, at the one place an oyster actually clasps. It reads as an oyster first at any size.'),
    ('butterfly', '02', 'Two valves, one hinge', butterfly,
     'The oyster opened and laid flat, as on a plate: two valves, near mirror images, joined at the hinge by the gold ligament.',
     'The SELFTAC idea at a glance, two halves held by one clasp, and still unmistakably shellfish.'),
    ('chain', '03', 'The seam is the linker', chain_seam,
     'The oyster from above, split from hinge to lip. The seam is a zigzag, a chain in a chemist&rsquo;s skeletal formula, with its middle bond in gold.',
     'A biologist sees an oyster; a chemist sees a linker. The growth layers run across both halves, so it stays one shell.'),
    ('side', '04', 'The lip is the linker', side_lip,
     'A closed oyster from the side, a flat layered lid on a deep cup. The lip where the valves meet is the zigzag chain, with a gold middle bond.',
     'The oyster&rsquo;s real profile; the zigzag lip is true to life, and chemists read it as a chain.'),
    ('kintsugi', '05', 'Kintsugi', kintsugi,
     'Kintsugi is the Japanese craft of rejoining broken pieces with gold. The oyster in two halves, the whole seam between them a line of gold.',
     'Halves rejoined, and better for it: a story people already know. The seam keeps the chain&rsquo;s zigzag, so it is still a linker.'),
    ('ajar', '06', 'Ajar', side_ajar,
     'The side-on oyster of 04 with its lid lifted about the hinge: the zigzag lips part, and the ligament that springs the shell open and shut is gold.',
     'Built to move: in the intro it opens and clasps shut, as a SELFTAC does. Closed, it becomes 04.'),
]
