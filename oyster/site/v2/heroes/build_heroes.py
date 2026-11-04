"""Build the hero mockups (index.html): four static heroes built around one still of the SELFTAC ternary complex,
with the SELFTAC degrader in the middle and its reversible linker (the pearl strand and gold clasp) in plain view.

  python build_heroes.py --harness   writes .harness.html, the v2 Science page with its 3D scene opened up
  node render_heroes.js              renders img/*.png and img/*.json from it (see that file)
  python build_heroes.py             writes index.html from the renders

The renders use the site's own models and colours: BRD4, VHL and Elongin B and C from PDB 5T35, and the generic
degrader. The degrader is drawn larger than true scale and the two proteins are eased apart a little so that both
of its ends and the whole linker show; the credit on every mockup says so. Each mockup is a 1440 x 810 hero drawn in
the palette its render was made in, scaled to fit the page."""
import json, os, re, sys
D = os.path.dirname(os.path.abspath(__file__)) + '/'
PAGES = D + '../pages/'

if '--harness' in sys.argv:
    s = open(PAGES + 'science.html').read()
    k = '\nwindow.__story = {'
    assert k in s
    s = s.replace(k, '\nwindow.__dbg = { THREE, scene, camera, renderer, P, mol, flash, e2, ubs, prot, wall, cell, PAL, frame: p => frame(p), '
                     'setPal: v => { pal = v; applyPalette(); }, hold: p => { hold = true; prog = p; }, S, C, Q };' + k, 1)
    open(D + '.harness.html', 'w').write(s)
    print('.harness.html written'); sys.exit()

A = {k: json.load(open(D + f'img/{k}.json')) for k in ('a-centre', 'b-split', 'c-annot', 'd-macro', 'e-pearl')}
home = re.search(r'<a class="home".*?</a>', open(PAGES + 'index.html').read(), re.S).group(0)
WM = re.search(r'<svg class="wm".*?</svg>', home, re.S).group(0)
CG = '<svg class="cg" viewBox="0 0 30 12" aria-hidden="true"><line x1="6" y1="6" x2="24" y2="6"/><circle cx="6" cy="6" r="4.6"/><circle cx="24" cy="6" r="4.6"/></svg>'
ARROW = '<svg viewBox="0 0 14 14" aria-hidden="true"><path d="M2 7h10M8 3l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
R = '&reg;'
SELFTAC = f'<span translate="no">SELFTAC{R}</span>'
NAV = ''.join(f'<span>{n}</span>' for n in ('Science', 'Pipeline', 'Team', 'Investors', 'News', 'Contact'))
CREDIT = ('BRD4, VHL and Elongin B and C from PDB 5T35 (Gadd et al., Nat. Chem. Biol. 2017). The degrader is drawn generically, '
          'larger than true scale, with the proteins eased apart so its linker shows.')
# page tokens per palette (palette.md and palettes.json)
PAL = {
    'nacre': dict(ink='#2B2230', muted='#65586A', accent='#8C5572', paper='#EFE6E1', band='#F6EFEC', pearl='#C99BB0', clasp='#D9A443', line='rgba(43,34,48,.16)', on='#2B2230',
                  sky='radial-gradient(130% 120% at 68% 28%, #F6EEEC 0%, #E3D3D8 100%)'),
    'tidepool': dict(ink='#EAF3EF', muted='#B6D3CB', accent='#F2B84B', paper='#0F4C4A', band='#0C4341', pearl='#F2B84B', clasp='#F27D62', line='rgba(234,243,239,.18)', on='#06302E',
                     sky='radial-gradient(130% 120% at 68% 28%, #1B6763 0%, #0F4C4A 100%)'),
    'shellcoral': dict(ink='#2A1410', muted='#6B5446', accent='#2F6B5E', paper='#F3E3CF', band='#F8EDDF', pearl='#E26D5A', clasp='#E26D5A', line='rgba(42,20,16,.16)', on='#2A1410',
                       sky='radial-gradient(130% 120% at 30% 20%, #F8EDDF 0%, #F3E3CF 70%)'),
}
def tokens(p):
    t = PAL[p]
    return (f'--ink:{t["ink"]};--muted:{t["muted"]};--accent:{t["accent"]};--paper:{t["paper"]};--band:{t["band"]};--pearl:{t["pearl"]};'
            f'--clasp:{t["clasp"]};--line:{t["line"]};--on:{t["on"]};background:{t["sky"]};color:{t["ink"]}')
def head(): return f'<div class="mh">{WM}<nav>{NAV}</nav></div>'
def ctas(a, b): return f'<div class="mc"><span class="b"><span>{a}</span>{ARROW}</span><span class="b gh"><span>{b}</span></span></div>'
def pt(key, k, box):
    """an anchor of render key in mockup pixels, for an image placed at box = (x, y, w, h)"""
    x, y = A[key][k]; return round(box[0] + x * box[2]), round(box[1] + y * box[3])
def tag(text, ax, ay, lx, ly, cls=''):
    """a label at (lx, ly) with a leader line to the anchor (ax, ay)"""
    return (f'<svg class="ld" width="1440" height="810" aria-hidden="true"><line x1="{lx}" y1="{ly}" x2="{ax}" y2="{ay}"/><circle cx="{ax}" cy="{ay}" r="3.5"/></svg>'
            f'<span class="tg {cls}" style="left:{lx}px;top:{ly}px">{text}</span>')

# A: centre stage (Nacre). The line and the buttons above, the complex across the middle, three plain labels under it
boxA = (0, 230, 1440, 600)
tx, ty = pt('a-centre', 'target', boxA); cx, cy = pt('a-centre', 'clasp', boxA); lx_, ly_ = pt('a-centre', 'ligase', boxA)
mockA = (f'<div class="mock" style="{tokens("nacre")}">{head()}'
         f'<div class="ac"><p class="ey">{CG}<span>The {SELFTAC} platform</span></p><h2 class="h1">One degrader, rebuilt from two halves.</h2>'
         f'<p class="lede">A reversible linker lets a {SELFTAC} molecule travel as two small molecules, then clasp back together inside the cell.</p></div>'
         f'<img src="img/a-centre.png" alt="" style="left:{boxA[0]}px;top:{boxA[1]}px;width:{boxA[2]}px;height:{boxA[3]}px">'
         + tag('Target protein', tx, ty + 46, tx, 650, 'c') + tag('Reversible linker', cx, cy + 14, cx, 650, 'c hi') + tag('E3 ligase', lx_, ly_ + 56, lx_, 650, 'c')
         + f'<div class="ab">{ctas("See how it works", "Our pipeline")}</div><p class="cr">{CREDIT}</p></div>')

# B: split (Tidepool). Copy on the left, the complex bleeding off the right edge, a chip on the clasp
boxB = (640, 0, 860, 810)
cx, cy = pt('b-split', 'clasp', boxB)
mockB = (f'<div class="mock" style="{tokens("tidepool")}">'
         f'<img src="img/b-split.png" alt="" style="left:{boxB[0]}px;top:{boxB[1]}px;width:{boxB[2]}px;height:{boxB[3]}px">{head()}'
         f'<div class="bl"><p class="ey">{CG}<span>Oral, brain-penetrant</span></p><h2 class="h1">Protein degraders, made small enough to reach the brain.</h2>'
         f'<p class="lede">Two small halves cross the blood-brain barrier and click back together at the clasp, inside the neuron.</p>'
         f'{ctas("See how " + SELFTAC + " works", "Our pipeline")}</div>'
         + tag('The clasp &middot; reversible linker', cx, cy + 16, cx - 30, cy + 110, 'chip')
         + f'<p class="cr">{CREDIT}</p></div>')

# C: annotated (Nacre, on the band). A small title, the complex as a labelled diagram: ends above, parts below
boxC = (0, 200, 1440, 620)
P = {k: pt('c-annot', k, boxC) for k in A['c-annot']}
mockC = (f'<div class="mock" style="{tokens("nacre")};background:#F6EFEC">{head()}'
         f'<div class="cl"><p class="ey">{CG}<span>The ternary complex</span></p><h2 class="h2">One {SELFTAC} molecule holds the target and the ligase together.</h2></div>'
         f'<img src="img/c-annot.png" alt="" style="left:{boxC[0]}px;top:{boxC[1]}px;width:{boxC[2]}px;height:{boxC[3]}px">'
         + tag('Target-binding end', P['endW'][0], P['endW'][1] - 22, P['endW'][0] - 40, 352, 'up')
         + tag('Ligase-binding end', P['endE'][0], P['endE'][1] - 30, P['endE'][0] + 40, 352, 'up')
         + tag('Target protein<b>BRD4</b>', P['target'][0], P['target'][1] + 50, P['target'][0] - 30, 640)
         + tag('Reversible linker<b>The clasp, where the halves meet</b>', P['clasp'][0], P['clasp'][1] + 12, P['clasp'][0], 640, 'hi')
         + tag('E3 ligase<b>VHL with Elongin B and C</b>', P['ligase'][0], P['ligase'][1] + 58, P['ligase'][0] + 70, 640)
         + f'<p class="cr">{CREDIT}</p></div>')

# D: macro (Shell Coral). Close in on the linker and clasp on a rising diagonal, the target cropped into the bottom-left
# corner and the ligase off the top-right; the picture starts below the header, the line sits in the clear top-left
boxD = (0, 70, 1440, 810)
cx, cy = pt('d-macro', 'clasp', boxD)
mockD = (f'<div class="mock" style="{tokens("shellcoral")}">'
         f'<img src="img/d-macro.png" alt="" style="left:{boxD[0]}px;top:{boxD[1]}px;width:{boxD[2]}px;height:{boxD[3]}px">{head()}'
         f'<div class="dl"><p class="ey">{CG}<span>The clasp</span></p><h2 class="h1">Where two halves become one degrader.</h2>'
         f'<p class="lede">{SELFTAC} molecules travel as two small halves and close at a reversible linker inside the cell.</p>'
         f'{ctas("See how it works", "Our pipeline")}</div>'
         + tag('Reversible linker', cx, cy + 30, cx + 20, cy + 100, 'chip')
         + f'<p class="cr r">{CREDIT}</p></div>')

# E: D made abstract (Shell Coral). The ends of the degrader are plain glossy pods and the reversible linker's join is
# one large pearl, named as such: the pearl strand with the pearl at its heart
CREDIT_E = ('BRD4, VHL and Elongin B and C from PDB 5T35 (Gadd et al., Nat. Chem. Biol. 2017). The degrader is drawn abstractly '
            'and larger than true scale, with the proteins eased apart so its linker shows.')
PEARL = '<svg class="cg" viewBox="0 0 30 12" aria-hidden="true" style="width:14px"><circle cx="6" cy="6" r="5.4"/></svg>'   # one pearl, for the pearl
boxE = (0, 70, 1440, 810)
cx, cy = pt('e-pearl', 'clasp', boxE)
mockE = (f'<div class="mock" style="{tokens("shellcoral")}">'
         f'<img src="img/e-pearl.png" alt="" style="left:{boxE[0]}px;top:{boxE[1]}px;width:{boxE[2]}px;height:{boxE[3]}px">{head()}'
         f'<div class="dl"><p class="ey">{PEARL}<span>The pearl</span></p><h2 class="h1">Where two halves become one degrader.</h2>'
         f'<p class="lede">{SELFTAC} molecules travel as two small halves. Inside the cell they close at the pearl, a reversible linker, and rebuild the full degrader.</p>'
         f'{ctas("See how it works", "Our pipeline")}</div>'
         + tag('The pearl &middot; reversible linker', cx, cy + 62, cx + 20, cy + 120, 'chip')
         + f'<p class="cr r">{CREDIT_E}</p></div>')

MOCKS = [('A', 'Centre stage', 'Nacre', 'The complex runs across the middle under the line, with three plain labels. The calmest of the four.', mockA, 'a-centre'),
         ('B', 'Split', 'Tidepool', 'Copy on the left as on the current site, the complex in three-quarter view bleeding off the right edge, one chip on the clasp.', mockB, 'b-split'),
         ('C', 'Annotated', 'Nacre', 'The complex as a labelled diagram: both ends of the degrader, the linker and clasp, the target and the ligase. Most explanatory.', mockC, 'c-annot'),
         ('D', 'Macro', 'Shell Coral', 'Close in on the linker and clasp on a rising diagonal, the proteins cropped into opposite corners, the line top left. Most striking.', mockD, 'd-macro'),
         ('E', 'Macro, abstract', 'Shell Coral', 'D made abstract: each end of the degrader is a plain glossy pod, and the reversible linker meets at one large pearl, called the pearl. The linker is the only detailed thing in the picture.', mockE, 'e-pearl')]

page = '''<title>Oyster Hero Mockups</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=swap">
<style>
/* Layout: a column of four 1440 x 810 heroes, each drawn at full size and scaled to the column. The page around
   them is quiet paper; each hero carries its own palette. */
:root { --g-bg: #EFE6E1; --g-ink: #2B2230; --g-muted: #65586A; --g-accent: #8C5572; --g-line: rgba(43, 34, 48, .16); --g-card: #F6EFEC;
  --serif: "Newsreader", "Iowan Old Style", Georgia, serif; --sans: "Archivo", "Helvetica Neue", Arial, sans-serif; --mono: "IBM Plex Mono", ui-monospace, Menlo, monospace; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --g-bg: #1C171F; --g-ink: #EFE6E1; --g-muted: #B3A7B6; --g-accent: #D9A443; --g-line: rgba(239, 230, 225, .16); --g-card: #241E28; color-scheme: dark; } }
:root[data-theme="dark"] { --g-bg: #1C171F; --g-ink: #EFE6E1; --g-muted: #B3A7B6; --g-accent: #D9A443; --g-line: rgba(239, 230, 225, .16); --g-card: #241E28; color-scheme: dark; }
* { box-sizing: border-box; }
body { margin: 0; background: var(--g-bg); color: var(--g-ink); font: 400 16px/1.55 var(--sans); -webkit-font-smoothing: antialiased; }
.wrap { max-width: 1240px; margin: 0 auto; padding-block: 56px 80px; padding-inline: max(16px, 4vw); }
.top h1 { font: 500 clamp(36px, 5vw, 64px)/1.02 var(--serif); letter-spacing: -.02em; margin: 0; }
.top p { color: var(--g-muted); max-width: 62ch; margin: 18px 0 0; }
.k { font: 500 12px/1 var(--mono); letter-spacing: .14em; text-transform: uppercase; color: var(--g-accent); margin: 0 0 18px; }
section.v { margin-top: 64px; }
.vh { display: grid; grid-template-columns: auto minmax(0, 1fr); gap: 6px 18px; align-items: baseline; margin-bottom: 18px; }
.vh b { font: 500 13px/1 var(--mono); letter-spacing: .12em; text-transform: uppercase; color: var(--g-accent); }
.vh h2 { font: 500 clamp(24px, 2.4vw, 32px)/1.1 var(--serif); margin: 0; }
.vh p { grid-column: 2; margin: 0; color: var(--g-muted); max-width: 70ch; }
.frame { position: relative; width: 100%; aspect-ratio: 16 / 9; max-width: 100%; overflow: hidden; border-radius: 14px; border: 1px solid var(--g-line); background: var(--g-card); }
.frame .mock { transform: scale(var(--s, .5)); transform-origin: 0 0; }
.foot { margin-top: 72px; color: var(--g-muted); font-size: 14px; max-width: 80ch; }

/* ---------- a hero, at 1440 x 810 ---------- */
.mock { position: absolute; left: 0; top: 0; width: 1440px; height: 810px; overflow: hidden; font: 400 16px/1.55 var(--sans); }
.mock img { position: absolute; display: block; max-width: none; }
.mh { position: absolute; left: 40px; right: 40px; top: 22px; display: flex; align-items: center; gap: 28px; z-index: 2; color: var(--ink); }
.mh .wm { height: 42px; width: auto; display: block; }
.mh .wm .pearl { fill: var(--pearl); }
.mh nav { margin-left: auto; display: flex; gap: 22px; font: 500 13.5px/1 var(--sans); }
.cg { width: 30px; height: 12px; margin-right: 10px; vertical-align: -1px; overflow: visible; }
.cg line { stroke: var(--clasp); stroke-width: 3; stroke-linecap: round; }
.cg circle { fill: var(--clasp); stroke: var(--ink); stroke-width: 1.2; }
.ey { font: 500 12px/1 var(--mono); letter-spacing: .14em; text-transform: uppercase; color: var(--accent); margin: 0 0 24px; display: flex; align-items: center; }
.h1 { font: 500 64px/1.02 var(--serif); letter-spacing: -.02em; margin: 0; text-wrap: balance; }
.h2 { font: 500 44px/1.08 var(--serif); letter-spacing: -.015em; margin: 0; text-wrap: balance; }
.lede { font-size: 19px; color: var(--muted); margin: 22px 0 0; max-width: 46ch; }
.mc { display: flex; gap: 12px; margin-top: 34px; }
.b { display: inline-flex; align-items: center; gap: 10px; font: 500 14px/1 var(--sans); padding: 14px 20px; border-radius: 999px; background: var(--ink); color: var(--paper); border: 1px solid var(--ink); }
.b svg { width: 13px; height: 13px; }
.b.gh { background: transparent; color: var(--ink); border-color: var(--line); }
.cr { position: absolute; left: 40px; bottom: 20px; margin: 0; font-size: 11.5px; color: var(--muted); max-width: 92ch; z-index: 2; }
.cr.r { left: auto; right: 40px; text-align: right; max-width: 60ch; }
.ld { position: absolute; left: 0; top: 0; pointer-events: none; z-index: 1; }
.ld line { stroke: var(--ink); stroke-width: 1; stroke-opacity: .45; }
.ld circle { fill: var(--paper); stroke: var(--ink); stroke-width: 1.2; }
.tg { position: absolute; z-index: 2; transform: translate(-50%, 0); font: 500 11px/1.3 var(--mono); letter-spacing: .12em; text-transform: uppercase; color: var(--ink); white-space: nowrap; text-align: center; padding-top: 6px; }
.tg b { display: block; font: 400 13px/1.35 var(--sans); letter-spacing: 0; text-transform: none; color: var(--muted); margin-top: 6px; }
.tg.up { transform: translate(-50%, -100%); padding: 0 0 6px; }
.tg.hi { color: var(--ink); }
.tg.hi::before { content: ""; display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: var(--clasp); margin-right: 8px; vertical-align: 0; box-shadow: 0 0 0 3px color-mix(in srgb, var(--clasp) 30%, transparent); }
.tg.chip { transform: translate(-50%, 0); padding: 9px 14px; border-radius: 999px; background: color-mix(in srgb, var(--paper) 80%, transparent); border: 1px solid var(--line); backdrop-filter: blur(6px); }
.tg.chip::before { content: ""; display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: var(--clasp); margin-right: 9px; }
/* A */ .ac { position: absolute; left: 0; right: 0; top: 118px; text-align: center; display: grid; justify-items: center; z-index: 2; }
.ac .ey { justify-content: center; } .ac .h1 { font-size: 58px; } .ac .lede { margin-top: 16px; max-width: 54ch; }
.ab { position: absolute; left: 0; right: 0; top: 708px; display: grid; justify-items: center; } .ab .mc { margin: 0; }
/* B */ .bl { position: absolute; left: 96px; top: 200px; width: 540px; z-index: 2; } .bl .h1 { font-size: 58px; }
/* C */ .cl { position: absolute; left: 96px; top: 120px; width: 640px; z-index: 2; }
/* D */ .dl { position: absolute; left: 96px; top: 118px; width: 600px; z-index: 2; } .dl .h1 { font-size: 54px; } .dl .lede { margin-top: 16px; max-width: 46ch; } .dl .mc { margin-top: 26px; }
</style>
<div class="wrap">
  <header class="top"><p class="k">Oyster &middot; Website v2</p><h1>Hero mockups</h1>
  <p>Four static heroes built around one still of the ternary complex: the target protein on the left, the E3 ligase on the right, and a SELFTAC&reg; degrader between them with its reversible linker, the pearl strand and gold clasp, in plain view. Every still is rendered from the website&rsquo;s own 3D models and colours.</p></header>
<!--MOCKS-->
  <p class="foot">The degrader is drawn larger than true scale, and the two proteins are eased apart a little, so both of its ends and the whole linker show. At true scale it sits almost entirely inside the two proteins. Structures: BRD4, VHL and Elongin B and C from PDB 5T35 (Gadd et al., Nat. Chem. Biol. 2017). The degrader is generic and stands in for a SELFTAC&reg; compound.</p>
</div>
<script>
// draw each hero at 1440 wide and scale it to its frame
(() => {
  const fit = () => document.querySelectorAll('.frame').forEach(f => f.style.setProperty('--s', (f.clientWidth / 1440).toFixed(4)));
  fit(); addEventListener('resize', fit);
  if (window.ResizeObserver) new ResizeObserver(fit).observe(document.querySelector('.wrap'));
})();
</script>
'''
body = ''.join(f'<section class="v" id="{key}"><div class="vh"><b>{l}</b><h2>{n} &middot; {p}</h2><p>{d}</p></div>'
               f'<div class="frame" role="img" aria-label="Hero mockup {l}, {n}, in the {p} palette">{m}</div></section>\n'
               for l, n, p, d, m, key in MOCKS)
open(D + 'index.html', 'w').write(page.replace('<!--MOCKS-->', body))
print('index.html', os.path.getsize(D + 'index.html') // 1024, 'KB')
