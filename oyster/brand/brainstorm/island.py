"""Round nineteen: round seventeen's 05 (Model: toon shading and contour rings, in the 3D story's colours) with a small
ring in the left-hand part of the upper protein (BRD4), like a peak on a contour map. Clasped only.
See proteins._island()."""
from nacre import T

def C(**k):
    fn = T('model', **k); fn.clasped_only = True; return fn

CONCEPTS = [
    ('model', '01', 'Model, as it was', C(),
     'Round seventeen&rsquo;s 05 for reference: toon shading and contour rings.', ''),
    ('small', '02', 'Small ring', C(island=dict(r=1.6)),
     'A small, slightly wobbly ring at the deepest point of BRD4&rsquo;s left-hand lobe.',
     'A quiet peak, like the top of a hill on a contour map.'),
    ('medium', '03', 'Larger ring', C(island=dict(r=2.4)),
     'The same ring a little larger.',
     'Reads at smaller sizes.'),
    ('double', '04', 'Two rings', C(island=dict(r=1.4, count=2)),
     'Two concentric rings at the same point.',
     'More clearly a contour peak.'),
    ('contour', '05', 'Traced contour', C(island=(2.2, 1)),
     'A ring traced from the protein&rsquo;s own depth at that point, so it follows the lobe&rsquo;s shape.',
     'Matches the other contour lines exactly; longer than round.'),
]
