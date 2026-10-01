"""Build beads.html: logo options built on the bead linker from the SELFTAC molecule icon.

Every mark lives in a 0-100 viewBox and uses three colours: currentColor for the shells and
beads, --p1 and --p2 for the palette accents. Run measure_beads.js afterwards to refresh
beads_ink.json (each mark's ink bounds), which sizes the mark when it stands in for the O.
"""
import json, math, os

D = os.path.dirname(os.path.abspath(__file__)) + '/'
LOW = 'M10 60C10 58 12 57 14 57H84C90 57 93 60 92 64C88 80 70 90 48 90C27 90 11 78 10 60Z'
UP = 'M12 53C12 51 13 50 15 50H84C90 50 93 47 91 44C85 34 66 29 46 30C27 31 13 40 12 53Z'
UPR = 'rotate(-24 12 53)'

def rot(p, deg=-24, c=(12, 53)):
    a = math.radians(deg); x, y = p[0] - c[0], p[1] - c[1]
    return (c[0] + x * math.cos(a) - y * math.sin(a), c[1] + x * math.sin(a) + y * math.cos(a))

def bead(x, y, r, fill=None):
    st = f' style="fill:var(--{fill})"' if fill else ''
    return f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}"{st}/>'

def ring(x, y, r, w):  # a hollow bead that stays hollow in one-colour use
    return f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r - w / 2:.2f}" fill="none" stroke="currentColor" stroke-width="{w:.2f}"/>'

def shells(mask_low='', mask_up=''):
    ml = f' mask="url(#{mask_low})"' if mask_low else ''
    mu = f' mask="url(#{mask_up})"' if mask_up else ''
    return f'<path d="{LOW}"{ml}/><path transform="{UPR}" d="{UP}"{mu}/>'

masks, syms = [], {}
def sym(id, body):
    syms[id] = f'<symbol id="{id}" viewBox="0 0 100 100"><g transform="translate(-1.5 1.5)">{body}</g></symbol>'

# 00 the current mark, for reference
sym('b-open', shells() + bead(62, 45.5, 10, 'p1'))

# 01 Bead Hinge: the hinge is cut away and replaced by a short chain of beads,
# so the two shells are held together by a linker, with the break bead in colour
masks.append('<mask id="mHinge" maskUnits="userSpaceOnUse" x="0" y="0" width="100" height="100"><rect width="100" height="100" fill="#fff"/><circle cx="18" cy="55" r="12.5" fill="#000"/></mask>')
hc, hr = (17.5, 55), 9
hinge = ''.join(bead(hc[0] + hr * math.cos(math.radians(a)), hc[1] + hr * math.sin(math.radians(a)), 5, 'p1' if a == 180 else None)
                for a in (-122, 180, 122))
sym('b-hinge', f'<g mask="url(#mHinge)">{shells()}</g>' + hinge + bead(62, 45.5, 9.5, 'p1'))

# 02 Pearl on a Strand: beads grow along a strand from the hinge into the pearl
strand = bead(26, 51.8, 2.8) + bead(35, 50.4, 3.5) + bead(45.2, 48.8, 4.3)
sym('b-strand', shells() + strand + bead(60, 46, 9, 'p1'))

# 03 Two Halves, Linked: the pearl becomes the degrader, two halves joined by a bead linker
linked = (bead(40.5, 48.4, 7.6, 'p1') + bead(51, 46.4, 2.7) + ring(57.1, 45.1, 3.4, 1.5) + bead(63.2, 43.8, 2.7)
          + bead(73.6, 40.8, 7.6, 'p2'))
sym('b-linked', shells() + linked)

# 04 Bead Ring: a macrocycle of beads makes the O; one link is open, flanked by the two
# accent beads, and the shell sits inside
N, R, rb = 15, 40.5, 5.3
ringb = ''
for i in range(N):
    a = -60 + i * 360 / N
    if i == 0: continue  # the open link
    x, y = 51.5 + R * math.cos(math.radians(a)), 48.5 + R * math.sin(math.radians(a))
    ringb += bead(x, y, rb, 'p1' if i == 1 else 'p2' if i == N - 1 else None)
sym('b-ring', ringb + f'<g transform="translate(51.5 49) scale(.6) translate(-51 -56)">{shells()}{bead(62, 45.5, 10, "p1")}</g>')

# 05 Beaded Valve: the upper shell is rebuilt as graduated beads, a linker opening the shell
cl = [(17, 49.5, 3.2), (26.5, 44.5, 4.6), (38, 41, 5.8), (50.5, 39.4, 6.4), (63, 39.6, 6.1), (74.5, 41.2, 5.1), (84.5, 43.8, 3.8)]
valve = ''.join(bead(*rot((x, y), -14), r) for x, y, r in cl)
sym('b-valve', f'<path d="{LOW}"/>' + valve + bead(62, 48.5, 8.2, 'p1'))

OPTS = [
    ('b-open', '00', 'The Open Shell', 'The current mark, shown for reference.',
     'Simple and recognisable at every size.', 'Says oyster and pearl, but nothing yet about the chemistry.'),
    ('b-hinge', '01', 'Bead Hinge', 'The hinge of the shell is replaced by a short chain of beads, so the two shells are joined by a linker, exactly as the two halves of a SELFTAC molecule are. The coloured bead is the reversible bond.',
     'The cleverest of the set: the linker is the hinge. The shell still reads first, and the idea rewards a second look.', 'The beads are small. Below 32px they merge into a solid hinge, which still looks like the original mark.'),
    ('b-strand', '02', 'Pearl on a Strand', 'Beads grow along a strand from the hinge into the pearl. It reads as a pearl being made, and as a linker leading to its payload.',
     'Calm and elegant, and the closest to the current mark. The growing beads add movement and work well animated.', 'The smallest bead drops out first. At 16px it is the current mark with a few dots.'),
    ('b-linked', '03', 'Two Halves, Linked', 'The pearl becomes the degrader: two halves in the two accent colours, joined by a three-bead linker with an open bead for the reversible bond. It is the SELFTAC icon from the animation, inside the shell.',
     'Ties the logo directly to the animation and the science. Uses both palette accents.', 'The most detailed option. It needs colour, and the linker is lost below 32px, where the two halves read as twin pearls.'),
    ('b-ring', '04', 'Bead Ring', 'A ring of beads, like a macrocycle, makes the O. One link is open, with the two accent beads on either side of the break, and the shell sits inside.',
     'A strong, compact badge with a built-in O for the wordmark. The open link gives the circle direction and tension.', 'Busy at 16px. Ring-of-dots marks are common, so the shell inside has to carry the identity.'),
    ('b-valve', '05', 'Beaded Valve', 'The upper shell is rebuilt as a row of graduated beads, so the shell that opens is made of linker. The lower shell stays solid.',
     'The most distinctive silhouette, and the most playful. The beads suggest assembly: the shell is being built.', 'Less like an oyster at first glance. The beads need to be at least 2px, so it suits 32px and above.'),
]

AH = 'aria-hidden="true"'
def use(id, sz, ink, p1, p2, extra=''):
    return f'<svg width="{sz}" height="{sz}" viewBox="0 0 100 100" style="color:{ink};fill:currentColor;--p1:{p1};--p2:{p2}" {extra}><use href="#{id}"/></svg>'
def app(id, tile, fg, p1, p2, sz):
    return f'<svg class="app" width="{sz}" height="{sz}" viewBox="0 0 100 100" {AH}><rect width="100" height="100" fill="{tile}"/><g transform="translate(9 9) scale(.82)" style="color:{fg};fill:currentColor;--p1:{p1};--p2:{p2}"><use href="#{id}" width="100" height="100"/></g></svg>'

# ink bounds of each mark (from measure_beads.js) and font metrics in em, as on the variations sheet
try: INK = json.load(open(D + 'beads_ink.json'))
except FileNotFoundError: INK = {}
FONT = {'serif': dict(top=.478, over=.011, lsb=.03, rsb=.03), 'sans': dict(top=.536, over=.011, lsb=.03, rsb=.035)}
def omark(id, face, ink, p1, p2):
    """The mark standing in for the O: its ink runs from the round-letter overshoot below the
    baseline up to the x-height of s, e and r, with side bearings matched to the letter o."""
    x0, y0, x1, y1 = INK.get(id, (8.5, 10.5, 90.7, 91.5)); f = FONT[face]
    size = (f['top'] + f['over']) * 100 / (y1 - y0)
    va = -f['over'] - (100 - y1) / 100 * size
    ml = -x0 / 100 * size + f['lsb']; mr = -(100 - x1) / 100 * size + f['rsb']
    st = f'width:{size:.4f}em;height:{size:.4f}em;vertical-align:{va:.4f}em;margin:0 {mr:.4f}em 0 {ml:.4f}em;color:{ink};fill:currentColor;--p1:{p1};--p2:{p2}'
    return f'<svg class="omark" viewBox="0 0 100 100" style="{st}" {AH}><use href="#{id}"/></svg>'

N_ = ('#2B2230', '#C99BB0', '#B8A7C9'); TD = ('#EAF3EF', '#F2B84B', '#7FC4B0')
defs = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>' + ''.join(masks) + '</defs>'
        + ''.join(syms[i] for i, *_ in OPTS) + '</svg>')
strip = ''.join(f'<a class="cell" href="#{i}"><span class="mono">{n}</span>{use(i, 72, *N_, AH)}<span class="nm">{t}</span></a>' for i, n, t, *_ in OPTS)
strip2 = ''.join(f'<a class="cell" href="#{i}">{use(i, 72, *TD, AH)}<span class="mono">{n}</span></a>' for i, n, t, *_ in OPTS)
cards = ''
for i, n, t, idea, good, watch in OPTS:
    lockN = f'<div class="lock serif">{use(i, "1em", *N_, AH)}<span>Oyster<small>Therapeutics</small></span></div>'
    lockT = f'<div class="lock sans">{use(i, "1em", *TD, AH)}<span>Oyster<small>Therapeutics</small></span></div>'
    extra = (f'<div class="panel nacre oword"><span class="mono">Mark as the O &middot; Nacre</span>'
             f'<div class="olock serif">{omark(i, "serif", *N_)}<span>yster</span></div></div>'
             f'<div class="panel tide oword"><span class="mono">Mark as the O &middot; Tidepool</span>'
             f'<div class="olock sans">{omark(i, "sans", *TD)}<span>yster</span></div></div>')
    smallN = use(i, 48, *N_, AH) + use(i, 32, *N_, AH) + use(i, 24, *N_, AH) + app(i, N_[0], '#EFE6E1', N_[1], N_[2], 32) + app(i, N_[0], '#EFE6E1', N_[1], N_[2], 16)
    smallT = use(i, 48, *TD, AH) + use(i, 32, *TD, AH) + use(i, 24, *TD, AH) + app(i, '#EAF3EF', '#0F4C4A', TD[1], TD[2], 32) + app(i, '#EAF3EF', '#0F4C4A', TD[1], TD[2], 16)
    mono = use(i, 64, '#2B2230', '#2B2230', '#2B2230', AH) + use(i, 64, '#0F4C4A', '#0F4C4A', '#0F4C4A', AH)
    heroN = use(i, 220, *N_, f'role="img" aria-label="{t} mark in Nacre colours" class="hero-m"')
    heroT = use(i, 220, *TD, f'role="img" aria-label="{t} mark in Tidepool colours" class="hero-m"')
    cards += f'''
  <section class="opt" id="{i}">
    <div class="wrap">
      <div class="opt-head"><span class="num">{n}</span><div><h2>{t}</h2><p>{idea}</p></div></div>
      <div class="panels">
        <div class="panel nacre"><span class="mono">Nacre</span>{heroN}{lockN}<div class="small">{smallN}</div></div>
        <div class="panel tide"><span class="mono">Tidepool</span>{heroT}{lockT}<div class="small">{smallT}</div></div>
        {extra}
        <div class="panel mono-p wide"><span class="mono">One colour</span>{mono}</div>
      </div>
      <div class="notes"><div><h3>Strength</h3><p>{good}</p></div><div><h3>Watch out</h3><p>{watch}</p></div></div>
    </div>
  </section>'''

CSS = open(D + 'sheet.css').read().replace('repeat(6, minmax(0, 1fr))', 'repeat(6, minmax(0, 1fr))') + '\n.panel.mono-p { background: #FFFFFF; color: #2B2230; padding-block: 24px; }\n'
html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<!-- artifact:start -->
<title>Oyster Bead Marks</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=swap">
<style>
{CSS}
</style>
</head>
<body>
{defs}
<header class="top">
  <div class="wrap">
    <span class="mono">Oyster Therapeutics &middot; Brand mark</span>
    <h1>The Bead Linker</h1>
    <p>Five directions that bring the bead linker from the SELFTAC molecule into the oyster mark, so the logo carries the science. The current mark is shown first for comparison. Each option is shown in both palettes, as the O of the wordmark, at small sizes and in one colour.</p>
  </div>
</header>
<main>
  <div class="wrap">
    <div class="strip n">{strip}</div>
    <div class="strip t">{strip2}</div>
  </div>
{cards}
</main>
<footer><div class="wrap">Concepts for review, generated by <code>oyster/brand/build_beads.py</code>.</div></footer>
<!-- artifact:end -->
</body>
</html>
'''
open(D + 'beads.html', 'w').write(html)
print('written', len(html))
