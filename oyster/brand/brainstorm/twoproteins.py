"""Round twelve: two proteins first, the oyster only in their silhouette. BRD4 and VHL at (close to) their own
traced proportions, drawn as molecular surfaces (scalloped, as space-filling surfaces are), placed so each takes
half of the pearl and docked along their whole facing side at a hairline gap. No growth lines or shell shading.
See proteins.two_proteins()."""
from proteins import TP, natural

N = lambda **k: natural(62, 68, **k)
CONCEPTS = [
    ('main', '01', 'Two proteins, one pearl', TP(bump=3.2, balance=4, **N(squash=.7)),
     'BRD4 and VHL as molecular surfaces, close to their real proportions, each holding half of the pearl and docked along their whole facing side. No shell lines: the oyster is only in the shape the two make together.',
     'Proteins first: you see two molecules meeting round a pearl, and then an oyster.'),
    ('flat', '02', 'Flatter', TP(bump=3.2, balance=4, **N(squash=.6)),
     'Each protein flattened a little more along the seam, so the pair is longer and lower.',
     'More oyster in the silhouette, still clearly two proteins.'),
    ('full', '03', 'Fuller', TP(bump=3.2, balance=4, **N(squash=.82)),
     'Each protein nearer its true shape: rounder, taller halves.',
     'The most protein; the oyster is a hint.'),
    ('coarse', '04', 'Bolder surface', TP(bump=4.2, balance=4, **N(squash=.7)),
     'Larger bumps on the molecular surface.',
     'Reads as a molecular surface from further away.'),
    ('smooth', '05', 'Smooth', TP(bump=0, balance=4, **N(squash=.7)),
     '01 without the bumps: the traced outlines alone.',
     'Sleekest; compare to see what the bumps add.'),
    ('pose2', '06', 'Another view', TP(bump=3.2, balance=4, pose=2, **N(squash=.7, pose=2)),
     'The two proteins from another of the traced views of the complex.',
     'Different silhouettes, the same idea.'),
    ('contour', '07', 'With a contour', TP(bump=3.2, balance=4, contour=True, **N(squash=.7)),
     '01 with one real surface contour from the trace inside each protein, as a quiet line.',
     'A touch of depth from the structure itself, not from a shell.'),
    ('level', '08', 'Level', TP(bump=3.2, balance=4, angle=0, **N(squash=.7)),
     '01 not turned: the seam runs level, lid above and cup below.',
     'The calmest; compare with the diagonal.'),
]
