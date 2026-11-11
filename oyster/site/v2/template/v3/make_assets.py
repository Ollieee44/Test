"""Artwork for the v3 Oyster template (assets/): grounds with depth, in the Colors.pdf palette, after the website's
speckled emerald and the brand's textured greens.
  ground-title / -section / -closing   the brand textures' mid green, speckle ribbons framing the text
  ground-statement / -contents / -cards   Abyss Green with a Forest glow and a ribbon clear of the text
  ground-quiet / -light / -white   dark, Sea Foam and white for content slides: only a faint corner dusting
  panel-deep     the Divided layout's dark column
Speckles are drawn, never filtered out: ribbons of dots placed around where each layout puts its text.
The logo SVGs/PNGs and the SELFTAC complex come from ../v2."""
import json, math, os, random, shutil
from PIL import Image, ImageDraw, ImageFilter
D = os.path.dirname(os.path.abspath(__file__)) + '/'
A = D + 'assets/'; V2 = D + '../v2/'
os.makedirs(A, exist_ok=True)
hexrgb = lambda h: tuple(int(h.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
W, H, S = 2400, 1350, 2

def glow(base, spots):
    """a flat ground with soft radial glows: spots = [(cx, cy, radius, colour, strength)] in 0..1 units (of the width),
    smooth falloff with a touch of dither so it doesn't band"""
    import numpy as np
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    im = np.ones((H, W, 3), np.float32) * np.array(hexrgb(base), np.float32)
    for cx, cy, r, col, k in spots:
        dd = np.hypot(x - cx * W, y - cy * H) / (r * W)
        a = (k * np.clip(1 - dd, 0, 1) ** 2)[..., None]
        im = im * (1 - a) + np.array(hexrgb(col), np.float32) * a
    im += np.random.default_rng(0).normal(0, .9, im.shape)
    return Image.fromarray(np.clip(im, 0, 255).astype(np.uint8))

IN = W / 13.333
def bez(p, t):
    """a point on a cubic Bezier through four (x, y) points"""
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = p; u = 1 - t
    return (u**3 * x0 + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t**3 * x3, u**3 * y0 + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t**3 * y3)

def speckle(im, ribbons, cols, keep_out=(), feather=.6, seed=1, alpha=(70, 235), size=(.55, 1.9), glints=.035):
    """speckles drawn along ribbons, nothing filtered: each ribbon = (four Bezier points in inches, dots, width in
    inches); dots crowd the ribbon's spine and thin out across it. keep_out = boxes (inches) where text sits: no dot
    lands inside one, and they thin out over `feather` inches on the way in, so the edge reads as the ribbon fading."""
    rnd = random.Random(seed)
    big = im.convert('RGBA').resize((W * S, H * S)); d = ImageDraw.Draw(big, 'RGBA')
    def gap(x, y):   # distance (inches) outside the nearest keep-out box; 0 inside
        g = 99
        for x0, y0, x1, y1 in keep_out:
            dx = max(x0 - x, 0, x - x1); dy = max(y0 - y, 0, y - y1); g = min(g, math.hypot(dx, dy))
        return g
    for pts, n, width in ribbons:
        for _ in range(n):
            t = rnd.random(); x, y = bez(pts, t)
            (xa, ya), (xb, yb) = bez(pts, max(0, t - .01)), bez(pts, min(1, t + .01))
            nx, ny = -(yb - ya), xb - xa; L = math.hypot(nx, ny) or 1
            o = rnd.gauss(0, width) * (1 if rnd.random() < .8 else 2.2)      # a few strays well off the spine
            x += nx / L * o + rnd.gauss(0, .06); y += ny / L * o + rnd.gauss(0, .06)
            if not (-.1 < x < 13.43 and -.1 < y < 7.6): continue
            g = gap(x, y)
            if g < feather and rnd.random() > (g / feather) ** 1.5: continue
            r = rnd.uniform(*size) * (1.6 if rnd.random() < .04 else 1) * S * IN / 180
            c = rnd.choices(*zip(*cols))[0]; a = rnd.randint(*alpha)
            X, Y = x * IN * S, y * IN * S
            if rnd.random() < glints:   # a few catch the light
                h = r * 3.4; d.ellipse((X - h, Y - h, X + h, Y + h), fill=hexrgb(c) + (a // 7,))
            d.ellipse((X - r, Y - r, X + r, Y + r), fill=hexrgb(c) + (a,))
    return big.resize((W, H), Image.LANCZOS).convert('RGB')

DARK_DOTS = [('#FFFFFF', 38), ('#BADECD', 26), ('#67B791', 16), ('#DCA84E', 12), ('#CEE5F3', 8)]
LIGHT_DOTS = [('#408967', 38), ('#67B791', 24), ('#DCA84E', 20), ('#2E6149', 18)]
FOOT = [(0, 6.75, 4.9, 7.5), (11.9, 6.75, 13.333, 7.5)]   # the footer line and the page-number pill
def save(im, name): im.save(A + name, quality=92)

# grounds: the brand textures' mid green (title, section, closing), the deep Abyss, Sea Foam and white
kelp = glow('#2F6A50', [(.95, .0, .8, '#428D69', .75), (.0, 1.0, .6, '#28583F', .7)])
deep = glow('#1A372A', [(.92, .05, .75, '#2E6149', .9), (.05, 1.0, .5, '#070D0A', .6)])
light = glow('#EBEBE3', [(.1, .05, .7, '#FFFFFF', .85)])
white = glow('#FFFFFF', [(1.0, 1.0, .45, '#EBEBE3', .7)])

# ribbons that run along the edges (side and foot), shared by several grounds
FOOT_RIBBON = ([(-.3, 7.55), (4.0, 7.05), (8.5, 7.6), (13.8, 7.0)], .16)        # along the foot
RIGHT_RIBBON = ([(13.5, 7.8), (13.0, 5.0), (13.45, 2.5), (13.0, -.3)], .14)       # down the right edge
LEFT_RIBBON = ([(.05, 7.8), (.3, 5.2), (-.05, 2.6), (.25, -.3)], .12)             # down the left edge
def edges(n_foot, n_right, n_left=0):
    r = [(FOOT_RIBBON[0], n_foot, FOOT_RIBBON[1]), (RIGHT_RIBBON[0], n_right, RIGHT_RIBBON[1])]
    return r + ([(LEFT_RIBBON[0], n_left, LEFT_RIBBON[1])] if n_left else [])

# title: a ribbon sweeping up the right-hand side, the foot and the left edge framing the title block
save(speckle(kelp, [([(8.6, 7.8), (10.2, 5.2), (10.6, 2.4), (13.8, -.3)], 7000, .55), ([(11.0, 7.8), (12.0, 6.6), (12.8, 6.4), (13.8, 5.6)], 1800, .35)] + edges(2600, 1600, 900),
             DARK_DOTS, [(.45, .3, 9.4, 6.95)], feather=.45, seed=11), 'ground-title.jpg')
# section: a ribbon along the foot and up the right edge, under the big number, and down the left edge
save(speckle(kelp, [([(-.3, 7.6), (4.0, 6.9), (9.5, 7.4), (13.8, 4.6)], 6500, .4), ([(13.6, 4.8), (12.6, 3.6), (13.4, 1.8), (12.8, -.3)], 1600, .3)] + edges(0, 0, 1200)
             + [([(-.3, 1.4), (1.5, 1.9), (4.0, 1.0), (7.0, 2.6)], 2200, .35)],
             DARK_DOTS, [(.45, 3.4, 12.0, 6.5), (6.9, .2, 13.0, 3.5), (.45, .35, 1.1, 1.05)] + FOOT, feather=.45, seed=12), 'ground-section.jpg')
# closing: ribbons framing the centred lockup, along the top, the foot and both sides
save(speckle(kelp, [([(-.3, .9), (3.5, -.2), (9.0, 1.2), (13.8, .1)], 4200, .35), ([(-.3, 7.7), (4.5, 6.4), (9.0, 7.8), (13.8, 6.6)], 4200, .35)] + edges(0, 1500, 1500),
             DARK_DOTS, [(.9, 1.3, 12.4, 6.2)], feather=.45, seed=13), 'ground-closing.jpg')
# statement and contents: a ribbon in the top-right corner, plus the foot and the right edge
save(speckle(deep, [([(8.0, -.3), (10.6, 1.0), (12.2, .4), (13.8, 1.6)], 3600, .35)] + edges(3400, 2600, 1100), DARK_DOTS,
             [(.45, 1.25, 12.8, 6.4), (.45, .35, 1.1, 1.05)] + FOOT, feather=.45, seed=14), 'ground-statement.jpg')
save(speckle(deep, [([(5.5, -.3), (8.5, .9), (11.0, .3), (13.8, 1.0)], 3000, .3), ([(-.3, 6.4), (1.2, 4.6), (2.8, 5.6), (4.3, 3.2)], 2600, .35)] + edges(3400, 2600, 1100), DARK_DOTS,
             [(4.5, 1.25, 13.1, 6.5), (.45, .3, 4.4, 2.6), (.45, .35, 1.1, 1.05)] + FOOT, feather=.45, seed=15), 'ground-contents.jpg')
# Three Cards: a thin ribbon along the very top, plus the foot (between the cards and the footer) and the sides
save(speckle(deep, [([(6.5, -.3), (9.0, .5), (11.5, .1), (13.8, .7)], 2200, .22)] + edges(3400, 2200, 1300), DARK_DOTS,
             [(.45, .45, 12.85, 6.72)] + FOOT, feather=.25, seed=16), 'ground-cards.jpg')
# content slides put text anywhere inside the margins: speckles stay in the margins, the foot and the sides
MARGINS = [(.45, .25, 12.88, 6.78)] + FOOT
save(speckle(deep, [([(10.0, 7.8), (11.8, 7.1), (12.6, 6.4), (13.8, 5.2)], 1100, .25)] + edges(3200, 2200, 1200), DARK_DOTS, MARGINS, feather=.2, seed=17, alpha=(50, 190), size=(.45, 1.5), glints=.02), 'ground-quiet.jpg')
save(speckle(light, [([(10.0, 7.8), (11.8, 7.1), (12.6, 6.4), (13.8, 5.2)], 1000, .25)] + edges(3000, 2000, 1100), LIGHT_DOTS, MARGINS, feather=.2, seed=18, alpha=(45, 160), size=(.45, 1.4), glints=0), 'ground-light.jpg')
save(speckle(white, [([(10.8, 7.8), (12.2, 7.2), (12.9, 6.7), (13.8, 5.9)], 700, .2)] + edges(2300, 1500, 800), LIGHT_DOTS, MARGINS, feather=.2, seed=19, alpha=(35, 130), size=(.45, 1.3), glints=0), 'ground-white.jpg')
# the Divided column: a ribbon crossing the column below its heading, and one along its left edge
pd = glow('#1A372A', [(.0, .0, .9, '#2E6149', .85)])
pd = speckle(pd, [([(-.3, 6.6), (1.2, 5.7), (2.4, 6.4), (4.0, 5.2)], 2600, .28), (LEFT_RIBBON[0], 900, .12), ([(-.3, .25), (1.5, .05), (2.6, .4), (4.0, .1)], 900, .12)],
             DARK_DOTS, [(.45, 1.0, 3.5, 5.55), (.45, .35, 1.1, 1.05)] + FOOT, feather=.35, seed=20)
pd.crop((0, 0, int(W * 3.7 / 13.333), H)).save(A + 'panel-deep.jpg', quality=92)

# from v2: the brand textures, the logo files, the complex
for f in ('complex-hero.png', 'complex-panel.png'): shutil.copy(V2 + 'assets/' + f, A + f)
for f in os.listdir(V2 + 'assets'):
    if f.startswith(('logo-', 'mark-')): shutil.copy(V2 + 'assets/' + f, A + f)
json.dump({n: Image.open(A + n).size for n in os.listdir(A) if n.endswith(('.png', '.jpg'))}, open(A + 'sizes.json', 'w'))
print(sorted(os.listdir(A)))
