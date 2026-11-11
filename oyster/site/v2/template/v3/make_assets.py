"""Artwork for the v3 Oyster template (assets/): grounds with depth, in the Colors.pdf palette, after the website's
speckled emerald and the brand's textured greens.
  ground-deep    Abyss Green, a Forest glow from the top right, a drift of speckles across it (title-free dark slides)
  ground-quiet   the same with a sparse drift, for dark slides that carry content
  ground-light   Sea Foam with a white glow and a few speckles gathered in the lower right
  ground-white   white with the faintest speckle in the lower right, for dense content (tables, charts)
  panel-deep     the deep ground cut to the Divided layout's left column
The logo SVGs/PNGs, the brand's two textures and the SELFTAC complex come from ../v2 (its src and assets)."""
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

def drift(im, n, cols, path, spread, alpha=(60, 220), seed=1, size=(.7, 2.3), scatter=0., halo=.06):
    """speckles gathered along a path (a list of points in 0..1 units), thinning out with distance from it"""
    rnd = random.Random(seed)
    big = im.convert('RGBA').resize((W * S, H * S)); d = ImageDraw.Draw(big, 'RGBA')
    for _ in range(n):
        if rnd.random() < scatter: x, y = rnd.random(), rnd.random()
        else:
            t = rnd.random(); i = min(int(t * (len(path) - 1)), len(path) - 2); f = t * (len(path) - 1) - i
            px = path[i][0] + (path[i + 1][0] - path[i][0]) * f; py = path[i][1] + (path[i + 1][1] - path[i][1]) * f
            x, y = px + rnd.gauss(0, spread), py + rnd.gauss(0, spread * 1.3)
        r = rnd.uniform(*size) * S; c = rnd.choices(*zip(*cols))[0]; a = rnd.randint(*alpha)
        if rnd.random() < halo:   # a few catch the light, as on the brand's textures
            h = r * 3.2; d.ellipse((x * W * S - h, y * H * S - h, x * W * S + h, y * H * S + h), fill=hexrgb(c) + (a // 6,))
        d.ellipse((x * W * S - r, y * H * S - r, x * W * S + r, y * H * S + r), fill=hexrgb(c) + (a,))
    return big.resize((W, H), Image.LANCZOS).convert('RGB')

DARK_DOTS = [('#FFFFFF', 40), ('#BADECD', 25), ('#67B791', 18), ('#DCA84E', 10), ('#CEE5F3', 7)]
LIGHT_DOTS = [('#408967', 40), ('#67B791', 25), ('#DCA84E', 18), ('#2E6149', 17)]
BAND = [(-.05, .95), (.3, .62), (.62, .38), (1.05, .05)]

# text comes first: wherever a layout puts text, the speckles are taken out of its ground (a median filter at low
# resolution keeps the glow and colour but drops the dots), feathered in so there's no hard edge
IN = W / 13.333
FOOT = [(0, 6.7, 4.8, 7.5), (11.8, 6.7, 13.1, 7.5)]       # the footer line and the page-number pill
def quiet(im, zones, feather=.35):
    from PIL import ImageFilter as F
    w, h = im.size; k = w / W
    clean = im.resize((w // 6, h // 6), Image.BILINEAR).filter(F.MedianFilter(7)).filter(F.GaussianBlur(2)).resize((w, h), Image.BICUBIC)
    m = Image.new('L', (w, h), 0); d = ImageDraw.Draw(m)
    for x0, y0, x1, y1 in zones: d.rectangle((x0 * IN * k, y0 * IN * k, x1 * IN * k, y1 * IN * k), fill=255)
    m = m.filter(F.GaussianBlur(feather * IN * k))
    return Image.composite(clean, im, m)
def save(im, name): im.save(A + name, quality=90)

band, corner = (Image.open(V2 + 'assets/texture-' + n + '.jpg').convert('RGB').resize((W, H), Image.LANCZOS) for n in ('band', 'corner'))
deep = glow('#1A372A', [(.92, .05, .75, '#2E6149', .9), (.05, 1.0, .5, '#070D0A', .6)])
deepd = drift(deep, 5200, DARK_DOTS, BAND, .07, seed=3, scatter=.18)
# the title, section and closing pages on the brand's textures; the speckle stays where the text isn't
save(quiet(band, [(0, .3, 9.9, 7.3)]), 'ground-title.jpg')
save(quiet(corner, [(0, 3.3, 12.1, 6.5), (6.9, .2, 13.1, 3.6)] + FOOT), 'ground-section.jpg')
save(quiet(band, [(.8, 1.3, 12.5, 6.2)]), 'ground-closing.jpg')
# statement and contents on the deep drift, cleared under their text
save(quiet(deepd, [(0, 1.2, 12.7, 6.4)] + FOOT), 'ground-statement.jpg')
save(quiet(deepd, [(.3, 1.2, 13.1, 6.5)] + FOOT), 'ground-contents.jpg')
save(quiet(deepd, [(0, .4, 13.1, 2.0), (.45, 2.1, 12.9, 6.75)] + FOOT), 'ground-cards.jpg')   # Three Cards: clear under the title and the cards
# content slides can put text anywhere: the glow with only a faint, sparse dusting
save(drift(deep, 900, DARK_DOTS, BAND, .2, alpha=(18, 55), seed=4, size=(.5, 1.3), scatter=.6, halo=0), 'ground-quiet.jpg')
light = glow('#EBEBE3', [(.1, .05, .7, '#FFFFFF', .85)])
save(drift(light, 700, LIGHT_DOTS, [(.7, 1.04), (1.04, .66)], .045, alpha=(18, 60), seed=5, size=(.5, 1.3), halo=0), 'ground-light.jpg')
white = glow('#FFFFFF', [(1.0, 1.0, .45, '#EBEBE3', .7)])
save(drift(white, 450, LIGHT_DOTS, [(.8, 1.04), (1.04, .76)], .04, alpha=(15, 50), seed=6, size=(.5, 1.2), halo=0), 'ground-white.jpg')
# the Divided column: speckles only below its heading, clear of the footer
pdeep = glow('#1A372A', [(.0, .0, .9, '#2E6149', .85)])
pdeep = drift(pdeep, 2200, DARK_DOTS, [(-.02, .8), (.3, .7)], .035, seed=8, scatter=.04)
pdeep = quiet(pdeep, [(0, 1.0, 3.7, 5.6)] + FOOT)
pdeep.crop((0, 0, int(W * 3.7 / 13.333), H)).save(A + 'panel-deep.jpg', quality=90)

# from v2: the brand textures, the logo files, the complex
for f in ('complex-hero.png', 'complex-panel.png'): shutil.copy(V2 + 'assets/' + f, A + f)
for f in os.listdir(V2 + 'assets'):
    if f.startswith(('logo-', 'mark-')): shutil.copy(V2 + 'assets/' + f, A + f)
json.dump({n: Image.open(A + n).size for n in os.listdir(A) if n.endswith(('.png', '.jpg'))}, open(A + 'sizes.json', 'w'))
print(sorted(os.listdir(A)))
