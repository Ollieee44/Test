"""Build the SELFTAC journey (journey/index.html): the slide's story told left to right as the page scrolls, with the
site's own 3D models. Oral dosing; the dimer and its monomers in equilibrium; across the cell membrane and the
blood-brain barrier; the halves clasped back together in a ternary complex; tagging and the proteasome.

The scene setup (palettes, renderer, the protein parts, the degrader, ubiquitin, the proteasome) is the story's own,
taken from ../../palettes.html up to its timeline; journey.js adds the left-to-right timeline. The page shell is the
v2 Science page's styles (site.css, published beside it). It stands alone, in the Tidepool palette only: no header,
palette switch or page sections, and the structure credit sits in the end card.
The person, the gut, the absorption beam and the membrane are flat illustrations drawn in the 3D scene's plane.
Run ../build_v2.py first."""
import json, math, os, re
D = os.path.dirname(os.path.abspath(__file__)) + '/'
SITE = D + '../../'
pal = open(SITE + 'palettes.html').read()
module = pal[pal.index('<script type="module">') + len('<script type="module">'):]
module = module[:module.index('</script>')]
prefix = module[:module.index('// ---------- the story ----------')]
sci = open(D + '../pages/science.html').read()

def once(s, old, new):
    assert old in s, old[:60]
    return s.replace(old, new, 1)

# ---------- head: the Science page's, retitled, with the journey's styles ----------
head = sci[:sci.index('<canvas id="bgArt"')]
head = re.sub(r'<title>.*?</title>', '<title>SELFTAC Journey</title>', head)
head = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="How a SELFTAC degrader goes from a pill to a cleared protein, told left to right as you scroll.">', head)
CSS = '''<style>
/* the journey: a pinned stage that pans left to right; flat illustration under the 3D, labels over it */
.story { height: 1150vh; }
@media (max-width: 760px) { .story { height: 1000vh; } }
.jsvg { position: absolute; inset: 0; width: 100%; height: 100%; display: block; overflow: visible; }
.jsvg path, .jsvg circle, .jsvg rect, .jsvg line { vector-effect: non-scaling-stroke; }
.jl { position: absolute; left: 0; top: 0; z-index: 2; font: 500 11px/1.25 var(--mono); letter-spacing: .12em; text-transform: uppercase; color: var(--ink);
  white-space: nowrap; pointer-events: none; text-align: center; opacity: 0; padding: 6px 10px; border-radius: 999px;
  background: color-mix(in srgb, var(--paper) 55%, transparent); -webkit-backdrop-filter: blur(4px); backdrop-filter: blur(4px); }
.jl.hi { color: var(--accent); }
.jl.plus { font: 500 34px/1 var(--serif); color: var(--ink); background: none; padding: 0; -webkit-backdrop-filter: none; backdrop-filter: none; }
.jl.eq { background: none; padding: 0; -webkit-backdrop-filter: none; backdrop-filter: none; }
.jl.eq svg { width: 52px; height: 24px; display: block; }
@media (max-width: 760px) { .jl { font-size: 9.5px; padding: 4px 8px; } .jl.eq svg { width: 40px; height: 18px; } }
/* five beats on the rail, the fourth (the clasp closing) the gold one */
.rail { grid-template-columns: repeat(5, minmax(0, 1fr)); }
.rail div:nth-child(5)::before { width: 12px; height: 12px; }
.rail div:nth-child(5).on::before { background: #fff; box-shadow: none; }
.rail div:nth-child(4)::before { width: 14px; height: 14px; }
.rail div:nth-child(4).on::before { background: var(--clasp); border-color: var(--ink); box-shadow: 0 0 0 5px color-mix(in srgb, var(--clasp) 28%, transparent); }
</style>
'''
head += CSS

# ---------- header: the logo and the palette switch (no page links: this page stands alone) ----------
header = re.search(r'<header class="head".*?</header>', sci, re.S).group(0)
header = re.sub(r'<nav id="nav".*?</nav>', '', header, flags=re.S)
header = re.sub(r'<button type="button" class="menu-btn".*?</button>', '', header, flags=re.S)
header = header.replace('href="index.html"', 'href="#story"', 1)
CG = re.search(r'<svg class="cg".*?</svg>', sci, re.S).group(0)
end = re.search(r'<div class="end" id="end">.*?</div>', sci, re.S).group(0)
end = re.sub(r'<a href="#[^"]*">[^<]*</a>', '<a href="#more">About this story</a>', end)

# ---------- the flat layer, in world units with y up (see journey.js) ----------
X = dict(person=0, dimer=150, mono=238, mem=345, inside=420, complex=470, prot=640)
R, BAND = 300, 18
cx = X['mem'] + R
def arc(r, a0, a1, n):
    return [(cx + r * math.cos(math.radians(a)), r * math.sin(math.radians(a))) for a in [a0 + (a1 - a0) * i / n for i in range(n + 1)]]
outer, innr = arc(R, 140, 220, 120), arc(R + BAND, 140, 220, 120)
band = 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in outer + innr[::-1]) + ' Z'
heads, tails = [], []
for r, inward in ((R, 1), (R + BAND, -1)):
    n = int(2 * math.pi * r * 80 / 360 / 5.4)
    for x, y in arc(r, 140, 220, n):
        heads.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.1"/>')
        ux, uy = (x - cx) / r, y / r
        tails.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x + inward * ux * 6:.1f}" y2="{y + inward * uy * 6:.1f}"/>')
membrane = (f'<g id="jmem"><path d="{band}" style="fill:var(--ink);fill-opacity:.07"/>'
            f'<g style="stroke:var(--ink);stroke-opacity:.28;stroke-width:1">{"".join(tails)}</g>'
            f'<g style="fill:var(--muted);fill-opacity:.75">{"".join(heads)}</g></g>')
# the person in side profile, facing right, drawn y-down and flipped into the world (the lips about y -42, the gut at
# y -25): the head, the jaw into the throat, chest and back, with a faint edge
# a natural skull, the face one smooth curve from the forehead with only the lips and chin shaped (no nose or ear),
# the jaw, and a neck into the chest
HEAD_NECK = ('M -2,-78 C 8,-79 15,-73 17,-64 C 18.2,-58 18.6,-53 18.2,-49 C 18.4,-47.5 19.4,-46.6 19.6,-45.6 '
             'C 19.7,-44.8 19,-44.2 18.4,-44 C 19.2,-43.4 19.4,-42.2 18.8,-41.4 C 18,-40.4 17,-40 17.4,-38.6 '
             'C 17.8,-36.6 17.2,-34.4 15,-33.4 C 12,-32.2 8.5,-32 6.5,-31 C 6.6,-26 7,-18 8,-12 ')
FRONT = 'C 11,-8 16,-5 19,1 C 23,9 24,16 23,26 C 22.5,34 23.5,42 24,52 C 24.5,62 23.5,72 23,88'
BACK = ('M -21,88 C -21.5,70 -22,56 -21,44 C -20,34 -19.5,24 -20.5,14 C -21.5,4 -21,-4 -17,-10 C -15,-14 -13,-19 -12,-24 '
        'C -12,-29 -13.5,-33 -15.5,-37 C -20,-43 -22,-55 -19,-65 C -16,-73 -10,-78 -2,-78')
PERSON_D = HEAD_NECK + FRONT + ' L -21,88 ' + BACK[len('M -21,88 '):] + ' Z'          # the filled silhouette
EDGE_D = HEAD_NECK + FRONT + ' M ' + BACK[2:]                                       # its outline, open at the bottom
ARM = 'M -9,-8 C -7,-15 4,-17 9,-10 C 12,-5 11,8 10,24 C 9.5,34 9,42 8,50 C 6,53 -6,53 -8,50 C -9.5,40 -10.5,20 -9,-8 Z'
EAR = 'M -2.5,-55 C 1,-56 2.5,-52 1.8,-49 C 1.2,-46.5 -1,-45.5 -2.6,-46.4'
# the gut, front view in an inset: the oesophagus in at the top, a J-shaped stomach, the small intestine coiled in
# the middle, and the large intestine framing it down to the rectum; each tube an ink outline round a light core
def tube(d, w, core):
    return (f'<path d="{d}" style="fill:none;stroke:var(--ink);stroke-width:{w};stroke-linecap:round;stroke-linejoin:round"/>'
            f'<path d="{d}" style="fill:none;stroke:var(--paper);stroke-width:{core};stroke-linecap:round;stroke-linejoin:round"/>')
COLON = 'M 0 40 C -6 41 -13 40 -13.5 35 L -13.5 21 C -13.5 17.5 -11 16 -7 16 L 7 16.5 C 11 16.5 13.5 18 13.5 22 L 13.5 33 C 13.5 37.5 9.5 39 5.5 39.5 L 2.5 40.5 L 2.5 45.5'
SMALL = 'M 6 20.5 C 2 19.3 -6 19.3 -8.5 21.3 C -10 23.3 -6 24.8 0 24.4 C 6 24 9.5 25 9 27.4 C 8.5 29.9 3 30 -2 29.6 C -7 29.2 -10 30.6 -8.5 33 C -7 35 0 35.4 4 34.6'
# the stomach as a filled J: the oesophagus comes in at its top left, the sac swells to the right and narrows
# back toward the middle, where the duodenum leaves for the small intestine
STOMACH = 'M -1.6 3.2 L -1.6 6.2 C -1.6 9.6 1.4 12.2 5.2 12.6 C 9.2 13 12.8 11.4 12.9 8.2 C 13 5.2 10.4 3.4 7.6 4.6 C 5.8 5.4 4.6 6.6 3 6.6 C 1.6 6.6 1.2 5.4 1.2 3.2 Z'
GUT = (f'<circle cx="0" cy="25" r="22" style="fill:var(--paper);fill-opacity:.92;stroke:var(--ink);stroke-width:1.6"/>'
       f'<circle id="jgutring" cx="0" cy="25" r="25.5" style="fill:none;stroke:var(--accent);stroke-width:2;opacity:0"/>'
       f'<g id="jtract">{tube(COLON, 4.4, 2)}{tube(SMALL, 3.2, 1.3)}<path d="{STOMACH}" style="fill:var(--paper);stroke:var(--ink);stroke-width:1.5;stroke-linejoin:round"/><path d="M 4.5 12.4 C 4.5 15 3 17 1 18.6" style="fill:none;stroke:var(--ink);stroke-width:1.5;stroke-linecap:round"/></g>')
# the capsule's route: in at the lips, back through the mouth, down the middle of the neck and the chest to the gut
ROUTE = 'M 18.6,-44.4 C 13,-43.5 7,-41 4.5,-37 C 2,-32 1.5,-25 1.5,-18 C 1.5,-10 0.8,-3 0.5,2.5'
person = (f'<g id="jperson"><g transform="scale(1 -1)">'
          f'<path d="{PERSON_D}" style="fill:url(#jpersonG)"/>'
          f'<path d="{ARM}" style="fill:var(--ink);fill-opacity:.05;stroke:url(#jedgeG);stroke-width:1"/>'
          f'<path d="{EDGE_D}" style="fill:none;stroke:url(#jedgeG);stroke-width:1.1;stroke-linejoin:round;stroke-linecap:round"/>'
          f'<path id="jroute" d="{ROUTE}" style="fill:none;stroke:var(--accent);stroke-opacity:.7;stroke-width:1.4;stroke-dasharray:2 3;stroke-linecap:round;opacity:0"/>'
          f'</g></g>'
          f'<g id="jgut"><g transform="scale(1 -1)">{GUT}</g></g>')
pill = ('<g id="jpill"><rect x="-8" y="-3.2" width="16" height="6.4" rx="3.2" style="fill:var(--mol-b, #8A73B2)"/>'
        '<path d="M 0 -3.2 L -4.8 -3.2 A 3.2 3.2 0 0 0 -4.8 3.2 L 0 3.2 Z" style="fill:var(--mol-a, #B4678B)"/>'
        '<rect x="-.9" y="-3.2" width="1.8" height="6.4" style="fill:var(--mol-c, #D9A443)"/>'
        '<rect x="-8" y="-3.2" width="16" height="6.4" rx="3.2" style="fill:none;stroke:var(--ink);stroke-width:1.2"/></g>')
beam = f'<path id="jbeam" d="M 19 -12 L {X["mem"] - 6} 95 L {X["mem"] - 6} -135 L 19 -38 Z" style="fill:url(#jbeamG)"/>'
svg = (f'<svg id="jsvg" class="jsvg" aria-hidden="true"><defs>'
       f'<linearGradient id="jbeamG" gradientUnits="userSpaceOnUse" x1="19" y1="0" x2="{X["mem"]}" y2="0">'
       '<stop offset="0" style="stop-color:var(--accent);stop-opacity:.24"/><stop offset=".55" style="stop-color:var(--accent);stop-opacity:.09"/><stop offset="1" style="stop-color:var(--accent);stop-opacity:.02"/></linearGradient>'
       '<linearGradient id="jpersonG" gradientUnits="userSpaceOnUse" x1="0" y1="-80" x2="0" y2="80">'
       '<stop offset="0" style="stop-color:var(--ink);stop-opacity:.16"/><stop offset=".75" style="stop-color:var(--ink);stop-opacity:.12"/><stop offset="1" style="stop-color:var(--ink);stop-opacity:0"/></linearGradient>'
       '<linearGradient id="jedgeG" gradientUnits="userSpaceOnUse" x1="0" y1="-84" x2="0" y2="88">'
       '<stop offset="0" style="stop-color:var(--ink);stop-opacity:.38"/><stop offset=".72" style="stop-color:var(--ink);stop-opacity:.3"/><stop offset="1" style="stop-color:var(--ink);stop-opacity:0"/></linearGradient>'
       f'</defs><g id="jworld">{beam}{membrane}{person}{pill}</g></svg>')

EQ = ('<svg viewBox="0 0 52 24" aria-hidden="true"><path d="M4 8 H46 L39 3" fill="none" stroke="var(--clasp)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>'
      '<path d="M48 16 H6 L13 21" fill="none" stroke="var(--clasp)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>')
def label(text, x, y, a, b, cls=''):
    return f'<span class="jl {cls}" data-x="{x}" data-y="{y}" data-a="{a}" data-b="{b}">{text}</span>'
labels = ('<span class="jl plus" id="jplus">+</span><span class="jl" id="jdimer">Dimer</span><span class="jl" id="jmono">Monomers</span>'
          f'<span class="jl eq" id="jeq">{EQ}</span>') + ''.join([
    label('Oral dosing', 74, 78, -1, .13),
    label('In the gut', 0, 1.5, .2, .34, 'hi'),
    label('Cell membrane &middot; blood-brain barrier', X['mem'] + 4, -50, .42, .62),
    label('Target cell', X['mem'] + 70, 52, .5, .62, 'hi'),
    label('Target protein', X['complex'] + 62, 58, .64, .84), label('E3 ligase', X['complex'] + 66, -62, .64, .84),
    label('Ternary complex', X['complex'], -96, .68, .84, 'hi'),
    label('Proteasome', X['prot'], 50, .84, .99), label('Degradation', X['prot'], -86, .915, .99, 'hi'),
])
TM = '<span translate="no">SELFTAC&reg;</span>'
beats = [
    ('01 &middot; Oral dosing', 'h1', 'Taken by mouth, as a pill.', f'{TM} degraders are designed to be small enough to be swallowed, not injected.'),
    ('02 &middot; In the gut', 'h2', 'The dimer comes apart into two monomers.', f'In the gut, each {TM} dimer dissociates at its reversible linker into two small monomers, which are absorbed.'),
    ('03 &middot; The barrier', 'h2', 'Small enough to cross into the cell.', 'As monomers, each half crosses the cell membrane, and the blood-brain barrier into the brain.'),
    ('04 &middot; Ternary complex', 'h2', 'Inside the cell, the halves clasp back together.', 'One end holds the target protein, the other an E3 ligase: a ternary complex.'),
    ('05 &middot; Degradation', 'h2', 'Tagged, then broken down.', 'Ubiquitin marks the target and the proteasome destroys it. The degrader is free to find the next one.'),
]
copy = ''.join(f'<div class="beat"><span class="k">{k}</span><{h}>{t}</{h}><p>{d}</p></div>' for k, h, t, d in beats)
rail = ''.join(f'<div><span>{n}</span><i><b></b></i></div>' for n in ('Oral', 'Gut', 'Barrier', 'Complex', 'Degraded'))
DOWN = '<svg viewBox="0 0 14 14" aria-hidden="true"><path d="M7 2v10M3 8l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
# a standalone animation in Tidepool: no header, palette switch or page sections; the credit sits in the end card
end = end.replace('<a href="#more">About this story</a>',
                  '<a href="#story">Watch again</a><p class="ecr">BRD4, VHL and Elongin B and C from PDB 5T35 (Gadd et al., Nat. Chem. Biol. 2017), ubiquitin from PDB 1UBQ. '
                  f'The degrader is generic and stands in for a {TM} compound; the proteasome is a stand-in, and the person, gut and membrane are illustrations.</p>')
story = (f'<section class="story" id="story" aria-label="How a SELFTAC degrader goes from a pill to a cleared protein">'
         f'<div class="stage" id="stage">{svg}<canvas id="gl" aria-hidden="true"></canvas>{labels}'
         f'<div class="copy" id="copy">{copy}</div>{end}'
         f'<div class="hint" id="hint"><span>Scroll to follow a {TM} molecule</span><i aria-hidden="true"></i></div>'
         f'<a class="skip" id="skip" href="#storyEnd">Skip to the end{DOWN}</a>'
         f'<div class="rail" id="rail" aria-hidden="true">{rail}</div></div><div id="storyEnd" class="story-end"></div></section>\n')
SMALL = """<script type="module">
// the skip control stays until the end card; every visit starts at the top
const skip = document.getElementById('skip'), story = document.getElementById('story');
try { history.scrollRestoration = 'manual'; } catch (e) {}
if (location.hash.length < 2) scrollTo(0, 0);
let q = false;
addEventListener('scroll', () => { if (q) return; q = true; requestAnimationFrame(() => { q = false; const r = story.getBoundingClientRect();
  skip.classList.toggle('gone', -r.top / Math.max(1, r.height - innerHeight) > .92); }); }, { passive: true });
</script>
"""
head = head.replace('<html lang="en">', '<html lang="en" data-palette="tidepool">', 1)
head = re.sub(r'<meta name="theme-color" content="[^"]*">', '<meta name="theme-color" content="#0F4C4A">', head)
head = head.replace('</style>\n', """.story-end { position: absolute; left: 0; right: 0; bottom: 0; height: 100vh; height: 100svh; pointer-events: none; }
.end .ecr { max-width: 62ch; margin: 6px auto 0; padding: 0 24px; font: 400 12px/1.5 var(--sans); color: var(--muted); }
.skip { top: auto; }
@media (max-width: 760px) { .skip { top: calc(16px + env(safe-area-inset-top, 0px)); bottom: auto; } .hint { top: calc(70px + env(safe-area-inset-top, 0px)); } }
</style>\n""", 1)
meshes = re.search(r'<script type="application/json" id="meshes">.*?</script>', sci, re.S).group(0)
page = (head + '<main id="main">\n' + story + '</main>\n' + meshes + '\n<script type="module">' + prefix + "\npal = 'tidepool';   // Tidepool only\n" + open(D + 'journey.js').read() + '</script>\n' + SMALL)
open(D + 'index.html', 'w').write(page)
print('index.html', os.path.getsize(D + 'index.html') // 1024, 'KB')

# ---------- the oyster-tx.com theme (otx/index.html): the same journey restyled after the new site ----------
# Emerald ground with a speckle of tiny dots, Geist and Monomaniac One, translucent rounded controls, proteins as
# particle clouds (otx.js), the degrader in the site's icon colours (pink to the target, pale blue to the ligase,
# a yellow join), and the site's headline and mark on the end card. Colours sampled from the site's screenshots.
import random, urllib.parse
rnd = random.Random(11)
dots = []
for _ in range(300):
    r = rnd.random()
    col = '#FFFFFF' if r < .55 else '#CFFFFF' if r < .8 else rnd.choice(['#F7D16B', '#96FF87', '#FFB36B'])
    dots.append(f'<circle cx="{rnd.uniform(0, 520):.1f}" cy="{rnd.uniform(0, 520):.1f}" r="{rnd.uniform(.5, 1.35):.2f}" fill="{col}" fill-opacity="{rnd.uniform(.22, .85):.2f}"/>')
STARS = 'data:image/svg+xml,' + urllib.parse.quote('<svg xmlns="http://www.w3.org/2000/svg" width="520" height="520">' + ''.join(dots) + '</svg>')
OTX_CSS = '''<style>
/* oyster-tx.com: emerald, white type with mint accents, Geist and Monomaniac One, translucent rounded controls */
:root[data-palette="otx"] { --ink: #F5FFFC; --muted: #A8D8C6; --accent: #30FCBA; --paper: #158B63; --band: #12805B; --pearl: #F7D16B; --clasp: #F7D16B;
  --line: rgba(245, 255, 252, .22); --card: rgba(255, 255, 255, .08); --sans: "Geist", "Helvetica Neue", Arial, sans-serif; --mono: "Geist Mono", ui-monospace, Menlo, monospace;
  --pixel: "Monomaniac One", "Geist Mono", ui-monospace, monospace; color-scheme: dark; }
body { font-family: var(--sans); }
.jstars { position: absolute; inset: 0; pointer-events: none; background-image: url("''' + STARS + '''"); background-size: 520px 520px; opacity: .9; }
.beat .k { font: 400 15px/1 var(--pixel); letter-spacing: .03em; text-transform: uppercase; color: var(--ink); }
.beat .k b { font-weight: 400; color: #8AC3B1; margin-right: 8px; }
.beat h1, .beat h2 { font-weight: 400; color: #FFFFFF; }
.beat p { color: rgba(245, 255, 252, .84); font-family: var(--sans); }
.jl { font: 400 11px/1.25 var(--mono); letter-spacing: .14em; background: rgba(12, 92, 64, .55); border-radius: 6px; }
.jl.hi { color: var(--accent); }
.jl.plus { font: 400 34px/1 var(--serif); }
.skip, .end a { border-radius: 12px; background: rgba(255, 255, 255, .17); border: 1px solid rgba(255, 255, 255, .12); color: #FFFFFF; font: 500 14px/1 var(--sans); }
.skip:hover, .end a:hover { background: rgba(255, 255, 255, .28); color: #FFFFFF; border-color: rgba(255, 255, 255, .2); }
.rail span { font: 400 12px/1 var(--pixel); letter-spacing: .04em; }
.hint { font-family: var(--mono); }
.end .otx-logo { width: min(40vw, 420px); height: auto; color: #FFFFFF; }
.end .tag { margin: 0; font: 400 clamp(26px, 3.2vw, 50px)/1.06 var(--serif); letter-spacing: -.015em; color: #FFFFFF; text-wrap: balance; }
.end .tag em { font-style: normal; color: var(--accent); }
@media (max-width: 760px) { .end .otx-logo { width: 62vw; } .beat .k { font-size: 13px; } }
</style>
'''
# the site's logo, traced from a screenshot of oyster-tx.com (trace_otx_logo.py writes otx_logo.svg); swap in the
# real file when there is one
OTX_LOGO = open(D + 'otx_logo.svg').read().replace('<svg ', '<svg class="otx-logo" role="img" aria-label="Oyster Therapeutics" translate="no" ', 1)
otx_story = story.replace('<div class="stage" id="stage">', '<div class="stage" id="stage"><div class="jstars" id="jstars" aria-hidden="true"></div>', 1)
otx_story = re.sub(r'<span class="k">(\d\d) &middot; ([^<]+)</span>', r'<span class="k"><b>\1</b>\2</span>', otx_story)
otx_story = re.sub(r'<svg class="lt".*?</svg>', OTX_LOGO, otx_story, count=1, flags=re.S)
otx_story = once(otx_story, '<p>Oral, brain-penetrant protein degraders.</p>', '<p class="tag">Targeted protein degradation <em>beyond conventional limits.</em></p>')
otx_head = head.replace('data-palette="tidepool"', 'data-palette="otx"', 1)
otx_head = otx_head.replace('<title>SELFTAC Journey</title>', '<title>SELFTAC Journey, New Site</title>', 1)
otx_head = re.sub(r'<meta name="theme-color" content="[^"]*">', '<meta name="theme-color" content="#158B63">', otx_head)
otx_head = re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/css2\?[^"]*">',
                  '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500&family=Monomaniac+One&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=swap">', otx_head)
otx_head += OTX_CSS
OTX_PAL = ("PAL.otx = { ...PAL.tidepool, ring: '#0F5A41', ink: '#0B3B2B', brd4: '#F0A6CA', vhl: '#CEE5F3', elob: '#6CFEED', eloc: '#30FCBA', "
           "warhead: '#F0A6CA', e3lig: '#CEE5F3', linker: '#F5FFFC', brk: '#F7D16B', ub: '#F0A6CA', pearl3d: '#FFFFFF', clasp: '#F7D16B', "
           "e2: '#CEE5F3', prot: '#6CFEED', wall: '#2E9E78', cell: '#2E9E78', flash: '#F7D16B', "
           "sky: [['#1A9A6E', '#158B63'], ['#1A9A6E', '#158B63'], ['#17845F', '#0F6A4E']] };\npal = 'otx';   // the oyster-tx.com palette only\n")
otx_prefix = once(prefix, "import * as THREE from 'three';", "import * as THREE from 'three';\nimport { MeshSurfaceSampler } from 'three/addons/math/MeshSurfaceSampler.js';")
os.makedirs(D + 'otx', exist_ok=True)
otx_page = (otx_head + '<main id="main">\n' + otx_story + '</main>\n' + meshes + '\n<script type="module">' + otx_prefix + '\n' + OTX_PAL
            + open(D + 'journey.js').read() + '\n' + open(D + 'otx.js').read() + '</script>\n' + SMALL)
open(D + 'otx/index.html', 'w').write(otx_page)
print('otx/index.html', os.path.getsize(D + 'otx/index.html') // 1024, 'KB')

# ---------- the plasma version (plasma/index.html): the oyster-tx.com journey with a bloodstream beat ----------
# After the gut, the bloodstream holds dimers and monomers together; at the membrane a dimer bounces off while the
# monomers pass through (plasma.js, which also re-times the journey and its copy to six beats).
pl_beats = [
    ('01 &middot; Oral dosing', 'h1', 'Taken by mouth, as a pill.', f'{TM} degraders are designed to be small enough to be swallowed, not injected.'),
    ('02 &middot; In the gut', 'h2', 'The dimer comes apart into two monomers.', f'In the gut, each {TM} dimer dissociates at its reversible linker into two small monomers, which are absorbed.'),
    ('03 &middot; In the bloodstream', 'h2', 'Dimer and monomers, side by side.', 'Absorbed into the blood vessels, they circulate in plasma. The linker is reversible, so all three exist together: the intact dimer and both of its monomers, in equilibrium.'),
    ('04 &middot; The barrier', 'h2', 'Only the monomers get through.', 'The dimer is too large to penetrate the cell membrane or the blood-brain barrier. Each small monomer passes through on its own.'),
    ('05 &middot; Ternary complex', 'h2', 'Inside the cell, the halves clasp back together.', 'One end holds the target protein, the other an E3 ligase: a ternary complex.'),
    ('06 &middot; Degradation', 'h2', 'Tagged, then broken down.', 'Ubiquitin marks the target and the proteasome destroys it. The degrader is free to find the next one.'),
]
pl_copy = ''.join(f'<div class="beat"><span class="k"><b>{k.split(" &middot; ")[0]}</b>{k.split(" &middot; ")[1]}</span><{h}>{t}</{h}><p>{d}</p></div>' for k, h, t, d in pl_beats)
pl_rail = ''.join(f'<div><span>{n}</span><i><b></b></i></div>' for n in ('Oral', 'Gut', 'Plasma', 'Barrier', 'Complex', 'Degraded'))
pl_labels = ''.join(f'<span class="jl {c}" data-pl="{at}" data-a="{a}" data-b="{b}">{t}</span>' for at, t, a, b, c in [
    ('plasma', 'Blood vessel &middot; plasma', .39, .52, 'hi'),
    ('bounce', 'Dimer: too large to penetrate', .588, .69, 'hi'), ('pass', 'Monomers pass through', .6, .69, 'hi')])
pl_story = re.sub(r'<div class="copy" id="copy">.*?</div></div>(?=<div class="end")', '<div class="copy" id="copy">' + pl_copy + '</div>', otx_story, count=1, flags=re.S)
assert pl_copy in pl_story, 'copy not replaced'
pl_story = re.sub(r'<div class="rail" id="rail" aria-hidden="true">.*?</div></div><div id="storyEnd"', f'<div class="rail" id="rail" aria-hidden="true">{pl_rail}</div></div><div id="storyEnd"', pl_story, count=1, flags=re.S)
pl_story = pl_story.replace('<div class="copy" id="copy">', pl_labels + '<div class="copy" id="copy">', 1)
# the blood vessel from the gut to the barrier, in the flat layer (world units, y up): two walls widening out of the gut,
# a faint plasma fill, and a few red blood cells (in the site's pink) that drift along it; its far end meets the membrane
VY = 66; VX1 = X['mem'] + R - math.sqrt((R + BAND) ** 2 - VY ** 2)   # the membrane's blood-facing surface at the walls
wall_t = f'M 16 -14 C 46 -10 64 {VY} 112 {VY} L {VX1:.1f} {VY}'
wall_b = f'M 16 -36 C 46 -40 64 {-VY} 112 {-VY} L {VX1:.1f} {-VY}'
lumen = f'M 16 -14 C 46 -10 64 {VY} 112 {VY} L {VX1:.1f} {VY} L {VX1:.1f} {-VY} L 112 {-VY} C 64 {-VY} 46 -40 16 -36 Z'
rnd2 = random.Random(5); rbcs = ''
for i in range(9):
    x, y, r, a = rnd2.uniform(120, VX1 - 30), rnd2.uniform(-VY + 14, VY - 14), rnd2.uniform(6, 8.5), rnd2.uniform(-40, 40)
    rbcs += (f'<g transform="translate({x:.1f} {y:.1f}) rotate({a:.0f})"><ellipse rx="{r:.1f}" ry="{r * .62:.1f}" style="fill:#F59BC8;fill-opacity:.72;stroke:#FBC6E0;stroke-opacity:.9;stroke-width:1"/>'
             f'<ellipse rx="{r * .45:.1f}" ry="{r * .24:.1f}" style="fill:#D9719F;fill-opacity:.55"/></g>')
VESSEL = (f'<g id="jvessel" style="opacity:0"><path d="{lumen}" style="fill:#FFFFFF;fill-opacity:.07"/>'
          f'<g id="jrbc">{rbcs}</g>'
          + ''.join(f'<path d="{w}" style="fill:none;stroke:var(--ink);stroke-opacity:.16;stroke-width:9;stroke-linecap:round"/>'
                    f'<path d="{w}" style="fill:none;stroke:var(--ink);stroke-opacity:.55;stroke-width:1.3;stroke-linecap:round"/>' for w in (wall_t, wall_b))
          + '</g>')
pl_story = once(pl_story, '<g id="jmem">', VESSEL + '<g id="jmem">')
pl_head = otx_head.replace('<title>SELFTAC Journey, New Site</title>', '<title>SELFTAC Journey, Plasma</title>', 1)
pl_head += '''<style>
#jbeam { display: none; }   /* the vessel carries the molecules from the gut instead */
/* labels on each molecule in the bloodstream: small on the crowd, larger and highlighted on the focal ones */
.jl.sm { font-size: 9px; letter-spacing: .1em; padding: 3px 7px; background: rgba(12, 92, 64, .45); color: rgba(245, 255, 252, .85); }
.jl.big { font-size: 12.5px; font-weight: 500; letter-spacing: .12em; padding: 6px 11px; color: var(--accent); background: rgba(9, 70, 49, .78); border: 1px solid rgba(48, 252, 186, .45); }
@media (max-width: 760px) { .jl.sm { font-size: 8px; padding: 2px 5px; } .jl.big { font-size: 10px; padding: 4px 8px; } }
/* six beats: a longer scroll, and the gold pearl on the fifth (the clasp closing) */
.story { height: 1550vh; }
@media (max-width: 760px) { .story { height: 1350vh; } }
.rail { grid-template-columns: repeat(6, minmax(0, 1fr)); }
.rail div:nth-child(4)::before { width: 12px; height: 12px; }
.rail div:nth-child(4).on::before { background: #fff; box-shadow: none; border-color: var(--ink); }
.rail div:nth-child(5)::before { width: 14px; height: 14px; }
.rail div:nth-child(5).on::before { background: var(--clasp); border-color: var(--ink); box-shadow: 0 0 0 5px color-mix(in srgb, var(--clasp) 28%, transparent); }
</style>
'''
pl_js = open(D + 'journey.js').read()
pl_js = once(pl_js, 'const BEATS = [[0, .17], [.17, .42], [.42, .6], [.6, .8], [.8, 1]];', 'const BEATS = [[0, .17], [.17, .42], [.42, .6], [.6, .8], [.8, 1], [2, 3]];   // plasma.js sets the six beats')
pl_js = once(pl_js, '  const p = clamp(p0, 0, 1);', '  const p = WARP(clamp(p0, 0, 1));   // the journey\'s own timeline, held back for the bloodstream beat')
pl_js = once(pl_js, "const LABELS = [...document.querySelectorAll('.jl[data-x]')]", "const LABELS = [...document.querySelectorAll('.jl[data-x]:not([data-pl])')]")
# goTo: move the journey without drawing; its own loop draws once per screen refresh (the click version's transitions)
pl_js = once(pl_js, 'setPal: v => { pal = v; applyPalette(); } };', 'goTo: p => { hold = true; prog = p; }, setPal: v => { pal = v; applyPalette(); } };')
os.makedirs(D + 'plasma', exist_ok=True)
# ubiquitin and the proteasome share a lavender accent, distinct from the pink target: the tags and the machinery that acts on them
PL_PAL = OTX_PAL + "PAL.otx.ub = '#B9A6F5'; PAL.otx.prot = '#B9A6F5';\n"
pl_page = (pl_head + '<main id="main">\n' + pl_story + '</main>\n' + meshes + '\n<script type="module">' + otx_prefix + '\n' + PL_PAL
           + pl_js + '\n' + open(D + 'otx.js').read() + '\n' + open(D + 'plasma.js').read() + '</script>\n' + SMALL)
open(D + 'plasma/index.html', 'w').write(pl_page)
print('plasma/index.html', os.path.getsize(D + 'plasma/index.html') // 1024, 'KB')

# ---------- the click-through version (click/index.html): the plasma journey stepped with Next / Back ----------
# Same content; the page does not scroll, and click.js plays the journey from one key moment to the next.
CK_CONTROLS = ('<div class="jctl" id="jctl">'
               '<button type="button" class="jbtn jplay" id="jplay" aria-pressed="false"><i aria-hidden="true"></i><span>Watch the whole journey</span></button>'
               '<span class="jcount" id="jcount" aria-live="polite">1 / 11</span>'
               '<button type="button" class="jbtn" id="jback" aria-label="Back"><svg viewBox="0 0 14 14" aria-hidden="true"><path d="M12 7H2M6 3L2 7l4 4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button>'
               '<button type="button" class="jbtn jnext" id="jnext"><span>Next</span><svg viewBox="0 0 14 14" aria-hidden="true"><path d="M2 7h10M8 3l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button></div>')
ck_story = re.sub(r'<a class="skip" id="skip".*?</a>', CK_CONTROLS, pl_story, count=1, flags=re.S)
assert 'id="jctl"' in ck_story
ck_story = re.sub(r'<div class="hint" id="hint"><span>.*?molecule</span>', '<div class="hint" id="hint"><span>Press Next, or use the arrow keys</span>', ck_story, count=1, flags=re.S)
assert 'arrow keys</span>' in ck_story and 'molecule</span><i' not in ck_story
ck_head = pl_head.replace('<title>SELFTAC Journey, Plasma</title>', '<title>SELFTAC Journey, Click-Through</title>', 1) + '''<style>
/* click-through: one screen, no scrolling; Next and Back bottom right, the rail's pearls clickable */
.story, .story { height: 100vh; height: 100svh; }
@media (max-width: 760px) { .story { height: 100svh; } }
html, body { overflow: hidden; overscroll-behavior: none; }
.jctl { position: absolute; right: clamp(16px, 3vw, 40px); bottom: 76px; z-index: 4; display: flex; align-items: center; gap: 10px; }
.jcount { font: 400 12px/1 var(--mono); letter-spacing: .12em; color: var(--muted); margin-right: 6px; font-variant-numeric: tabular-nums; }
.jbtn { display: inline-flex; align-items: center; gap: 10px; height: 46px; min-width: 46px; justify-content: center; padding: 0 14px; border-radius: 12px; cursor: pointer;
  background: rgba(255, 255, 255, .17); border: 1px solid rgba(255, 255, 255, .14); color: #FFFFFF; font: 500 15px/1 var(--sans); transition: background-color .2s, transform .2s; }
.jbtn svg { width: 15px; height: 15px; }
.jbtn.jnext { padding: 0 20px; background: rgba(255, 255, 255, .92); color: #0E5C42; }
.jbtn:hover { background: rgba(255, 255, 255, .28); } .jbtn.jnext:hover { background: #FFFFFF; transform: translateX(2px); }
.jbtn:disabled { opacity: .35; cursor: default; transform: none; }
.jbtn:focus-visible, .rail > div:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }
.rail > div { cursor: pointer; }
/* the whole journey: a play triangle that turns to pause bars while it plays */
.jbtn.jplay { padding: 0 16px 0 14px; margin-right: 8px; }
.jplay i { width: 0; height: 0; border-left: 9px solid currentColor; border-top: 5.5px solid transparent; border-bottom: 5.5px solid transparent; }
.jplay.on i { width: 9px; height: 11px; border: 0; border-left: 3px solid currentColor; border-right: 3px solid currentColor; }
.jplay.on { background: rgba(48, 252, 186, .22); border-color: rgba(48, 252, 186, .5); }
@media (max-width: 760px) { .jctl { top: calc(14px + env(safe-area-inset-top, 0px)); bottom: auto; right: 12px; left: 12px; justify-content: flex-end; flex-wrap: wrap; } .jbtn.jplay { margin-right: auto; padding: 0 12px; } .jcount { display: none; } .jbtn { height: 40px; min-width: 40px; font-size: 14px; } .jbtn.jnext { padding: 0 14px; } }
</style>
'''
ck_page = (ck_head + '<main id="main">\n' + ck_story + '</main>\n' + meshes + '\n<script type="module">' + otx_prefix + '\n' + PL_PAL
           + pl_js + '\n' + open(D + 'otx.js').read() + '\n' + open(D + 'plasma.js').read() + '\n' + open(D + 'click.js').read() + '</script>\n')
os.makedirs(D + 'click', exist_ok=True)
open(D + 'click/index.html', 'w').write(ck_page)
print('click/index.html', os.path.getsize(D + 'click/index.html') // 1024, 'KB')

# ---------- click-through v2 (click2/index.html): a live equilibrium, a population in the cell, persistent labels ----------
c2_beats = list(pl_beats)
c2_beats[2] = ('03 &middot; In the bloodstream', 'h2', 'Monomers and dimer, in equilibrium.',
               'In the plasma, two monomers keep joining into the dimer and coming apart again at the reversible linker: a dynamic equilibrium.')
c2_beats[4] = ('05 &middot; Ternary complex', 'h2', 'Inside the cell, a dimer forms the ternary complex.',
               'Monomers and dimers are in equilibrium here too. One dimer binds the target protein and an E3 ligase: a ternary complex.')
c2_copy = ''.join(f'<div class="beat"><span class="k"><b>{k.split(" &middot; ")[0]}</b>{k.split(" &middot; ")[1]}</span><{h}>{t}</{h}><p>{d}</p></div>' for k, h, t, d in c2_beats)
c2_story = re.sub(r'<div class="copy" id="copy">.*?</div></div>(?=<div class="end")', '<div class="copy" id="copy">' + c2_copy + '</div>', ck_story, count=1, flags=re.S)
assert c2_copy in c2_story
c2_head = ck_head.replace('<title>SELFTAC Journey, Click-Through</title>', '<title>SELFTAC Journey, Click-Through 2</title>', 1) + '''<style>
/* the equilibrium formula in the blood */
.jl.eqf { font-size: 14px; letter-spacing: .1em; }
.jl.eqf b { font-weight: 400; color: var(--clasp); margin: 0 .35em; font-size: 1.25em; }
/* persistent labels beside the proteins and ubiquitin: larger, plain type, a swatch in the protein's colour */
.jl.key { font: 600 15px/1 var(--sans); letter-spacing: .01em; text-transform: none; padding: 8px 13px 8px 11px; border-radius: 999px; color: #FFFFFF;
  background: rgba(8, 58, 41, .86); border: 1px solid rgba(255, 255, 255, .18); display: inline-flex; align-items: center; gap: 9px; }
.jl.key::before { content: ""; width: 11px; height: 11px; border-radius: 50%; background: var(--dot); box-shadow: 0 0 0 2px rgba(255, 255, 255, .25); }
/* larger copy on the left: the click-through holds each step, so it reads like a slide */
.copy { width: min(34vw, 520px); }
.beat .k { font-size: 17px; }
.beat h1, .beat h2 { font-size: clamp(38px, 4.1vw, 66px); line-height: 1.02; }
.beat p { font-size: clamp(17px, 1.45vw, 23px); line-height: 1.45; max-width: 32ch; margin-top: 20px; }
/* phones: Play, Back and Next in one row under the copy card, above the rail; the top of the screen is the scene's */
@media (max-width: 760px) {
  .jctl { top: auto; bottom: calc(44px + env(safe-area-inset-bottom, 0px)); flex-wrap: nowrap; gap: 8px; }
  .copy { bottom: calc(96px + env(safe-area-inset-bottom, 0px)); }
  .hint { display: none; }   /* keyboard advice; the buttons are right there */
  .jbtn.jplay { font-size: 13px; padding: 0 11px; white-space: nowrap; min-width: 0; overflow: hidden; }
}
@media (max-width: 760px) and (max-height: 700px) { .beat { padding: 13px 15px 14px; } .beat h1, .beat h2 { font-size: 23px !important; margin-top: 8px; } .beat p { font-size: 14px !important; margin-top: 8px; } }
@media (max-width: 760px) { .copy { width: auto; } .beat .k { font-size: 14px; } .beat h1, .beat h2 { font-size: 28px; } .beat p { font-size: 16px; margin-top: 12px; } .jl.key { font-size: 12px; padding: 5px 9px 5px 8px; } .jl.eqf { font-size: 11px; } }
</style>
'''
c2_click = open(D + 'click.js').read()
c2_click = once(c2_click, 'const dur = reduce ? 0 :', 'const dur = (SLOW[i] || 1) * (reduce ? 0 :')
c2_click = once(c2_click, ', t0 = performance.now();\n    at = i;', '), t0 = performance.now();\n    at = i;')
c2_click = once(c2_click, '  const BEAT_STOP', '  const SLOW = { 8: 1.8, 9: 1.7 };                          // tagging and degradation: unhurried\n  const BEAT_STOP')
c2_click = re.sub(r'const HOLD = \[[^\]]*\];', 'const HOLD = [300, 150, 550, 300, 2400, 200, 550, 2200, 450, 400];   // longer where an equilibrium is playing', c2_click, count=1)
c2_click = once(c2_click, '  J.frame(0); show(); setPlaying(false);', '''  J.frame(0); show(); setPlaying(false);
  // while a stop holds a live equilibrium, keep drawing it (one redraw a frame, only when nothing else is moving)
  (function idle() { if (!anim && window.__liveAt && window.__liveAt(p)) J.redraw(); requestAnimationFrame(idle); })();''')
c2_js = once(pl_js, 'goTo: p => { hold = true; prog = p; },', "goTo: p => { hold = true; prog = p; }, redraw: () => { drawnSig = ''; },")
# the two monomers cross side by side: the pair turns across its path as it leaves the gut and again before the membrane
# (horizontal in the bloodstream between, under its equilibrium), so both cross each boundary at the same moment
# the complex tightens for ubiquitination: the ligase and the target close in (the degrader shortening with them) while
# the chain is built, and ease apart again as the target leaves for the proteasome
c2_js = once(c2_js, 'const p = WARP(clamp(p0, 0, 1));', 'const p = WARP(clamp(p0, 0, 1)), CMP = 5 * kf(WARP(clamp(p0, 0, 1)), [[.735, 0], [.78, 1], [.86, 1], [.9, 0]]);')
c2_js = once(c2_js, 'hx = p < .27 ? 7 : HX(p);', 'hx = p < .27 ? 7 : HX(p) - CMP;')
c2_js = once(c2_js, 'P.brd4.position.set(-GAPJ - 110 * tIn, 0, 0);', 'P.brd4.position.set(-GAPJ + CMP - 110 * tIn, 0, 0);')
c2_js = once(c2_js, 'P[key].position.set(GAPJ + 130 * tIn, 0, 0);', 'P[key].position.set(GAPJ - CMP + 130 * tIn, 0, 0);')
c2_js = once(c2_js, 'home = V3(-GAPJ, 0, 0)', 'home = V3(-GAPJ + CMP, 0, 0)')
# the chain goes on a lysine on the target's flank near the ligase (in the turned crystal frame +x is toward the ligase,
# -y the screen-left flank once the complex stands upright), and each ubiquitin is handed over from the ligase's side
c2_js = once(c2_js, 'const s = -v.x + .35 * v.z + .2 * v.y;', 'const s = .5 * v.x - v.y + .3 * v.z;')
# ubiquitin as a real K48-linked chain (PDB 2O6V, see tools/ub_chain.py): built on the target one at a time, proximal
# first, and taken into the proteasome with it
UB_OLD = """  ubs.forEach((u, i) => {
    const t0 = .8 + i * .012, on = clamp((p - t0) / .012, 0, 1);
    const spot = P.brd4.localToWorld(ubLocal.clone().add(V3(-2 - 3 * i, (i % 2 ? 3 : -3), 4)));
    u.position.copy(spot).add(V3(0, 26 * (1 - ease(on)), 0)); u.scale.setScalar(.42 * SC * P.brd4.scale.x);
    u.visible = on > .01 && P.brd4.visible;
  });"""
UB_NEW = """  {
    const spot = P.brd4.localToWorld(ubLocal.clone()), out = spot.clone().sub(P.brd4.localToWorld(B4C.clone())).normalize().add(V3(-.1, .3, .35)).normalize();
    const from = P.vhl.localToWorld(E3SPOT.clone()).sub(spot), Ro = new THREE.Quaternion().setFromUnitVectors(UBAX, out), s = .42 * SC * P.brd4.scale.x;
    ubs.forEach((u, i) => {
      const on = clamp((p - (.745 + i * .022)) / .03, 0, 1), e = ease(on);
      u.quaternion.copy(Ro).multiply(UBQ[i]);
      u.position.copy(UBT[i]).sub(UBG).applyQuaternion(Ro).multiplyScalar(s).add(spot).addScaledVector(from, 1 - e).addScaledVector(out, 6 * Math.sin(Math.PI * e));
      u.scale.setScalar(s * (.55 + .45 * e)); u.visible = on > .01 && P.brd4.visible;
    });
  }"""
UBC = json.load(open(D + 'ubchain.json'))
UB_SETUP = ('const UBC = ' + json.dumps(UBC) + ';\n'
            'const UBQ = UBC.poses.map(q => new THREE.Quaternion(q[0], q[1], q[2], q[3])), UBT = UBC.poses.map(q => V3(q[4], q[5], q[6])), UBG = V3(...UBC.g);\n'
            'const UBAX = UBT.reduce((a, t) => a.add(t), V3(0, 0, 0)).multiplyScalar(1 / UBT.length).sub(UBG).normalize();   // the chain, from its root\n'
            'const E3SPOT = (() => { const g = P.vhl.children[0].geometry, pos = g.attributes.position, v = V3(); let best = null, bs = -1e9;   // the ligase flank the ubiquitin comes from\n'
            '  for (let i = 0; i < pos.count; i++) { v.fromBufferAttribute(pos, i).applyQuaternion(Q); const s = -.4 * v.x - v.y + .3 * v.z; if (s > bs) { bs = s; best = v.clone(); } } return best; })();\n'
            'const B4C = (() => { const g = P.brd4.children[0].geometry; g.computeBoundingBox(); return g.boundingBox.getCenter(V3()).applyQuaternion(Q); })();\n')
c2_js = once(c2_js, UB_OLD, UB_NEW)
c2_js = once(c2_js, '// ---------- the timeline ----------', UB_SETUP + '// ---------- the timeline ----------')
c2_js = once(c2_js, 'cg.rotation.z = kf(p, [[.44, 0], [.58, -Math.PI / 2]])',
             'cg.rotation.z = kf(p, [[.295, 0], [.32, -Math.PI / 2], [.37, -Math.PI / 2], [.395, 0], [.425, 0], [.47, -Math.PI / 2]])')
# the larger copy takes more of the left: the subject sits further right, and further still once the target is in the
# proteasome, so the complex left behind stays clear of the degradation copy (spread over the whole move, so the camera
# only ever moves on, never back); inside the cell it sits a little higher,
# clear of the controls
# phones: around tagging the camera pulls back a little and frames further left, so the complex and its ubiquitin
# chain (on the target's left flank) stay on screen with room for the label
c2_js = once(c2_js, 'const dist = DIST(p) * (narrow ? Math.max(1, 1.05 / camera.aspect) * .8 : 1);',
             'const tagW = camera.aspect < .9 ? kf(p, [[.76, 0], [.82, 1], [.9, 1], [.95, 0]]) : 0, dist = DIST(p) * (narrow ? Math.max(1, 1.05 / camera.aspect) * .8 : 1) * (1 + .16 * tagW);')
c2_js = once(c2_js, 'if (narrow) ay -= .17 * vh * settle; else ax -= .17 * vw * settle;',
             'if (narrow) { ay -= .22 * vh * settle; ax -= .09 * vw * tagW; } else { ax -= (.2 + .1 * kf(p, [[.8, 0], [.869, .47], [.948, 1]])) * vw * settle; ay -= .035 * vh * kf(p, [[.6, 0], [.68, 1]]) * settle; }')
# the proteasome: the human 26S (PDB 6MSB, tools/proteasome_mesh.py), core and cap, cap up; the target goes into the core
PROT_OLD = re.search(r"const prot = new THREE.Group\(\); scene.add\(prot\);\n.*?prot.add\(c\); \}\n", otx_prefix, re.S).group(0)
PROT_NEW = """const prot = new THREE.Group(); scene.add(prot);
// scale, and the middle of its length (A); the cap a lighter lavender than the core
const PDATA = JSON.parse(document.getElementById('protmesh').textContent), PK = .225, PMID = 76;
for (const key of ['core', 'cap']) { const g = geom(PDATA[key]); g.translate(-PMID, 0, 0); g.computeBoundingSphere();
  const mat = cmat(key === 'cap' ? 'protcap' : 'prot', 9, g.boundingSphere.center.clone()); mats.push(mat); const m = new THREE.Mesh(g, mat); m.scale.setScalar(PK); addOutline(m, 2); prot.add(m); }
"""
c2_prefix = once(otx_prefix, PROT_OLD, PROT_NEW)
c2_js = once(c2_js, 'const PROT = V3(X.prot, 6, 0)', 'const PROT = V3(X.prot - 10, 6, 0)')   # the real cap is wider: a little further in from the edge
c2_js = once(c2_js, 'into = inner.worldToLocal(PROT.clone())', 'into = inner.worldToLocal(PROT.clone().add(V3(0, -PMID * PK * 1.15, 0)))')   # the core's middle
c2_story = once(c2_story, 'data-x="640" data-y="50"', 'data-x="630" data-y="58"')
c2_story = once(c2_story, 'data-x="640" data-y="-86"', 'data-x="630" data-y="-86"')
c2_story = once(c2_story, 'ubiquitin from PDB 1UBQ. ', 'ubiquitin from PDB 1UBQ, arranged as the K48-linked chain of PDB 2O6V (Eddins et al., J. Mol. Biol. 2007); the human 26S proteasome from PDB 6MSB (Dong et al., Nature 2019). ')
c2_story = once(c2_story, 'the proteasome is a stand-in, and the person', 'the person')
C2_PAL = PL_PAL + "PAL.otx.protcap = '#D6CBFA';\n"
PROTMESH = '<script type="application/json" id="protmesh">' + open(D + 'proteasome.json').read() + '</script>'
# the words: one data block (#c2text) the page applies as it loads, and an in-page editor that saves it (editor.js);
# the end card no longer carries the model credits
c2_story = re.sub(r'<p class="ecr">.*?</p>', '', c2_story, count=1, flags=re.S)
assert 'class="ecr"' not in c2_story
def _plain(h): return re.sub(r'<[^>]+>', '', h).replace('&reg;', '\u00ae').replace('&middot;', '\u00b7').replace('&amp;', '&').replace('&rsquo;', '\u2019')
C2_TEXT = {'sections': [{'title': r, 'label': _plain(k.split(' &middot; ')[1]), 'heading': _plain(t), 'body': _plain(d)}
                        for r, (k, h, t, d) in zip(['Oral', 'Gut', 'Plasma', 'Barrier', 'Complex', 'Degraded'], c2_beats)],
           'tagline': ['Targeted protein degradation', 'beyond conventional limits.']}
# the version of record for the words: text/click2.json when present (pulled from the live page with tools/pull_text.py
# after edits are saved in it), else the defaults above
if os.path.exists(D + 'text/click2.json'): C2_TEXT = json.load(open(D + 'text/click2.json', encoding='utf8'))
assert '<p class="tag">Targeted protein degradation <em>beyond conventional limits.</em></p>' in c2_story
c2_story = c2_story.replace('</section>', '</section><script type="application/json" id="c2text">' + json.dumps(C2_TEXT, ensure_ascii=False).replace('<', '\\u003c')
                            + '</script><script>' + open(D + 'text_apply.js').read() + '</script>', 1)
c2_head = c2_head + """<style>
/* the in-page text editor: a button top right, and a panel beside the copy (a sheet over the scene on phones) */
.jedit-btn { position: absolute; top: calc(16px + env(safe-area-inset-top, 0px)); right: clamp(16px, 3vw, 40px); z-index: 6; display: inline-flex; align-items: center; gap: 8px;
  height: 38px; padding: 0 14px; border-radius: 10px; cursor: pointer; font: 500 14px/1 var(--sans); color: #FFFFFF; background: rgba(255, 255, 255, .14); border: 1px solid rgba(255, 255, 255, .16); }
.jedit-btn svg { width: 15px; height: 15px; } .jedit-btn:hover { background: rgba(255, 255, 255, .26); }
.jedit-btn:focus-visible, .jedit button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.jediting .jedit-btn { display: none; }
@media (min-width: 761px) { .jediting .jctl { right: calc(min(420px, 100%) + 24px); } }
.jedit { position: absolute; top: 0; right: 0; bottom: 0; width: min(420px, 100%); z-index: 7; display: flex; flex-direction: column;
  background: rgba(8, 52, 37, .95); -webkit-backdrop-filter: blur(10px); backdrop-filter: blur(10px); border-left: 1px solid rgba(255, 255, 255, .12); color: #FFFFFF; }
.jedit[hidden] { display: none; }
.jedit header { display: flex; align-items: center; justify-content: space-between; padding: 18px 20px 12px; border-bottom: 1px solid rgba(255, 255, 255, .1); }
.jedit h2 { margin: 0; font: 500 20px/1.2 var(--serif); }
.jedit .jx { width: 36px; height: 36px; border-radius: 9px; border: 0; background: rgba(255, 255, 255, .1); color: #FFFFFF; font: 400 22px/1 var(--sans); cursor: pointer; }
.jedit .jbody { flex: 1; overflow: auto; padding: 8px 20px 20px; overscroll-behavior: contain; }
.jedit fieldset { border: 0; margin: 0; padding: 16px 0 14px; border-bottom: 1px solid rgba(255, 255, 255, .1); display: grid; gap: 10px; }
.jedit legend { padding: 0; margin-bottom: 4px; display: flex; gap: 10px; align-items: baseline; font: 400 15px/1.2 var(--pixel); letter-spacing: .03em; text-transform: uppercase; color: #FFFFFF; }
.jedit legend b { font-weight: 400; color: #8AC3B1; }
.jedit .jf { display: grid; gap: 5px; }
.jedit .jf span { font: 500 12px/1.2 var(--sans); color: #A8D8C6; }
.jedit input, .jedit textarea { width: 100%; box-sizing: border-box; font: 400 15px/1.45 var(--sans); color: #FFFFFF; background: rgba(255, 255, 255, .07);
  border: 1px solid rgba(255, 255, 255, .16); border-radius: 8px; padding: 8px 10px; resize: vertical; }
.jedit input:focus, .jedit textarea:focus { outline: none; border-color: var(--accent); background: rgba(255, 255, 255, .1); }
.jedit footer { display: flex; align-items: center; gap: 10px; padding: 12px 20px calc(14px + env(safe-area-inset-bottom, 0px)); border-top: 1px solid rgba(255, 255, 255, .1); }
.jedit .jst { flex: 1; font: 400 13px/1.35 var(--sans); color: #A8D8C6; }
.jedit .jbtn { height: 40px; } .jedit .jsave:disabled { opacity: .45; cursor: default; }
@media (max-width: 760px) {
  .jedit { left: 0; width: auto; bottom: auto; height: 56%; border-left: 0; border-bottom: 1px solid rgba(255, 255, 255, .14); }
  .jedit input, .jedit textarea { font-size: 16px; }
  .jedit-btn { height: 34px; font-size: 13px; padding: 0 11px; }
}
</style>
"""
c2_page = (c2_head + '<main id="main">\n' + c2_story + '</main>\n' + meshes + '\n' + PROTMESH + '\n<script type="module">' + c2_prefix + '\n' + C2_PAL
           + c2_js + '\n' + open(D + 'otx.js').read() + '\n' + open(D + 'plasma.js').read() + '\n' + open(D + 'cell.js').read() + '\n' + c2_click + '\n' + open(D + 'editor.js').read() + '</script>\n')
os.makedirs(D + 'click2', exist_ok=True)
open(D + 'click2/index.html', 'w').write(c2_page)
print('click2/index.html', os.path.getsize(D + 'click2/index.html') // 1024, 'KB')

# ---------- Rob's edits (click3/index.html): click2 with a set of review changes ----------
# a side-view body silhouette; no 'Oral dosing' label, and the first click takes the capsule all the way to the gut; larger,
# higher-contrast location labels; a narrower vessel with no red cells (a layered wall, endothelial nuclei, faint flow
# streaks); one dimer at the barrier, which bounces off, comes apart and goes through as monomers (rob.js); the ternary
# complex forms more slowly; the equilibrium inside the cell runs at half speed
import sys; sys.path.insert(0, D + 'tools'); from person_profile import profile
P_FILL, P_EDGE, P_ARM = profile()
c3_story = c2_story
for old, new in [(PERSON_D, P_FILL), (EDGE_D, P_EDGE), (ARM, P_ARM)]:
    c3_story = once(c3_story, f'd="{old}"', f'd="{new}"')
c3_story = re.sub(r'<span class="jl " data-x="74" data-y="78"[^>]*>Oral dosing</span>', '', c3_story, count=1)
# the figure drawn like the reference: a clear outline over a light fill, carried down past the waist and the seat
c3_story, n = re.subn(r'<linearGradient id="jpersonG".*?</linearGradient>', lambda m: '<linearGradient id="jpersonG" gradientUnits="userSpaceOnUse" x1="0" y1="-80" x2="0" y2="128">'
    '<stop offset="0" style="stop-color:var(--ink);stop-opacity:.09"/><stop offset=".78" style="stop-color:var(--ink);stop-opacity:.07"/><stop offset="1" style="stop-color:var(--ink);stop-opacity:0"/></linearGradient>', c3_story, count=1, flags=re.S)
assert n == 1
c3_story, n = re.subn(r'<linearGradient id="jedgeG".*?</linearGradient>', lambda m: '<linearGradient id="jedgeG" gradientUnits="userSpaceOnUse" x1="0" y1="-84" x2="0" y2="132">'
    '<stop offset="0" style="stop-color:var(--ink);stop-opacity:.85"/><stop offset=".8" style="stop-color:var(--ink);stop-opacity:.75"/><stop offset="1" style="stop-color:var(--ink);stop-opacity:0"/></linearGradient>', c3_story, count=1, flags=re.S)
assert n == 1
c3_story = once(c3_story, 'style="fill:none;stroke:url(#jedgeG);stroke-width:1.1;', 'style="fill:none;stroke:url(#jedgeG);stroke-width:2;')
# the capsule's way down sits a little further back, inside the traced neck
c3_story = once(c3_story, f'd="{ROUTE}"', 'd="M 18.6,-44.4 C 12,-43.6 4,-41.5 0,-37 C -3.2,-32 -3.6,-25 -3.2,-18 C -2.8,-10 -0.6,-3 0.5,2.5"')
assert 'data-x="74" data-y="78"' not in c3_story
for txt in ['In the gut', 'Cell membrane &middot; blood-brain barrier', 'Target cell', 'Proteasome', 'Degradation', 'Blood vessel &middot; plasma',
            'Dimer: too large to penetrate', 'Monomers pass through']:
    c3_story, n = re.subn(r'<span class="jl ([^"]*)"([^>]*)>' + re.escape(txt) + '</span>', lambda m: f'<span class="jl loc"{m.group(2)}>{txt}</span>', c3_story, count=1)
    assert n == 1, txt
c3_story = once(c3_story, f'data-x="{X["mem"] + 4}" data-y="-50"', f'data-x="{X["mem"] + 4}" data-y="63"')   # above the vessel (its wall at 50), at the top
c3_story = once(c3_story, f'data-x="{X["mem"] + 70}" data-y="52"', f'data-x="{X["mem"] + 88}" data-y="46"')   # Target cell: a fixed spot, above the monomers' way in   # Target cell: inside, below the membrane's label
# Rob's reference figure (tools/trace_person_ref.py -> person_ref.json): a soft silhouette, solid and fading out at the
# bottom, with the gut icon in its ring, in the theme's colours (the page's green disc in a white ring, the large intestine
# in white, stomach and small intestine in the mint accent; strokes that scale with the zoom)
PR = json.load(open(D + 'person_ref.json'))
# the gut sits centred on the body: the figure (and its mouth) shift so the torso's middle is over the gut inset
_xs = [x for x, y in PR['outline'] if -5 <= y <= 35]; GDX = round(-(min(_xs) + max(_xs)) / 2, 2)
PR['outline'] = [(round(x + GDX, 2), y) for x, y in PR['outline']]; PR['mouth'] = (round(PR['mouth'][0] + GDX, 2), PR['mouth'][1])
def _cr(pts, closed=False):
    n = len(pts); o = [f'M {pts[0][0]},{pts[0][1]}']
    for i in range(n if closed else n - 1):
        p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[i]; p1, p2 = pts[i], pts[(i + 1) % n]; p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else p2
        o.append(f'C {p1[0] + (p2[0] - p0[0]) / 6:.2f},{p1[1] + (p2[1] - p0[1]) / 6:.2f} {p2[0] - (p3[0] - p1[0]) / 6:.2f},{p2[1] - (p3[1] - p1[1]) / 6:.2f} {p2[0]},{p2[1]}')
    return ' '.join(o) + (' Z' if closed else '')
c3_story = once(c3_story, f'd="{P_FILL}"', f'd="{_cr(PR["outline"], True)}"')
c3_story = once(c3_story, f'd="{P_EDGE}"', 'd=""')
c3_story, n = re.subn(r'<linearGradient id="jpersonG".*?</linearGradient>', lambda m: '<linearGradient id="jpersonG" gradientUnits="userSpaceOnUse" x1="0" y1="-60" x2="0" y2="52">'
    '<stop offset="0" style="stop-color:var(--ink);stop-opacity:.2"/><stop offset=".86" style="stop-color:var(--ink);stop-opacity:.2"/><stop offset="1" style="stop-color:var(--ink);stop-opacity:0"/></linearGradient>', c3_story, count=1, flags=re.S)
assert n == 1
mx, my = PR['mouth']; SW = PR['stroke']
c3_story = once(c3_story, 'd="M 18.6,-44.4 C 12,-43.6 4,-41.5 0,-37 C -3.2,-32 -3.6,-25 -3.2,-18 C -2.8,-10 -0.6,-3 0.5,2.5"',
                f'd="M {mx},{my} C {mx + 5.6:.2f},-34.6 {mx + 10:.2f},-33 {mx + 11.4:.2f},-29.5 C {mx + 12.6:.2f},-25 {mx + 13.4:.2f},-17 {mx + 14:.2f},-10.5 C {mx + 14.6:.2f},-3.5 {mx + 15.4:.2f},1 0.6,3.8"')
_st = lambda col: f'style="fill:none;stroke:{col};stroke-width:{SW};stroke-linecap:round;stroke-linejoin:round;vector-effect:none"'
GUT3 = (f'<circle id="jgutdisc" cx="0" cy="25" r="22" style="fill:var(--paper);fill-opacity:.92;stroke:var(--ink);stroke-width:{SW};vector-effect:none"/>'
        f'<circle id="jgutring" cx="0" cy="25" r="25.5" style="fill:none;stroke:var(--accent);stroke-width:2;opacity:0"/>'
        f'<g id="jtract">' + ''.join(f'<path d="{_cr(c)}" {_st("var(--accent)")}/>' for c in PR['tract'])
        + '<g id="jcolon">' + ''.join(f'<path d="{_cr(c)}" {_st("var(--ink)")}/>' for c in PR['colon']) + '</g></g>')
c3_story = once(c3_story, GUT, GUT3)
# once the target is degraded only 'Degradation' stays: the proteasome's label hands over to it
c3_story = once(c3_story, 'data-a="0.84" data-b="0.99">Proteasome', 'data-a="0.84" data-b="0.925">Proteasome')
# the vessel: narrower, its wall drawn in layers (tissue, endothelium, outer edge), flattened nuclei along the lining, and a
# few faint streaks drifting with the flow in place of the red cells (they ride in #jrbc, which already drifts and fades)
VY3 = 50; VX3 = X['mem'] + R - math.sqrt((R + BAND) ** 2 - VY3 ** 2)
w3t = f'M 16 -14 C 46 -10 64 {VY3} 112 {VY3} L {VX3:.1f} {VY3}'; w3b = f'M 16 -36 C 46 -40 64 {-VY3} 112 {-VY3} L {VX3:.1f} {-VY3}'
lum3 = f'M 16 -14 C 46 -10 64 {VY3} 112 {VY3} L {VX3:.1f} {VY3} L {VX3:.1f} {-VY3} L 112 {-VY3} C 64 {-VY3} 46 -40 16 -36 Z'
rnd3 = random.Random(11); streaks = ''
for i in range(14):
    x, y, L = rnd3.uniform(118, VX3 - 26), rnd3.uniform(-VY3 + 9, VY3 - 9), rnd3.uniform(7, 16)
    streaks += f'<g transform="translate({x:.1f} {y:.1f})"><path d="M {-L / 2:.1f} 0 L {L / 2:.1f} 0" style="stroke:var(--ink);stroke-opacity:{rnd3.uniform(.1, .2):.2f};stroke-width:1.2;stroke-linecap:round"/></g>'
nuclei = ''.join(f'<ellipse cx="{x:.1f}" cy="{s * (VY3 - 3.2):.1f}" rx="3.4" ry="1.1" style="fill:var(--ink);fill-opacity:.2"/>'
                 for s in (1, -1) for x in [126 + k * 21 + (0 if s > 0 else 10) for k in range(int((VX3 - 140) // 21))])
wall = lambda w, dy: f'<path d="{w}" transform="translate(0 {dy})" '
V3G = (f'<g id="jvessel" style="opacity:0"><path d="{lum3}" style="fill:#FFFFFF;fill-opacity:.06"/>'
       f'<g id="jrbc">{streaks}</g>'
       + ''.join(f'<path d="{w}" style="fill:none;stroke:var(--ink);stroke-opacity:.13;stroke-width:9;stroke-linecap:round"/>'
                 + wall(w, d * -3.6) + 'style="fill:none;stroke:var(--ink);stroke-opacity:.55;stroke-width:1.1;stroke-linecap:round"/>'
                 + wall(w, d * 4.2) + 'style="fill:none;stroke:var(--ink);stroke-opacity:.24;stroke-width:.9;stroke-linecap:round"/>'
                 for w, d in ((w3t, 1), (w3b, -1)))
       + nuclei + '</g>')
c3_story, n = re.subn(r'<g id="jvessel".*?</g>(?=<g id="jmem">)', lambda m: V3G, c3_story, count=1, flags=re.S)
assert n == 1, 'vessel'
# the barrier labels follow the one dimer: too large while it bounces, then the monomers going through
c3_story = once(c3_story, 'data-pl="bounce" data-a="0.588" data-b="0.69"', 'data-pl="bounce" data-a="0.556" data-b="0.614"')
c3_story = once(c3_story, 'data-pl="pass" data-a="0.6" data-b="0.69"', 'data-pl="pass" data-a="0.625" data-b="0.69"')
c3_story = c3_story.replace('>1 / 11<', '>1 / 10<')
C3_TEXT = json.loads(json.dumps(C2_TEXT))
C3_TEXT['sections'][3]['body'] = 'The dimer is too large to penetrate the cell membrane or the blood-brain barrier. It comes apart at its reversible linker, and the two small monomers pass through.'
if os.path.exists(D + 'text/click3.json'): C3_TEXT = json.load(open(D + 'text/click3.json', encoding='utf8'))   # the version of record, as for click2
c3_story = re.sub(r'(<script type="application/json" id="c2text">).*?(</script>)', lambda m: m.group(1) + json.dumps(C3_TEXT, ensure_ascii=False).replace('<', '\\u003c') + m.group(2), c3_story, count=1, flags=re.S)
c3_head = c2_head.replace('<title>SELFTAC Journey, Click-Through 2</title>', "<title>SELFTAC Journey Rob's Edits</title>", 1) + '''<style>
/* location labels: larger, white on a dark pill */
.jl.key.dright::before { display: none; }
.jl.key.dright::after { content: ""; width: 11px; height: 11px; border-radius: 50%; background: var(--dot); box-shadow: 0 0 0 2px rgba(255, 255, 255, .25); }
.jl.loc { font: 600 13px/1.2 var(--mono); letter-spacing: .1em; color: #FFFFFF; background: rgba(6, 46, 33, .9); border: 1px solid rgba(255, 255, 255, .3);
  padding: 8px 13px; -webkit-backdrop-filter: none; backdrop-filter: none; }
@media (max-width: 760px) { .jl.loc { font-size: 11px; padding: 6px 10px; } }
</style>
'''
assert "<title>SELFTAC Journey Rob's Edits</title>" in c3_head
# the journey hands the molecule to rob.js at the barrier
c3_js = once(c2_js, 'const brk = mol.update(V3(-hx, 0, 0), V3(hx, 0, 0), rW, rE, j);', 'const brk = heroOverride(clamp(p0, 0, 1), mol.update(V3(-hx, 0, 0), V3(hx, 0, 0), rW, rE, j));')
c3_plasma = once(open(D + 'plasma.js').read(), 'const VESSEL_IN = 50;', 'const VESSEL_IN = 36;')
c3_plasma = once(c3_plasma, 'pass: () => { const c = cg.position; return [c.x + 34, c.y - 30]; }', 'pass: () => { const c = cg.position; return [c.x + 44, c.y]; }')   # beside the pair, not under it
c3_plasma = once(c3_plasma, 'bounce: () => [BOUNCER.g.position.x - 6, BOUNCER.g.position.y + 24]', 'bounce: () => [cg.position.x - 4, cg.position.y + 30]')
# the protein labels measured against the proteins' actual surfaces (not their loose bounding boxes), and set close
c3_plasma = once(c3_plasma, 'const box = new THREE.Box3().setFromObject(t.at());', 'const box = new THREE.Box3().setFromObject(t.at(), !!t.side);')
c3_cell = open(D + 'cell.js').read()
# the cell's monomers and dimer stay to the end, drifting along with the camera as it follows the target, so they stay in view
c3_cell = c3_cell.replace("win: pn => cellIn(pn) * clamp((.845 - pn) / .02, 0, 1)", "win: pn => cellIn(pn)").replace("win: pn => cellIn(pn) * clamp((.9 - pn) / .02, 0, 1)", "win: pn => cellIn(pn)")
# the ubiquitin label sits left of the chain, so its dot goes on its right, next to the chain
c3_cell = once(c3_cell, "k.el.style.setProperty('--dot', col);", "k.el.style.setProperty('--dot', col); if (i === 2) k.el.classList.add('dright');")
# the target's and ubiquitin's labels tuck in against their protein, as the E3 ligase's does (it sits over its partners' edge)
c3_plasma = once(c3_plasma, 'xr = Math.min(x1 + t.gap, stage.clientWidth - hw2)', 'xr = Math.min(x1 + t.gap - (t.ov || 0) * (stage.clientWidth < 760 ? .6 : 1), stage.clientWidth - hw2)')
c3_plasma = once(c3_plasma, 'xl = x0 - t.gap - w;', 'xl = x0 - t.gap - w + (t.ov || 0) * (stage.clientWidth < 760 ? .6 : 1);')
c3_cell = once(c3_cell, "if (i === 2) k.el.classList.add('dright');", "if (i === 2) k.el.classList.add('dright'); k.ov = [22, 0, 18][i];")
# the cell's monomers and dimer keep well clear of the ternary complex: all three in the free band above it (nothing else
# passes there, and drifting with the camera they stay in it to the end)
c3_cell = once(c3_cell, "{ at: 'cell', kind: 'dimer', dx: -80, y: 70,", "{ at: 'cell', kind: 'dimer', dx: -60, y: 92,")
c3_cell = once(c3_cell, "{ at: 'cell', kind: 'split', dx: -76, y: -58,", "{ at: 'cell', kind: 'split', dx: -30, y: 104,")
c3_cell = once(c3_cell, "{ at: 'cell', kind: 'eq', dx: 86, y: 70,", "{ at: 'cell', kind: 'eq', dx: 70, y: 92,")
c3_cell = once(c3_cell, "const k = tag(t, 'key', at, win, 14);", "const k = tag(t, 'key', at, win, 8);")
c3_cell = once(c3_cell, "pn => winOf(.715, stage.clientWidth < 760 ? .905 : .985)(pn)", "winOf(.715, .905)")   # the E3 ligase's label goes as the target is degraded
c3_cell = once(c3_cell, "const w = clamp(Math.min((pn - .405) / .03, (.525 - pn) / .03), 0, 1);", "const w = clamp(Math.min((pn - .405) / .03, (.5 - pn) / .025), 0, 1);")   # rob.js joins them up after
c3_cell = once(c3_cell, "const blWin = winOf(.405, .53, .03)", "const blWin = winOf(.405, .52, .03)")
c3_cell = once(c3_cell, "kind: 'split', dx: -30, y: -34,", "kind: 'split', dx: -34, y: -26,")
c3_cell = once(c3_cell, "kind: 'eq', dx: -66, y: 44,", "kind: 'eq', dx: -66, y: 28,")
c3_cell = once(c3_cell, "const e = eqWave(5.2, c.ph)", "const e = eqWave(7.8, c.ph)")   # half speed in the cell (the blood's pair is the hero's own)
c3_cell = once(c3_cell, "IN = 66 - 7;", "IN = 50 - 7;")
c3_cell = once(c3_cell, "window.__liveAt = p => (p > .4 && p < .53)", "window.__liveAt = p => (p > .4 && p < .5)")
# the blood vessel's label sits just above its top wall
c3_plasma = once(c3_plasma, 'plasma: () => { const [x, y] = at(R, .5, 1.04); return [x, y]; },', 'plasma: () => { const [x] = at(R, .5, 1.04); return [x, ' + str(VY3 + 11) + ']; },')
# no labels on the background molecules, in the blood or in the cell: only the focal pair is named
c3_cell = once(c3_cell, "POP.forEach(c => { const d0", "POP.forEach(c => { c.tags = []; });\n[].forEach(c => { const d0")
c3_cell = once(c3_cell, "if (c.tags[0].el.textContent !== st) c.tags[0].el.textContent = st;", "if (c.tags[0] && c.tags[0].el.textContent !== st) c.tags[0].el.textContent = st;")
# into the proteasome the way a substrate goes: up to the 19S cap, then fed down its central channel into the 20S core
# (shrinking as it goes, as it is unfolded and threaded through)
c3_js = once(c3_js, 'P.brd4.position.lerpVectors(home, into, go);',
             'const capTop = inner.worldToLocal(PROT.clone().add(V3(0, (239 - PMID) * PK * 1.15 + 8, 0))).sub(S(\'brd4\').multiplyScalar(sc)); '
             'if (go < .55) P.brd4.position.lerpVectors(home, capTop, ease(go / .55)); else P.brd4.position.lerpVectors(capTop, into, (go - .55) / .45);')
c3_story = once(c3_story, 'class="jl loc" data-x="630" data-y="58"', f'class="jl loc" data-x="{X["prot"] - 10 + 66}" data-y="14"')   # beside the cap, clear of the way in
# the target leaves for the proteasome a little later and its labels go first: they fade as the next click starts, the
# target only moves once they have gone (and the complex eases apart with it)
c3_js = once(c3_js, 'const go = kf(p, [[.86, 0], [.92, 1]]);', 'const go = kf(p, [[.88, 0], [.925, 1]]);')
c3_js = once(c3_js, '[[.735, 0], [.78, 1], [.86, 1], [.9, 0]]', '[[.735, 0], [.78, 1], [.88, 1], [.915, 0]]')
c3_cell = once(c3_cell, "() => P.brd4, winOf(.715, .892, .015)", "() => P.brd4, winOf(.715, .872, .006)")
c3_cell = once(c3_cell, "winOf(.848, .892, .015)", "winOf(.848, .872, .006)")
c3_js = once(c3_js, 'px = 74 + (19 - 74) * pp; py = 64 + (44.4 - 64) * pp - 10 * Math.sin(Math.PI * pp); rot = -18 + 18 * pp;', f'px = -50 + ({mx} + 50) * pp; py = 64 + ({-my} - 64) * pp - 10 * Math.sin(Math.PI * pp); rot = 18 - 18 * pp;')   # in from the left, into the traced mouth (the figure faces left)
# the cell's monomers and dimers: fixed in the cell (the camera pans past them, and others come into view), at spots chosen by
# measurement (cell_layout.json: sampled from the complex forming to degradation at desktop and phone sizes, clear of the
# membrane, the complex, the target's way into the proteasome, the proteasome and its fragments, every label, the copy and
# the controls, and of each other)
_kinds = ['dimer', 'split', 'eq']
_cells = ''.join(f"  {{ at: 'cell', kind: '{_kinds[i % 3]}', dx: {x - X['complex']}, y: {y}, s: .68, r: {[.5, -.3, -.4, .35, .2, -.5, .45][i % 7]}, hx: 11, ph: {1 + .7 * i:.1f}, win: pn => cellIn(pn) }},\n"
                 for i, (x, y) in enumerate(json.load(open(D + 'cell_layout.json'))))
c3_cell, n = re.subn(r"(  \{ at: 'cell', kind: [^\n]*\n)+", lambda m: _cells, c3_cell, count=1)
assert n == 1
c3_cell = once(c3_cell, 'const e = eqWave(7.8, c.ph), hx = 22 - 15 * e', 'const e = eqWave(7.8, c.ph), hx = 13 - 6 * e')   # the cycling pair stays compact
# the gut's equilibrium arrows go once the dimer has split, before the monomers leave the gut
c3_js = once(c3_js, '[winO(p, .255, .34), 15]', '[winO(p, .255, .305), 15]')
c3_click = c2_click
c3_click = once(c3_click, 'const STOPS = [0, .145, .25, .335, .45, .612, .665, .79, .865, .92, .998];', 'const STOPS = [0, .25, .335, .45, .59, .665, .79, .865, .92, .998];')
c3_click = once(c3_click, 'const BEAT_STOP = [0, 2, 4, 5, 7, 8];', 'const BEAT_STOP = [0, 1, 3, 4, 6, 7];')
c3_click = once(c3_click, 'const SLOW = { 8: 1.8, 9: 1.7 };', 'const SLOW = { 4: 1.3, 5: 2.6, 6: 1.9, 7: 1.8, 8: 2.6 };')
# every move unhurried: about half as long again as the click-through's, clicks and autoplay alike
c3_click = once(c3_click, 'glide ? Math.max(1600, Math.min(3400, 1300 + d * 9000)) : Math.max(1100, Math.min(2600, 900 + d * 7000))',
                'glide ? Math.max(2300, Math.min(4800, 1900 + d * 12000)) : Math.max(1700, Math.min(4000, 1400 + d * 10500))')
c3_click = re.sub(r'const HOLD = \[[^\]]*\];', 'const HOLD = [300, 550, 300, 2400, 900, 550, 2200, 450, 400];', c3_click, count=1)
c3_page = (c3_head + '<main id="main">\n' + c3_story + '</main>\n' + meshes + '\n' + PROTMESH + '\n<script type="module">' + c2_prefix + '\n' + C2_PAL
           + c3_js + '\n' + open(D + 'otx.js').read() + '\n' + c3_plasma + '\n' + c3_cell + '\n' + open(D + 'rob.js').read() + '\n' + c3_click + '\n' + open(D + 'editor.js').read() + '</script>\n')
os.makedirs(D + 'click3', exist_ok=True)
open(D + 'click3/index.html', 'w').write(c3_page)
print('click3/index.html', os.path.getsize(D + 'click3/index.html') // 1024, 'KB')

# ---------- Rob's edits v2 (click4/index.html): Rob's edits in the brand palette (Colors.pdf) ----------
# greens Abyss #070D0A, #1A372A, #2E6149, Kelp #408967, #67B791, #BADECD, Sea Foam #EBEBE3; accents gold #DCA84E, pink
# #F0A6CA, mauve #A2839E, sage #8AB0AB, deep green #3F7965, ice blue #CEE5F3, slate #90A9B7. Deep Abyss greens behind,
# Sea Foam type and lines, Kelp for accents, the palette's gold for the clasp, its accents for the proteins.
C4_PAL = ("PAL.otx = { ...PAL.otx, ring: '#1A372A', ink: '#070D0A', brd4: '#F0A6CA', vhl: '#CEE5F3', elob: '#8AB0AB', eloc: '#67B791', warhead: '#F0A6CA', e3lig: '#CEE5F3', "
          "linker: '#EBEBE3', brk: '#DCA84E', ub: '#A2839E', pearl3d: '#FFFFFF', clasp: '#DCA84E', e2: '#CEE5F3', prot: '#A2839E', protcap: '#90A9B7', wall: '#408967', cell: '#2E6149', "
          "flash: '#DCA84E', sky: [['#2E6149', '#1A372A'], ['#2E6149', '#1A372A'], ['#1A372A', '#070D0A']] };\n")
c4_head = c3_head.replace("<title>SELFTAC Journey Rob's Edits</title>", "<title>SELFTAC Journey Rob's Edits v2</title>", 1).replace('<meta name="theme-color" content="#158B63">', '<meta name="theme-color" content="#1A372A">') + '''<style>
/* the brand palette */
:root[data-palette="otx"] { --ink: #EBEBE3; --muted: #BADECD; --accent: #67B791; --paper: #1A372A; --band: #2E6149; --pearl: #DCA84E; --clasp: #DCA84E;
  --line: #408967; --card: #2E6149; }
/* every colour below is a swatch from the palette, used solid */
body { background: #1A372A; }
.beat h1, .beat h2 { color: #EBEBE3; } .beat p { color: #BADECD; } .beat .k { color: #EBEBE3; } .beat .k b { color: #67B791; }
.jl { background: #070D0A; color: #EBEBE3; -webkit-backdrop-filter: none; backdrop-filter: none; }
.jl.sm { background: #070D0A; color: #BADECD; }
.jl.big { background: #070D0A; color: #67B791; border-color: #408967; }
.jl.hi { color: #67B791; }
.jl.loc { background: #070D0A; border-color: #408967; color: #EBEBE3; }
.jl.key { background: #070D0A; border-color: #408967; color: #EBEBE3; }
.jbtn { background: #2E6149; border-color: #408967; color: #EBEBE3; } .jbtn:hover { background: #408967; }
.jbtn.jnext { background: #EBEBE3; border-color: #EBEBE3; color: #1A372A; } .jbtn.jnext:hover { background: #FFFFFF; }
.jplay.on { background: #408967; border-color: #67B791; }
.jcount { color: #BADECD; }
.jedit { background: #070D0A; border-color: #2E6149; } .jedit .jf span, .jedit .jst { color: #BADECD; } .jedit legend b { color: #67B791; }
.jedit input, .jedit textarea { background: #1A372A; border-color: #408967; color: #EBEBE3; } .jedit .jx { background: #2E6149; color: #EBEBE3; }
.jedit header, .jedit footer, .jedit fieldset { border-color: #2E6149; }
.jedit-btn { background: #2E6149; border-color: #408967; color: #EBEBE3; }
.end .tag { color: #EBEBE3; } .end .tag em { color: #67B791; } .end a { background: #2E6149; color: #EBEBE3; border-color: #408967; }
/* the palette's gold, more: the progress bar (its dots and fill) and the Next button */
.rail i { background: #2E6149; } .rail i b { background: #DCA84E; }
.rail div::before { border-color: #408967; }
.rail div.on::before, .rail div:nth-child(4).on::before { background: #DCA84E; border-color: #DCA84E; }
.jbtn.jnext { background: #DCA84E; border-color: #DCA84E; color: #070D0A; } .jbtn.jnext:hover { background: #DCA84E; border-color: #DCA84E; }   /* stays gold (it nudges right on hover) */
/* the hint's mouse clicks (its left button flashes gold) rather than scrolls */
.hint i::before { content: ""; position: absolute; left: 50%; top: 0; width: 1.5px; height: 42%; margin-left: -.75px; background: #EBEBE3; }
.hint i::after { left: 0; top: 0; width: 50%; height: 42%; margin: 0; border-radius: 10px 0 0 0; background: #DCA84E; animation: jclick 1.6s ease-in-out infinite; }
@keyframes jclick { 0%, 45%, 100% { opacity: .15; } 55%, 70% { opacity: 1; } }
@media (prefers-reduced-motion: reduce) { .hint i::after { animation: none; opacity: 1; } }
</style>
'''
assert "<title>SELFTAC Journey Rob's Edits v2</title>" in c4_head
c4_page = c4_head + c3_page[len(c3_head):]
c4_page = once(c4_page, "PAL.otx.protcap = '#D6CBFA';\n", "PAL.otx.protcap = '#D6CBFA';\n" + C4_PAL)
# the background takes the palette's exact values (a colour-space round trip would nudge the last digit)
c4_page = once(c4_page, "const mix = (a, b, t) => '#' + new THREE.Color(a).lerp(new THREE.Color(b), t).getHexString();",
               "const mix = (a, b, t) => t <= .01 ? a : t >= .99 ? b : '#' + new THREE.Color(a).lerp(new THREE.Color(b), t).getHexString();")
# the background stars in the palette's tones
for a, b in (('%23CFFFFF', '%23BADECD'), ('%2396FF87', '%2367B791'), ('%23FFB36B', '%23DCA84E'), ('%23F7D16B', '%23DCA84E'), ('%23FFFFFF', '%23EBEBE3')):
    c4_page = c4_page.replace(a, b)
C4_TEXT = json.load(open(D + 'text/click4.json', encoding='utf8'))   # this page's own words (its version of record)
c4_page = re.sub(r'(<script type="application/json" id="c2text">).*?(</script>)', lambda m: m.group(1) + json.dumps(C4_TEXT, ensure_ascii=False).replace('<', '\\u003c') + m.group(2), c4_page, count=1, flags=re.S)
# v2 takes v3's larger proteasome too (and the cell's molecules measured around it); c4_page itself stays as v3's base
def big_proteasome(pg):
    pg = once(pg, 'PK = .225, PMID = 76;', 'PK = .28, PMID = 76;')
    pg = once(pg, 'PROT.y - 30 - f.dy * ease(t)', 'PROT.y - 44 - f.dy * ease(t)')
    pg = once(pg, 'const PROT = V3(X.prot - 10, 6, 0)', 'const PROT = V3(X.prot - 22, 6, 0)')
    pg = once(pg, f'class="jl loc" data-x="{X["prot"] - 10 + 66}" data-y="14"', f'class="jl loc" data-x="{X["prot"] - 22 + 76}" data-y="18"')
    pg = once(pg, 'class="jl loc" data-x="630" data-y="-86"', f'class="jl loc" data-x="{X["prot"] - 22 + 74}" data-y="-78"')
    cells = ''.join(f"  {{ at: 'cell', kind: '{_kinds[i % 3]}', dx: {x - X['complex']}, y: {y}, s: .68, r: {[.5, -.3, -.4, .35, .2, -.5, .45][i % 7]}, hx: 11, ph: {1 + .7 * i:.1f}, win: pn => cellIn(pn) }},\n"
                    for i, (x, y) in enumerate(json.load(open(D + 'cell_layout_v3.json'))))
    pg, n = re.subn(r"(  \{ at: 'cell', kind: [^\n]*\n)+", lambda m: cells, pg, count=1); assert n == 1
    return pg
os.makedirs(D + 'click4', exist_ok=True)
open(D + 'click4/index.html', 'w').write(big_proteasome(c4_page))
print('click4/index.html', os.path.getsize(D + 'click4/index.html') // 1024, 'KB')

# ---------- Rob's edits v3 (click5/index.html): v2 with the review's changes ----------
# the degrader lets go and moves on after the target is degraded (v3.js); the barrier labelled "Biological membrane" (the
# blood-brain barrier stays in the copy); a tighter autoplay (clicks unchanged); copy trimmed to about 20 words a step;
# two label styles only (places, and things); gold kept for the SELFTAC and the next step; a lighter proteasome mesh
c5_head = c4_head.replace("<title>SELFTAC Journey Rob's Edits v2</title>", "<title>SELFTAC Journey Rob's Edits v3</title>", 1) + '''<style>
/* two label styles: places (mono, uppercase pills) and things (sans pills, like the protein labels) */
.jl:not(.loc):not(.key):not(.plus):not(.eq) { font: 600 13px/1 var(--sans); letter-spacing: .01em; text-transform: none; padding: 7px 12px; border-radius: 999px;
  background: #070D0A; border: 1px solid #408967; color: #EBEBE3; }
.jl.eqf b { color: #DCA84E; }
@media (max-width: 760px) { .jl:not(.loc):not(.key):not(.plus):not(.eq) { font-size: 11.5px; padding: 5px 10px; } }
</style>
'''
c5_page = c5_head + c4_page[len(c4_head):]
c5_page = c5_page.replace('>Cell membrane &middot; blood-brain barrier</span>', '>Biological membrane</span>')
assert '>Biological membrane</span>' in c5_page
c5_page = once(c5_page, PROTMESH, '<script type="application/json" id="protmesh">' + open(D + 'proteasome_lite.json').read() + '</script>')
c5_page = once(c5_page, open(D + 'rob.js').read(), open(D + 'rob.js').read() + '\n' + open(D + 'v3.js').read())
# autoplay a quarter quicker, with shorter holds where an equilibrium plays; clicks unchanged
c5_page = once(c5_page, 'Math.max(2300, Math.min(4800, 1900 + d * 12000))', 'Math.max(1700, Math.min(3600, 1400 + d * 9000))')
c5_page = once(c5_page, 'const HOLD = [300, 550, 300, 2400, 900, 550, 2200, 450, 400];', 'const HOLD = [250, 450, 250, 1700, 700, 450, 1600, 350, 900];')
# a bigger proteasome (a quarter up), its fragments leaving from the bottom of the larger core, its labels moved out with it
# the monomers that cross the membrane click back together into a dimer in the cell first (a flash at the clasp and a
# label), and only then do the proteins come in and the dimer form the ternary complex; a stop holds on the dimer
c5_page = once(c5_page, "const HX = curve([[.27, 7], [.31, 13], [.44, 13], [.56, 30], [.6, 30], [.67, GAPJ]]);",
               "const HX = curve([[.27, 7], [.31, 13], [.44, 13], [.585, 13], [.615, 7], [.645, 7], [.68, GAPJ]]);   // apart through the membrane; a compact dimer in the cell; opened to the proteins")
c5_page = once(c5_page, "const j = kf(p, [[.27, 1], [.31, 0], [.64, 0], [.68, 1]]);", "const j = kf(p, [[.27, 1], [.31, 0], [.585, 0], [.615, 1]]);   // rejoined in the cell, before the proteins")
c5_page = once(c5_page, "const tIn = kf(p, [[.58, 1], [.66, 0]]);", "const tIn = kf(p, [[.622, 1], [.68, 0]]);   // the proteins come in once the dimer has formed")
c5_page = once(c5_page, "const fb = bump(p, .27, .31), fj = bump(p, .655, .7), fx = Math.max(fb, fj);", "const fb = bump(p, .27, .31), fj = bump(p, .588, .628), fx = Math.max(fb, fj);")
c5_page = once(c5_page, ": 1 + 3 * clamp((p - .655) / .045, 0, 1)));", ": 1 + 3 * clamp((p - .588) / .04, 0, 1)));")
c5_page = once(c5_page, "const STOPS = [0, .25, .335, .45, .59, .665, .79, .865, .92, .998];", "const STOPS = [0, .25, .335, .45, .59, .665, .716, .79, .865, .92, .998];")
c5_page = once(c5_page, "const SLOW = { 4: 1.3, 5: 2.6, 6: 1.9, 7: 1.8, 8: 2.6 };", "const SLOW = { 4: 1.3, 5: 2.6, 6: 2.2, 7: 1.9, 8: 1.8, 9: 2.6 };")
c5_page = once(c5_page, "const BEAT_STOP = [0, 1, 3, 4, 6, 7];", "const BEAT_STOP = [0, 1, 3, 4, 6, 8];")
c5_page = once(c5_page, "const HOLD = [250, 450, 250, 1700, 700, 450, 1600, 350, 900];", "const HOLD = [250, 450, 250, 1700, 700, 450, 1300, 1600, 350, 900];")
c5_page = big_proteasome(c5_page)   # the larger proteasome, its labels and fragments, and the cell's molecules placed around it
C5_TEXT = json.load(open(D + 'text/click5.json', encoding='utf8'))
c5_page = re.sub(r'(<script type="application/json" id="c2text">).*?(</script>)', lambda m: m.group(1) + json.dumps(C5_TEXT, ensure_ascii=False).replace('<', '\\u003c') + m.group(2), c5_page, count=1, flags=re.S)
os.makedirs(D + 'click5', exist_ok=True)
open(D + 'click5/index.html', 'w').write(c5_page)
print('click5/index.html', os.path.getsize(D + 'click5/index.html') // 1024, 'KB')

# ---------- Rob's edits v4 (click6/index.html): v3 with the SELFTAC drawn as pearl clusters ----------
# The "Pearl cluster" option from the representations gallery (reps/): each half of the degrader drawn as a few glossy
# pearls in its colour, set at centres spread along the half's mass (reps/reps_data.json), in place of the traced rings.
# The halves keep their places, so the linker, its pearls and the gold clasp are unchanged; the pearls use the halves'
# own materials, so colours and fades carry over. Everything else is v3.
PEARLS = json.load(open(D + 'reps/reps_data.json'))['reps']
c6_page = c5_page.replace("<title>SELFTAC Journey Rob's Edits v3</title>", "<title>SELFTAC Journey Rob's Edits v4</title>", 1)
c6_page = once(c6_page, '  const [cW, cE] = heads.map(h => h.c);\n', '''  const [cW, cE] = heads.map(h => h.c);
  // v4: each half drawn as a cluster of pearls in its colour (the traced rings hidden, their geometry kept for the
  // linker's inside test and the halves' extents)
  { const PC = ''' + json.dumps({k: PEARLS[k]['pearls'] for k in ('warhead', 'e3lig')}) + ''', pb = new THREE.SphereGeometry(1, 32, 22);
    heads.forEach((h, i) => { const k = ['warhead', 'e3lig'][i]; h.mesh.material = new THREE.MeshBasicMaterial({ visible: false }); h.mesh.children[0].visible = false;   // (its own material, as the pearls share the half's)
      PC[k].forEach(c => { const s = new THREE.Mesh(pb, mats[k]); s.position.set(...c); s.scale.setScalar(1.55); s.add(outline(s)); h.mesh.add(s); }); });
    mats.warhead.uniforms.gloss.value = mats.e3lig.uniforms.gloss.value = .9; }
''')
C6_TEXT = json.load(open(D + 'text/click6.json', encoding='utf8'))
c6_page = re.sub(r'(<script type="application/json" id="c2text">).*?(</script>)', lambda m: m.group(1) + json.dumps(C6_TEXT, ensure_ascii=False).replace('<', '\\u003c') + m.group(2), c6_page, count=1, flags=re.S)
os.makedirs(D + 'click6', exist_ok=True)
open(D + 'click6/index.html', 'w').write(c6_page)
print('click6/index.html', os.path.getsize(D + 'click6/index.html') // 1024, 'KB')
