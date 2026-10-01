"""Build the SELFTAC molecule design-options page (options.html) from mz1_2d.json.

Four static treatments of a bifunctional degrader, each drawn joined and split at the
reversible linker, in the Nacre and Tidepool palettes and at several sizes.
"""
import json, math, os

D = os.path.dirname(os.path.abspath(__file__)) + '/'
d = json.load(open(D + 'mz1_2d.json'))
A, EL, PART, BONDS, PATH, BRK = d['atoms'], d['el'], d['part'], d['bonds'], d['linker_path'], d['break']
MID = PATH.index(BRK[1])
nbrs = {i: [] for i in range(len(A))}
for i, j, o in BONDS:
    nbrs[i].append(j); nbrs[j].append(i)

def side(i):
    if PART[i] == 'warhead': return 'L'
    if PART[i] == 'e3lig': return 'R'
    if i in PATH: return 'L' if PATH.index(i) < MID else 'R'
    return side([n for n in nbrs[i] if n in PATH][0])

SIDE = [side(i) for i in range(len(A))]
SPLIT = {'L': (-2.6, -.5, -7), 'R': (2.6, .5, 6)}  # dx, dy, degrees for the split state

def tf(p, s, split):
    if not split: return p
    dx, dy, deg = SPLIT[s]; a = math.radians(deg); cx = -7 if s == 'L' else 8
    x, y = p[0] - cx, p[1]
    return [cx + x * math.cos(a) - y * math.sin(a) + dx, y * math.cos(a) + x * math.sin(a) + dy]

def P(i, split): return tf(A[i], SIDE[i], split)
def f(v): return f'{v:.3f}'

def poly(pts, s, split):
    q = [tf(p, s, split) for p in pts]; n = len(q); out = f'M{f(q[0][0])},{f(q[0][1])}'
    for k in range(n):  # closed Catmull-Rom
        p0, p1, p2, p3 = q[k - 1], q[k], q[(k + 1) % n], q[(k + 2) % n]
        out += f'C{f(p1[0] + (p2[0] - p0[0]) / 6)},{f(p1[1] + (p2[1] - p0[1]) / 6)} {f(p2[0] - (p3[0] - p1[0]) / 6)},{f(p2[1] - (p3[1] - p1[1]) / 6)} {f(p2[0])},{f(p2[1])}'
    return out + 'Z'

def curve(pts):  # open Catmull-Rom through points
    n = len(pts); out = f'M{f(pts[0][0])},{f(pts[0][1])}'
    for k in range(n - 1):
        p0, p1, p2, p3 = pts[max(k - 1, 0)], pts[k], pts[k + 1], pts[min(k + 2, n - 1)]
        out += f'C{f(p1[0] + (p2[0] - p0[0]) / 6)},{f(p1[1] + (p2[1] - p0[1]) / 6)} {f(p2[0] - (p3[0] - p1[0]) / 6)},{f(p2[1] - (p3[1] - p1[1]) / 6)} {f(p2[0])},{f(p2[1])}'
    return out

def linker_pts(split):
    """Linker centreline on each side of the break, extended into the heads."""
    head_L = [n for n in nbrs[PATH[0]] if PART[n] == 'warhead'][0]
    head_R = [n for n in nbrs[PATH[-1]] if PART[n] == 'e3lig'][0]
    L = [P(head_L, split)] + [P(i, split) for i in PATH[:MID]]
    R = [P(i, split) for i in PATH[MID:]] + [P(head_R, split)]
    return L, R

def break_mid(split):
    a, b = P(BRK[0], split), P(BRK[1], split)
    return [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2], a, b

def skeleton(split, heads_w=.085, link_w=.24, halo=True):
    s = ''
    if halo:  # pale halo under the linker so it reads as the emphasised part
        for pts in linker_pts(split):
            s += f'<path d="{curve(pts)}" fill="none" stroke="var(--lk)" stroke-opacity=".18" stroke-width="{link_w * 4.2}" stroke-linecap="round"/>'
    for i, j, o in BONDS:
        if split and {i, j} == set(BRK): continue
        a, b = P(i, split), P(j, split); lk = PART[i] == 'linker' or PART[j] == 'linker'
        if {i, j} == set(BRK): continue
        s += f'<line x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}" stroke="{"var(--lk)" if lk else "var(--ink)"}" stroke-width="{link_w if lk else heads_w}" stroke-linecap="round"/>'
        if o == 2 and not lk:  # second line for double bonds, offset to one side
            dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy); ox, oy = -dy / L * .22, dx / L * .22
            s += f'<line x1="{f(a[0] + ox + dx * .15)}" y1="{f(a[1] + oy + dy * .15)}" x2="{f(b[0] + ox - dx * .15)}" y2="{f(b[1] + oy - dy * .15)}" stroke="var(--ink)" stroke-width="{heads_w}" stroke-linecap="round"/>'
    for r in d['rings']:  # aromatic circles
        pts = [P(i, split) for i in r]; cx = sum(p[0] for p in pts) / len(pts); cy = sum(p[1] for p in pts) / len(pts)
        rad = min(math.hypot(p[0] - cx, p[1] - cy) for p in pts) * .58
        s += f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(rad)}" fill="none" stroke="var(--ink)" stroke-width="{heads_w}"/>'
    return s

def clasp(split, size=.75):
    """The reversible bond: joined, an open ring around the bond; split, two facing half-cups."""
    m, a, b = break_mid(split)
    if not split:
        return (f'<circle cx="{f(m[0])}" cy="{f(m[1])}" r="{size}" fill="var(--bg)" stroke="var(--hi)" stroke-width=".2"/>'
                f'<line x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}" stroke="var(--lk)" stroke-width=".24" stroke-dasharray=".18 .2" stroke-linecap="round"/>')
    s = ''
    for p, q in ((a, b), (b, a)):
        ang = math.degrees(math.atan2(q[1] - p[1], q[0] - p[0]))
        s += (f'<g transform="translate({f(p[0])} {f(p[1])}) rotate({f(ang)})">'
              f'<path d="M.15,-.55 A.55,.55 0 0 1 .15,.55" fill="none" stroke="var(--hi)" stroke-width=".2" stroke-linecap="round"/></g>')
    return s

def opt_surface(split):
    s = ''
    for k, side_ in (('warhead', 'L'), ('e3lig', 'R')):
        s += f'<path d="{poly(d["blob"][k], side_, split)}" fill="var(--{"a" if k == "warhead" else "b"})" fill-opacity=".42" stroke="var(--ink)" stroke-opacity=".35" stroke-width=".07"/>'
    return s + skeleton(split) + clasp(split)

def opt_silhouette(split):
    s = ''
    for k, side_ in (('warhead', 'L'), ('e3lig', 'R')):
        s += f'<path d="{poly(d["blob_soft"][k], side_, split)}" fill="var(--{"a" if k == "warhead" else "b"})" stroke="var(--ink)" stroke-opacity=".5" stroke-width=".09"/>'
        s += f'<path d="{poly(d["blob_core"][k], side_, split)}" fill="none" stroke="var(--ink)" stroke-opacity=".22" stroke-width=".07"/>'
    Lp, Rp = linker_pts(split)
    m, a, b = break_mid(split)
    Lp = Lp + [[a[0] + (m[0] - a[0]) * .35, a[1] + (m[1] - a[1]) * .35]]; Rp = [[b[0] + (m[0] - b[0]) * .35, b[1] + (m[1] - b[1]) * .35]] + Rp
    for pts in (Lp, Rp):
        s += f'<path d="{curve(pts)}" fill="none" stroke="var(--lk)" stroke-width=".55" stroke-linecap="round" stroke-linejoin="round"/>'
    if not split:
        s += f'<circle cx="{f(m[0])}" cy="{f(m[1])}" r=".62" fill="none" stroke="var(--hi)" stroke-width=".22"/>'
    else:
        for p in (Lp[-1], Rp[0]):
            s += f'<circle cx="{f(p[0])}" cy="{f(p[1])}" r=".42" fill="var(--bg)" stroke="var(--hi)" stroke-width=".2"/>'
    return s

def opt_beads(split):
    s = ''
    for k, side_ in (('warhead', 'L'), ('e3lig', 'R')):
        s += f'<path d="{poly(d["blob_soft"][k], side_, split)}" fill="var(--{"a" if k == "warhead" else "b"})" fill-opacity=".22" stroke="var(--ink)" stroke-opacity=".45" stroke-width=".08"/>'
        s += f'<path d="{poly(d["blob"][k], side_, split)}" fill="none" stroke="var(--ink)" stroke-opacity=".3" stroke-width=".07"/>'
        s += f'<path d="{poly(d["blob_core"][k], side_, split)}" fill="var(--{"a" if k == "warhead" else "b"})" fill-opacity=".55" stroke="var(--ink)" stroke-opacity=".25" stroke-width=".06"/>'
    Lp, Rp = linker_pts(split)
    for pts in (Lp, Rp):
        s += f'<path d="{curve(pts)}" fill="none" stroke="var(--lk)" stroke-width=".14"/>'
    for idx, i in enumerate(PATH):
        p = P(i, split); is_o = EL[i] == 'O'
        if i in BRK: continue
        s += f'<circle cx="{f(p[0])}" cy="{f(p[1])}" r="{.42 if is_o else .3}" fill="{"var(--lk)" if is_o else "var(--bg)"}" stroke="var(--lk)" stroke-width=".12"/>'
    for i in BRK:
        p = P(i, split)
        s += f'<circle cx="{f(p[0])}" cy="{f(p[1])}" r=".42" fill="var(--bg)" stroke="var(--hi)" stroke-width=".2"/>'
    if not split:
        a, b = P(BRK[0], split), P(BRK[1], split)
        s += f'<line x1="{f(a[0])}" y1="{f(a[1])}" x2="{f(b[0])}" y2="{f(b[1])}" stroke="var(--hi)" stroke-width=".14" stroke-dasharray=".12 .14"/>'
    return s

def opt_glyph(split):
    s = ''
    for k, side_ in (('warhead', 'L'), ('e3lig', 'R')):
        s += f'<path d="{poly(d["blob_soft"][k], side_, split)}" fill="var(--{"a" if k == "warhead" else "b"})"/>'
    Lp, Rp = linker_pts(split)
    m, a, b = break_mid(split)
    # simplify the linker to a smooth arc through every third point
    Ls = Lp[::3] + [[a[0] + (m[0] - a[0]) * .1, a[1] + (m[1] - a[1]) * .1]]; Rs = [[b[0] + (m[0] - b[0]) * .1, b[1] + (m[1] - b[1]) * .1]] + Rp[::-1][::3][::-1]
    for pts in (Ls, Rs):
        s += f'<path d="{curve(pts)}" fill="none" stroke="var(--lk)" stroke-width=".95" stroke-linecap="round"/>'
    if not split:
        s += f'<circle cx="{f(m[0])}" cy="{f(m[1])}" r=".95" fill="var(--hi)"/>'
    return s

OPTIONS = [
    ('surface', '01', 'Surface and skeleton', opt_surface,
     'Each half is a soft molecular-surface outline traced around its atoms, with the skeletal formula drawn inside. The linker is drawn heavier, in its own colour with a pale halo, and the reversible bond is marked by an open ring.',
     'The most chemically literate. Scientists will recognise JQ1, the PEG linker and VH032.',
     'Busy below about 160px wide. Best for the SELFTAC section, papers and slides, not icons.'),
    ('silhouette', '02', 'Silhouette', opt_silhouette,
     'The skeletal formula is removed. Each half becomes a solid blob with one inner contour, and the linker becomes a single bold strand following its real path. The reversible bond is a ring in the gap.',
     'Reads as a molecule without needing chemistry. Strongest linker emphasis, and it holds up from 60px upwards.',
     'Loses the specific chemistry, so it reads as a degrader in general.'),
    ('beads', '03', 'Beads', opt_beads,
     'The heads are layered contour blobs, like the protein wallpaper. The linker is a string of beads, one per backbone atom, with filled beads for the PEG oxygens. The two atoms of the reversible bond are highlighted.',
     'Matches the 5T35 wallpaper, and the beads make the linker countable and tangible.',
     'More delicate. The beads merge below about 100px wide.'),
    ('glyph', '04', 'Glyph', opt_glyph,
     'Icon-weight: two solid blobs and a thick simplified linker, with a solid dot for the reversible bond. Built for small sizes.',
     'Works down to 32px as a UI icon, bullet or favicon companion. Use it alongside one of the richer versions.',
     'Too simple to explain the mechanism on its own.'),
]

PAL = {
    'nacre': dict(bg='#EFE6E1', ink='#2B2230', a='#C99BB0', b='#B8A7C9', lk='#8C5572', hi='#2B2230'),
    'tidepool': dict(bg='#0F4C4A', ink='#EAF3EF', a='#F2B84B', b='#7FC4B0', lk='#EAF3EF', hi='#F2B84B'),
}
def vars_(p): return ';'.join(f'--{k}:{v}' for k, v in PAL[p].items())

VB_J = '-14.5 -6.2 31.8 12.4'; VB_S = '-18.5 -8 39.8 16'

def svg(fn, split, w=None, label=''):
    vb = VB_S if split else VB_J
    size = f'width="{w}"' if w else 'class="full"'
    return f'<svg {size} viewBox="{vb}" role="img" aria-label="{label}">{fn(split)}</svg>'

sections = ''
strip = ''
for key, num, name, fn, idea, good, watch in OPTIONS:
    panels = ''
    for pal in ('nacre', 'tidepool'):
        smalls = ''.join(f'<div class="sz">{svg(fn, False, w)}<span>{w}px</span></div>' for w in (240, 120, 64, 32))
        panels += (f'<div class="panel {pal}" style="{vars_(pal)}"><span class="cap">{pal.title()}</span>'
                   f'<div class="state"><span class="st">Assembled degrader</span>{svg(fn, False, label=name + " assembled, " + pal)}</div>'
                   f'<div class="state"><span class="st">Split at the reversible linker</span>{svg(fn, True, label=name + " split, " + pal)}</div>'
                   f'<div class="small">{smalls}</div></div>')
    sections += f'''
  <section id="{key}">
    <div class="wrap">
      <div class="head"><span class="num">{num}</span><div><h2>{name}</h2><p>{idea}</p></div></div>
      <div class="panels">{panels}</div>
      <div class="notes"><div><h3>Strength</h3><p>{good}</p></div><div><h3>Watch out</h3><p>{watch}</p></div></div>
    </div>
  </section>'''
    strip += f'<a class="cell" href="#{key}" style="{vars_("nacre")}"><span class="cap">{num}</span>{svg(fn, False, label=name)}<span class="nm">{name}</span></a>'

CSS = '''
/* Layout: a comparison sheet. A strip of the four treatments, then one section per option with
   Nacre and Tidepool specimen panels (assembled, split, size test) and notes. Specimen panels use the
   literal palette colours; the page chrome follows the viewer's theme. */
:root { --pbg: #F3EEEB; --surface: #FBF8F6; --text: #241D28; --muted: #6A5E6C; --rule: rgba(36,29,40,.13);
  --serif: "Newsreader", Georgia, serif; --sans: "Archivo", "Helvetica Neue", Arial, sans-serif; --mono: "IBM Plex Mono", ui-monospace, Menlo, monospace; color-scheme: light; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --pbg: #17131A; --surface: #211C25; --text: #EFE6E1; --muted: #B3A6B4; --rule: rgba(239,230,225,.13); color-scheme: dark; } }
:root[data-theme="dark"] { --pbg: #17131A; --surface: #211C25; --text: #EFE6E1; --muted: #B3A6B4; --rule: rgba(239,230,225,.13); color-scheme: dark; }
* { box-sizing: border-box; }
body { margin: 0; background: var(--pbg); color: var(--text); font: 400 17px/1.6 var(--sans); -webkit-font-smoothing: antialiased; }
.wrap { max-width: 1240px; margin: 0 auto; padding-inline: clamp(16px, 4vw, 48px); }
h1, h2 { font-family: var(--serif); font-weight: 500; letter-spacing: -0.015em; line-height: 1.05; margin: 0; text-wrap: balance; }
p { margin: 0; }
.cap, .st, .sz span { font-family: var(--mono); font-size: 11px; letter-spacing: .08em; text-transform: uppercase; }
header { padding-block: clamp(48px, 7vw, 88px) 36px; }
header h1 { font-size: clamp(40px, 5.4vw, 72px); margin-top: 12px; }
header p { margin-top: 16px; color: var(--muted); max-width: 64ch; }
.note { margin-top: 14px; font-size: 14px; color: var(--muted); max-width: 70ch; }
.strip { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); border-radius: 18px; overflow: hidden; background: #EFE6E1; color: #2B2230; }
.strip .cell { display: flex; flex-direction: column; gap: 10px; padding: 22px 18px; text-decoration: none; color: inherit; min-width: 0; transition: background-color .3s; }
.strip .cell:hover { background: rgba(43,34,48,.05); }
.strip svg { width: 100%; height: auto; }
.strip .nm { font-weight: 600; font-size: 14px; }
section { padding-block: clamp(56px, 7vw, 92px); border-top: 1px solid var(--rule); }
section:first-of-type { margin-top: clamp(48px, 6vw, 72px); }
.head { display: grid; grid-template-columns: 64px 1fr; gap: 20px; margin-bottom: 28px; }
.head .num { font-family: var(--mono); font-size: 14px; width: 52px; height: 52px; border-radius: 50%; border: 1px solid var(--rule); display: grid; place-items: center; background: var(--surface); }
.head h2 { font-size: clamp(30px, 3.2vw, 44px); }
.head p { color: var(--muted); margin-top: 10px; max-width: 70ch; }
.panels { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.panel { border-radius: 20px; padding: clamp(20px, 2.6vw, 34px); background: var(--bg); color: var(--ink); display: grid; gap: 18px; min-width: 0; }
.panel .cap { opacity: .7; }
.state { display: grid; gap: 6px; }
.state .st { opacity: .6; }
svg.full { width: 100%; height: auto; display: block; }
.small { display: flex; align-items: flex-end; gap: 18px; flex-wrap: wrap; padding-top: 10px; border-top: 1px solid currentColor; border-color: color-mix(in srgb, var(--ink) 18%, transparent); }
.sz { display: flex; flex-direction: column; align-items: flex-start; gap: 6px; }
.sz span { opacity: .6; }
.notes { margin-top: 16px; display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.notes > div { background: var(--surface); border: 1px solid var(--rule); border-radius: 16px; padding: 20px 22px; }
.notes h3 { margin: 0 0 6px; font-size: 15px; }
.notes p { color: var(--muted); font-size: 15px; }
.deploy { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; margin-top: 24px; }
.deploy > div { background: var(--surface); border: 1px solid var(--rule); border-radius: 16px; padding: 22px; }
.deploy h3 { margin: 0 0 6px; font-size: 16px; }
.deploy p { color: var(--muted); font-size: 15px; }
footer { padding-block: 36px 56px; border-top: 1px solid var(--rule); color: var(--muted); font-size: 14px; }
@media (max-width: 900px) { .panels, .notes, .deploy { grid-template-columns: 1fr; } .strip { grid-template-columns: 1fr 1fr; } }
'''

html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<!-- artifact:start -->
<title>SELFTAC Molecule Studies</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=swap">
<style>{CSS}</style>
</head>
<body>
<header>
  <div class="wrap">
    <span class="cap" style="color:var(--muted)">Oyster Therapeutics &middot; Illustration system</span>
    <h1>Drawing the degrader</h1>
    <p>Four static treatments for the molecule in the SELFTAC story, replacing the circle and square. Each is drawn from a real 2D layout of a bifunctional degrader: the BRD4 binder on the left, the E3-ligase binder on the right, and the linker between them, emphasised and broken at its reversible bond.</p>
    <p class="note">The geometry is MZ1 (JQ1, a PEG linker and VH032), the PROTAC in PDB 5T35. It stands in for "a degrader" and is not a SELFTAC compound. The break point is placed at the middle of the linker for illustration only.</p>
  </div>
</header>
<main>
  <div class="wrap"><div class="strip">{strip}</div></div>
{sections}
  <section>
    <div class="wrap">
      <div class="head"><span class="num">&rarr;</span><div><h2>Where these would go</h2><p>Any option can replace the current circle-and-square halves. They are all drawn from the same coordinates, so they can be mixed by size.</p></div></div>
      <div class="deploy">
        <div><h3>SELFTAC animation</h3><p>The two halves travel through the barrier and rejoin in the neuron. Option 02 or 03 at about 120px wide, switching to the split state between steps 2 and 4.</p></div>
        <div><h3>Approach and hero sections</h3><p>Option 01 at full width beside the SELFTAC copy, drawn split, so the linker and the reversible bond are the focus.</p></div>
        <div><h3>Icons and small UI</h3><p>Option 04 for list bullets, the announcement strip or section markers, from 32px upwards.</p></div>
      </div>
    </div>
  </section>
</main>
<footer><div class="wrap">Static studies for review. Built with RDKit from the MZ1 ligand definition (RCSB ligand 759). Source: <code>oyster/molecule/</code>.</div></footer>
<!-- artifact:end -->
</body>
</html>
'''
open(D + 'options.html', 'w').write(html)
print('written', len(html))
