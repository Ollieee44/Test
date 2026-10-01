"""Write the SELFTAC diagram's neuron and molecule into both websites.

The neuron holds BRD4 (target protein) and VHL (E3 ligase), traced from the 5T35 crystal pose,
pulled apart a little so the degrader's linker shows between them. Then the Beads treatment of the SELFTAC halves into both websites' SELFTAC diagram.

Each half (warhead or E3 ligand plus its half of the linker) is drawn about its own centre
so the scroll code can move the halves independently. Placed at the offset HALF_DX/HALF_DY
(scaled), the two halves sit exactly as in the joined molecule. The script replaces the
markup between the selftac-halves markers and the HALF_DX/HALF_DY constants in each site.
"""
import json, os, re

D = os.path.dirname(os.path.abspath(__file__)) + '/'
SITES = [D + '../index.html', D + '../editorial/index.html']
d = json.load(open(D + 'mz1_2d.json'))
A, EL, PART, BONDS, PATH, BRK = d['atoms'], d['el'], d['part'], d['bonds'], d['linker_path'], d['break']
MID = PATH.index(BRK[1])
K = 4.0  # px per angstrom at scale 1
STRETCH = 3.5  # extra angstroms of linker per side, to give the linker more presence at diagram size
nbrs = {i: [] for i in range(len(A))}
for i, j, o in BONDS:
    nbrs[i].append(j); nbrs[j].append(i)

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


def stretch(p, s, i=None):
    """Push each head outward along x; linker atoms move in proportion to their distance from the break."""
    if i is not None and i in PATH:
        t = abs(PATH.index(i) - (MID - .5)) / (MID - .5 if s == 'L' else len(PATH) - MID - .5)
    else:
        t = 1
    return [p[0] + (-1 if s == 'L' else 1) * STRETCH * min(t, 1), p[1]]

halves = {}
for part, s in (('warhead', 'L'), ('e3lig', 'R')):
    head = [n for n in nbrs[PATH[0] if s == 'L' else PATH[-1]] if PART[n] == part][0]
    chain = [head] + PATH[:MID] if s == 'L' else PATH[MID:] + [head]
    blob = {k: [stretch(p, s) for p in d[k][part]] for k in ('blob_soft', 'blob', 'blob_core')}
    at = {i: stretch(A[i], s, i) for i in chain}
    pts = blob['blob_soft'] + list(at.values())
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    c = ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2)
    T = lambda p: [(p[0] - c[0]) * K, (p[1] - c[1]) * K]
    g = (f'<path class="bz-s" d="{closed([T(p) for p in blob["blob_soft"]])}"/>'
         f'<path class="bz-o" d="{closed([T(p) for p in blob["blob"]])}"/>'
         f'<path class="bz-c" d="{closed([T(p) for p in blob["blob_core"]])}"/>'
         f'<path class="bz-ln" d="{opened([T(at[i]) for i in chain])}"/>')
    for i in chain[1:] if s == 'L' else chain[:-1]:
        x, y = T(at[i])
        cls = 'bz-x' if i in BRK else 'bz-ox' if EL[i] == 'O' else 'bz-b'
        g += f'<circle class="{cls}" cx="{f(x)}" cy="{f(y)}" r="{3 if i in BRK else 2.5 if EL[i] == "O" else 1.9}"/>'
    halves[s] = (c, g)

# ---------- neuron: soma, BRD4 and VHL from 5T35, proteasome, nucleus ----------
POSE = json.load(open(D + '../editorial/5t35/5t35_poses.json'))['poses'][0]
PS, PC, GAP, MIDX = 230, (395, 438), 56, -0.14  # px per pose unit, complex centre, extra gap, interface x
def place(p, dx): return [PC[0] + (p[0] - MIDX) * PS + dx, PC[1] + (p[1] + .17) * PS]
def protein(key, cls, dx):
    out = [place(p, dx) for p in POSE[key]['outer']]
    det = [place(p, dx) for p in POSE[key]['inner'][0]]
    return out, f'<path class="{cls}" d="{closed(out)}"/><path class="pdet" d="{closed(det)}"/>'
brd4, brd4_svg = protein('target', 'brd4', -GAP / 2)
vhl, vhl_svg = protein('e3', 'e3', GAP / 2)
tgt_c = [sum(p[0] for p in brd4) / len(brd4), sum(p[1] for p in brd4) / len(brd4)]
SOMA = (400, 440, 180, 150)
cx, cy, rx, ry = SOMA; kx, ky = rx * .5523, ry * .5523
soma = (f'M{cx - rx} {cy} C{cx - rx} {f(cy - ky)} {f(cx - kx)} {cy - ry} {cx} {cy - ry} C{f(cx + kx)} {cy - ry} {cx + rx} {f(cy - ky)} {cx + rx} {cy} '
        f'C{cx + rx} {f(cy + ky)} {f(cx + kx)} {cy + ry} {cx} {cy + ry} C{f(cx - kx)} {cy + ry} {cx - rx} {f(cy + ky)} {cx - rx} {cy} Z')
PR = (392, 530, 1.3)  # proteasome centre and scale (rects from the original 75 x 36 drawing)
rects = [(-37.5, -13, 10, 26, 4), (-24.5, -18, 11, 36, 3), (-11.5, -18, 11, 36, 3), (1.5, -18, 11, 36, 3), (14.5, -18, 11, 36, 3), (27.5, -13, 10, 26, 4)]
prot = ''.join(f'<rect x="{f(PR[0] + x * PR[2])}" y="{f(PR[1] + y * PR[2])}" width="{f(w * PR[2])}" height="{f(h * PR[2])}" rx="{f(r * PR[2])}"/>' for x, y, w, h, r in rects)
cell = f'''<!-- selftac-cell:start (generated by molecule/gen_site_icon.py) -->
          <!-- neuron -->
          <g class="dend"><path d="M292 330 C270 306 252 288 238 262"/><path d="M400 292 C398 280 392 262 380 238"/><path d="M392 268 C410 254 428 244 452 240"/><path d="M540 346 C566 322 590 304 630 292"/><path d="M538 536 C562 558 592 576 630 592"/></g>
          <path class="soma" d="{soma}"/>
          <circle class="nuc fl" style="--fa:1.5px;--fd:-2.7s" cx="522" cy="520" r="20"/>
          <circle class="nucl" cx="527" cy="525" r="5.5"/>

          <!-- proteasome -->
          <g class="prot fl" style="--fa:1.5px;--fd:-4s">{prot}</g>
          <text x="{PR[0]}" y="{PR[1] + 44}" text-anchor="middle" class="in-lbl">Proteasome</text>

          <!-- E3 ligase: VHL, outline traced from PDB 5T35 -->
          <g class="fl" style="--fa:1.5px;--fd:-.6s">{vhl_svg}</g>
          <text x="528" y="374" text-anchor="end" class="in-lbl">E3 ligase</text>

          <!-- target protein: BRD4 bromodomain 2 from PDB 5T35, with ubiquitin chain -->
          <g id="tgtG" class="fl" style="--fa:1.5px;--fd:-2.2s">
            {brd4_svg}
            <g id="ubq"><circle cx="296" cy="478" r="5.5"/><circle cx="287" cy="488" r="5.5"/><circle cx="283" cy="500" r="5.5"/><circle cx="290" cy="511" r="5.5"/></g>
          </g>
          <text x="270" y="376" id="tgtLbl" class="in-lbl">Target protein</text>
          <g id="frags" opacity="0"><circle cx="452" cy="522" r="3"/><circle cx="464" cy="532" r="2.5"/><circle cx="458" cy="514" r="2"/><circle cx="474" cy="524" r="2.8"/><circle cx="468" cy="540" r="2"/></g>
          <!-- selftac-cell:end -->'''
CELL = {'endA': [352, 402], 'endB': [438, 398], 'asm': [PC[0], PC[1]], 'tgt': [round(tgt_c[0], 1), round(tgt_c[1], 1)], 'into': [PR[0] - 30, PR[1]]}

dx = (halves['R'][0][0] - halves['L'][0][0]) * K
dy = (halves['R'][0][1] - halves['L'][0][1]) * K
markup = ('<!-- selftac-halves:start (generated by molecule/gen_site_icon.py) -->\n'
          f'          <g id="halfA" class="fl hz-a" style="--fa:1.5px;--fd:-1.2s">{halves["L"][1]}</g>\n'
          f'          <g id="halfB" class="fl hz-b" style="--fa:1.5px;--fd:-3.1s">{halves["R"][1]}</g>\n'
          '          <!-- selftac-halves:end -->')
for path in SITES:
    src = open(path).read()
    src, n1 = re.subn(r'<!-- selftac-halves:start.*?selftac-halves:end -->', lambda m: markup, src, flags=re.S)
    src, n3 = re.subn(r'<!-- selftac-cell:start.*?selftac-cell:end -->', lambda m: cell, src, flags=re.S)
    src, n4 = re.subn(r'var CELL = \{.*?\};', 'var CELL = ' + json.dumps(CELL, separators=(', ', ': ')) + ';', src)
    assert n3 == 1 and n4 == 1, (path, n3, n4)
    src, n2 = re.subn(r'var HALF_DX = [-\d.]+, HALF_DY = [-\d.]+;', f'var HALF_DX = {dx:.1f}, HALF_DY = {dy:.1f};', src)
    assert n1 == 1 and n2 == 1, (path, n1, n2)
    open(path, 'w').write(src)
    print('updated', os.path.relpath(path, D), f'dx={dx:.1f} dy={dy:.1f}')
