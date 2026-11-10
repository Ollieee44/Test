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
# proteasome, so the complex left behind stays clear of the degradation copy; inside the cell it sits a little higher,
# clear of the controls
c2_js = once(c2_js, 'if (narrow) ay -= .17 * vh * settle; else ax -= .17 * vw * settle;',
             'if (narrow) ay -= .22 * vh * settle; else { ax -= (.2 + .1 * kf(p, [[.855, 0], [.885, 1]])) * vw * settle; ay -= .035 * vh * kf(p, [[.6, 0], [.68, 1]]) * settle; }')
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
c2_page = (c2_head + '<main id="main">\n' + c2_story + '</main>\n' + meshes + '\n' + PROTMESH + '\n<script type="module">' + c2_prefix + '\n' + C2_PAL
           + c2_js + '\n' + open(D + 'otx.js').read() + '\n' + open(D + 'plasma.js').read() + '\n' + open(D + 'cell.js').read() + '\n' + c2_click + '</script>\n')
os.makedirs(D + 'click2', exist_ok=True)
open(D + 'click2/index.html', 'w').write(c2_page)
print('click2/index.html', os.path.getsize(D + 'click2/index.html') // 1024, 'KB')
