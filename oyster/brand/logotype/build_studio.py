"""Build studio.html, the Oyster Logotype spacing studio.

The wordmark is drawn from the font outlines (Newsreader 500 at opsz 72 for Nacre, Archivo 700 for
Tidepool), so each gap can be set by hand. For every letter the page gets its outline, its advance
and its left and right ink edge on a stack of scanlines across the x-height; the page uses those
profiles to measure the white space between letters and to solve optically even spacing.
"""
import json, os, sys
D = os.path.dirname(os.path.abspath(__file__)) + '/'
sys.path.insert(0, D); sys.path.insert(0, D + '..')
from glyphs import glyph, profile
from wordmark_metrics import FONT, omark
from marks import marks

N = 56  # scanlines across the band from the baseline to the top of the round letters
FACES = {
    # face, metrics key, the site's letter-spacing, where "therapeutics" starts relative to the end of the y
    'nacre': dict(face='newsreader', key='newsreader-500', track=-.015, subdx=-.225,
                  bg='#EFE6E1', ink='#2B2230', p1='#C99BB0', label='Nacre', font='Newsreader 500'),
    'tidepool': dict(face='archivo', key='archivo-700', track=-.035, subdx=-.176,
                     bg='#0F4C4A', ink='#EAF3EF', p1='#F2B84B', label='Tidepool', font='Archivo 700'),
}

data = {}
for pal, c in FACES.items():
    top, bot = FONT[c['key']]['top'], FONT[c['key']]['bot']
    ys = [top * (k + .5) / N for k in range(N)]
    s, va, ml, mr = omark((8, 9.5, 92, 93.5), c['key'])
    gl = {}
    for ch in 'yster':
        g = glyph(c['face'], ch)
        pr = profile(g['polys'], ys)
        gl[ch] = {'adv': round(g['adv'], 4), 'path': g['path'],
                  'L': [None if p is None else round(p[0], 4) for p in pr],
                  'R': [None if p is None else round(p[1], 4) for p in pr]}
    data[pal] = {'label': c['label'], 'font': c['font'], 'bg': c['bg'], 'ink': c['ink'], 'p1': c['p1'],
                 'track': c['track'], 'top': top, 'bot': bot, 'ys': [round(y, 4) for y in ys],
                 'mark': {'s': round(s, 4), 'va': round(va, 4), 'ml': round(ml, 4), 'mr': round(mr, 4)},
                 'glyphs': gl, 'sub': {'dx': c['subdx'], 'gap': .04, 'size': .12}}

masks, sym, _ = marks('lt-')
mark_svg = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>' + masks['inside'] + '</defs>'
            '<symbol id="omark" viewBox="0 0 100 100"><g transform="translate(-1.5 1.5)">' + sym['inside'] + '</g></symbol></svg>')

html = open(D + 'studio_template.html').read()
html = html.replace('/*DATA*/null', json.dumps(data, separators=(',', ':'))).replace('<!--MARK-->', mark_svg)
open(D + 'studio.html', 'w').write(html)
print('studio.html', len(html))
