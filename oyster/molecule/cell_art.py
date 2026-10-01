"""Background artwork for the SELFTAC diagram (viewBox 0 0 640 600): capillary lumen, endothelium,
basement membrane, pericyte, astrocyte end-feet and the neuron, drawn as organic shapes with a
cartoon lipid bilayer.

Membranes: each cell's shapes are defined once and drawn as four <use> layers (dark, light and dark
strokes, then the cytoplasm fill on top). The fill hides the inner half of every stroke and any
outline that falls inside another shape of the same cell, so a cell made of several overlapping
shapes (soma, dendrites, spines) gets one continuous dark-light-dark membrane around its outside.
"""
import math

def f(v): return f'{v:.1f}'

def closed(q):  # closed Catmull-Rom
    n = len(q); out = f'M{f(q[0][0])} {f(q[0][1])}'
    for k in range(n):
        p0, p1, p2, p3 = q[k - 1], q[k], q[(k + 1) % n], q[(k + 2) % n]
        out += f'C{f(p1[0] + (p2[0] - p0[0]) / 6)} {f(p1[1] + (p2[1] - p0[1]) / 6)} {f(p2[0] - (p3[0] - p1[0]) / 6)} {f(p2[1] - (p3[1] - p1[1]) / 6)} {f(p2[0])} {f(p2[1])}'
    return out + 'Z'

def opened(q):  # open Catmull-Rom
    n = len(q); out = f'M{f(q[0][0])} {f(q[0][1])}'
    for k in range(n - 1):
        p0, p1, p2, p3 = q[max(k - 1, 0)], q[k], q[k + 1], q[min(k + 2, n - 1)]
        out += f'C{f(p1[0] + (p2[0] - p0[0]) / 6)} {f(p1[1] + (p2[1] - p0[1]) / 6)} {f(p2[0] - (p3[0] - p1[0]) / 6)} {f(p2[1] - (p3[1] - p1[1]) / 6)} {f(p2[0])} {f(p2[1])}'
    return out

def sample(q, per=10):
    """Points along an open Catmull-Rom curve."""
    n = len(q); pts = []
    for k in range(n - 1):
        p0, p1, p2, p3 = q[max(k - 1, 0)], q[k], q[k + 1], q[min(k + 2, n - 1)]
        for j in range(per):
            t = j / per; t2, t3 = t * t, t * t * t
            pts.append([.5 * (2 * p1[i] + (-p0[i] + p2[i]) * t + (2 * p0[i] - 5 * p1[i] + 4 * p2[i] - p3[i]) * t2 + (-p0[i] + 3 * p1[i] - 3 * p2[i] + p3[i]) * t3) for i in (0, 1)])
    return pts + [q[-1]]

def taper(q, w0, w1, cap=True):
    """Filled outline of a tube along q whose width goes from w0 to w1 (a dendrite or a process)."""
    c = sample(q); n = len(c); L, R = [], []
    for i, p in enumerate(c):
        a, b = c[max(i - 1, 0)], c[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]; d = math.hypot(dx, dy) or 1
        w = (w0 + (w1 - w0) * (i / (n - 1)) ** .8) / 2
        L.append([p[0] - dy / d * w, p[1] + dx / d * w]); R.append([p[0] + dy / d * w, p[1] - dx / d * w])
    e = c[-1]; dx, dy = e[0] - c[-2][0], e[1] - c[-2][1]; d = math.hypot(dx, dy) or 1
    tip = [[e[0] + dx / d * w1 * .5, e[1] + dy / d * w1 * .5]] if cap else []
    pts = L + tip + R[::-1]
    return 'M' + ' L'.join(f'{f(x)} {f(y)}' for x, y in pts) + 'Z'

def blob(cx, cy, rx, ry, lumps=(), n=36, rot=0):
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        r = 1 + sum(amp * math.cos(k * a + ph) for k, amp, ph in lumps)
        x, y = math.cos(a) * rx * r, math.sin(a) * ry * r
        pts.append([cx + x * math.cos(rot) - y * math.sin(rot), cy + x * math.sin(rot) + y * math.cos(rot)])
    return pts

def cell(name, shapes, cls):
    """Shapes drawn as one cell with a continuous bilayer outline."""
    defs = f'<g id="{name}">' + ''.join(shapes) + '</g>'
    uses = ''.join(f'<use href="#{name}" class="mb{i}"/>' for i in (1, 2, 3, 4))
    return defs, f'<g class="{cls}">{uses}</g>'

# ---------- layout constants shared with gen_site_icon.py ----------
SOMA_C, SOMA_R = (400, 440), (180, 150)
NUC = (522, 520, 20)
JUNCTIONS = [168, 328, 488]

def soma_pts():
    pts = blob(*SOMA_C, *SOMA_R, lumps=((3, .025, 1.2), (5, .015, .3), (2, .02, 2.2)), n=40)
    # draw the top up toward the apical dendrite
    out = []
    for x, y in pts:
        k = math.exp(-((x - 400) / 60) ** 2) if y < SOMA_C[1] else 0
        out.append([x, y - 10 * k])
    return out

def art():
    defs, body = [], []
    D = lambda d, b: (defs.append(d), body.append(b))

    # ---------- capillary lumen: plasma, red cells, a platelet ----------
    body.append('<rect class="lumen" x="0" y="0" width="640" height="150"/>')
    dots = [(38, 22), (96, 104), (150, 30), (212, 96), (298, 18), (352, 108), (420, 34), (486, 100), (548, 24), (606, 70), (180, 66), (520, 60), (70, 62), (400, 80)]
    body.append('<g class="plasma">' + ''.join(f'<circle cx="{x}" cy="{y}" r="{1.2 + (x * 7 % 5) / 4:.1f}"/>' for x, y in dots) + '</g>')
    disc = ('<ellipse class="rbc-o" rx="24" ry="10"/><ellipse class="rbc-d" cx="-1" cy="-.6" rx="13" ry="4.4"/>'
            '<path class="rbc-h" d="M-17 -5.5 C-9 -9.4 9 -9.4 17 -5.5"/>')
    side = ('<path class="rbc-o" d="M-8 -16 C-2 -16 0 -9 0 0 C0 9 -2 16 -8 16 C-14 16 -12 8 -12 0 C-12 -8 -14 -16 -8 -16Z" transform="translate(4 0) rotate(-14)"/>'
            '<path class="rbc-h" d="M-9 -12 C-6 -13 -4 -9 -4 -3" transform="translate(4 0) rotate(-14)"/>')
    for y, x, delay, kind, sc in [(40, 120, -2, disc, 1), (80, 420, -7, disc, .95), (58, 560, -10, side, .9), (94, 40, -4.5, disc, .92), (30, 260, -8.6, side, .85)]:
        body.append(f'<g class="rbc" style="--y:{y}px;--x:{x}px;animation-delay:{delay}s"><g transform="scale({sc})">{kind}</g></g>')
    body.append('<g class="rbc" style="--y:110px;--x:300px;animation-delay:-5.4s;animation-duration:15s"><ellipse class="plt" rx="5.5" ry="2.4"/></g>')

    # ---------- endothelium: squamous cells, bulging over their nuclei ----------
    nuclei = [86, 300, 356, 590]
    cells = [(-24, JUNCTIONS[0] - 1), (JUNCTIONS[0] + 1, JUNCTIONS[1] - 1), (JUNCTIONS[1] + 1, JUNCTIONS[2] - 1), (JUNCTIONS[2] + 1, 664)]
    hair = []
    for k, ((x0, x1), xn) in enumerate(zip(cells, nuclei)):
        top = lambda x: 136 - 17 * math.exp(-((x - xn) / 24) ** 2) + 1.6 * math.sin(x / 17 + k)
        bot = lambda x: 166 + 1.2 * math.sin(x / 29 + k * 2)
        xs = [x0 + 7 + i * (x1 - x0 - 14) / 14 for i in range(15)]
        pts = [[x0 + 1, 151]] + [[x, top(x)] for x in xs] + [[x1 - 1, 151]] + [[x, bot(x)] for x in xs[::-1]]
        D(*cell(f'endo{k}', [f'<path d="{closed(pts)}"/>'], 'cl-endo'))
        body.append(f'<ellipse class="endo-n" cx="{xn}" cy="{f(top(xn) + 14)}" rx="25" ry="7.5"/><ellipse class="endo-nc" cx="{xn + 6}" cy="{f(top(xn) + 15)}" rx="4" ry="2.2"/>')
        for x in range(int(x0 + 10), int(x1 - 8), 7):  # glycocalyx on the luminal surface
            y = top(x) - 2.5
            hair.append(f'M{x} {f(y)}l{(x % 3) - 1} -{4 + x % 4}')
    body.append(f'<path class="glyx" d="{" ".join(hair)}"/>')
    # transcytotic vesicles and caveolae
    ves = [(232, 160), (246, 141), (262, 155), (392, 158), (404, 140), (424, 152), (122, 158), (520, 156), (612, 141)]
    body.append('<g class="ves">' + ''.join(f'<circle cx="{x}" cy="{y}" r="2.6"/>' for x, y in ves) + '</g>')
    # tight junctions where neighbouring membranes meet
    body.append('<g class="tj">' + ''.join(f'<circle cx="{x}" cy="{y}" r="1.9"/>' for x in JUNCTIONS for y in (140, 146, 152, 158)) + '</g>')

    # ---------- basement membrane and pericyte ----------
    bm = [[x, 174 + 1.4 * math.sin(x / 21)] for x in range(-10, 660, 30)]
    body.append(f'<path class="bm" d="{opened(bm)}"/><path class="bm-f" d="{opened(bm)}"/>')
    D(*cell('peri', [f'<path d="{closed(blob(578, 179, 34, 5, ((2, .06, 0), (3, .04, 1))))}"/>', f'<path d="{closed(blob(578, 181, 15, 6.5))}"/>'], 'cl-peri'))
    body.append('<ellipse class="peri-n" cx="578" cy="181" rx="11" ry="3.6"/>')

    # ---------- astrocytes: end-feet wrapping the vessel, joined to their processes ----------
    def foot(x0, x1):
        xs = [x0 + 6 + i * (x1 - x0 - 12) / 10 for i in range(11)]
        top = [[x, 185 + .8 * math.sin(x / 13)] for x in xs]
        bot = [[x, 208 + 5 * math.sin(math.pi * (x - x0) / (x1 - x0)) + 1.2 * math.sin(x / 9)] for x in xs[::-1]]
        return f'<path d="{closed([[x0 + 1, 197]] + top + [[x1 - 1, 197]] + bot)}"/>'
    a_body = closed(blob(84, 300, 19, 17, ((3, .12, .4), (5, .06, 1.1)), n=30))
    a_shapes = [foot(-30, 150), foot(156, 306), f'<path d="{a_body}"/>',
                f'<path d="{taper([[84, 300], [80, 262], [74, 230], [70, 204]], 6, 11, cap=False)}"/>',
                f'<path d="{taper([[84, 300], [130, 280], [184, 244], [226, 204]], 6, 10, cap=False)}"/>',
                f'<path d="{taper([[84, 300], [52, 326], [20, 344], [-10, 356]], 6, 2.5)}"/>',
                f'<path d="{taper([[84, 300], [112, 334], [146, 370], [188, 404]], 5, 1.6)}"/>',
                f'<path d="{taper([[84, 300], [70, 340], [56, 384], [44, 420]], 4.5, 1.6)}"/>',
                f'<path d="{taper([[146, 370], [126, 392], [118, 414]], 2.4, 1)}"/>',
                f'<path d="{taper([[52, 326], [46, 300], [30, 282]], 2.4, 1)}"/>']
    D(*cell('astro', a_shapes, 'cl-astro'))
    b_shapes = [foot(320, 468), foot(478, 680),
                f'<path d="{taper([[420, 204], [470, 230], [560, 242], [660, 248]], 6, 9, cap=False)}"/>',
                f'<path d="{taper([[562, 206], [590, 226], [630, 238]], 5, 8, cap=False)}"/>']
    D(*cell('astro2', b_shapes, 'cl-astro'))
    body.append(f'<ellipse class="astro-n" cx="86" cy="301" rx="9" ry="7.5"/>')

    # ---------- neuron: soma, tapering dendrites with spines, axon ----------
    dends = [
        ([[400, 300], [396, 278], [390, 256], [384, 232]], 18, 6),
        ([[392, 262], [366, 252], [344, 246]], 6, 2.5),
        ([[300, 336], [276, 312], [256, 288], [236, 262]], 15, 4),
        ([[256, 288], [232, 292], [208, 288]], 5, 2),
        ([[548, 360], [576, 334], [604, 314], [650, 296]], 15, 5),
        ([[548, 524], [572, 548], [600, 568], [652, 594]], 13, 5),
    ]
    spines = []
    for q, w0, w1 in dends:
        c = sample(q, 6)
        for i in range(5, len(c) - 3, 8):
            a, b = c[i - 1], c[i + 1]; dx, dy = b[0] - a[0], b[1] - a[1]; d = math.hypot(dx, dy) or 1
            side_ = 1 if i % 2 else -1; w = (w0 + (w1 - w0) * i / len(c)) / 2
            s0 = [c[i][0] - dy / d * w * side_ * .6, c[i][1] + dx / d * w * side_ * .6]
            s1 = [c[i][0] - dy / d * (w + 4.5) * side_, c[i][1] + dx / d * (w + 4.5) * side_]
            spines.append(f'<path d="{taper([s0, s1], 1.6, 1.4, cap=False)}"/><circle cx="{f(s1[0])}" cy="{f(s1[1])}" r="2"/>')
    axon = [[262, 532], [236, 556], [204, 578], [168, 604]]
    hillock = taper([[276, 516], [262, 532], [248, 546]], 26, 7, cap=False)
    n_shapes = ([f'<path class="soma" d="{closed(soma_pts())}"/>'] + [f'<path d="{taper(q, w0, w1)}"/>' for q, w0, w1 in dends]
                + spines + [f'<path d="{hillock}"/>', f'<path d="{taper(axon, 6, 5, cap=False)}"/>'])
    D(*cell('nrn', n_shapes, 'cl-nrn'))
    # microtubules running into the dendrites and axon
    mts = [q for q, _, _ in dends[::2]] + [[[268, 524], [236, 556], [204, 578]]]
    body.append('<g class="mt">' + ''.join(f'<path d="{opened(q)}"/>' for q in mts) + '</g>')

    # organelles, faint and unlabelled: mitochondria, rough ER beside the nucleus
    org = ''
    for x, y, r in [(246, 432, 1.3), (322, 334, -.2), (460, 334, .25), (550, 418, 1.2), (318, 540, .4), (444, 566, -.3)]:
        org += f'<g transform="translate({x} {y}) rotate({math.degrees(r):.0f})"><rect class="mito" x="-10" y="-4.6" width="20" height="9.2" rx="4.6"/><path class="cris" d="M-6 -3 v4 M-2 3 v-4 M2 -3 v4 M6 3 v-4"/></g>'
    nx, ny, nr = NUC
    body.append(f'<g class="org">{org}</g>')
    # nucleus: double envelope with pores, chromatin, nucleolus
    body.append(f'<g class="fl" style="--fa:1.5px;--fd:-2.7s"><circle class="nuc" cx="{nx}" cy="{ny}" r="{nr}"/>'
                f'<circle class="nuc-env" cx="{nx}" cy="{ny}" r="{nr}"/><circle class="nuc-in" cx="{nx}" cy="{ny}" r="{nr - 2.4}"/>'
                + ''.join(f'<circle class="pore" cx="{f(nx + nr * math.cos(a))}" cy="{f(ny + nr * math.sin(a))}" r="1"/>' for a in [i * .9 + .3 for i in range(7)])
                + ''.join(f'<circle class="chrom" cx="{f(nx + d * math.cos(a))}" cy="{f(ny + d * math.sin(a))}" r="{r}"/>' for d, a, r in [(11, .6, 2.6), (13, 2.4, 2), (9, 4, 2.4), (14, 5.3, 1.8)])
                + f'<circle class="nucl" cx="{nx + 4}" cy="{ny + 3}" r="5.5"/></g>')
    # clip to the viewBox: on wide layouts the SVG box is wider than 640 x 600
    return ('<defs>' + ''.join(defs) + '<clipPath id="dgClip"><rect width="640" height="600"/></clipPath></defs>\n          <g clip-path="url(#dgClip)">\n          '
            + '\n          '.join(body) + '\n          </g>')

def proteasome(cx, cy, s=1.0):
    """26S proteasome side view: four stacked rings of the 20S core, a 19S cap on each end."""
    out = ''
    for i in range(4):
        x = cx - 27 * s + i * 13.6 * s
        out += f'<rect class="p20" x="{f(x)}" y="{f(cy - 18 * s)}" width="{f(12 * s)}" height="{f(36 * s)}" rx="{f(4.5 * s)}"/>'
        out += ''.join(f'<path class="psub" d="M{f(x + 1.5 * s)} {f(cy + k * s)}h{f(9 * s)}"/>' for k in (-9, 0, 9))
    for side_ in (-1, 1):
        pts = blob(cx + side_ * 38 * s, cy, 10 * s, 21 * s, ((2, .06, 0), (4, .07, .5 if side_ < 0 else 2.1), (6, .05, 1.2)), n=30)
        out += f'<path class="p19" d="{closed(pts)}"/>'
    return out

CSS = '''.dg { overflow: hidden; }
.dg .lumen { fill: color-mix(in srgb, var(--rbc) 13%, var(--surface)); }
.dg .plasma circle { fill: var(--rbc); opacity: .28; }
.dg .rbc-o { fill: var(--rbc); stroke: color-mix(in srgb, var(--rbc) 70%, #3a0f16); stroke-width: .8; }
.dg .rbc-d { fill: color-mix(in srgb, var(--rbc) 72%, #3a0f16); opacity: .5; }
.dg .rbc-h { fill: none; stroke: #fff; stroke-opacity: .35; stroke-width: 1.4; stroke-linecap: round; }
.dg .plt { fill: color-mix(in srgb, var(--accent-2) 50%, var(--ink)); opacity: .55; }
.dg .rbc { transform: translate(var(--x), var(--y)); }
@media (prefers-reduced-motion: no-preference) { .dg .rbc { animation: flow 12s linear infinite; } }
@keyframes flow { from { transform: translate(-60px, var(--y)); } to { transform: translate(700px, var(--y)); } }
/* cartoon lipid bilayer: dark, light, dark, then the cytoplasm fill over the inner half */
.dg .mb1 { fill: none; stroke: var(--mem); stroke-width: 4.6; stroke-linejoin: round; }
.dg .mb2 { fill: none; stroke: var(--lip); stroke-width: 2.8; stroke-linejoin: round; }
.dg .mb3 { fill: none; stroke: var(--mem); stroke-width: 1; stroke-linejoin: round; }
.dg .mb4 { fill: var(--cyt); stroke: none; }
.dg .cl-endo { --mem: color-mix(in srgb, var(--ink) 45%, var(--surface-2)); --lip: color-mix(in srgb, var(--ink) 6%, var(--surface)); --cyt: var(--surface-2); }
.dg .cl-peri { --mem: color-mix(in srgb, var(--accent-2) 60%, var(--ink)); --lip: var(--surface); --cyt: color-mix(in srgb, var(--accent-2) 40%, var(--surface)); }
.dg .cl-astro { --mem: color-mix(in srgb, var(--accent-2) 75%, var(--ink)); --lip: var(--surface); --cyt: color-mix(in srgb, var(--accent-2) 20%, var(--surface)); }
.dg .cl-nrn { --mem: color-mix(in srgb, var(--accent) 70%, var(--ink)); --lip: var(--surface); --cyt: color-mix(in srgb, var(--accent) 14%, var(--surface)); }
.dg .endo-n { fill: color-mix(in srgb, var(--ink) 16%, var(--surface-2)); stroke: color-mix(in srgb, var(--ink) 40%, transparent); stroke-width: .8; }
.dg .endo-nc { fill: color-mix(in srgb, var(--ink) 30%, var(--surface-2)); }
.dg .glyx { fill: none; stroke: color-mix(in srgb, var(--accent-2) 70%, var(--ink)); stroke-opacity: .45; stroke-width: .9; stroke-linecap: round; }
.dg .ves circle { fill: var(--surface); stroke: color-mix(in srgb, var(--ink) 40%, transparent); stroke-width: .9; }
.dg .tj circle { fill: var(--ink); }
.dg .bm { fill: none; stroke: color-mix(in srgb, var(--accent-2) 55%, var(--surface)); stroke-width: 5; }
.dg .bm-f { fill: none; stroke: color-mix(in srgb, var(--accent-2) 80%, var(--ink)); stroke-opacity: .5; stroke-width: .8; stroke-dasharray: 5 2 1 2; }
.dg .peri-n, .dg .astro-n { fill: color-mix(in srgb, var(--accent-2) 55%, var(--ink)); opacity: .45; }
.dg .mt path { fill: none; stroke: color-mix(in srgb, var(--accent) 60%, var(--ink)); stroke-opacity: .22; stroke-width: 1; stroke-dasharray: 9 4; }
.dg .org { opacity: .5; }
.dg .mito { fill: color-mix(in srgb, var(--accent) 30%, var(--surface)); stroke: color-mix(in srgb, var(--accent) 70%, var(--ink)); stroke-width: 1; }
.dg .cris { fill: none; stroke: color-mix(in srgb, var(--accent) 70%, var(--ink)); stroke-width: .8; }
.dg .er { fill: none; stroke: color-mix(in srgb, var(--accent) 60%, var(--ink)); stroke-width: 1.4; }
.dg .ribo { fill: color-mix(in srgb, var(--accent) 60%, var(--ink)); }
.dg .nuc { fill: color-mix(in srgb, var(--ink) 7%, var(--surface)); }
.dg .nuc-env { fill: none; stroke: color-mix(in srgb, var(--ink) 38%, var(--surface)); stroke-width: 2.4; }
.dg .nuc-in { fill: none; stroke: color-mix(in srgb, var(--ink) 22%, var(--surface)); stroke-width: .8; }
.dg .pore { fill: var(--surface); }
.dg .chrom { fill: color-mix(in srgb, var(--ink) 16%, var(--surface)); }
.dg .nucl { fill: color-mix(in srgb, var(--ink) 32%, var(--surface)); }
.dg .p20 { fill: color-mix(in srgb, var(--ink) 52%, var(--surface)); }
.dg .psub { stroke: var(--surface); stroke-opacity: .35; stroke-width: 1; }
.dg .p19 { fill: color-mix(in srgb, var(--ink) 36%, var(--surface)); stroke: color-mix(in srgb, var(--ink) 52%, var(--surface)); stroke-width: 1; }
.dg .e2 { fill: color-mix(in srgb, var(--accent-2) 55%, var(--surface)); stroke: color-mix(in srgb, var(--accent-2) 70%, var(--ink)); stroke-width: 1.3; }
.dg .e2-l { font-size: 9px; font-weight: 600; fill: var(--ink); }
.dg #e2ub { fill: var(--accent-ink); stroke: var(--surface); stroke-width: 1.2; }
.dg .rip { fill: none; stroke: var(--accent-ink); stroke-width: 1.6; }
.dg .fx-ring { fill: none; stroke: var(--accent-ink); stroke-width: 2; }
.dg .fx-ray { stroke: var(--accent-ink); stroke-width: 1.8; stroke-linecap: round; }
'''
