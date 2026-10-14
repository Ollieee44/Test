"""Round eight: round seven's 02 (pure outline), docked. BRD4 and VHL brought together until their facing
surfaces fit each other an even gap apart, as docked proteins do, and the same gap round the pearl. The backs
keep their traced 5T35 shapes. See proteins.docked() for how: the outlines start overlapping and are pushed
apart until every point is one gap-width (between the drawn lines' edges) from the other protein and the
pearl, smoothing lightly as they go.
"""
from proteins import DV, V

CONCEPTS = [
    ('dock', '01', 'Docked', DV(overlap=14),
     'The two proteins brought together until their facing surfaces fit each other, an even gap apart, with the same gap round the pearl. The backs keep their traced shapes.',
     'The fit itself says &ldquo;these belong together&rdquo;: two proteins made to meet, held by the SELFTAC.'),
    ('tight', '02', 'Tighter', DV(overlap=20),
     'Docked further: more of each surface reshaped to fit, the pair more compact and rounder.',
     'Closest to a single oyster shape, and to the O.'),
    ('loose', '03', 'Looser', DV(overlap=8),
     'Docked less: only the surfaces nearest each other move, so more of each protein&rsquo;s own outline survives.',
     'The most like the real structures.'),
    ('hair', '04', 'Hairline gap', DV(overlap=14, gap=1.8),
     'As 01 with a finer gap, so the pair reads as one form at a glance and two up close.',
     'Sleekest; the gap may close up below 32px.'),
    ('wide', '05', 'Wider gap', DV(overlap=14, gap=4),
     'As 01 with a wider gap, so the two halves always read apart.',
     'Holds the two halves apart at small sizes.'),
    ('pose2', '06', 'Another view', DV(overlap=14, pose=2),
     'The complex turned to another traced view, docked the same way.',
     'Different silhouettes, the same fit.'),
    ('open', '07', 'Mouth open', DV(overlap=14, lid=('target', 66, 28, -17)),
     'Docked at the hinge, but the lid tipped up a little more, so the gap opens toward the mouth on the right, as an oyster opens.',
     'Adds the oyster&rsquo;s gape without losing the fit at the hinge.'),
    ('mol', '08', 'Molecule pearl', DV(overlap=14, pearl='mol'),
     'As 01 with the SELFTAC cut into the pearl: two open rings on a linker, the gold clasp at the centre.',
     'The molecule is there for anyone who looks closely.'),
]
