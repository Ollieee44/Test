"""Build brand/brainstorm.html, "Oyster Mark Brainstorm": new brandmark concepts (concepts.py) that tell the
SELFTAC story with the oyster's own anatomy. Each shown clasped and split in Nacre and Tidepool, at small
sizes, and locked up with the logotype in place of the current mark. Usage: python3 build_brainstorm.py"""
import os, re
import numpy as np
import sys, importlib
C = importlib.import_module(sys.argv[1] if len(sys.argv) > 1 else "concepts")
ROUND3 = C.__name__ == "geo"; ROUND4 = C.__name__ == "selftac_o"; ROUND5 = C.__name__ == "bifunctional"; ROUND6 = C.__name__ == "lidcup"; ROUND7 = C.__name__ == "proteins"; ROUND8 = C.__name__ == "docked"; ROUND9 = C.__name__ == "textured"; ROUND10 = C.__name__ == "rounded"; ROUND11 = C.__name__ == "roundpair"; ROUND12 = C.__name__ == "twoproteins"; ROUND13 = C.__name__ == "blobby"; ROUND14 = C.__name__ == "filled"; ROUND15 = C.__name__ == "wavy"; ROUND16 = C.__name__ == "undulate"; ROUND17 = C.__name__ == "nacre"
D = os.path.dirname(os.path.abspath(__file__)) + '/'
SITE = D + '../../intro/fan-site.html'
PAL = {'nacre': 'color:#2B2230;background:#EFE6E1;--clasp:#D9A443;--pearl:#C99BB0;--brd4:#E7C9D6;--vhl:#D6CBE6;--ring:#8C5572;--outline:#2B2230',
       'tidepool': 'color:#EAF3EF;background:#0F4C4A;--clasp:#F27D62;--pearl:#F2B84B;--brd4:#F5D89A;--vhl:#9FD6C6;--ring:#06302E;--outline:#06302E'}
LT = re.search(r'<svg class="lt"[^>]*>.*?</svg>', open(SITE).read(), re.S).group(0)
HEAD = '<g transform="translate(-17.1 -583.4) scale(6.3571)">'

def mark(fn, ns, split=False, size=None, cls='mk'):
    sz = f' width="{size}" height="{size}"' if size else ''
    return f'<svg class="{cls}" viewBox="0 0 100 100"{sz} aria-hidden="true"><g fill="currentColor">{fn(ns, split)}</g></svg>'

def _bounds(d):
    """Ink bounds (x0, y0, x1, y1) of a glyph path in its own units, y up."""
    import sys; sys.path.insert(0, D + '../sdeg'); import sgeom
    p = sgeom.polygon(d, 12); return (*p.min(0), *p.max(0))

def _letter_ink(d, x):
    """A logotype letter's outline in page units (y down), densified, from its path and x offset."""
    import sys; sys.path.insert(0, D + '../sdeg'); import sgeom
    out = []
    for c in re.findall(r'M[^M]*', d):
        q = sgeom.polygon(c, 12); q = np.vstack([q, q[:1]])
        for a, b in zip(q[:-1], q[1:]):
            n = max(1, int(np.linalg.norm(b - a) / 1.0)); out.append(a + (b - a) * np.arange(n)[:, None] / n)
    p = np.vstack(out); return np.stack([x + .5 * p[:, 0], -.5 * p[:, 1]], 1)

def _ink_from_svg(svg):
    """Every drawn point of a mark: path (M/L), polygon and polyline vertices and circle edges, densified,
    ignoring masks, clip paths and defs (they shape the ink but are not ink)."""
    svg = re.sub(r'<(mask|clipPath|defs)\b.*?</\1>', '', svg, flags=re.S); out = []
    for d in re.findall(r'<path[^>]* d="([^"]+)"', svg):
        # walk the commands so arc parameters (radii, flags) are not mistaken for points: M/L give points, A gives its end point
        pts, cur = [], None
        for cmd, args in re.findall(r'([MLAZ])([^MLAZ]*)', d):
            v = [float(x) for x in re.findall(r'-?\d+\.?\d*', args)]
            if cmd in 'ML':
                for i in range(0, len(v) - 1, 2): pts.append((v[i], v[i + 1]))
            elif cmd == 'A':
                for i in range(0, len(v) - 6, 7): pts.append((v[i + 5], v[i + 6]))
            elif cmd == 'Z' and pts:
                out.append(np.array(pts)); pts = []
        if len(pts) > 1: out.append(np.array(pts))
    for q in re.findall(r'points="([^"]+)"', svg):
        out.append(np.array([[float(a) for a in p.split(',')] for p in q.split()]))
    for cx, cy, r in re.findall(r'<circle cx="([-\d.]+)" cy="([-\d.]+)" r="([-\d.]+)"', svg):
        t = np.linspace(0, 2 * np.pi, 48); out.append(np.stack([float(cx) + float(r) * np.cos(t), float(cy) + float(r) * np.sin(t)], 1))
    dense = []
    for q in out:
        for a, b in zip(q[:-1], q[1:]):
            n = max(1, int(np.linalg.norm(b - a) / .5)); dense.append(a + (b - a) * np.arange(n)[:, None] / n)
    return np.vstack(dense)

def _gap(A, B):
    return min(np.sqrt(((A[i:i + 1500, None] - B[None]) ** 2).sum(-1)).min() for i in range(0, len(A), 1500))

def lockup_xheight(fn, ns):
    """The logotype with the mark's shell (lid, pearl and cup) set exactly at the letters' x-height, from the
    baseline to the top of the e. Its spacing is set per mark: moved until the closest distance from any of
    its ink (shell, bonds, ligand rings) to the y equals the closest distance from the y to the s, so the
    mark sits as tight to the y as the s does. The viewBox grows to take the ligands."""
    if C.__name__ == 'lidcup':
        import lidcup
        body, (sx0, sy0, sx1, sy1), (ax0, ay0, ax1, ay1), ink = lidcup.lid_cup(ns + 'k', False, raw=True, **fn.kw)
    else:   # the whole mark is the shell: measure its drawn ink
        body = fn(ns + 'k', False); ink = _ink_from_svg(body)
        sx0, sy0 = ink.min(0); sx1, sy1 = ink.max(0); ax0, ay0, ax1, ay1 = sx0, sy0, sx1, sy1
    P = dict((x, d) for d, x in re.findall(r'<path d="([^"]*)" transform="translate\(([\d.]+) 0\.0\) scale\(0\.5000 -0\.5000\)"/>', LT))
    e = _bounds(P['1596.9'])
    top, bot = -.5 * e[3], -.5 * e[1]                    # the e's top and bottom (overshoots included), page units
    k = (bot - top) / (sy1 - sy0); ty = top - k * sy0
    y_ink, s_ink = _letter_ink(P['488.1'], 488.1), _letter_ink(P['949.8'], 949.8)
    target = _gap(y_ink, s_ink) + k * 1.4               # the y-s gap, plus half the mark's stroke
    m = ink * k + [0, ty]
    lo_, hi_ = 488.1 - 900.0, 488.1 + 200.0             # tx: far left (too loose) .. overlapping
    for _ in range(28):
        mid = (lo_ + hi_) / 2
        if _gap(m + [mid, 0], y_ink) > target: lo_ = mid
        else: hi_ = mid
    tx = lo_
    print(f'{ns}: gap to y {_gap(m + [tx, 0], y_ink) - k * 1.4:.1f} (y-s {target - k * 1.4:.1f})')
    i = LT.index(HEAD); j = LT.rfind('</g><path d=', 0, LT.index('transform="translate(488.1 0.0)')) + 4
    s = LT[:i] + f'<g transform="translate({tx:.1f} {ty:.1f}) scale({k:.4f})">{body}</g>' + LT[j:]
    vx, vy, vw, vh = map(float, re.search(r'viewBox="([^"]+)"', LT).group(1).split())
    nx0 = min(vx, k * ax0 + tx - 40); ny0 = min(vy, k * ay0 + ty - 40); ny1 = max(vy + vh, k * ay1 + ty + 40)
    s = s.replace(f'viewBox="{vx} {vy} {vw} {vh}"', f'viewBox="{nx0:.1f} {ny0:.1f} {vx + vw - nx0:.1f} {ny1 - ny0:.1f}"', 1)
    for q in set(re.findall(r'id="([^"]+)"', s)):
        s = s.replace(f'id="{q}"', f'id="{ns}{q}"').replace(f'url(#{q})', f'url(#{ns}{q})')
    return re.sub(r'<svg class="lt"[^>]*?(viewBox="[^"]+")[^>]*>', r'<svg class="lt" \1 aria-hidden="true">', s, count=1)

def lockup(fn, ns):
    """The logotype with the concept in the mark's box (the same box the current mark uses)."""
    i = LT.index(HEAD) + len(HEAD); j = LT.rfind('</g><path d=', 0, LT.index('transform="translate(488.1 0.0)'))
    s = LT[:i] + fn(ns + 'k', False) + LT[j:]
    for k in set(re.findall(r'id="([^"]+)"', LT)):
        s = s.replace(f'id="{k}"', f'id="{ns}{k}"').replace(f'url(#{k})', f'url(#{ns}{k})')
    return re.sub(r'<svg class="lt"[^>]*?(viewBox="[^"]+")[^>]*>', r'<svg class="lt" \1 aria-hidden="true">', s, count=1)

cards = ''
for key, num, name, fn, idea, why in C.CONCEPTS:
    states = ''
    for split, lab in ((False, 'Clasped'), (True, 'Split')):
        tiles = ''.join(f'<div class="tile sq" style="{st}" title="{p.title()}, {lab.lower()}">{mark(fn, f"{key}{p[0]}{int(split)}", split)}</div>' for p, st in PAL.items())
        states += f'<div class="state"><span class="lab">{lab}</span><div class="row">{tiles}</div></div>'
    small = ''.join(f'<div class="tile sm" style="{st}">' + ''.join(mark(fn, f'{key}{p[0]}s{px}', size=px, cls='px') for px in (16, 24, 32, 48)) + '</div>' for p, st in PAL.items())
    lk = lockup_xheight if hasattr(fn, 'kw') else lockup
    lock = ''.join(f'<div class="tile wide" style="{st}">{lk(fn, f"{key}{p[0]}L")}</div>' for p, st in PAL.items())
    cards += (f'<article class="card" id="c{num}"><header><b>{num}</b><h2>{name}</h2></header><p>{idea}</p>{f'<p class="why">{why}</p>' if why else ''}'
              f'<div class="states">{states}</div><span class="lab">16, 24, 32 and 48px</span><div class="row">{small}</div>'
              f'<span class="lab">{'With the logotype, the shell at the letters&rsquo; x-height' if hasattr(fn, 'kw') else 'With the logotype'}</span><div class="row">{lock}</div></article>')

OUT = 'nacre.html' if ROUND17 else 'undulate.html' if ROUND16 else 'wavy.html' if ROUND15 else 'filled.html' if ROUND14 else 'blobby.html' if ROUND13 else 'twoproteins.html' if ROUND12 else 'roundpair.html' if ROUND11 else 'rounded.html' if ROUND10 else 'textured.html' if ROUND9 else 'docked.html' if ROUND8 else 'proteins.html' if ROUND7 else 'lidcup.html' if ROUND6 else 'bifunctional.html' if ROUND5 else 'selftac-o.html' if ROUND4 else 'construct.html' if ROUND3 else 'brainstorm.html'
if ROUND17:
    import undulate as R16
    TITLE, EYEBROW, H1 = 'Oyster Nacre Proteins', 'brandmark brainstorm, round seventeen', 'Textures, and mother-of-pearl'
    LEDE = ('<p class="lede"><b>Round sixteen&rsquo;s 02, four broad waves, two ways.</b> First with the textures and shading from earlier rounds, in '
            'the 3D story&rsquo;s colours: contour rings, toon shading, a soft gradient, the model look, and the lumpy illustrated style. Then as '
            'mother-of-pearl: the proteins in iridescent nacre, with colour bands, a fibrous sheen, a highlight and shade, and the pearl drawn '
            'photographically, in colourways named after real pearls. Structures: PDB 5T35, Gadd et al., Nat. Chem. Biol. 2017; the degrader is drawn generically.</p>')
    REF = ('<div class="ref"><span class="lab">From round sixteen</span><div class="refrow">'
           f'<div class="tile" style="{PAL["nacre"]}">{mark(R16.CONCEPTS[1][3], "r16b")}</div><span>02 Four broad waves</span></div></div>')
elif ROUND16:
    import wavy as R15
    TITLE, EYEBROW, H1 = 'Oyster Big Waves', 'brandmark brainstorm, round sixteen', 'Fewer, bigger, deeper waves'
    LEDE = ('<p class="lede"><b>Round fifteen with a few big undulations instead of many small lobes.</b> Each protein&rsquo;s outer edge is bent '
            'into four to six smooth waves, as deep as you like; the waves fade out near the seam and the pearl, so the two proteins still fit each '
            'other at a hairline gap and the pearl sits in a clean pocket. Fill colours are the 3D story&rsquo;s. Structures: PDB 5T35, Gadd et '
            'al., Nat. Chem. Biol. 2017; the degrader is drawn generically.</p>')
    REF = ('<div class="ref"><span class="lab">From round fifteen</span><div class="refrow">'
           f'<div class="tile" style="{PAL["nacre"]}">{mark(R15.CONCEPTS[0][3], "r15w")}</div><span>01 Wavy</span></div></div>')
elif ROUND15:
    import filled as R14
    TITLE, EYEBROW, H1 = 'Oyster Wavy Proteins', 'brandmark brainstorm, round fifteen', 'Wavy, not jaggy'
    LEDE = ('<p class="lede"><b>Round fourteen with softer, wavier outlines, after the illustration you shared.</b> Instead of many fine bumps, each '
            'protein&rsquo;s edge has big, soft lobes with rounded dips between them. Some versions add soft lumps inside each protein, a shade '
            'lighter and darker, and an outline in a deeper shade of the protein&rsquo;s own colour, as in the reference. Fill colours are the 3D '
            'story&rsquo;s; the pearl and its linker are as before. Structures: PDB 5T35, Gadd et al., Nat. Chem. Biol. 2017; the degrader is drawn generically.</p>')
    REF = ('<div class="ref"><span class="lab">From round fourteen</span><div class="refrow">'
           f'<div class="tile" style="{PAL["nacre"]}">{mark(R14.CONCEPTS[0][3], "r14f")}</div><span>01 Flat fill</span></div></div>')
elif ROUND14:
    import blobby as R13
    TITLE, EYEBROW, H1 = 'Oyster Filled Proteins', 'brandmark brainstorm, round fourteen', 'Filled, like the 3D models'
    LEDE = ('<p class="lede"><b>Round thirteen&rsquo;s 01, filled in and given depth, in the language of the 3D story.</b> BRD4 and VHL take the '
            'story&rsquo;s protein colours (pink and lilac in Nacre, gold and mint in Tidepool) with its ink outline, and depth comes the way the '
            '3D models show it: contour rings at even depths, toon shading from a light at the top left, a soft gradient, or rings and shading '
            'together. The pearl and its linker are as before. Structures: PDB 5T35, Gadd et al., Nat. Chem. Biol. 2017; the degrader is drawn generically.</p>')
    REF = ('<div class="ref"><span class="lab">From round thirteen</span><div class="refrow">'
           f'<div class="tile" style="{PAL["nacre"]}">{mark(R13.CONCEPTS[0][3], "r13b")}</div><span>01 Blobby</span></div></div>')
elif ROUND13:
    import twoproteins as R12
    TITLE, EYEBROW, H1 = 'Oyster Blobby Proteins', 'brandmark brainstorm, round thirteen', 'Blobbier proteins'
    LEDE = ('<p class="lede"><b>Round twelve&rsquo;s 02, with blobbier proteins.</b> Each protein&rsquo;s own traced lobes are amplified, measured '
            'against its overall oval so only the local bulges grow, and clefts are pressed into its back; some get a wider domain at one end. '
            'They are then docked as before: each holds half the pearl, the facing sides fit at a hairline gap, and the surfaces are molecular. '
            'Structures: PDB 5T35, Gadd et al., Nat. Chem. Biol. 2017; the degrader is drawn generically.</p>')
    REF = ('<div class="ref"><span class="lab">From round twelve</span><div class="refrow">'
           f'<div class="tile" style="{PAL["nacre"]}">{mark(R12.CONCEPTS[1][3], "r12f")}</div><span>02 Flatter</span></div></div>')
elif ROUND12:
    TITLE, EYEBROW, H1, REF = 'Oyster Two Proteins', 'brandmark brainstorm, round twelve', 'Two proteins, one pearl', ''
    LEDE = ('<p class="lede"><b>Proteins first, the oyster only in the silhouette.</b> Round eleven had drifted back to a shell: a circle, with lines '
            'that read as growth rings. Here the circle and the shell lines are gone. BRD4 and VHL keep close to their real traced proportions and '
            'are drawn as molecular surfaces, the scalloped edge of a space-filling model. Each is placed to hold half of the pearl, and the two are '
            'docked along their whole facing side at a hairline gap, so the mouth is closed. Together they happen to make the rounded, lumpy shape '
            'of an oyster. The pearl is split along the seam and held by its linker. Structures: PDB 5T35, Gadd et al., Nat. Chem. Biol. 2017; '
            'the degrader is drawn generically.</p>')
elif ROUND11:
    import rounded as R10
    TITLE, EYEBROW, H1 = 'Oyster Round Pair', 'brandmark brainstorm, round eleven', 'One round form, two proteins'
    LEDE = ('<p class="lede"><b>The pair closed into a round form, with each half more clearly a protein.</b> The two halves now make one rounded '
            'shape, close to a circle, split by a gentle S-shaped seam through the pearl, so the gap that opened on the right is closed and the only '
            'opening is the hairline seam. Each half&rsquo;s outer edge carries the broad lobes of its own traced protein, BRD4 above and VHL below '
            '(PDB 5T35), so the two halves differ. Shading sits on the outer surface only; the pearl is split along the seam and held by its '
            'linker. The variations change how lumpy, the seam, and which view of the complex. Structures: PDB 5T35, Gadd et al., Nat. Chem. Biol. '
            '2017; the degrader is drawn generically.</p>')
    REF = ('<div class="ref"><span class="lab">From round ten</span><div class="refrow">'
           f'<div class="tile" style="{PAL["nacre"]}">{mark(R10.CONCEPTS[0][3], "r10m")}</div><span>01 Rounded, linker pearl</span></div></div>')
elif ROUND10:
    import textured as R9
    TITLE, EYEBROW, H1 = 'Oyster Rounded Shell', 'brandmark brainstorm, round ten', 'Rounded, with the linker pearl'
    LEDE = ('<p class="lede"><b>Round nine&rsquo;s 02, with three changes.</b> The right side is rounded off (smoothed more the further right, then '
            're-fitted so the gap between the proteins stays even). The pearl is turned so it splits along the same line as the shell, one half '
            'by BRD4 and one by VHL. And the halves are held by a short, thick linker, cut out of the pearl as negative space. The variations '
            'try how round, and the linker&rsquo;s proportions. Structures: PDB 5T35, Gadd et al., Nat. Chem. Biol. 2017; the degrader is drawn generically.</p>')
    REF = ('<div class="ref"><span class="lab">From round nine</span><div class="refrow">'
           f'<div class="tile" style="{PAL["nacre"]}">{mark(R9.CONCEPTS[1][3], "r9s")}</div><span>02 Diagonal, shaded</span></div></div>')
elif ROUND9:
    import docked as R8
    TITLE, EYEBROW, H1 = 'Oyster Textured Shell', 'brandmark brainstorm, round nine', 'Diagonal, with depth'
    LEDE = ('<p class="lede"><b>Round eight&rsquo;s 04, turned and given depth.</b> The docked pair, BRD4 and VHL fitted to each other with a hairline '
            'gap and the SELFTAC pearl between them, is turned so the seam runs on a diagonal. Texture lines are back to make it more 3D: lines '
            'at an even depth inside each protein&rsquo;s edge (traced as true contours, so they never tangle), shading kept to the side away '
            'from the light, a highlight, or the real surface contours from the 5T35 trace. Structures: PDB 5T35, Gadd et al., Nat. Chem. Biol. '
            '2017; the degrader is drawn generically.</p>')
    REF = ('<div class="ref"><span class="lab">From round eight</span><div class="refrow">'
           f'<div class="tile" style="{PAL["nacre"]}">{mark(R8.CONCEPTS[3][3], "r8h")}</div><span>04 Hairline gap</span></div></div>')
elif ROUND8:
    import proteins as R7
    TITLE, EYEBROW, H1 = 'Oyster Docked Shell', 'brandmark brainstorm, round eight', 'Docked'
    LEDE = ('<p class="lede"><b>Round seven&rsquo;s 02, with the proteins brought together.</b> BRD4 (the lid) and VHL (the cup) now fit each other: '
            'their facing surfaces are reshaped to follow one another an even gap apart, as docked proteins do, with the same gap round the pearl. '
            'Their backs keep the shapes traced from PDB 5T35, so they still read as protein outlines. The variations change how far they dock, '
            'the gap, the view and the mouth. Structures: PDB 5T35, Gadd et al., Nat. Chem. Biol. 2017; the degrader is drawn generically.</p>')
    REF = ('<div class="ref"><span class="lab">From round seven</span><div class="refrow">'
           f'<div class="tile" style="{PAL["nacre"]}">{mark(R7.CONCEPTS[1][3], "r7p")}</div><span>02 Pure outline</span></div></div>')
elif ROUND7:
    TITLE, EYEBROW, H1, REF = 'Oyster Protein Shell', 'brandmark brainstorm, round seven', 'The shell is the complex', ''
    LEDE = ('<p class="lede"><b>Each half of the oyster is a protein from PDB 5T35, and the pearl is the SELFTAC.</b> BRD4, the target, is the lid; '
            'VHL, the ligase, is the cup. Their outlines are traced from the structure and smoothed into blobs, and where they meet the pearl '
            'they curve round it, so the two proteins cup the degrader between them, as they do in the real ternary complex. The surface '
            'contours inside each protein double as an oyster&rsquo;s growth lines. One line weight throughout; the pearl in the logo&rsquo;s '
            'pearl colour, the clasp in gold. Structures: PDB 5T35, Gadd et al., Nat. Chem. Biol. 2017; the degrader is drawn generically.</p>')
elif ROUND6:
    TITLE, EYEBROW, H1, REF = 'Oyster Lid and Cup', 'brandmark brainstorm, round six', 'Variations on Lid and cup', ''
    LEDE = ('<p class="lede"><b>Round five&rsquo;s 02, pushed in nine directions.</b> The idea stays the same: a heterobifunctional degrader whose '
            'linker runs through an oyster, a flat lid over a deep cup, with the pearl between them as the reversible clasp. Each variation '
            'changes one or two things: the angle the molecule runs at, where the ligands leave the shell, how far the lid is open, the '
            'linker&rsquo;s form, the pearl&rsquo;s size, the shell&rsquo;s texture and the pearl&rsquo;s colour. 02 itself is first, for reference.</p>')
elif ROUND5:
    TITLE, EYEBROW, H1, REF = 'Oyster Bifunctional', 'brandmark brainstorm, round five', 'The mark is the molecule', ''
    LEDE = ('<p class="lede"><b>Your brief: a stylised bifunctional with the halves of an oyster in the middle of the linker, and the pearl as '
            'the secret sauce.</b> So each mark is a degrader: a different ligand at each end (a heterobifunctional&rsquo;s ends differ; both '
            'are invented ring systems, per the generic-degrader rule), the linker between them, and at its middle the two valves of an oyster '
            'with the pearl cupped between them as the reversible clasp. Split, the valves part and the pearl parts with them, each valve '
            'keeping half. The valves round the pearl make a loose O. The pearl is in the logo&rsquo;s pearl colour.</p>')
elif ROUND4:
    import geo as R3
    TITLE, EYEBROW, H1 = 'Oyster SELFTAC O', 'brandmark brainstorm, round four', 'The SELFTAC, curled into an O'
    LEDE = ('<p class="lede"><b>Another approach: start from the molecule, not the shell.</b> A SELFTAC is two halves, each a ligand on a linker, '
            'joined by the clasp. Curl it into an O and shape the O as an oyster side on: the hinge on the left, where the two halves meet in the '
            'gold clasp; the mouth on the right, where each half ends in its ligand, drawn as a generic open ring. The trick that makes it an oyster '
            'is a serif o&rsquo;s own contrast: a thin top and a heavy bottom are a flat lid on a deep cup, and a faint frill on the outside edge '
            'makes it shell. Thin, even-weight versions read as a bracelet or a horseshoe, so the bold O leads.</p>')
    REF = ('<div class="ref"><span class="lab">Kept from round three</span><div class="refrow">'
           f'<div class="tile" style="{PAL["nacre"]}">{mark(R3.growth, "r3g")}</div><span>01 Growth rings: the gold hinge</span></div></div>')
elif ROUND3:
    import concepts as R2
    TITLE, EYEBROW, H1 = 'Oyster Mark Constructions', 'brandmark brainstorm, round three', 'Built, not drawn'
    LEDE = ('<p class="lede"><b>A different approach: construction instead of illustration.</b> Round two drew the oyster&rsquo;s anatomy, '
            'frills and all. These are built from simple geometry only, circles, arcs, bars and dots on a strict system, the way a '
            'modernist symbol is made: sturdier at small sizes, easier to animate, and harder to mistake for clip art. They keep the two clasp '
            'devices you picked from round two, the gold hinge and the gold seam, and the same idea underneath: the oyster&rsquo;s two '
            'valves are the SELFTAC&rsquo;s two halves.</p>')
    REF = ('<div class="ref"><span class="lab">Kept from round two</span><div class="refrow">'
           + ''.join(f'<div class="tile" style="{PAL["nacre"]}">{mark(fn, "r2" + k)}</div><span>{n}</span>'
                     for k, n, fn in (('h', '01 The ligament: the gold hinge', R2.gold_hinge), ('k', '05 Kintsugi: the gold seam', R2.kintsugi)))
           + '</div></div>')
else:
    TITLE, EYEBROW, H1, REF = 'Oyster Mark Brainstorm', 'brandmark brainstorm', 'The oyster is already a SELFTAC', ''
    LEDE = ('<p class="lede"><b>An oyster is two separate halves, its valves, held together by one reversible joint, the hinge ligament.</b> '
            'A SELFTAC is two halves that clasp back together. So none of these adds a pearl or a molecule to a shell: the valves are the two '
            'halves, and the hinge, the lip or the seam between them carries the clasp, in the clasp colour. Every shell is drawn with a frilled '
            'edge and growth layers, which is what makes an oyster read as an oyster and not a clam, a cowrie or a coffee bean (smooth first '
            'sketches read as all three). Each is shown clasped and split: the split state is for motion, the halves coming together in the intro.</p>')

CSS = '''
:root { --bg: #F3EEEB; --surface: #FBF8F6; --ink: #241D28; --muted: #6A5E6C; --line: rgba(36,29,40,.13); --accent: #8C5572;
  --serif: "Newsreader", Georgia, serif; --sans: "Archivo", "Helvetica Neue", Arial, sans-serif; --mono: "IBM Plex Mono", ui-monospace, Menlo, monospace; color-scheme: light; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --bg: #17131A; --surface: #211C25; --ink: #EFE6E1; --muted: #B3A6B4; --line: rgba(239,230,225,.13); --accent: #D9AFC2; color-scheme: dark; } }
:root[data-theme="dark"] { --bg: #17131A; --surface: #211C25; --ink: #EFE6E1; --muted: #B3A6B4; --line: rgba(239,230,225,.13); --accent: #D9AFC2; color-scheme: dark; }
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink); font: 400 16px/1.55 var(--sans); -webkit-font-smoothing: antialiased; }
.wrap { max-width: 1240px; margin: 0 auto; padding: clamp(40px, 7vw, 80px) clamp(16px, 4vw, 48px) 56px; }
.eyebrow, .lab { font: 500 11px/1 var(--mono); letter-spacing: .12em; text-transform: uppercase; color: var(--muted); }
h1, h2 { font-family: var(--serif); font-weight: 500; letter-spacing: -.012em; margin: 0; }
h1 { font-size: clamp(36px, 5vw, 58px); line-height: 1.04; margin-top: 12px; }
.lede { color: var(--muted); max-width: 70ch; margin: 14px 0 0; font-size: clamp(16px, 1.4vw, 18px); }
.lede b { color: var(--ink); font-weight: 600; }
.grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; margin-top: 36px; }
@media (max-width: 900px) { .grid { grid-template-columns: minmax(0, 1fr); } }
.card { background: var(--surface); border: 1px solid var(--line); border-radius: 22px; padding: clamp(16px, 2.2vw, 24px); display: grid; gap: 10px; min-width: 0; align-content: start; }
.card header { display: flex; align-items: baseline; gap: 12px; }
.card header b { font: 500 13px/1 var(--mono); color: var(--accent); letter-spacing: .06em; }
.card h2 { font-size: clamp(24px, 2.4vw, 30px); }
.card p { margin: 0; color: var(--muted); font-size: 15px; }
.card p.why { color: var(--ink); }
.states { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 4px; }
.state { display: grid; gap: 6px; min-width: 0; }
.row { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.tile { border-radius: 14px; display: grid; place-items: center; min-width: 0; }
.tile.sq { aspect-ratio: 1 / 1; padding: 8%; }
.tile.sm { display: flex; align-items: center; justify-content: center; gap: 14px; padding: 14px 8px; flex-wrap: wrap; }
.tile.wide { padding: clamp(14px, 2.4vw, 22px) 10px; }
.mk { width: 100%; height: 100%; display: block; }
.px { display: block; flex: none; }
.lt { width: 100%; height: auto; display: block; }
.ref { margin-top: 22px; display: grid; gap: 8px; }
.refrow { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; color: var(--muted); font-size: 14px; }
.refrow .tile { width: 64px; height: 64px; padding: 8px; }
.refrow span { margin-right: 18px; }
footer { margin-top: 40px; color: var(--muted); font-size: 13px; max-width: 80ch; }
code { font-family: var(--mono); font-size: .92em; }
'''
html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{TITLE}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=swap">
<style>{CSS}</style>
</head>
<body>
<main class="wrap">
  <span class="eyebrow">Oyster Therapeutics &middot; {EYEBROW}</span>
  <h1>{H1}</h1>
  {LEDE}{REF}
  <div class="grid">{cards}</div>
  <footer>Rough concepts for choosing a direction, not finished artwork: the frills, layers and clasp proportions would all be redrawn for the chosen idea, and a small-size cut made for favicons. Built by <code>oyster/brand/brainstorm/build_brainstorm.py {C.__name__}</code> from <code>{C.__name__}.py</code>.</footer>
</main>
</body>
</html>
'''
open(D + '../' + OUT, 'w').write(html)
print(OUT, len(html) // 1024, 'KB')
