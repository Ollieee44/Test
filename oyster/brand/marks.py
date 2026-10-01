"""The Open Shell marks, all with The Hollow's cradle: the pearl drops into a round hollow cut
into the lower shell, with a ring of clear space around it.

Each mark is SVG in a 0-100 viewBox: currentColor for the shells, var(--p1) and var(--p2) for the
accents. Masks are returned separately so a page can define them once. Running this file writes
the SVG exports (oyster-<name>-<palette>.svg) and variations_defs.svg.
"""
import os

D = os.path.dirname(os.path.abspath(__file__)) + '/'
LOW = 'M10 60C10 58 12 57 14 57H84C90 57 93 60 92 64C88 80 70 90 48 90C27 90 11 78 10 60Z'
UP = 'M12 53C12 51 13 50 15 50H84C90 50 93 47 91 44C85 34 66 29 46 30C27 31 13 40 12 53Z'
UPPER = f'<path transform="rotate(-24 12 53)" d="{UP}"/>'
CRADLE, PEARL = (62, 52, 13.5), 9.5           # the hollow in the lower shell, and the pearl in it
INSIDE = (51.5, 50, .76, 50.5, 47.5)           # Inside Out: the shell, scaled into a disc

def _mask(id, black):
    return (f'<mask id="{id}" maskUnits="userSpaceOnUse" x="0" y="0" width="100" height="100">'
            f'<rect width="100" height="100" fill="#fff"/>{black}</mask>')

def _cradle(cx=CRADLE[0], cy=CRADLE[1], r=CRADLE[2]):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#000"/>'

def _in(x, y):  # shell coordinates to Inside Out coordinates
    tx, ty, s, ox, oy = INSIDE
    return tx + s * (x - ox), ty + s * (y - oy)

def marks(ns=''):
    """Returns (masks, symbols): symbols maps a short name to the mark's inner SVG. ns prefixes mask ids."""
    m = lambda id: ns + id
    ix, iy = _in(CRADLE[0], CRADLE[1]); s = INSIDE[2]
    masks = {
        'hollow': _mask(m('mHollow'), _cradle()),
        'inside': _mask(m('mInside'), f'<g fill="#000" transform="translate({INSIDE[0]} {INSIDE[1]}) scale({s}) translate(-{INSIDE[3]} -{INSIDE[4]})">'
                                      f'<path d="{LOW}"/>{UPPER}</g><circle cx="{ix:.2f}" cy="{iy:.2f}" r="{CRADLE[2] * s:.2f}" fill="#000"/>'),
        'layers': _mask(m('mLayers'), '<g fill="#000"><rect x="0" y="66" width="100" height="2.6"/><rect x="0" y="75" width="100" height="2.6"/>'
                                      f'<rect x="0" y="83.5" width="100" height="2.6"/></g>{_cradle()}'),
        'strand': _mask(m('mStrand'), _cradle(60, 52, 13)),
    }
    p1 = 'style="fill:var(--p1)"'; p2 = 'style="fill:var(--p2)"'
    cx, cy = CRADLE[0], CRADLE[1]
    sym = {
        'open': f'<path d="{LOW}"/>{UPPER}<circle cx="62" cy="45.5" r="10" {p1}/>',  # the original, for reference
        'hollow': f'<path d="{LOW}" mask="url(#{m("mHollow")})"/>{UPPER}<circle cx="{cx}" cy="{cy}" r="{PEARL}" {p1}/>',
        'inside': f'<circle cx="51.5" cy="50" r="42" mask="url(#{m("mInside")})"/><circle cx="{ix:.2f}" cy="{iy:.2f}" r="{PEARL * s:.2f}" {p1}/>',
        'layers': f'<path d="{LOW}" mask="url(#{m("mLayers")})"/>{UPPER}<circle cx="{cx}" cy="{cy}" r="{PEARL}" {p1}/>',
        'halves': (f'<path d="{LOW}" mask="url(#{m("mHollow")})"/>{UPPER}'
                   f'<path d="M{cx - 1} {cy - PEARL} A{PEARL} {PEARL} 0 0 0 {cx - 1} {cy + PEARL} Z" {p1}/>'
                   f'<path d="M{cx + 1} {cy - PEARL} A{PEARL} {PEARL} 0 0 1 {cx + 1} {cy + PEARL} Z" {p2}/>'),
        'strand': (f'<path d="{LOW}" mask="url(#{m("mStrand")})"/>{UPPER}'
                   '<circle cx="24" cy="52.6" r="2.6"/><circle cx="32.5" cy="52.4" r="3.3"/><circle cx="41.5" cy="52.2" r="4"/>'
                   f'<circle cx="60" cy="52" r="9" {p1}/>'),
    }
    uses = {'hollow': ['hollow'], 'inside': ['inside'], 'layers': ['layers'], 'halves': ['hollow'], 'strand': ['strand'], 'open': []}
    return masks, sym, uses

def svg(name, ink, a1, a2):
    """A standalone SVG file of one mark in literal colours."""
    masks, sym, uses = marks()
    body = sym[name].replace('style="fill:var(--p1)"', f'fill="{a1}"').replace('style="fill:var(--p2)"', f'fill="{a2}"')
    defs = ''.join(masks[k] for k in uses[name])
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">' + (f'<defs>{defs}</defs>' if defs else '')
            + f'<g fill="{ink}"><g transform="translate(-1.5 1.5)">{body}</g></g></svg>')

PALETTES = {'nacre': ('#2B2230', '#C99BB0', '#B8A7C9'), 'tidepool': ('#0F4C4A', '#F2B84B', '#7FC4B0')}

if __name__ == '__main__':
    masks, sym, _ = marks()
    defs = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>' + '\n'.join(masks.values()) + '</defs>'
            + ''.join(f'<symbol id="v-{k}" viewBox="0 0 100 100"><g transform="translate(-1.5 1.5)">{v}</g></symbol>' for k, v in sym.items()) + '</svg>')
    open(D + 'variations_defs.svg', 'w').write(defs)
    for name in ('hollow', 'inside', 'layers', 'halves', 'strand'):
        for pal, cols in PALETTES.items():
            open(D + f'oyster-{name}-{pal}.svg', 'w').write(svg(name, *cols))
    print('wrote variations_defs.svg and', 5 * len(PALETTES), 'SVG exports')
