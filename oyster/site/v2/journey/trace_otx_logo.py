# Trace the oyster-tx.com logo (white on green) from a screenshot of the site into otx_logo.svg: the mark and "oyster"
# traced, and the small "therapeutics" set in Geist at the same place and width. Usage: python trace_otx_logo.py <screenshot> otx_logo.svg
# (the crop below is for a 1918 x 1060 screenshot of the home page, logo top left). Needs numpy, scipy, scikit-image.
import sys, numpy as np
from PIL import Image
from scipy import ndimage
from skimage import measure
src, out = sys.argv[1], sys.argv[2]
X0, Y0 = 150, 150                                   # the crop's corner in the screenshot
full = Image.open(src).convert('RGB').crop((X0, Y0, 410, 235))
def whiteness(im, U, blur):
    a = np.asarray(im.resize((im.width * U, im.height * U), Image.LANCZOS)).astype(float)
    lum = a.mean(axis=2); sat = a.max(axis=2) - a.min(axis=2)
    return ndimage.gaussian_filter(np.clip((lum - 120) / 110, 0, 1) * np.clip(1 - (sat - 40) / 80, 0, 1), blur)
def smooth(pts):
    n = len(pts); P = lambda i: pts[i % n]; o = [f'M{pts[0][0]:.2f} {pts[0][1]:.2f}']
    for i in range(n):
        p0, p1, p2, p3 = P(i - 1), P(i), P(i + 1), P(i + 2)
        o.append(f'C{p1[0] + (p2[0] - p0[0]) / 6:.2f} {p1[1] + (p2[1] - p0[1]) / 6:.2f} {p2[0] - (p3[0] - p1[0]) / 6:.2f} {p2[1] - (p3[1] - p1[1]) / 6:.2f} {p2[0]:.2f} {p2[1]:.2f}')
    return ' '.join(o) + 'Z'
def trace(box, U, blur, level, tol, minlen, mask=None):
    x0, y0, x1, y1 = box
    w = whiteness(full.crop(box), U, blur)
    if mask is not None: w = w * mask(w.shape, U)
    paths = []
    for c in measure.find_contours(np.pad(w, 2), level):
        if len(c) < minlen: continue
        c = measure.approximate_polygon(c - 2, tolerance=tol)[:-1]
        if len(c) < 3: continue
        paths.append(smooth([(x0 + p[1] / U, y0 + p[0] / U) for p in c]))
    return paths
SMALL = (156, 53, 244, 71)                          # 'therapeutics', in crop pixels
def not_small(shape, U):                            # blank the small word out of the big trace
    m = np.ones(shape); m[int(SMALL[1] * U):int(SMALL[3] * U), int(SMALL[0] * U):int(SMALL[2] * U)] = 0; return m
big = trace((0, 0, 260, 85), 8, 2.0, .6, 1.2, 30, not_small)
small = trace(SMALL, 14, 1.1, .4, .6, 12)
d = ' '.join(big)   # the small word is set in Geist below: traced at this size it breaks up
x0, y0, x1, y1 = 11, 9, 244, 77
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {x1 - x0} {y1 - y0}">'
       f'<path fill="currentColor" fill-rule="evenodd" d="{d}"/>'
       '<text x="160.2" y="65.6" textLength="79" lengthAdjust="spacingAndGlyphs" fill="currentColor" '
       'style="font: 400 12.4px Geist, Helvetica Neue, Arial, sans-serif">therapeutics</text></svg>')
open(out, 'w').write(svg); print(len(big), 'big +', len(small), 'small shapes,', len(svg), 'bytes')
