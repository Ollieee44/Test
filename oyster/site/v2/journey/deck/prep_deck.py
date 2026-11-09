"""Prepare the exported pictures for the deck: crop each 3D still to its drawing (recording where the crop starts, so
its anchor still lines up), and draw each keyframe's ground (the page's radial gradient, from its two sky colours).
Run after export_deck.js; writes out/c/*.png and out/prep.json."""
import json, os
import numpy as np
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__)) + '/out/'
os.makedirs(D + 'c', exist_ok=True)
data = json.load(open(D + 'keyframes.json'))
crops = {}
for name in list(data['refs']) + list(data['flats']) + ['stars', 'eq', 'logo']:
    im = Image.open(D + name + '.png').convert('RGBA')
    if name in data['refs']:
        bb = im.getchannel('A').point(lambda a: 255 if a > 6 else 0).getbbox()
        x0, y0, x1, y1 = max(0, bb[0] - 4), max(0, bb[1] - 4), min(im.width, bb[2] + 4), min(im.height, bb[3] + 4)
        im = im.crop((x0, y0, x1, y1))
    else:
        x0 = y0 = 0
    im.save(D + 'c/' + name + '.png', optimize=True)
    crops[name] = {'x0': x0, 'y0': y0, 'w': im.width, 'h': im.height}

def hexrgb(h):
    h = h.strip().lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)
W, H = 1920, 1080
yy, xx = np.mgrid[0:H, 0:W].astype(float)
t = np.clip(np.sqrt(((xx - .68 * W) / (1.3 * W)) ** 2 + ((yy - .28 * H) / (1.2 * H)) ** 2), 0, 1)[..., None]
grounds = {}
for k in data['keys']:
    key = '-'.join(c.strip().lstrip('#').upper() for c in k['sky'])
    if key not in grounds:
        a, b = (hexrgb(c) for c in k['sky'])
        img = (a * (1 - t) + b * t).round().clip(0, 255).astype(np.uint8)
        name = f'ground{len(grounds)}'
        Image.fromarray(img, 'RGB').save(D + 'c/' + name + '.png', optimize=True)
        grounds[key] = name
    k['ground'] = grounds[key]
json.dump({'crops': crops, 'grounds': grounds, **data}, open(D + 'prep.json', 'w'))
print(len(crops), 'pictures,', len(grounds), 'grounds')
