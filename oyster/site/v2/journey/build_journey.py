"""Build the SELFTAC journey (journey/index.html): the slide's story told left to right as the page scrolls, with the
site's own 3D models. Oral dosing; the dimer and its monomers in equilibrium; across the cell membrane and the
blood-brain barrier; the halves clasped back together in a ternary complex; tagging and the proteasome.

The scene setup (palettes, renderer, the protein parts, the degrader, ubiquitin, the proteasome) is the story's own,
taken from ../../palettes.html up to its timeline; journey.js adds the left-to-right timeline. The page shell is the
v2 Science page's (site.css and site.js, published beside it), with the logo and palette switch and no page links.
The person, the gut, the absorption beam and the membrane are flat illustrations drawn in the 3D scene's plane.
Run ../build_v2.py first."""
import math, os, re
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
# the person, facing right, drawn y-down and flipped into the world (head about y 42, the gut at y -25)
PERSON_D = ('M -10,-74 C -2,-80 10,-78 14,-70 C 16,-66 16,-62 17,-59 L 21,-53 L 17,-51 C 17,-49 17,-48 18,-46 C 17,-45 16,-44 17,-43 '
            'C 16,-40 14,-37 11,-36 C 9,-35 8,-33 8,-29 L 9,-22 C 20,-19 34,-15 38,-2 L 42,80 L -42,80 L -38,-2 C -34,-15 -20,-19 -10,-22 '
            'L -10,-30 C -18,-36 -20,-48 -19,-58 C -18,-68 -14,-72 -10,-74 Z')
GUT = ('<circle cx="0" cy="25" r="21" style="fill:var(--paper);fill-opacity:.9;stroke:var(--ink);stroke-width:1.6"/>'
       '<g style="fill:none;stroke:var(--ink);stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round">'
       '<path d="M -12 36 L -12 15 Q -12 10 -7 10 L 7 10 Q 12 10 12 15 L 12 33 Q 12 37 8 37 L 3 37"/>'
       '<path d="M -7 16 C -2 13 4 13 7 16 C 4 19 -3 19 -7 22 C -3 25 4 25 7 22 C 4 26 -2 28 -6 30"/>'
       '<path d="M 1 37 L 1 43"/></g>')
person = (f'<g id="jperson"><g transform="scale(1 -1)"><path d="{PERSON_D}" style="fill:url(#jpersonG)"/>'
          f'<path d="M 16,-40 L 26,-44" style="stroke:var(--ink);stroke-opacity:.25;stroke-width:1"/>{GUT}</g></g>')
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
       f'</defs><g id="jworld">{beam}{membrane}{person}{pill}</g></svg>')

EQ = ('<svg viewBox="0 0 52 24" aria-hidden="true"><path d="M4 8 H46 L39 3" fill="none" stroke="var(--clasp)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>'
      '<path d="M48 16 H6 L13 21" fill="none" stroke="var(--clasp)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>')
def label(text, x, y, a, b, cls=''):
    return f'<span class="jl {cls}" data-x="{x}" data-y="{y}" data-a="{a}" data-b="{b}">{text}</span>'
labels = '<span class="jl plus" id="jplus">+</span>' + ''.join([
    label('Oral dosing', 74, 78, -1, .13),
    label('Dimer', X['dimer'], -27, .18, .45), label('Monomers', X['mono'], -31, .18, .45),
    label(EQ, (X['dimer'] + X['mono']) / 2 - 2, 0, .18, .45, 'eq'),
    label('Cell membrane &middot; blood-brain barrier', X['mem'] + 4, -50, .42, .62),
    label('Target cell', X['mem'] + 70, 52, .5, .62, 'hi'),
    label('Target protein', X['complex'] + 62, 58, .64, .84), label('E3 ligase', X['complex'] + 66, -62, .64, .84),
    label('Ternary complex', X['complex'], -96, .68, .84, 'hi'),
    label('Proteasome', X['prot'], 50, .84, .99), label('Degradation', X['prot'], -86, .915, .99, 'hi'),
])
TM = '<span translate="no">SELFTAC&reg;</span>'
beats = [
    ('01 &middot; Oral dosing', 'h1', 'Taken by mouth, as a pill.', f'{TM} degraders are designed to be small enough to be swallowed, not injected.'),
    ('02 &middot; Dimer &#8652; monomers', 'h2', 'Two halves that come apart and back together.', f'A reversible linker lets each {TM} molecule shift between one degrader, the dimer, and its two small monomers.'),
    ('03 &middot; The barrier', 'h2', 'Small enough to cross into the cell.', 'As monomers, each half crosses the cell membrane, and the blood-brain barrier into the brain.'),
    ('04 &middot; Ternary complex', 'h2', 'Inside the cell, the halves clasp back together.', 'One end holds the target protein, the other an E3 ligase: a ternary complex.'),
    ('05 &middot; Degradation', 'h2', 'Tagged, then broken down.', 'Ubiquitin marks the target and the proteasome destroys it. The degrader is free to find the next one.'),
]
copy = ''.join(f'<div class="beat"><span class="k">{k}</span><{h}>{t}</{h}><p>{d}</p></div>' for k, h, t, d in beats)
rail = ''.join(f'<div><span>{n}</span><i><b></b></i></div>' for n in ('Oral', 'Equilibrium', 'Barrier', 'Complex', 'Degraded'))
DOWN = '<svg viewBox="0 0 14 14" aria-hidden="true"><path d="M7 2v10M3 8l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
story = (f'<section class="story" id="story" aria-label="How a SELFTAC degrader goes from a pill to a cleared protein">'
         f'<div class="stage" id="stage">{svg}<canvas id="gl" aria-hidden="true"></canvas>{labels}'
         f'<div class="copy" id="copy">{copy}</div>{end}'
         f'<div class="hint" id="hint"><span>Scroll to follow a {TM} molecule</span><i aria-hidden="true"></i></div>'
         f'<a class="skip" id="skip" href="#more">Skip the story{DOWN}</a>'
         f'<div class="rail" id="rail" aria-hidden="true">{rail}</div></div></section>\n')
more = (f'<section class="band" id="more"><div class="wrap"><p class="eyebrow rv">{CG}<span>About this story</span></p>'
        '<h2 class="say rv">From a pill to a cleared protein.</h2>'
        '<p class="lede rv">The proteins are smoothed surfaces of real structures: BRD4, VHL and Elongin B and C from PDB 5T35 (Gadd et al., Nat. Chem. Biol. 2017), '
        f'and ubiquitin from PDB 1UBQ. The degrader is drawn generically and stands in for a {TM} compound, and the proteasome is a stand-in. '
        'The person, the gut and the membrane are illustrations.</p></div></section>\n')
meshes = re.search(r'<script type="application/json" id="meshes">.*?</script>', sci, re.S).group(0)
page = (head + '<canvas id="bgArt" aria-hidden="true"></canvas>\n<a class="sr-only" href="#more">Skip to content</a>\n' + header + '\n'
        + '<main id="main">\n' + story + more + '</main>\n' + meshes + '\n<script type="module">' + prefix + open(D + 'journey.js').read() + '</script>\n'
        + '<script type="module" src="site.js"></script>\n')
for gone in ('href="index.html"', 'href="science.html"'):
    assert gone not in header, gone
open(D + 'index.html', 'w').write(page)
print('index.html', os.path.getsize(D + 'index.html') // 1024, 'KB')
