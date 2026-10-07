"""The wordmark's s redrawn as a degrader: two ends (the ligands) joined through the spine (the linker),
with the SELFTAC clasp where the halves meet. Each variant returns SVG in glyph units (y up), to be
placed with the s's own transform. Ink is currentColor; the clasp is var(--clasp); linker pearls are
var(--bead) on a var(--strand) strand. Masks take a namespace so a page can hold many copies.
"""
import math
import numpy as np
from sgeom import s_path, spine, seg_dist

D = s_path()

def _resample(c, w, step=4.0):
    k = 7; pad = lambda a: np.concatenate([a[:1].repeat(k // 2, 0), a, a[-1:].repeat(k // 2, 0)])
    ker = np.ones(k) / k
    c = np.stack([np.convolve(pad(c[:, i]), ker, 'valid') for i in range(2)], 1)
    w = np.convolve(pad(w), ker, 'valid')
    s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(c, axis=0), axis=1))]
    t = np.arange(0, s[-1], step)
    return np.stack([np.interp(t, s, c[:, 0]), np.interp(t, s, c[:, 1])], 1), np.interp(t, s, w), t

C, W, S = _resample(*spine())
L = S[-1]

def at(s):
    """Point, unit tangent, normal and half-width at arc length s (straight on past either end)."""
    sc = min(max(s, 0), L - 1e-6); i = min(int(sc / 4.0), len(C) - 2); f = sc / 4.0 - i
    p = C[i] * (1 - f) + C[i + 1] * f; t = C[i + 1] - C[i]; t = t / np.linalg.norm(t)
    return p + t * (s - sc), t, np.array([-t[1], t[0]]), W[i] * (1 - f) + W[i + 1] * f

# The spine's middle: where the centreline passes closest to the middle of the letter.
S_MID = float(S[np.argmin(np.linalg.norm(C - np.array([460, 535]), axis=1))])
W_MID = at(S_MID)[3]
# Shoulders where the serifs begin (found from the traced centreline; see the sheet's construction view).
S_TOP = float(S[np.argmin(np.linalg.norm(C - np.array([668, 975]), axis=1))])
S_BOT = float(S[np.argmin(np.linalg.norm(C - np.array([170, 75]), axis=1))])

f = lambda v: f'{v:.1f}'
pts = lambda a: ' '.join(f'{f(x)},{f(y)}' for x, y in a)

def band(s0, s1, extra=1.7, half=None):
    """A polygon covering the stroke between arc lengths s0 and s1, cut square to the centreline
    (half-width: extra times the stroke's, or a fixed half in glyph units)."""
    ss = np.linspace(s0, s1, max(2, int(abs(s1 - s0) / 8)))
    hw = lambda s: half if half else at(s)[3] * extra
    left = [at(s)[0] + at(s)[2] * hw(s) for s in ss]
    right = [at(s)[0] - at(s)[2] * hw(s) for s in ss]
    return f'<polygon points="{pts(left + right[::-1])}"/>'

def glyph(ns, cuts=(), halos=()):
    """The s outline with bands cut out and circular halos knocked out (masks in glyph units)."""
    if not cuts and not halos:
        return f'<path d="{D}"/>'
    holes = ''.join(cuts) + ''.join(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}"/>' for x, y, r in halos)
    return (f'<mask id="{ns}" maskUnits="userSpaceOnUse" x="-200" y="-200" width="1400" height="1500">'
            f'<rect x="-200" y="-200" width="1400" height="1500" fill="#fff"/><g fill="#000">{holes}</g></mask>'
            f'<path d="{D}" mask="url(#{ns})"/>')

def clasp(s, gap, r, bond):
    """Two clasp pearls a gap apart along the centreline, joined by a bond."""
    a = at(s - gap / 2)[0]; b = at(s + gap / 2)[0]
    return (f'<g style="fill:var(--clasp);stroke:var(--clasp)"><line x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}" '
            f'stroke-width="{f(bond)}" stroke-linecap="round"/><circle cx="{f(a[0])}" cy="{f(a[1])}" r="{f(r)}" stroke="none"/>'
            f'<circle cx="{f(b[0])}" cy="{f(b[1])}" r="{f(r)}" stroke="none"/></g>')

def strand(s0, s1, r, width, clear):
    """Linker pearls on a strand along the centreline from s0 to s1 (the cut ends), packed evenly on each
    side of the middle and stopping short of the clasp (clear: distance kept free either side of S_MID).
    The strand runs a little into both cut ends so it is bonded to the letter."""
    line = pts([at(s)[0] for s in np.linspace(s0 - 40, s1 + 40, 60)])
    beads = ''
    for a, b in ((s0 + r * .9, S_MID - clear), (S_MID + clear, s1 - r * .9)):
        n = max(1, int((b - a) / (2.5 * r)) + 1)
        for k in range(n):
            p = at(a + (b - a) * (k / (n - 1) if n > 1 else .5))[0]
            beads += f'<circle cx="{f(p[0])}" cy="{f(p[1])}" r="{f(r)}"/>'
    return (f'<polyline points="{line}" fill="none" style="stroke:var(--strand)" stroke-width="{f(width)}" stroke-linecap="round"/>'
            f'<g style="fill:var(--bead);stroke:var(--strand)" stroke-width="{f(width * .7)}">{beads}</g>')

def ring(s_cut, toward, R, width):
    """An open hexagonal ring (a ligand's ring, drawn as a tube) hung off the stroke where it is cut.
    toward=-1 puts it on the serif side of a cut near the start, +1 near the end."""
    p, t, n, _ = at(s_cut); c = at(s_cut + toward * R * .95)[0]
    a0 = math.atan2(p[1] - c[1], p[0] - c[0])
    hexa = [(c[0] + R * math.cos(a0 + k * math.pi / 3), c[1] + R * math.sin(a0 + k * math.pi / 3)) for k in range(6)]
    return (f'<polygon points="{pts(hexa)}" fill="none" stroke="currentColor" stroke-width="{f(width)}" stroke-linejoin="round"/>')

def serif_cuts():
    """Bands removing both serifs beyond the shoulders."""
    return [band(-120, S_TOP, half=170), band(S_BOT, L + 120, half=170)]

def v_current(ns):
    return glyph(ns)

def v_inset(ns):
    r = .42 * W_MID; gap = 1.25 * W_MID
    a = at(S_MID - gap / 2)[0]; b = at(S_MID + gap / 2)[0]
    return glyph(ns, halos=[(a[0], a[1], r + .16 * W_MID), (b[0], b[1], r + .16 * W_MID)]) + clasp(S_MID, gap, r, .36 * W_MID)

def v_gap(ns):
    g = 1.25 * W_MID
    return glyph(ns, cuts=[band(S_MID - g / 2, S_MID + g / 2)]) + clasp(S_MID, g, .5 * W_MID, .36 * W_MID)

def linker(ns, half, cuts=()):
    s0, s1 = S_MID - half, S_MID + half; r = .3 * W_MID; g = 1.1 * W_MID; rc = .46 * W_MID
    return (glyph(ns, cuts=list(cuts) + [band(s0, s1)]) + strand(s0, s1, r, .12 * W_MID, g / 2 + rc + .25 * r + r)
            + clasp(S_MID, g, rc, .34 * W_MID))

def v_linker(ns, half=190):
    return linker(ns, half)

RING_R, RING_W = 100, 44

def rings():
    return ring(S_TOP, -1, RING_R, RING_W) + ring(S_BOT, 1, RING_R, RING_W)

def v_rings(ns):
    g = 1.25 * W_MID
    return (glyph(ns, cuts=serif_cuts() + [band(S_MID - g / 2, S_MID + g / 2)]) + rings()
            + clasp(S_MID, g, .5 * W_MID, .36 * W_MID))

def v_full(ns, half=190):
    return linker(ns, half, serif_cuts()) + rings()

def v_mono(ns, width=104, half=150):
    s0, s1 = S_MID - half, S_MID + half; r = .34 * width; g = 1.1 * width; rc = .44 * width
    seg = lambda a, b: f'<polyline points="{pts([at(s)[0] for s in np.linspace(a, b, 120)])}" fill="none" stroke="currentColor" stroke-width="{width}" stroke-linecap="butt" stroke-linejoin="round"/>'
    return (seg(S_TOP, s0) + seg(s1, S_BOT) + ring(S_TOP, -1, RING_R, RING_W) + ring(S_BOT, 1, RING_R, RING_W)
            + strand(s0, s1, r, .12 * width, g / 2 + rc + 1.25 * r) + clasp(S_MID, g, rc, .32 * width))

VARIANTS = [  # number, name, idea, function
    ('00', 'Current', 'The Newsreader s as it is today, for comparison.', v_current),
    ('01', 'Inset clasp', 'The letter untouched; the gold clasp sits in the spine, where the two halves of a SELFTAC meet.', v_inset),
    ('02', 'Clasp gap', 'The spine is cut square and the halves are held by the clasp: each half keeps its pearl, as in the story.', v_gap),
    ('03', 'Pearl linker', 'The ends stay as letter (the two ligands); the spine becomes the linker, a strand of pearls with the clasp at its middle.', v_linker),
    ('04', 'Ring ends', 'The serifs become open rings, the generic ligand rings of the 3D story, with the clasp in the spine.', v_rings),
    ('05', 'Full degrader', 'Ring ends and the pearl linker together: ligand, linker, clasp, linker, ligand, still read as an s.', v_full),
    ('06', 'Monoline', 'The s redrawn as one even tube, like the story&rsquo;s degrader, with ring ends and a pearl linker. Furthest from the type.', v_mono),
]
