"""Glyph outlines and scanline profiles for the wordmark faces (Newsreader 500 at opsz 72, Archivo 700),
read from the Google Fonts files. Coordinates are in em with y up and the baseline at 0."""
import math, os
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.basePen import BasePen
from fontTools.pens.svgPathPen import SVGPathPen

FONTS = os.environ.get('OYSTER_FONTS', '/tmp/claude-0/-home-user-Test/41e222d5-fef3-5806-9f71-b3d37440c66d/scratchpad/fonts/')
FACES = {'newsreader': ('news.woff2', {'wght': 500, 'opsz': 72}), 'archivo': ('arch.ttf', {'wght': 700}),
         'archivo500': ('arch500.ttf', {'wght': 500})}
_cache = {}

def font(face):
    if face not in _cache:
        fn, loc = FACES[face]; f = TTFont(FONTS + fn)
        _cache[face] = instantiateVariableFont(f, {k: v for k, v in loc.items() if k in [a.axisTag for a in f['fvar'].axes]}) if 'fvar' in f else f
    return _cache[face]

class Flatten(BasePen):
    def __init__(self, gs, n=12):
        super().__init__(gs); self.polys, self.n = [], n
    def _moveTo(self, p): self.polys.append([p])
    def _lineTo(self, p): self.polys[-1].append(p)
    def _curveToOne(self, a, b, c):
        p0 = self.polys[-1][-1]
        for i in range(1, self.n + 1):
            t = i / self.n; u = 1 - t
            self.polys[-1].append((u**3*p0[0] + 3*u*u*t*a[0] + 3*u*t*t*b[0] + t**3*c[0], u**3*p0[1] + 3*u*u*t*a[1] + 3*u*t*t*b[1] + t**3*c[1]))
    def _qCurveToOne(self, a, b):
        p0 = self.polys[-1][-1]
        for i in range(1, self.n + 1):
            t = i / self.n; u = 1 - t
            self.polys[-1].append((u*u*p0[0] + 2*u*t*a[0] + t*t*b[0], u*u*p0[1] + 2*u*t*a[1] + t*t*b[1]))
    def _closePath(self): pass

def glyph(face, ch):
    """Returns dict(adv, path (SVG, em units, y down), polys (em, y up))."""
    f = font(face); upm = f['head'].unitsPerEm; gs = f.getGlyphSet(); g = f.getBestCmap()[ord(ch)]
    fp = Flatten(gs); gs[g].draw(fp)
    polys = [[(x / upm, y / upm) for x, y in poly] for poly in fp.polys]
    sp = SVGPathPen(gs, lambda v: f'{v / upm:.4f}'); gs[g].draw(sp)
    return {'adv': f['hmtx'][g][0] / upm, 'path': sp.getCommands(), 'polys': polys}

def intervals(polys, y):
    """Ink intervals of a glyph along the horizontal line at height y (even-odd)."""
    xs = []
    for poly in polys:
        n = len(poly)
        for i in range(n):
            (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
            if (y1 <= y < y2) or (y2 <= y < y1):
                xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
    xs.sort(); return [(xs[i], xs[i + 1]) for i in range(0, len(xs) - 1, 2)]

def profile(polys, ys):
    """Leftmost and rightmost ink at each height, or None where the line misses the glyph."""
    out = []
    for y in ys:
        iv = intervals(polys, y)
        out.append((iv[0][0], iv[-1][1]) if iv else None)
    return out
