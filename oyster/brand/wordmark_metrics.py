"""Sizing for a mark that stands in for the O of the wordmark.

Glyph metrics (em) are measured from the outlines of the Google Fonts files: the letter o's ink top
and bottom (round letters overshoot the x-height and the baseline) and its side bearings.
Newsreader's x-height grows with its optical size axis, so the wordmark is always set at
opsz 72 (font-variation-settings) and these are the opsz 72 values.
"""
FONT = {
    'newsreader-500': dict(top=.5230, bot=.0110, lsb=.0338, rsb=.0336),
    'newsreader-400': dict(top=.5220, bot=.0100, lsb=.0365, rsb=.0365),
    'archivo-700': dict(top=.5380, bot=.0120, lsb=.0380, rsb=.0380),
    'archivo-600': dict(top=.5380, bot=.0120, lsb=.0390, rsb=.0390),
}

def omark(ink, face):
    """ink: the mark's ink bounds (x0, y0, x1, y1) in its 0-100 viewBox. Returns size, vertical-align,
    margin-left and margin-right in em, so the mark's ink runs from the o's bottom overshoot to its top."""
    x0, y0, x1, y1 = ink; f = FONT[face]
    size = (f['top'] + f['bot']) * 100 / (y1 - y0)
    va = -f['bot'] - (100 - y1) / 100 * size
    return size, va, -x0 / 100 * size + f['lsb'], -(100 - x1) / 100 * size + f['rsb']

def style(ink, face):
    s, va, ml, mr = omark(ink, face)
    return f'width:{s:.4f}em;height:{s:.4f}em;vertical-align:{va:.4f}em;margin:0 {mr:.4f}em 0 {ml:.4f}em'

if __name__ == '__main__':
    for face in FONT: print(face, style((8, 9.5, 92, 93.5), face))
