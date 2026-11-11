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

# the logo, from the brand's own SVGs (src/logo): the colour versions for the title and closing pages and the mark
# at the top of a page, the one-colour versions for the small mark in the footer. Each goes in as SVG with a PNG copy
# for older PowerPoint (finish_template.py pairs them). The mark is the logo's first 134 units, its paths left of x 140.
import re, cairosvg
for f in os.listdir(A):
    if f.startswith(('logo-', 'mark-')): os.remove(A + f)
def mark_only(svg):
    keep = [m.group(0) for m in re.finditer(r'<path d="M([\d.]+)[^>]*/>', svg) if float(m.group(1)) < 140]
    defs = re.search(r'<defs>.*</defs>', svg, re.S)
    return ('<svg width="134" height="134" viewBox="0 0 134 134" fill="none" xmlns="http://www.w3.org/2000/svg">\n' + '\n'.join(keep)
            + ('\n' + defs.group(0) if defs else '') + '\n</svg>\n')
for src, name in [('white-color', 'logo-on-dark'), ('black-color', 'logo-on-light')]:
    svg = open(D + 'src/logo/' + src + '.svg').read()
    open(A + name + '.svg', 'w').write(svg)
    open(A + name.replace('logo', 'mark') + '.svg', 'w').write(mark_only(svg))
for src in ('white', 'black'):
    open(A + 'mark-' + src + '.svg', 'w').write(mark_only(open(D + 'src/logo/' + src + '.svg').read()))
for f in sorted(os.listdir(A)):
    if f.endswith('.svg'): cairosvg.svg2png(url=A + f, write_to=A + f[:-4] + '.png', output_width=2400 if f.startswith('logo') else 700)

# the brand's textured greens, for the title, section and closing pages
for n in ('band', 'corner'):
    Image.open(D + 'src/texture-' + n + '.webp').convert('RGB').save(A + 'texture-' + n + '.jpg', quality=92)

# the complex: full-bleed (16:9, already on the dark ground) and a portrait panel cropped round it
still = Image.open(D + 'src/complex-still.png').convert('RGB')
still.save(A + 'complex-hero.png', optimize=True)
W, Hh = still.size; cx = int(W * .72)
panel_w = int(Hh * 5.6 / 6.3)
still.crop((cx - panel_w // 2, 0, cx + panel_w // 2, Hh)).save(A + 'complex-panel.png', optimize=True)
json.dump({n: Image.open(A + n).size for n in os.listdir(A) if n.endswith('.png')}, open(A + 'sizes.json', 'w'))
print(sorted(os.listdir(A)))
