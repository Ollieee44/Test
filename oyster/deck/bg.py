"""Backgrounds (the story's three grounds: blood, barrier, neuron) and the clasp glow, as PNGs for the deck."""
import sys, os
import numpy as np
from PIL import Image
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
def hexc(h): return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], float)
W, H = 1920, 1080
y, x = np.mgrid[0:H, 0:W]
# radial ground, lightest up and to the right, as on the site
r = np.sqrt(((x - .68 * W) / (1.3 * W)) ** 2 + ((y - .28 * H) / (1.2 * H)) ** 2) * 2
t = np.clip(r, 0, 1)[..., None]
for name, a, b in (('blood', '#F6EEEC', '#E3D3D8'), ('barrier', '#F4E7E6', '#E6CBD0'), ('neuron', '#EFE6EE', '#D9CCE2')):
    img = hexc(a) * (1 - t) + hexc(b) * t
    Image.fromarray(img.astype(np.uint8)).save(os.path.join(OUT, f'bg_{name}.png'))
# the glow: clasp gold, soft radial falloff to transparent
S = 512; yy, xx = np.mgrid[0:S, 0:S]; d = np.sqrt((xx - S / 2) ** 2 + (yy - S / 2) ** 2) / (S / 2)
alpha = np.clip(1 - d, 0, 1) ** 1.8 * 200
g = np.zeros((S, S, 4), np.uint8); g[..., :3] = hexc('#D9A443'); g[..., 3] = alpha.astype(np.uint8)
Image.fromarray(g, 'RGBA').save(os.path.join(OUT, 'glow.png'))
print('backgrounds and glow written')
