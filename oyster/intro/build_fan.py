"""Build the pages for the face-on fan mark (11.7 in the Mark Catalogue: the
line fan and 80% pearl inside out, rim 3.5): intro/fan-tidepool.html and intro/fan-nacre.html (the website opened
by the reworked intro, in each palette) and intro/fan-site.html (the website alone).

The site (../site/index.html, left untouched) gets the new mark as the 'o' of every wordmark (header, end card,
footer). The intro's 3D oyster is rebuilt to match it: both valves have the mark's fan outline, hinged at the back;
the lid lifts until it stands upright, the camera swings round to face it and drops to the mark's low angle, and it
recedes into the 'o', where the line-cut disc closes round it. The mark's geometry is exported to the script, so
the 3D lands on the logo's lines by construction. Run ../site/build_site.py first.
"""
import json, math, os, re, sys
D = os.path.dirname(os.path.abspath(__file__)) + '/'
sys.path.insert(0, D + '../brand')
import linepearl
from refs import _fan
from riffs import HINGE

NAME = 'io-s-rim35'                     # 11.7
SCALE, RIM = linepearl.SIZES['s'], 3.5
h = open(D + '../site/index.html').read()

def once(old, new):
    global h
    assert old in h, old[:60]
    h = h.replace(old, new, 1)

# ---------- the mark as the 'o' of every wordmark ----------
MARK_RE = re.compile(r'<g transform="translate\(-17\.1 -583\.4\) scale\(6\.3571\)"><g transform="translate\(-1\.5 1\.5\)">.*?</g></g>', re.S)
def mark_group(ns, gid=None, style=''):
    masks, sym = linepearl.build(ns)
    body = sym[NAME].replace('style="fill:var(--p1)"', 'class="pearl" style="fill:var(--pearl)"')
    ida = f' id="{gid}"' if gid else ''
    return (f'<g{ida}{style} transform="translate(-17.1 -583.4) scale(6.3571)"><defs>{masks[NAME]}</defs>'
            f'<g transform="translate(-1.5 1.5)">{body}</g></g>')
n = [0]
def swap(m):
    n[0] += 1; return mark_group(f'fan{n[0]}-')
h, count = MARK_RE.subn(swap, h)
assert count >= 3, count

# ---------- the intro's logotype: the wordmark with its parts named for the animation ----------
wm = re.search(r'<svg class="lt"[^>]*>.*?</svg>', h, re.S).group(0)   # the end card's logotype: the header's, with 'therapeutics'
vb = re.search(r'viewBox="([^"]+)"', wm).group(1)
paths = re.findall(r'<path d="[^"]*" transform="translate\([^)]*\) scale\((?:0\.5000|0\.1200) -[^)]*\)"/>', wm)
big = [p for p in paths if 'scale(0.5000' in p]; small = [p for p in paths if 'scale(0.1200' in p]
assert len(big) == 5 and len(small) == 12, (len(big), len(small))
ilogo = (f'<svg class="ilogo" id="ilogo" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" viewBox="{vb}"><defs>'
         '<clipPath id="ioClip"><rect id="ioClipR" x="470" y="-700" width="0" height="1000"/></clipPath></defs><g fill="currentColor">'
         + mark_group('io-', 'ioMark', ' style="opacity:0"')
         + '<g id="ioLetters" style="opacity:0" clip-path="url(#ioClip)">' + ''.join(big) + '</g><g id="ioTher" style="opacity:0">' + ''.join(small) + '</g></g></svg>')

# ---------- the mark's geometry, for the 3D oyster (reference units: the second reference image's pixels) ----------
(fan, dish, dish_in), ribs, (px, py, pr) = linepearl.drawing(SCALE, linepearl.circle_box(SCALE, RIM))
k = pr / (linepearl.PR * SCALE)                          # mark box units per reference unit
ox, oy = fan[0][0] - k * _fan()[0][0], fan[0][1] - k * _fan()[0][1]
F = _fan(); dense = []
for (x0, y0), (x1, y1) in zip(F, F[1:] + F[:1]):
    dense += [(x0 + (x1 - x0) * t / 40, y0 + (y1 - y0) * t / 40) for t in range(40)]
edge = []                                                # the fan's outline as a distance from the hinge, every 3 degrees
for i in range(61):
    phi = math.radians(-90 + 3 * i)                      # 0 is straight up the fan, positive to the right
    best = min(dense, key=lambda p: abs((math.atan2(p[0] - HINGE[0], HINGE[1] - p[1]) - phi + math.pi) % (2 * math.pi) - math.pi))
    edge.append(round(math.hypot(best[0] - HINGE[0], best[1] - HINGE[1]), 1))
side = math.degrees(math.atan2(F[1][0] - HINGE[0], HINGE[1] - F[1][1]))   # where the fan's straight sides meet its arc
GEO = {'edge': edge, 'k': round(k, 6), 'hinge': [round(ox + k * HINGE[0], 3), round(oy + k * HINGE[1], 3)],
       'pearl': [round(px, 3), round(py, 3), round(pr, 3)], 'pearlRef': round(linepearl.PR * SCALE, 2),
       'ribs': [round(math.degrees(math.atan2(b[0] - a[0], -(b[1] - a[1]))), 2) for a, b in ribs], 'side': round(side, 2)}

# ---------- the website alone, with the new mark and no intro ----------
site = h.replace('<title>Oyster Therapeutics</title>', '<title>Oyster Website, Fan Mark</title>', 1)
open(D + 'fan-site.html', 'w').write(site)

# ---------- the intro, as build_intro.py does: one page opening in each palette ----------
once('<figcaption><span class="dot"></span>The clasp: closes as you scroll</figcaption>',
     '<figcaption><span class="dot"></span>A reversible clasp: it closes, then lets go</figcaption>')
once('aria-label="The two halves of a SELFTAC molecule closing at the clasp as you scroll"',
     'aria-label="The two halves of a SELFTAC molecule joining at the clasp and coming apart again"')
once("goal = Math.max(0, Math.min(1, 1 - (r.top + r.height / 2 - innerHeight * .45) / (innerHeight * .45))); };",
     "const v = Math.max(0, Math.min(1, 1 - (r.top + r.height / 2) / innerHeight)), up = Math.min(1, v / .45), down = Math.min(1, (1 - v) / .4); goal = Math.max(0, Math.min(up, down)); };   // 0 low on the screen, 1 through the middle, 0 again as it leaves the top")
once('</style>', open(D + 'intro.css').read() + '</style>')
js = open(D + 'intro_fan.js').read().replace('/*GEO*/null', json.dumps(GEO))
once('\nwindow.__story = {', '\n' + js + '\nwindow.__story = {')
base = h
for pal, start in (('tidepool', '<script>document.documentElement.classList.add("intro"); window.__startPal = "tidepool";</script>'
                                 '<style>.intro-ov .ibg { --intro-a: #0B3A38; --intro-b: #04201F; }</style>'),   # the stage teal from the first frame
                   ('nacre', '<script>document.documentElement.classList.add("intro");</script>')):   # Nacre is the site's default
    overlay = (start + '\n<div class="intro-ov" id="intro" aria-hidden="true"><div class="ibg"></div><canvas id="introGl"></canvas>' + ilogo + '</div>\n'
               '<button type="button" class="iskip" id="introSkip">Skip intro</button>\n')
    h = base
    once('<canvas id="bgArt"', overlay + '<canvas id="bgArt"')
    once('<title>Oyster Therapeutics</title>', f'<title>Oyster Intro, Fan Mark ({pal.title()})</title>')   # its own name, to tell it from the live site
    open(D + f'fan-{pal}.html', 'w').write(h)
    print(f'intro/fan-{pal}.html', len(h) // 1024, 'KB')
print('intro/fan-site.html;', count, 'wordmarks swapped; ribs', GEO['ribs'])
