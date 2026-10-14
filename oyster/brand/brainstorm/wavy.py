"""Round fifteen: round fourteen with wavy outlines, after the illustrated proteins the client shared: big soft lobes
along the edge (bumps set on the outline, further apart, and the union blurred so the notches round into waves),
optional soft lumps inside (merged blobs filled a shade lighter and darker) and an outline tinted from the
protein's own colour. See proteins.molecular(soften=, spacing=, sink=) and proteins._lumps()."""
from proteins import TP
from blobby import B1, N

W = dict(bump=6.5, spacing=1.8, sink=.2, soften=1.3)
V = lambda fill='flat', **k: TP(balance=4, blob=B1, fill=fill, **N, **{**W, **k})
CONCEPTS = [
    ('wavy', '01', 'Wavy', V(),
     'The outlines redrawn with big, soft lobes and rounded dips between them, instead of fine bumps: wavy, not jaggy.',
     'Friendlier and bolder; holds up much better at small sizes.'),
    ('wavier', '02', 'Wavier', V(bump=7.5, spacing=1.9, sink=.3, soften=1.5),
     'Fewer, larger lobes.',
     'The most cloud-like, closest to the reference.'),
    ('gentle', '03', 'Gentle waves', V(bump=4.5, spacing=1.6, sink=.1, soften=.8),
     'Smaller, more frequent lobes.',
     'Between round fourteen&rsquo;s surface and 01.'),
    ('lumps', '04', 'With lumps', V(lumps=4),
     'Soft lumps inside each protein, a shade lighter and darker, as in the reference.',
     'Gives the proteins bulk without lines.'),
    ('ref', '05', 'Like the reference', V(lumps=4, tint=True),
     'Lumps inside and the outline in a darker shade of each protein&rsquo;s own colour, not ink.',
     'The closest to the illustration you shared; softer and more illustrative.'),
    ('toon', '06', 'Wavy, toon shading', V('toon'),
     'The wavy outlines with round fourteen&rsquo;s toon shading.',
     'Crisp 3D in flat colour.'),
    ('rings', '07', 'Wavy, contour rings', V('rings'),
     'The wavy outlines with the 3D story&rsquo;s contour rings.',
     'Ties the mark to the 3D models.'),
]
