"""Artwork for the Oyster slide template (assets/): speckled grounds in the new site's emerald and deep green, the
logo in white and in ink, and the ternary complex in the new-site colours, put together from the journey deck's
stills at its .74 keyframe. Run after ../journey/deck (export_deck.js, prep_deck.py)."""
import json, math, os, random
import numpy as np
from PIL import Image, ImageDraw
D = os.path.dirname(os.path.abspath(__file__)) + '/'
A = D + 'assets/'; J = D + '../journey/deck/out/'
os.makedirs(A, exist_ok=True)

def speckle(name, ground, n, cols, alpha=(70, 230), seed=3, W=2400, H=1350, S=3):
    rnd = random.Random(seed)
    im = Image.new('RGBA', (W * S, H * S), ground); d = ImageDraw.Draw(im, 'RGBA')
    for _ in range(n):
        x, y, r = rnd.uniform(0, W) * S, rnd.uniform(0, H) * S, rnd.uniform(.6, 1.7) * S
        c = rnd.choices(*zip(*cols))[0]; a = rnd.randint(*alpha)
        d.ellipse((x - r, y - r, x + r, y + r), fill=c + (a,))
    im.resize((W, H), Image.LANCZOS).convert('RGB').save(A + name, optimize=True)
SPK = [((255, 255, 255), 55), ((207, 255, 255), 25), ((247, 209, 107), 8), ((150, 255, 135), 8), ((255, 179, 107), 4)]
speckle('ground-emerald.png', (21, 139, 99), 2600, SPK)
speckle('ground-deep.png', (41, 81, 67), 900, SPK, alpha=(35, 120), seed=5)
speckle('ground-sage.png', (58, 113, 94), 1800, SPK, seed=7, W=1200, H=700)

# the logo: white, and in the site's deep green ink
logo = Image.open(J + 'c/logo.png').convert('RGBA'); logo = logo.crop(logo.getbbox())
logo.save(A + 'logo-white.png')
ink = Image.new('RGBA', logo.size, (41, 81, 67, 255)); ink.putalpha(logo.getchannel('A')); ink.save(A + 'logo-ink.png')
mark = logo.crop((0, 0, int(logo.width * .27), logo.height)); mark = mark.crop(mark.getbbox()); mark.save(A + 'mark-white.png')
im2 = Image.new('RGBA', mark.size, (41, 81, 67, 255)); im2.putalpha(mark.getchannel('A')); im2.save(A + 'mark-ink.png')

# the ternary complex, as the journey deck places it at .74
data = json.load(open(J + 'prep.json')); k = [x for x in data['keys'] if abs(x['p'] - .74) < 1e-6][0]
S = 3; canvas = Image.new('RGBA', (1440 * S, 810 * S), (0, 0, 0, 0))
for name in ['dimerC', 'vhl', 'elob', 'eloc', 'brd4']:
    e = k['els'][name]; ref = data['refs'][e['img']]; c = data['crops'][e['img']]
    f = math.hypot(*e['v']) / math.hypot(*ref['v']); d = math.atan2(e['v'][1], e['v'][0]) - math.atan2(ref['v'][1], ref['v'][0])
    ox, oy = c['w'] / 2 - (ref['A'][0] - c['x0']), c['h'] / 2 - (ref['A'][1] - c['y0'])
    cx, cy = e['A'][0] + f * (ox * math.cos(d) - oy * math.sin(d)), e['A'][1] + f * (ox * math.sin(d) + oy * math.cos(d))
    im = Image.open(J + 'c/' + e['img'] + '.png').convert('RGBA')
    im = im.resize((max(1, round(c['w'] * f * S)), max(1, round(c['h'] * f * S))), Image.LANCZOS).rotate(-math.degrees(d), Image.BICUBIC, expand=True)
    canvas.alpha_composite(im, (round(cx * S - im.width / 2), round(cy * S - im.height / 2)))
canvas = canvas.crop(canvas.getbbox()); canvas.save(A + 'complex.png', optimize=True)
print('assets:', sorted(os.listdir(A)), 'complex', canvas.size)

# the complex pre-fitted to the template's picture placeholders: the two-column panel (5.83 x 6.0 in, transparent,
# so the sage panel shows) and the full-bleed image (16:9, on the emerald ground, the complex to the right)
def fit(canvas_size, art, box_frac, ground=None):
    W, H = canvas_size; c = Image.open(A + ground).convert('RGBA').resize((W, H), Image.LANCZOS) if ground else Image.new('RGBA', (W, H), (0, 0, 0, 0))
    bx, by, bw, bh = [int(v) for v in (box_frac[0] * W, box_frac[1] * H, box_frac[2] * W, box_frac[3] * H)]
    a = art.copy(); a.thumbnail((bw, bh), Image.LANCZOS)
    c.alpha_composite(a, (bx + (bw - a.width) // 2, by + (bh - a.height) // 2)); return c
art = Image.open(A + 'complex.png')
fit((1749, 1800), art, (.1, .06, .8, .88)).save(A + 'complex-panel.png', optimize=True)
fit((2400, 1350), art, (.58, .05, .36, .9), 'ground-emerald.png').convert('RGB').save(A + 'complex-hero.png', optimize=True)
json.dump({n: Image.open(A + n).size for n in os.listdir(A) if n.endswith('.png')}, open(A + 'sizes.json', 'w'))
print('fitted complex-panel, complex-hero')
