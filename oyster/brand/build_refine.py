"""Build refine.html, the comparison sheet for Inside Out, refined (marks from refine.py), in the same
format as variations.html. The "mark as the o" rows reuse the outlined logotype exports, so no font
files are needed; the pixel test rasterises each mark in the browser at real favicon sizes."""
import os, re, urllib.parse
import refine

D = os.path.dirname(os.path.abspath(__file__)) + '/'
AH = 'aria-hidden="true"'
N = ('#2B2230', '#C99BB0', '#D9A443'); T = ('#EAF3EF', '#F2B84B', '#F27D62')   # ink, pearl, clasp
OPTS = [
 ('inside', '00', 'Inside Out', 'The adopted mark, shown for reference: a disc with the open shell cut out of it, and the pearl in a round cradle.',
  'A strong silhouette, and already the o of the logotype, the favicon and the header.',
  'Nothing in it says clasp, which the house style calls the hero. Below 24px the cradle ring and the hinge fill in.'),
 ('seam', '01', 'Clasped Pearl', 'The pearl is two halves held together by a fine band in the clasp colour. From across the room it is the same pearl; up close it is two halves, clasped.',
  'The smallest change that tells the SELFTAC story. Nothing else about the mark or the logotype moves.',
  'The band is a detail: it disappears below 32px, which is a graceful fallback to the current mark.'),
 ('clasp', '02', 'The Clasp', 'The pearl becomes the clasp itself: two clasp pearls and their bond, the same glyph that marks every section label, lying in a long cradle in the lower shell.',
  'Ties the logo to the clasp motif used across the site, and the long cradle gives the mark a new, ownable shape.',
  'The pearl colour leaves the mark, so the clasp colour carries both meanings in the logo. It needs colour; in one colour the pair reads as a dumbbell.'),
 ('large', '03', 'Larger Shell', 'The same drawing with the shell scaled up inside a thinner rim, so the oyster reads before the disc does.',
  'More oyster, less button. The pearl and cradle grow with the shell, which helps at 24 to 32px.',
  'The rim thins to about 4 units at the shell tip, so it starts to break up at 16px.'),
 ('wide', '04', 'Wider Mouth', 'The upper shell opens further and the pearl moves up into the opening, a little larger.',
  'Opener and more optimistic, and the wider gap keeps the shells apart at small sizes.',
  'A more noticeable change to the logotype&rsquo;s o; the pearl sits higher than the x-height centre.'),
 ('small', '05', 'Small-size Cut', 'A companion for 16 to 32px only: no cradle ring, a wide mouth and a big pearl. The full mark is used everywhere else.',
  'Clearest at favicon and app-icon sizes, where the other options turn to mush.',
  'Not a logo in its own right: too blunt at large sizes. It only works as part of a pair with the main mark.'),
]

def use(id, sz, cols, extra=AH):
    ink, p1, p2 = cols
    return f'<svg width="{sz}" height="{sz}" viewBox="0 0 100 100" style="color:{ink};fill:currentColor;--p1:{p1};--p2:{p2}" {extra}><use href="#r-{id}"/></svg>'

def app(id, tile, fg, p1, p2, sz):
    return (f'<svg class="app" width="{sz}" height="{sz}" viewBox="0 0 100 100" {AH}><rect width="100" height="100" fill="{tile}"/>'
            f'<g transform="translate(9 9) scale(.82)" style="color:{fg};fill:currentColor;--p1:{p1};--p2:{p2}"><use href="#r-{id}" width="100" height="100"/></g></svg>')

def _lt(pal):
    """The logotype export split into its viewBox, mark box (x, y, size) and letter outlines."""
    s = open(D + f'oyster-logotype-{pal}.svg').read()
    vb = re.search(r'viewBox="([^"]+)"', s).group(1)
    tx, ty, k = map(float, re.search(r'<g transform="translate\(([-\d.]+) ([-\d.]+)\) scale\(([\d.]+)\)">', s).groups())
    letters = re.search(r'</g></g>(<path.*)</g></svg>$', s, re.S).group(1)
    return vb, (tx, ty, 100 * k), letters
LT = {p: _lt(p) for p in ('nacre', 'tidepool')}

def logotype(pal, id, cols):
    vb, (x, y, sz), letters = LT[pal]; w, h = map(float, vb.split()[2:])
    ink, p1, p2 = cols
    return (f'<svg class="lt" viewBox="{vb}" style="width:{w / 1000:.4f}em;height:{h / 1000:.4f}em;color:{ink};--p1:{p1};--p2:{p2}" {AH} fill="currentColor">'
            f'<use href="#r-{id}" x="{x}" y="{y}" width="{sz:.1f}" height="{sz:.1f}"/>{letters}</svg>')

M = refine   # the marks module the sheet is built from; sheet() swaps it

def tile_url(id, tile, fg, pearl, clasp):
    """A standalone app tile as a data URL, for the canvas pixel test."""
    inner = re.sub(r'^<svg[^>]*>|</svg>$', '', M.standalone(id, fg, pearl, clasp, ns=f'px-{id}-'))
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100"><rect width="100" height="100" rx="22" fill="{tile}"/>'
           f'<g transform="translate(9 9) scale(.82)">{inner}</g></svg>')
    return 'data:image/svg+xml,' + urllib.parse.quote(svg)

def pixels(id):
    out = ''
    for lab, tile, fg, pearl, clasp in (('Nacre', '#2B2230', '#EFE6E1', N[1], N[2]), ('Tidepool', '#EAF3EF', '#0F4C4A', T[1], T[2])):
        u = tile_url(id, tile, fg, pearl, clasp)
        for px in (16, 24, 32):
            out += (f'<figure class="px"><canvas data-src="{u}" data-px="{px}" width="{px}" height="{px}" role="img" '
                    f'aria-label="{lab} app tile rendered at {px} pixels, enlarged"></canvas><figcaption>{lab} &middot; {px}px</figcaption></figure>')
    return out

def sheet(module, opts, title, h1, intro, footer, out):
    """Write one comparison sheet: opts are (id, number, name, idea, strength, watch out)."""
    global M
    M = module
    strip = ''.join(f'<a class="cell" href="#{i}"><span class="mono">{n}</span>{use(i, 72, N)}<span class="nm">{t}</span></a>' for i, n, t, *_ in opts)
    strip2 = ''.join(f'<a class="cell" href="#{i}">{use(i, 72, T)}<span class="mono">{n}</span></a>' for i, n, t, *_ in opts)
    cards = ''
    for i, n, t, idea, good, watch in opts:
        smallN = use(i, 48, N) + use(i, 32, N) + use(i, 24, N) + app(i, N[0], '#EFE6E1', N[1], N[2], 32) + app(i, N[0], '#EFE6E1', N[1], N[2], 16)
        smallT = use(i, 48, T) + use(i, 32, T) + use(i, 24, T) + app(i, '#EAF3EF', '#0F4C4A', T[1], T[2], 32) + app(i, '#EAF3EF', '#0F4C4A', T[1], T[2], 16)
        heroN = use(i, 220, N, f'role="img" aria-label="{t} mark in Nacre colours" class="hero-m"')
        heroT = use(i, 220, T, f'role="img" aria-label="{t} mark in Tidepool colours" class="hero-m"')
        cards += f'''
      <section class="opt" id="{i}">
        <div class="wrap">
          <div class="opt-head"><span class="num">{n}</span><div><h2>{t}</h2><p>{idea}</p></div></div>
          <div class="panels">
            <div class="panel nacre"><span class="mono">Nacre</span>{heroN}<div class="small">{smallN}</div></div>
            <div class="panel tide"><span class="mono">Tidepool</span>{heroT}<div class="small">{smallT}</div></div>
            <div class="panel nacre oword"><span class="mono">In the logotype &middot; Nacre</span><div class="olock">{logotype("nacre", i, N)}</div></div>
            <div class="panel tide oword"><span class="mono">In the logotype &middot; Tidepool</span><div class="olock">{logotype("tidepool", i, T)}</div></div>
            <div class="panel pxp wide"><span class="mono">Pixel test: the app tile rasterised at real size, enlarged six times</span><div class="pxrow">{pixels(i)}</div></div>
            <div class="panel mono-p wide"><span class="mono">One colour</span>{use(i, 64, ("#2B2230",) * 3)}{use(i, 64, ("#0F4C4A",) * 3)}{use(i, 32, ("#2B2230",) * 3)}</div>
          </div>
          <div class="notes"><div><h3>Strength</h3><p>{good}</p></div><div><h3>Watch out</h3><p>{watch}</p></div></div>
        </div>
      </section>'''

    CSS = open(D + 'sheet.css').read() + '''
    .panel.mono-p { background: #FFFFFF; color: #2B2230; padding-block: 24px; }
    .olock .lt { display: block; max-width: 100%; height: auto !important; }
    .olock { font-size: clamp(40px, 5.4vw, 72px); white-space: normal; width: 100%; display: grid; place-items: center; }
    .panel.pxp { background: var(--surface); border: 1px solid var(--line); color: var(--ink); }
    .pxrow { display: flex; flex-wrap: wrap; gap: 20px 24px; justify-content: center; align-items: flex-end; width: 100%; }
    .px { margin: 0; display: grid; justify-items: center; gap: 8px; }
    .px canvas { image-rendering: pixelated; image-rendering: crisp-edges; }
    .px figcaption { font: 500 11px/1 var(--mono); letter-spacing: .06em; text-transform: uppercase; color: var(--muted); }
    .px:nth-child(3n+1) { margin-left: 12px; }
    '''
    JS = '''<script>
    // draw each tile at its real pixel size, then show the canvas six times larger with hard pixel edges
    document.querySelectorAll('canvas[data-src]').forEach(function (c) {
      var px = +c.dataset.px, img = new Image();
      c.style.width = c.style.height = (px * 6) + 'px';
      img.onload = function () { var g = c.getContext('2d'); g.clearRect(0, 0, px, px); g.drawImage(img, 0, 0, px, px); };
      img.src = c.dataset.src;
    });
    </script>'''

    html = f'''<!doctype html>
    <html lang="en">
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
    <!-- artifact:start -->
    <title>{title}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=swap">
    <style>
    {CSS}
    </style>
    </head>
    <body>
    {M.defs()}
    <header class="top">
      <div class="wrap">
        <span class="mono">Oyster Therapeutics &middot; Brand mark</span>
        <h1>{h1}</h1>
        <p>{intro}</p>
      </div>
    </header>
    <main>
      <div class="wrap">
        <div class="strip n">{strip}</div>
        <div class="strip t">{strip2}</div>
      </div>
    {cards}
    </main>
    <footer><div class="wrap">Concepts for review. {footer}</div></footer>
    {JS}
    <!-- artifact:end -->
    </body>
    </html>
    '''
    html = re.sub(r'^    ', '', html, flags=re.M)   # the template above is indented with the function
    open(D + out, 'w').write(html)
    print(out, len(html))

if __name__ == '__main__':
    sheet(refine, OPTS, 'Inside Out, Refined', 'Inside Out, refined',
          'Five refinements of the adopted mark. Two bring in the clasp, which the brand calls its hero; two make the shell read more clearly; one is a companion cut for favicons. Each is shown in both palettes, as the o of the logotype, at real pixel sizes and in one colour. The clasp colour is gold in Nacre and coral in Tidepool.',
          'Built by <code>oyster/brand/build_refine.py</code>; SVG files for each option, in both palettes, are in <code>oyster/brand/</code> as <code>oyster-refine-*.svg</code>.', 'refine.html')
