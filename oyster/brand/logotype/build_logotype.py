"""The Oyster logotype: the wordmark drawn as fixed outlines with the spacing saved in the Logotype
studio (settings.json), and "therapeutics" hung below it.

Coordinates are font units, 1000 to the em, y down, baseline at 0. Nacre is set in Newsreader 500
(opsz 72) and Tidepool in Archivo 700; "therapeutics" is Archivo 500 in both. Running this file:
  - replaces the wordmark in both websites (hero, header and footer on the main site; header and
    footer on the editorial site) and their wordmark CSS,
  - writes the SVG exports oyster-logotype-<palette>.svg (with "therapeutics") and
    oyster-wordmark-<palette>.svg (without) into brand/.
build_variations.py imports logotype_svg() for the "mark as the O" rows.
"""
import json, os, re, sys
D = os.path.dirname(os.path.abspath(__file__)) + '/'
sys.path.insert(0, D); sys.path.insert(0, D + '..')
from fontTools.pens.svgPathPen import SVGPathPen
from glyphs import font, glyph
from wordmark_metrics import omark
from marks import marks

S = json.load(open(D + 'settings.json'))
FACE = {'nacre': ('newsreader', 'newsreader-500'), 'tidepool': ('archivo', 'archivo-700')}
SUB_FACE, SUB_TRACK, SUB_CAP = 'archivo500', .02, .723   # descriptor face, tracking (em), height of t/h
INSIDE_OUT_INK = (8, 9.5, 92, 93.5)

def _path(face, ch, x, y=0, scale=1.0):
    f = font(face); gs = f.getGlyphSet(); g = f.getBestCmap()[ord(ch)]; k = 1000 / f['head'].unitsPerEm * scale
    pen = SVGPathPen(gs, lambda v: f'{v:.1f}'); gs[g].draw(pen)
    return f'<path d="{pen.getCommands()}" transform="translate({x:.1f} {y:.1f}) scale({k:.4f} {-k:.4f})"/>', f['hmtx'][g][0] * k

def _bounds(face, ch, x, y=0, scale=1.0):
    p = [q for poly in glyph(face, ch)['polys'] for q in poly]
    return (x + min(a for a, b in p) * 1000 * scale, y - max(b for a, b in p) * 1000 * scale,
            x + max(a for a, b in p) * 1000 * scale, y - min(b for a, b in p) * 1000 * scale)

def parts(pal, mark_ink=INSIDE_OUT_INK):
    """Outlines, mark box and bounds for one palette. A mark other than Inside Out keeps the same
    clear space between its right edge and the y, so the letters shift to suit its width."""
    face, key = FACE[pal]; st = S[pal]; pos = {p['ch']: p['x'] for p in st['positions']}
    s, va, ml, mr = omark(mark_ink, key); s_io, _, ml_io, _ = omark(INSIDE_OUT_INK, key)
    shift = (ml + mark_ink[2] / 100 * s - (ml_io + .92 * s_io)) * 1000
    box = (ml * 1000, -(va + s) * 1000, s * 1000)          # x, y of the top edge, size
    ink = [box[0] + mark_ink[0] / 100 * s * 1000, box[1] + mark_ink[1] / 100 * s * 1000,
           box[0] + mark_ink[2] / 100 * s * 1000, box[1] + mark_ink[3] / 100 * s * 1000]
    letters, bb = '', [ink]
    for ch in 'yster':
        x = pos[ch] + shift; p, _ = _path(face, ch, x); letters += p; bb.append(_bounds(face, ch, x))
    sub, sbb = '', []
    size, gap = st['sub']['size'] / 1000, st['sub']['gap']
    x = pos['y'] + shift + glyph(face, 'y')['adv'] * 1000 + st['sub']['dx']; base = gap + SUB_CAP * size * 1000
    for ch in 'therapeutics':
        p, adv = _path(SUB_FACE, ch, x, base, size); sub += p; sbb.append(_bounds(SUB_FACE, ch, x, base, size))
        x += adv + SUB_TRACK * size * 1000
    return {'box': box, 'letters': letters, 'sub': sub, 'bb': bb, 'sbb': sbb}

def _view(bbs, pad=4):
    x0 = min(b[0] for b in bbs) - pad; y0 = min(b[1] for b in bbs) - pad
    x1 = max(b[2] for b in bbs) + pad; y1 = max(b[3] for b in bbs) + pad
    return x0, y0, x1 - x0, y1 - y0

def logotype_svg(pal, mark_id='omark', sub=True, cls='', style='', mark_ink=INSIDE_OUT_INK, inline=False):
    """Inline SVG sized in em (1 em = the wordmark's font size). inline=True aligns its baseline with
    the surrounding text; otherwise it is a block from the top of the t to the bottom of its ink."""
    P = parts(pal, mark_ink)
    x0, y0, w, h = _view(P['bb'] + (P['sbb'] if sub else []))
    va = f'vertical-align:{-(y0 + h) / 1000:.4f}em;' if inline else ''
    box = P['box']
    use = f'<use href="#{mark_id}" x="{box[0]:.1f}" y="{box[1]:.1f}" width="{box[2]:.1f}" height="{box[2]:.1f}"/>'
    subg = f'<g class="wm-sub">{P["sub"]}</g>' if sub else ''
    return (f'<svg class="lt {cls}" viewBox="{x0:.1f} {y0:.1f} {w:.1f} {h:.1f}" style="width:{w / 1000:.4f}em;height:{h / 1000:.4f}em;{va}{style}" '
            f'aria-hidden="true" fill="currentColor">{use}<g>{P["letters"]}</g>{subg}</svg>')

def export_svg(pal, sub, colors):
    """A standalone file: the mark drawn in, literal colours."""
    ink, pearl = colors; P = parts(pal); x0, y0, w, h = _view(P['bb'] + (P['sbb'] if sub else []), 12)
    masks, sym, _ = marks('x-'); box = P['box']; k = box[2] / 100
    mark = sym['inside'].replace('style="fill:var(--p1)"', f'fill="{pearl}"')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:.1f} {y0:.1f} {w:.1f} {h:.1f}"><defs>{masks["inside"]}</defs>'
            f'<g fill="{ink}"><g transform="translate({box[0]:.1f} {box[1]:.1f}) scale({k:.4f})"><g transform="translate(-1.5 1.5)">{mark}</g></g>'
            f'{P["letters"]}{P["sub"] if sub else ""}</g></svg>')

CSS = '''/* wordmark:start (generated by brand/logotype/build_logotype.py) */
/* The wordmark is the Oyster logotype: fixed outlines with hand-set spacing, one per palette. */
.lt { display: inline-block; overflow: visible; }
.lt-tidepool { display: none; }
:root[data-palette="tidepool"] .lt-nacre { display: none; }
:root[data-palette="tidepool"] .lt-tidepool { display: inline-block; }
.lt .pearl { transition: fill .5s ease; }
.bigmark .lt, .giant .lt { vertical-align: top; }
.bigmark, div.giant { line-height: 0; }
/* wordmark:end */'''

def both(**kw):
    return logotype_svg('nacre', cls='lt-nacre', **kw) + logotype_svg('tidepool', cls='lt-tidepool', **kw)

if __name__ == '__main__':
    main, ed = D + '../../index.html', D + '../../editorial/index.html'
    # main site: hero/header and footer, with "therapeutics"
    s = open(main).read()
    old = re.compile(r'(?:<svg class="om" viewBox="0 0 100 100" aria-hidden="true"><use href="#omark"/></svg>y<span class="wm-anchor"><span class="wm-sub">therapeutics</span></span>ster'
                     r'|<!-- logotype -->.*?<!-- /logotype -->)', re.S)
    s, n = old.subn(lambda m: '<!-- logotype -->' + both(sub=True) + '<!-- /logotype -->', s); assert n == 2, n
    s, n = re.subn(r'/\* "therapeutics" hangs below.*?:root\[data-palette="tidepool"\] \.wm-sub \{ left: -1\.175em; \}\n', '', s, flags=re.S); assert n in (0, 1)
    s, n = re.subn(r'/\* wordmark:start.*?/\* wordmark:end \*/', lambda m: CSS, s, flags=re.S); assert n == 1
    s = s.replace("markSub = mark.querySelector('.wm-sub');", "markSub = mark.querySelectorAll('.wm-sub');")
    s = s.replace("if (markSub) markSub.style.opacity = (1 - clamp((q - .35) / .4, 0, 1)).toFixed(3);",
                  "var so = (1 - clamp((q - .35) / .4, 0, 1)).toFixed(3); markSub.forEach(function (g) { g.style.opacity = so; });")
    s = s.replace(".bigmark {\n  position: fixed;", ".bigmark {\n  position: fixed;", 1)
    open(main, 'w').write(s)
    # editorial site: header and footer, the logotype followed by " Therapeutics" set in type
    s = open(ed).read()
    old = re.compile(r'(?:<svg class="om" viewBox="0 0 100 100" aria-hidden="true"><use href="#omark"/></svg>yster|<!-- logotype -->.*?<!-- /logotype -->)', re.S)
    s, n = old.subn(lambda m: '<!-- logotype -->' + both(sub=False, inline=True) + '<!-- /logotype -->', s); assert n == 2, n
    s, n = re.subn(r'/\* wordmark:start.*?/\* wordmark:end \*/', lambda m: CSS, s, flags=re.S); assert n == 1
    open(ed, 'w').write(s)
    # exports
    for pal, cols in (('nacre', ('#2B2230', '#C99BB0')), ('tidepool', ('#0F4C4A', '#F2B84B'))):
        open(D + f'../oyster-logotype-{pal}.svg', 'w').write(export_svg(pal, True, cols))
        open(D + f'../oyster-wordmark-{pal}.svg', 'w').write(export_svg(pal, False, cols))
    print('updated both sites and wrote 4 SVG exports')
