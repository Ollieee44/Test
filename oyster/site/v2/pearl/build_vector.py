"""Build the editable vectors of variation 05 (Blueprint): vector/selftac-blueprint-05-full.svg (the whole complex,
from v5-asset) and vector/selftac-blueprint-05-hero-crop.svg (as framed in the hero, from v5-blueprint).

The shapes are measured from the 3D scene itself, not traced from the picture. render_pearl.js with EXPORT=1 renders
one exact data pass (no antialiasing) of the 05 framing: which part owns each pixel, and on the proteins the value
whose whole numbers draw the contour rings. Here every part's visible outline and every visible contour ring is turned
into smooth cubic Bezier paths, and the pearls become true circles with editable gradients. Parts are named layers
(ids, which Figma and Illustrator show as layer names), drawn at 1440 x 810 like the hero.

  EXPORT=1 THREE=... NODE_PATH=... node render_pearl.js v5-asset v5-blueprint
  python build_vector.py v5-asset; python build_vector.py v5-blueprint
Needs numpy, scipy and scikit-image."""
import json, os
import numpy as np
from scipy import ndimage
from skimage import measure

import sys
D = os.path.dirname(os.path.abspath(__file__)) + '/vector/'
NAME = sys.argv[1] if len(sys.argv) > 1 else 'v5-blueprint'
OUT = {'v5-blueprint': 'selftac-blueprint-05-hero-crop.svg', 'v5-asset': 'selftac-blueprint-05-full.svg'}[NAME]
meta = json.load(open(D + NAME + '-meta.json'))
W, H, S = meta['w'], meta['h'], meta['scale']
raw = np.fromfile(D + NAME + '-data.bin', dtype=np.uint8).reshape(H, W, 3)[::-1]   # GL rows run bottom up
ID = raw[..., 0].astype(int)
DV = (raw[..., 1].astype(np.uint32) << 8 | raw[..., 2]).astype(float) / 256

LINE, GROUND = '#EAF3EF', '#0C4341'

def smooth(pts, closed):
    """points (x, y) to a Catmull-Rom spline written as cubic Beziers"""
    n = len(pts)
    if n < 3:
        return 'M' + ' L'.join(f'{x:.2f} {y:.2f}' for x, y in pts) + (' Z' if closed else '')
    P = lambda i: pts[i % n] if closed else pts[max(0, min(n - 1, i))]
    out = [f'M{pts[0][0]:.2f} {pts[0][1]:.2f}']
    for i in range(n if closed else n - 1):
        p0, p1, p2, p3 = P(i - 1), P(i), P(i + 1), P(i + 2)
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        out.append(f'C{c1[0]:.2f} {c1[1]:.2f} {c2[0]:.2f} {c2[1]:.2f} {p2[0]:.2f} {p2[1]:.2f}')
    return ' '.join(out) + (' Z' if closed else '')

def to_pts(c, tol, closed):
    """a skimage contour (row, col at data scale) simplified, as (x, y) in hero pixels"""
    c = measure.approximate_polygon(c, tolerance=tol)
    if closed and len(c) > 2 and np.allclose(c[0], c[-1]):
        c = c[:-1]
    return [(p[1] / S, p[0] / S) for p in c]

def outline(mask, min_len=10):
    """the visible region's boundary (with any holes) as one even-odd path"""
    m = np.pad(mask.astype(float), 1)
    cs = [c - 1 for c in measure.find_contours(ndimage.gaussian_filter(m, .7), .5) if len(c) >= min_len]
    return ' '.join(smooth(to_pts(c, .6, True), True) for c in cs)

def rings(oid):
    """the visible contour rings on a protein: the whole-number level lines of its contour value"""
    mask = ID == oid
    inner = ndimage.binary_erosion(mask, iterations=3)
    v = np.where(mask, DV, np.nan)
    lo, hi = np.nanmin(v[inner]), np.nanmax(v[inner])
    vf = ndimage.gaussian_filter(np.where(mask, DV, np.nanmean(v)), 1.0)
    paths = []
    for level in range(int(np.ceil(lo)), int(np.floor(hi)) + 1):
        for c in measure.find_contours(vf, level, mask=inner):
            if len(c) < 14:
                continue
            closed = np.linalg.norm(c[0] - c[-1]) < 2
            pts = to_pts(c, .5, closed)
            if len(pts) >= 2:
                paths.append(smooth(pts, closed))
    return paths

objs = {o['id']: o for o in meta['objects']}
slug = lambda name: ''.join(ch if ch.isalnum() else '-' for ch in name).strip('-').replace('--', '-').replace('--', '-')
layers = []
for oid in meta['backToFront']:
    o = objs[oid]; kind = o['kind']; mask = ID == oid
    if kind in ('pearls', 'pearl') or not mask.any():
        continue
    if kind == 'protein':
        rs = rings(oid)
        layers.append(f'<g id="{slug(o["name"])}"><path id="{slug(o["name"])}-shape" d="{outline(mask)}" fill="{GROUND}" fill-rule="evenodd" stroke="{LINE}" stroke-width="1.6" stroke-linejoin="round"/>'
                      f'<g id="{slug(o["name"])}-contours" fill="none" stroke="{LINE}" stroke-width=".8" stroke-opacity=".55" stroke-linecap="round" stroke-linejoin="round">'
                      + ''.join(f'<path d="{p}"/>' for p in rs) + '</g></g>')
        print(f'{o["name"]}: outline and {len(rs)} contour paths')
    elif kind == 'pod':
        layers.append(f'<path id="{slug(o["name"])}" d="{outline(mask)}" fill="{GROUND}" fill-rule="evenodd" stroke="{LINE}" stroke-width="1.6" stroke-linejoin="round"/>')
    elif kind == 'strand':
        layers.append(f'<path id="{slug(o["name"])}" d="{outline(mask)}" fill="{LINE}" fill-rule="evenodd"/>')

# the pearls: true circles with editable gradients (cream body, a pink and green orient at the rim, highlights, halo)
sp = meta['pearls']; P = meta['pearl']
small = ''.join(f'<circle cx="{c["x"]:.2f}" cy="{c["y"]:.2f}" r="{c["r"]:.2f}" fill="url(#nacreSmall)" stroke="{LINE}" stroke-opacity=".7" stroke-width=".8"/>' for c in sp)
x, y, r = P['x'], P['y'], P['r']
the_pearl = (f'<g id="The-pearl">'
             f'<circle id="The-pearl-halo" cx="{x:.2f}" cy="{y:.2f}" r="{r * 2.3:.2f}" fill="url(#pearlHalo)"/>'
             f'<circle id="The-pearl-body" cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" fill="url(#nacre)"/>'
             f'<circle id="The-pearl-orient" cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" fill="url(#orient)"/>'
             f'<ellipse id="The-pearl-sheen" cx="{x - r * .18:.2f}" cy="{y - r * .26:.2f}" rx="{r * .55:.2f}" ry="{r * .42:.2f}" fill="url(#sheen)"/>'
             f'<circle id="The-pearl-highlight" cx="{x - r * .24:.2f}" cy="{y - r * .3:.2f}" r="{r * .13:.2f}" fill="url(#glint)"/>'
             f'<circle id="The-pearl-rim" cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" fill="none" stroke="{LINE}" stroke-opacity=".8" stroke-width="1.2"/></g>')
defs = f'''<defs>
<radialGradient id="nacre" cx="40%" cy="34%" r="72%"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".22" stop-color="#F6F0EA"/><stop offset=".6" stop-color="#ECE2DC"/><stop offset=".86" stop-color="#D8CAC9"/><stop offset="1" stop-color="#BFCFC8"/></radialGradient>
<radialGradient id="nacreSmall" cx="38%" cy="32%" r="72%"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".35" stop-color="#F1E9E2"/><stop offset=".8" stop-color="#E2D6D4"/><stop offset="1" stop-color="#C9D8CF"/></radialGradient>
<radialGradient id="orient" cx="50%" cy="50%" r="50%"><stop offset=".62" stop-color="#F4C9DA" stop-opacity="0"/><stop offset=".8" stop-color="#F4C9DA" stop-opacity=".28"/><stop offset=".9" stop-color="#CBE8D6" stop-opacity=".32"/><stop offset="1" stop-color="#B9CFEA" stop-opacity=".38"/></radialGradient>
<radialGradient id="sheen" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".55"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient>
<radialGradient id="glint" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".55" stop-color="#FFFFFF" stop-opacity=".85"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient>
<radialGradient id="pearlHalo" cx="50%" cy="50%" r="50%"><stop offset=".3" stop-color="#F4EEE6" stop-opacity=".3"/><stop offset="1" stop-color="#F4EEE6" stop-opacity="0"/></radialGradient>
<pattern id="gridFine" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="{LINE}" stroke-opacity=".03"/></pattern>
<pattern id="gridMajor" width="120" height="120" patternUnits="userSpaceOnUse"><path d="M120 0H0V120" fill="none" stroke="{LINE}" stroke-opacity=".07"/></pattern>
</defs>'''
VW, VH = W // S, H // S
# the full asset is cropped to the drawing (plus a margin) so it lands as a tidy artboard
OX = OY = 0
if NAME == 'v5-asset':
    rows, cols = np.nonzero(ID > 0)
    m = 40
    x0, x1 = max(0, cols.min() / S - m), min(VW, cols.max() / S + m)
    y0, y1 = max(0, rows.min() / S - m), min(VH, rows.max() / S + m)
    hx, hy = P['x'], P['y']; hr = P['r'] * 2.3                       # keep the pearl's halo inside too
    x0, y0, x1, y1 = min(x0, hx - hr), min(y0, hy - hr), max(x1, hx + hr), max(y1, hy + hr)
    OX, OY, VW, VH = round(x0), round(y0), round(x1 - x0), round(y1 - y0)
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{VW}" height="{VH}" viewBox="0 0 {VW} {VH}">\n'
       f'<title>SELFTAC ternary complex, blueprint (variation 05)</title>\n{defs}\n'
       f'<g id="Background"><rect id="Ground" width="{VW}" height="{VH}" fill="{GROUND}"/><rect id="Grid-fine" width="{VW}" height="{VH}" fill="url(#gridFine)"/><rect id="Grid-major" width="{VW}" height="{VH}" fill="url(#gridMajor)"/></g>\n'
       f'<g id="Complex" transform="translate({-OX} {-OY})">\n' + '\n'.join(layers) + f'\n<g id="Linker-pearls">{small}</g>\n{the_pearl}\n</g>\n</svg>\n')
open(D + OUT, 'w').write(svg)
print(OUT, os.path.getsize(D + OUT) // 1024, 'KB')
