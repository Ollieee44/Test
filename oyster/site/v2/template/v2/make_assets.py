"""Artwork for the v2 Oyster slide template (assets/), in the Colors.pdf palette: the brand's gradient edge (teal to kelp
to a yellow-green at the foot, sampled from the brand guide's pages), the logo and mark in white, Abyss Green and Sea Foam,
and the ternary complex from the v3 journey (src/complex-still.png, a still at p .79 on the #1A372A sky) cropped for the
picture layouts."""
import json, os
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__)) + '/'
A = D + 'assets/'; OLD = D + '../assets/'
os.makedirs(A, exist_ok=True)
hexrgb = lambda h: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))

# the gradient edge: 38 px of a 4000 px page in the guide; stops as sampled down its height
STOPS = [(0, '#309989'), (.5, '#41A68A'), (.62, '#43A774'), (.82, '#47A86F'), (.9, '#6DAC61'), (1, '#A3B451')]
H = 1350; bar = Image.new('RGB', (16, H))
for y in range(H):
    t = y / (H - 1)
    for (t0, c0), (t1, c1) in zip(STOPS, STOPS[1:]):
        if t0 <= t <= t1:
            f = (t - t0) / (t1 - t0); a, b = hexrgb(c0), hexrgb(c1)
            col = tuple(round(a[i] + (b[i] - a[i]) * f) for i in range(3)); break
    for x in range(16): bar.putpixel((x, y), col)
bar.save(A + 'edge.png', optimize=True)

# the logo and its mark, recoloured
logo = Image.open(OLD + 'logo-white.png').convert('RGBA')
mark = logo.crop((0, 0, int(logo.width * .27), logo.height)); mark = mark.crop(mark.getbbox())
def tint(im, hx):
    out = Image.new('RGBA', im.size, hexrgb(hx) + (255,)); out.putalpha(im.getchannel('A')); return out
for name, im in [('logo', logo), ('mark', mark)]:
    tint(im, '#FFFFFF').save(A + name + '-white.png'); tint(im, '#1A372A').save(A + name + '-abyss.png')

# the complex: full-bleed (16:9, already on the dark ground) and a portrait panel cropped round it
still = Image.open(D + 'src/complex-still.png').convert('RGB')
still.save(A + 'complex-hero.png', optimize=True)
# the title page's ground: the complex moved right, clear of a long title
shifted = Image.new('RGB', still.size, hexrgb('#1A372A')); shifted.paste(still, (int(still.width * .1), 0)); shifted.save(A + 'complex-title.png', optimize=True)
W, Hh = still.size; cx = int(W * .72)
panel_w = int(Hh * 5.6 / 6.3)
still.crop((cx - panel_w // 2, 0, cx + panel_w // 2, Hh)).save(A + 'complex-panel.png', optimize=True)
json.dump({n: Image.open(A + n).size for n in os.listdir(A) if n.endswith('.png')}, open(A + 'sizes.json', 'w'))
print(sorted(os.listdir(A)))
