"""Write the Inside Out mark (sprite symbol and favicon) into both websites. The wordmark itself, and its CSS,
come from logotype/build_logotype.py.

Older note: the O sizing in wordmark_metrics.py still sizes the mark within the logotype.

Main site: Newsreader 500 (Nacre) and Archivo 700 (Tidepool). Editorial: Newsreader 400 and Archivo 600.
The wordmark text is set at opsz 72 everywhere so its letters, and so the O, are the same drawing
at every size.
"""
import os, re, urllib.parse
from wordmark_metrics import omark
from marks import marks, svg

D = os.path.dirname(os.path.abspath(__file__)) + '/'
INSIDE_OUT = (8, 9.5, 92, 93.5)
SITES = [(D + '../index.html', 'newsreader-500', 'archivo-700', '.bigmark, .giant'),
         (D + '../editorial/index.html', 'newsreader-400', 'archivo-600', '.brand .wm')]

def rule(sel, face):
    s, va, ml, mr = omark(INSIDE_OUT, face)
    return f'{sel} {{ width: {s:.4f}em; height: {s:.4f}em; vertical-align: {va:.4f}em; margin: 0 {mr:.4f}em 0 {ml:.4f}em; }}'

# the Inside Out mark (with The Hollow's cradle) as the sprite symbol and the favicon
_m, _s, _ = marks('om-')
MASK = _m['inside'].replace('id="om-mInside"', 'id="mOm"')
SYMBOL = ('<symbol id="omark" viewBox="0 0 100 100"><g transform="translate(-1.5 1.5)">'
          + _s['inside'].replace('url(#om-mInside)', 'url(#mOm)').replace('style="fill:var(--p1)"', 'class="pearl" style="fill: var(--pearl-mark)"')
          + '</g></symbol>')
def favicon():
    inner = svg('inside', '#EFE6E1', '#C99BB0', '#C99BB0').replace('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">', '').replace('</svg>', '')
    tile = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" rx="22" fill="#2B2230"/>'
            f'<g transform="translate(9 9) scale(.82)">{inner}</g></svg>').replace('"', "'")
    return '<link rel="icon" href="data:image/svg+xml,' + urllib.parse.quote(tile, safe="/:=' ").replace(' ', '%20') + '">'

for path, serif, sans, words in SITES:
    src = open(path).read()
    src, a = re.subn(r'<mask id="mOm".*?</mask>', lambda m: MASK, src, flags=re.S)
    src, b = re.subn(r'<symbol id="omark".*?</symbol>', lambda m: SYMBOL, src, flags=re.S)
    src, c = re.subn(r'<link rel="icon" href="[^"]*">', lambda m: favicon(), src)
    assert a == b == c == 1, (path, a, b, c)
    open(path, 'w').write(src)
    print('updated', os.path.relpath(path, D))
