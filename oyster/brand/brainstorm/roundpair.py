"""Round eleven: one round form. A circle split by a gentle S-shaped seam through the pearl, the right-hand gap
closed, so the only opening is the hairline seam. Each half's outer edge carries the broad lobes of its own
traced protein (BRD4 above, VHL below, from PDB 5T35), so the halves differ and read as proteins while the whole
reads as round. Shading on the outer surface, the diagonal, and the split pearl with its linker, as before.
See proteins.circle_pair()."""
from proteins import CP

CONCEPTS = [
    ('main', '01', 'Round, protein lobes', CP(amp=.2, lobes=10),
     'The pair closed into one round form: the gap on the right is gone, and the only opening is the hairline seam. Each half&rsquo;s outer edge has the lobes of its own protein, BRD4 above and VHL below.',
     'Round enough to read as one oyster and as an O; lumpy enough that each half is plainly a protein.'),
    ('subtle', '02', 'Subtler lobes', CP(amp=.14, lobes=10),
     'The same with gentler lobes: closer to a circle.',
     'The calmest and most O-like.'),
    ('strong', '03', 'Stronger lobes', CP(amp=.26, lobes=10),
     'The protein lobes pushed further, so each half&rsquo;s outline varies more.',
     'The most clearly protein; the circle is felt rather than drawn.'),
    ('fine', '04', 'Finer surface', CP(amp=.2, lobes=14),
     'More of each protein&rsquo;s surface detail kept: smaller bumps on top of the lobes.',
     'More like a real protein surface; a little busier.'),
    ('wave', '05', 'Wavier seam', CP(amp=.2, lobes=14, wave=7),
     'The seam&rsquo;s S deepened, so the two halves interlock more, as docked proteins do.',
     'The interface itself becomes part of the story.'),
    ('pose2', '06', 'Another view', CP(amp=.2, lobes=10, pose=2),
     'The lobes taken from another of the traced views of the complex.',
     'Different silhouettes, the same idea.'),
    ('turned', '07', 'Turned profiles', CP(amp=.22, lobes=12, phase=(.3, .6)),
     'Each protein&rsquo;s profile turned before it is laid on its half, so different lobes land at the top and bottom.',
     'Shows how much the character changes with where the lobes fall.'),
    ('plain', '08', 'No shading', CP(amp=.2, lobes=10, shade=False),
     '01 as pure outline, without the shading lines.',
     'The sleekest; the best at small sizes.'),
]
