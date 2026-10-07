"""Fetch the candidate wordmark fonts from Google Fonts and save their "yster" outlines to fonts.json, so
build_sdeg.py runs offline. Outlines are scaled so each s is as tall as the logotype's Newsreader s (1034
units, the frame sdeg.py works in) and drawn y up, baseline 0. Needs fontTools; run once when FONTS changes.
"""
import io, json, os, re, subprocess, urllib.parse
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
D = os.path.dirname(os.path.abspath(__file__)) + '/'
S_HEIGHT = 1034.0   # the Newsreader s's ink height in the logotype export's units

# key: (display name, Google Fonts family spec, kind)
FONTS = {
    'fraunces': ('Fraunces 500', 'Fraunces:opsz,wght@72,500', 'serif'),
    'sourceserif': ('Source Serif 4 600', 'Source Serif 4:opsz,wght@60,600', 'serif'),
    'literata': ('Literata 500', 'Literata:opsz,wght@72,500', 'serif'),
    'lora': ('Lora 600', 'Lora:wght@600', 'serif'),
    'youngserif': ('Young Serif', 'Young Serif', 'serif'),
    'dmserif': ('DM Serif Text', 'DM Serif Text', 'serif'),
    'instrument': ('Instrument Serif', 'Instrument Serif', 'serif'),
    'inter': ('Inter 600', 'Inter:wght@600', 'sans'),
    'dmsans': ('DM Sans 600', 'DM Sans:wght@600', 'sans'),
    'manrope': ('Manrope 700', 'Manrope:wght@700', 'sans'),
    'plexsans': ('IBM Plex Sans 600', 'IBM Plex Sans:wght@600', 'sans'),
    'spacegrotesk': ('Space Grotesk 600', 'Space Grotesk:wght@600', 'sans'),
    'sora': ('Sora 600', 'Sora:wght@600', 'sans'),
    'outfit': ('Outfit 600', 'Outfit:wght@600', 'sans'),
}

def fetch(spec):
    url = 'https://fonts.googleapis.com/css2?family=' + urllib.parse.quote(spec, safe=':,@;') + '&text=yster'
    css = subprocess.run(['curl', '-sS', url], capture_output=True, text=True, check=True).stdout
    src = re.search(r'url\((https://[^)]+)\)', css).group(1)
    return TTFont(io.BytesIO(subprocess.run(['curl', '-sS', src], capture_output=True, check=True).stdout))

out = {}
for key, (name, spec, kind) in FONTS.items():
    f = fetch(spec); gs = f.getGlyphSet(); cmap = f.getBestCmap()
    bp = BoundsPen(gs); gs[cmap[ord('s')]].draw(bp); k = S_HEIGHT / (bp.bounds[3] - bp.bounds[1])
    glyphs = {}
    for ch in 'yster':
        g = cmap[ord(ch)]; sp = SVGPathPen(gs, lambda v: f'{v:.1f}')
        gs[g].draw(TransformPen(sp, (k, 0, 0, k, 0, 0)))
        bp = BoundsPen(gs); gs[g].draw(bp)
        glyphs[ch] = {'d': sp.getCommands(), 'adv': f['hmtx'][g][0] * k, 'x0': bp.bounds[0] * k, 'x1': bp.bounds[2] * k}
    out[key] = {'name': name, 'kind': kind, 'glyphs': glyphs}
    print(key, round(k, 3))
json.dump(out, open(D + 'fonts.json', 'w'), indent=0)
print('fonts.json', len(out))
