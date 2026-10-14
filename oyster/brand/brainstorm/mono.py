"""Round twenty: round nineteen's 05 (Model, with a traced-contour ring in BRD4's left-hand lobe) in one colour, for laying
over photographs and other images. Every version is drawn in currentColor on a clear ground, so it can be set in white
over a dark image or black over a light one. Clasped only. See proteins._mono()."""
from nacre import T

def M(style):
    fn = T('mono:' + style, island=(2.2, 1)); fn.clasped_only = True; fn.overlay = True; return fn

def badge(style, scale=.74):
    """The mark cut out of a solid disc, so the image shows through the mark: a badge for busy images."""
    fn = M(style)
    def g(ns, split=False):
        inner = fn(ns, False)
        return (f'<mask id="{ns}dm" maskUnits="userSpaceOnUse" x="0" y="0" width="100" height="100"><rect width="100" height="100" fill="#fff"/>'
                f'<g style="color:#000" transform="translate({50 - 50 * scale:.2f} {50 - 50 * scale:.2f}) scale({scale})">{inner}</g></mask>'
                f'<circle cx="50" cy="50" r="48" fill="currentColor" mask="url(#{ns}dm)"/>')
    g.clasped_only = True; g.overlay = True; g.kw = fn.kw
    return g

CONCEPTS = [
    ('line', '01', 'Line', M('line'),
     'The two outlines and the split pearl, nothing else.',
     'The lightest; sits quietly over an image.'),
    ('contour', '02', 'Contour lines', M('contour'),
     'The outlines with the contour rings and the traced ring in BRD4 as hairlines, like a topographic map.',
     'Keeps the 3D-model story; best at larger sizes.'),
    ('solid', '03', 'Solid', M('solid'),
     'Both proteins as solid shapes, the traced ring cut out of BRD4, the seam and pearl pocket left clear.',
     'The boldest and most legible at small sizes.'),
    ('cut', '04', 'Solid, rings cut out', M('cut'),
     'Solid shapes with the contour rings cut through them, so the image shows through in lines.',
     'Solid weight with the contour detail; the image lives inside the mark.'),
    ('duo', '05', 'Solid and line', M('duo'),
     'BRD4 solid with its ring cut out, VHL in outline: two different proteins, told apart by weight.',
     'Says &ldquo;two different proteins&rdquo; without colour.'),
    ('badge', '06', 'Badge', badge('solid'),
     'A solid disc with the solid mark cut out of it, so the image shows through the proteins and the pearl.',
     'A stamp for busy images, and a ready-made app icon.'),
]
