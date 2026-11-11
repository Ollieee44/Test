"""Trace Rob's reference figure (a side-view silhouette, head in profile facing left, with a gut icon in a ring) into
vector data for the journey: the body's outline (its pixels, with the ring's disc filled in, contoured and simplified),
and the icon's strokes (each colour thinned to a one-pixel centreline and walked into polylines). Kept as drawn (facing left)
and scaled so the ring lands on the journey's gut inset (centre (0, 25), radius 22, y down).
Usage: python trace_person_ref.py <reference.png> ../person_ref.json"""
import json, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage import measure
from skimage.morphology import skeletonize, remove_small_objects

src, dst = sys.argv[1:3]
img = Image.open(src).convert('RGBA'); bg = Image.new('RGBA', img.size, (255, 255, 255, 255)); bg.alpha_composite(img)
im = np.array(bg.convert('RGB')).astype(int); H, W, _ = im.shape
CX, CY, CR = 510, 734.5, 191                       # the ring (centre of its stroke), in the image's pixels
S = 22 / CR
to_j = lambda x, y: (round((x - CX) * S, 2), round((y - CY) * S + 25, 2))   # as drawn: facing left, the gut to the lower right

yy, xx = np.mgrid[0:H, 0:W]
body = ((255 - im).sum(2) > 40) | (((xx - CX) ** 2 + (yy - CY) ** 2) < (CR + 4) ** 2)
body = ndi.binary_fill_holes(body); body[945:] = False; body = ndi.binary_opening(body, iterations=1)
c = max(measure.find_contours(np.pad(body, 2).astype(float), .5), key=len) - 2
c = measure.approximate_polygon(c, 1.2)
outline = [to_j(x, y) for y, x in c[:-1]]

inside = ((xx - CX) ** 2 + (yy - CY) ** 2) < (CR - 5) ** 2
def chains(mask):
    sk = skeletonize(remove_small_objects(mask, max_size=30))
    P = set(zip(*np.where(sk)))
    nb = lambda p: [(p[0] + dy, p[1] + dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dy or dx) and (p[0] + dy, p[1] + dx) in P]
    deg = {p: len(nb(p)) for p in P}; used = set(); out = []
    def walk(a, b):
        ch = [a, b]; used.add(frozenset((a, b)))
        while deg[ch[-1]] == 2:
            nxt = [q for q in nb(ch[-1]) if frozenset((ch[-1], q)) not in used and q != ch[-2]]
            if not nxt: break
            used.add(frozenset((ch[-1], nxt[0]))); ch.append(nxt[0])
            if nxt[0] == ch[0]: break
        return ch
    for p in sorted(P, key=lambda p: deg[p] == 2):
        for q in nb(p):
            if frozenset((p, q)) not in used: out.append(walk(p, q))
    res = []
    for ch in out:
        if len(ch) < 6: continue
        a = np.array(ch, float); closed = len(ch) > 8 and np.hypot(*(a[0] - a[-1])) < 2
        # even spacing, then a Gaussian average along the line: the pixel steps go, the scallops (about 35 px) stay
        d = np.r_[0, np.cumsum(np.hypot(*np.diff(a, axis=0).T))]; t = np.arange(0, d[-1], 2.0)
        a = np.c_[np.interp(t, d, a[:, 0]), np.interp(t, d, a[:, 1])]
        if len(a) > 8:
            a = np.c_[ndi.gaussian_filter1d(a[:, 0], 2.6, mode='wrap' if closed else 'nearest'), ndi.gaussian_filter1d(a[:, 1], 2.6, mode='wrap' if closed else 'nearest')]
        res.append([to_j(x, y) for y, x in measure.approximate_polygon(a, .7)])
    return res
navy = chains((np.abs(im - np.array([13, 21, 80])).sum(2) < 120) & inside)
blue = chains((np.abs(im - np.array([158, 230, 255])).sum(2) < 90) & inside)
# the mouth (the lips' notch, below the nose) in the same frame
mouth = to_j(279, 212)
json.dump({'outline': outline, 'colon': navy, 'tract': blue, 'mouth': mouth, 'stroke': round(8 * S, 3)}, open(dst, 'w'))
print(dst, len(outline), 'outline points;', len(navy), 'colon and', len(blue), 'tract strokes; mouth', mouth)
