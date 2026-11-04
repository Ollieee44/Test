"""Build the SELFTAC pearl variations (index.html): a grid of eight static heroes in the Tidepool palette, from the
detailed complex to blueprint line-work and a macro of the pearl, each with the join of the reversible linker drawn as
one realistic pearl. Render the stills first with render_pearl.js (see that file).

Every hero is drawn at 1440 x 810 and scaled into its card. The degrader is generic and drawn larger than true
scale, with the proteins eased apart so its linker shows; the credit on each hero says so."""
import json, os, re
D = os.path.dirname(os.path.abspath(__file__)) + '/'
PAGES = D + '../pages/'
NAMES = ['v1-detailed', 'v2-pods', 'v3-silhouette', 'v4-ghost', 'v5-blueprint', 'v6-callouts', 'v7-strand', 'v8-macro']
A = {k: json.load(open(D + f'img/{k}.json')) for k in NAMES}
home = re.search(r'<a class="home".*?</a>', open(PAGES + 'index.html').read(), re.S).group(0)
WM = re.search(r'<svg class="wm".*?</svg>', home, re.S).group(0)
ARROW = '<svg viewBox="0 0 14 14" aria-hidden="true"><path d="M2 7h10M8 3l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
SELFTAC = '<span translate="no">SELFTAC&reg;</span>'
NAV = ''.join(f'<span>{n}</span>' for n in ('Science', 'Pipeline', 'Team', 'Investors', 'News', 'Contact'))
# one small pearl, shaded like the rendered one, for the eyebrows
_pg = [0]
def pearl_icon():
    _pg[0] += 1; i = f'pgG{_pg[0]}'   # each with its own gradient, so none depends on another card being shown
    return (f'<svg class="pg" viewBox="0 0 14 14" aria-hidden="true"><defs><radialGradient id="{i}" cx="38%" cy="32%" r="70%">'
            '<stop offset="0" stop-color="#FFFFFF"/><stop offset=".35" stop-color="#F1E9E2"/><stop offset=".8" stop-color="#E4D6D6"/><stop offset="1" stop-color="#C9D8CF"/></radialGradient></defs>'
            f'<circle cx="7" cy="7" r="6" fill="url(#{i})"/></svg>')
CREDIT = ('Drawn from PDB 5T35 (BRD4, VHL, Elongin B and C; Gadd et al., Nat. Chem. Biol. 2017). '
          'The degrader is generic, drawn larger than true scale, with the proteins eased apart so its linker shows.')
CREDIT_MOL = 'The degrader is generic and drawn abstractly, larger than true scale.'
LEDE = f'{SELFTAC} molecules travel as two small halves and close at the pearl, a reversible linker, inside the cell.'

def box(key): return (0, 0, 1440, 810)   # each still fills the hero (render_pearl.js frames it clear of the header)
def pt(key, k, bx=None):
    bx = bx or box(key); x, y = A[key][k]; return round(bx[0] + x * bx[2]), round(bx[1] + y * bx[3])
def radius(key, bx=None):
    (x0, y0), (x1, y1) = pt(key, 'pearl', bx), pt(key, 'pearlTop', bx); return round(((x1 - x0) ** 2 + (y1 - y0) ** 2) ** .5)
def tag(text, ax, ay, lx, ly, cls=''):
    return (f'<svg class="ld" width="1440" height="810" aria-hidden="true"><line x1="{lx}" y1="{ly}" x2="{ax}" y2="{ay}"/><circle cx="{ax}" cy="{ay}" r="3.5"/></svg>'
            f'<span class="tg {cls}" style="left:{lx}px;top:{ly}px">{text}</span>')
def pearl_chip(key, dx=0, dy=110):
    """the label on the pearl: a leader from the pearl's lower right edge to a chip below and to the right"""
    (cx, cy), r = pt(key, 'pearl'), radius(key)
    ax, ay = round(cx + r * .7), round(cy + r * .7)
    return tag('The pearl &middot; reversible linker', ax, ay, ax + dx, min(ay + dy, 700), 'chip')
def ctas(): return f'<div class="mc"><span class="b"><span>See how it works</span>{ARROW}</span><span class="b gh"><span>Our pipeline</span></span></div>'
def hero(key, eyebrow, title, lede, place='tl', extra='', credit=CREDIT, blueprint=False, size=58, buttons=True):
    copy = (f'<div class="tx {place}"><p class="ey">{pearl_icon()}<span>{eyebrow}</span></p><h2 class="h1" style="font-size:{size}px">{title}</h2>'
            + (f'<p class="lede">{lede}</p>' if lede else '') + (ctas() if buttons else '') + '</div>')
    return (f'<div class="mock{" bp" if blueprint else ""}"><img src="img/{key}.png" alt="" style="top:{box(key)[1]}px">'
            f'<div class="mh">{WM}<nav>{NAV}</nav></div>{copy}{extra}<p class="cr{" l" if place == "bl" else ""}">{credit}</p></div>')

# V6: the blueprint as an annotated drawing, labels above and below on a measured layout
v6 = 'v6-callouts'
P6 = {k: pt(v6, k) for k in A[v6]}
r6 = radius(v6)
callouts = (tag('Target-binding end', P6['endW'][0], P6['endW'][1] - 16, P6['endW'][0], 300, 'up')
            + tag('Ligase-binding end', P6['endE'][0], P6['endE'][1] + 22, P6['endE'][0] - 30, 670)
            + tag('Target protein<b>BRD4</b>', P6['target'][0], P6['target'][1] + 40, P6['target'][0] - 20, 670)
            + tag('The pearl<b>reversible linker</b>', P6['pearl'][0], P6['pearl'][1] + r6, P6['pearl'][0], 670, 'hi')
            + tag('E3 ligase<b>VHL, Elongin B and C</b>', P6['ligase'][0], P6['ligase'][1] + 50, P6['ligase'][0] + 40, 670))

V = [
    ('v1-detailed', 'Detailed', 'The traced ends of the degrader in their pockets, as on the Science page; the join is now the pearl.',
     hero('v1-detailed', 'The pearl', 'Where two halves become one degrader.', LEDE, extra=pearl_chip('v1-detailed', 150, 70))),
    ('v2-pods', 'Pods', 'E in Tidepool: each end of the degrader a plain glossy pod, threaded on the strand.',
     hero('v2-pods', 'The pearl', 'Two small halves, one pearl between them.', LEDE, extra=pearl_chip('v2-pods', 150, 70))),
    ('v3-silhouette', 'Silhouette', 'The proteins as flat shapes with no contour lines, so the only texture in the picture is the pearl&rsquo;s.',
     hero('v3-silhouette', 'The pearl', 'Small enough to travel. Whole where it works.', LEDE, extra=pearl_chip('v3-silhouette', 150, 70))),
    ('v4-ghost', 'Ghost', 'The proteins see-through, as if out of focus; the degrader and its pearl are the solid things.',
     hero('v4-ghost', 'The pearl', 'The pearl holds the target to the ligase.', LEDE, extra=pearl_chip('v4-ghost', 150, 70))),
    ('v5-blueprint', 'Blueprint', 'Line-work on a drafting grid: the proteins and the degrader are drawn, only the pearl is rendered.',
     hero('v5-blueprint', f'Fig. 1 &middot; {SELFTAC}', 'Built to come apart, and to close again at the pearl.', LEDE, extra=pearl_chip('v5-blueprint', 150, 70), blueprint=True, size=54)),
    ('v6-callouts', 'Blueprint, annotated', 'The blueprint as a labelled drawing: both ends, the pearl, the target and the ligase. Most explanatory.',
     hero('v6-callouts', f'Fig. 2 &middot; {SELFTAC}', f'Anatomy of a {SELFTAC} degrader.', '', extra=callouts, blueprint=True, size=46, buttons=False)),
    ('v7-strand', 'Strand', 'The proteins gone: just the degrader, a strand with a pod at each end and the pearl at its heart. Most abstract.',
     hero('v7-strand', 'The pearl', 'A strand of small molecules with a pearl at its heart.', LEDE, place='bl', extra=pearl_chip('v7-strand', 120, 60), credit=CREDIT_MOL, size=54)),
    ('v8-macro', 'Pearl macro', 'Right in on the pearl itself: its sheen, growth rings and highlights, with the strand running through it.',
     hero('v8-macro', 'The pearl', 'Where two halves become one.', LEDE, place='bl', credit=CREDIT_MOL)),
]

page = '''<title>SELFTAC Pearl Variations</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=swap">
<style>
/* Layout: a two-column grid of 1440 x 810 heroes, each drawn at full size and scaled into its card, with a name and
   a line under it. The whole page is in Tidepool, one dark look on purpose. */
:root { --ink: #EAF3EF; --muted: #B6D3CB; --accent: #F2B84B; --paper: #0F4C4A; --band: #0C4341; --deep: #0A3836; --pearl: #F2B84B; --clasp: #F27D62;
  --nacre: #F1E9E2; --line: rgba(234, 243, 239, .18);
  --serif: "Newsreader", "Iowan Old Style", Georgia, serif; --sans: "Archivo", "Helvetica Neue", Arial, sans-serif; --mono: "IBM Plex Mono", ui-monospace, Menlo, monospace;
  color-scheme: dark; }
* { box-sizing: border-box; }
body { margin: 0; background: var(--deep); color: var(--ink); font: 400 16px/1.55 var(--sans); -webkit-font-smoothing: antialiased; }
.wrap { max-width: 1480px; margin: 0 auto; padding-block: 56px 80px; padding-inline: max(16px, 3vw); }
.top { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 24px 48px; align-items: end; margin-bottom: 40px; }
@media (max-width: 860px) { .top { grid-template-columns: minmax(0, 1fr); } }
.top .k { font: 500 12px/1 var(--mono); letter-spacing: .14em; text-transform: uppercase; color: var(--accent); margin: 0 0 16px; display: flex; align-items: center; gap: 10px; }
.top h1 { font: 500 clamp(36px, 5vw, 64px)/1.02 var(--serif); letter-spacing: -.02em; margin: 0; }
.top p.d { color: var(--muted); margin: 0; max-width: 60ch; }
.grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 40px 24px; }
@media (max-width: 860px) { .grid { grid-template-columns: minmax(0, 1fr); } }
.card { margin: 0; display: grid; gap: 14px; }
.frame { position: relative; width: 100%; aspect-ratio: 16 / 9; max-width: 100%; overflow: hidden; border-radius: 14px; border: 1px solid var(--line); background: var(--paper); }
.frame .mock { transform: scale(var(--s, .45)); transform-origin: 0 0; }
.card figcaption { display: grid; grid-template-columns: auto minmax(0, 1fr); gap: 4px 14px; align-items: baseline; }
.card figcaption b { font: 500 12px/1 var(--mono); letter-spacing: .12em; color: var(--accent); }
.card figcaption h2 { font: 500 22px/1.15 var(--serif); margin: 0; }
.card figcaption p { grid-column: 2; margin: 0; color: var(--muted); font-size: 15px; }
.foot { margin-top: 64px; color: var(--muted); font-size: 14px; max-width: 80ch; }

/* ---------- a hero, at 1440 x 810, in Tidepool ---------- */
.mock { position: absolute; left: 0; top: 0; width: 1440px; height: 810px; overflow: hidden; color: var(--ink);
  background: radial-gradient(130% 120% at 68% 28%, #1B6763 0%, #0F4C4A 100%); font: 400 16px/1.55 var(--sans); }
.mock.bp { background: linear-gradient(rgba(234, 243, 239, .07) 1px, transparent 1px) 0 0 / 120px 120px, linear-gradient(90deg, rgba(234, 243, 239, .07) 1px, transparent 1px) 0 0 / 120px 120px,
  linear-gradient(rgba(234, 243, 239, .03) 1px, transparent 1px) 0 0 / 24px 24px, linear-gradient(90deg, rgba(234, 243, 239, .03) 1px, transparent 1px) 0 0 / 24px 24px, #0C4341; }
.mock > img { position: absolute; left: 0; top: 0; width: 1440px; height: 810px; display: block; max-width: none;
  -webkit-mask-image: linear-gradient(transparent 56px, #000 136px); mask-image: linear-gradient(transparent 56px, #000 136px); }   /* the header sits on clear ground */
.mh { position: absolute; left: 40px; right: 40px; top: 22px; display: flex; align-items: center; gap: 28px; z-index: 2; }
.mh .wm { height: 42px; width: auto; display: block; color: var(--ink); }
.mh nav { margin-left: auto; display: flex; gap: 22px; font: 500 13.5px/1 var(--sans); }
.pg { width: 14px; height: 14px; margin-right: 10px; flex: none; }
.ey { font: 500 12px/1 var(--mono); letter-spacing: .14em; text-transform: uppercase; color: var(--accent); margin: 0 0 22px; display: flex; align-items: center; }
.h1 { font: 500 58px/1.03 var(--serif); letter-spacing: -.02em; margin: 0; text-wrap: balance; }
.lede { font-size: 19px; color: var(--muted); margin: 18px 0 0; max-width: 44ch; }
.mc { display: flex; gap: 12px; margin-top: 28px; }
.b { display: inline-flex; align-items: center; gap: 10px; font: 500 14px/1 var(--sans); padding: 14px 20px; border-radius: 999px; background: var(--ink); color: var(--paper); border: 1px solid var(--ink); }
.b svg { width: 13px; height: 13px; }
.b.gh { background: transparent; color: var(--ink); border-color: var(--line); }
.tx { position: absolute; width: 600px; z-index: 2; }
#v6-callouts .tx { width: 1000px; }
.tx.tl { left: 96px; top: 118px; }
.tx.bl { left: 96px; bottom: 112px; }
.cr.l { right: auto; left: 96px; text-align: left; }
.cr { position: absolute; right: 40px; bottom: 20px; margin: 0; font-size: 11.5px; color: var(--muted); max-width: 62ch; text-align: right; z-index: 2; }
.ld { position: absolute; left: 0; top: 0; pointer-events: none; z-index: 1; }
.ld line { stroke: var(--ink); stroke-width: 1; stroke-opacity: .5; }
.ld circle { fill: var(--paper); stroke: var(--ink); stroke-width: 1.2; }
.bp .ld line { stroke-dasharray: 4 4; }
.tg { position: absolute; z-index: 2; transform: translate(-50%, 0); font: 500 11px/1.3 var(--mono); letter-spacing: .12em; text-transform: uppercase; white-space: nowrap; text-align: center; padding-top: 6px; }
.tg b { display: block; font: 400 13px/1.35 var(--sans); letter-spacing: 0; text-transform: none; color: var(--muted); margin-top: 6px; }
.tg.up { transform: translate(-50%, -100%); padding: 0 0 6px; }
.tg.hi::before, .tg.chip::before { content: ""; display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-right: 9px; vertical-align: -1px;
  background: radial-gradient(circle at 35% 30%, #FFFFFF, #F1E9E2 45%, #D9CCCB 85%); box-shadow: 0 0 6px rgba(241, 233, 226, .6); }
.tg.chip { padding: 9px 14px; border-radius: 999px; background: rgba(15, 76, 74, .72); border: 1px solid var(--line); backdrop-filter: blur(6px); }
</style>
<div class="wrap">
  <header class="top"><div><p class="k">''' + pearl_icon() + '''Oyster &middot; Website v2 &middot; Tidepool</p><h1>The SELFTAC&reg; pearl</h1></div>
  <p class="d">Eight static heroes, from the detailed complex to blueprint line-work, each with the reversible linker&rsquo;s join drawn as one realistic pearl: cream nacre with a sheen that shifts with the angle, fine growth rings and two highlights. D and E are the first two.</p></header>
  <div class="grid">
<!--CARDS-->
  </div>
  <p class="foot">Every still is rendered from the website&rsquo;s own 3D models. The degrader is generic and stands in for a SELFTAC&reg; compound; it is drawn larger than true scale, with the proteins eased apart so its linker shows. Structures: BRD4, VHL and Elongin B and C from PDB 5T35 (Gadd et al., Nat. Chem. Biol. 2017).</p>
</div>
<script>
// draw each hero at 1440 wide and scale it to its card
(() => {
  const fit = () => document.querySelectorAll('.frame').forEach(f => f.style.setProperty('--s', (f.clientWidth / 1440).toFixed(4)));
  fit(); addEventListener('resize', fit);
  if (window.ResizeObserver) new ResizeObserver(fit).observe(document.querySelector('.grid'));
})();
</script>
'''
cards = ''.join(f'<figure class="card" id="{key}"><div class="frame" role="img" aria-label="Hero variation {i + 1}, {name}">{m}</div>'
                f'<figcaption><b>{i + 1:02d}</b><h2>{name}</h2><p>{desc}</p></figcaption></figure>\n'
                for i, (key, name, desc, m) in enumerate(V))
open(D + 'index.html', 'w').write(page.replace('<!--CARDS-->', cards))
print('index.html', os.path.getsize(D + 'index.html') // 1024, 'KB')
