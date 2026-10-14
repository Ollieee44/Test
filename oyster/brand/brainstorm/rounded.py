"""Round ten: round nine's 02 (diagonal, shaded) rounder at the right, with the pearl split along the shell's
seam so each half sits by its protein, held by a short, thick linker cut out of it. See proteins.textured2()."""
from proteins import TV2

CONCEPTS = [
    ('main', '01', 'Rounded, linker pearl', TV2(rnd=.8),
     'Round nine&rsquo;s 02 with its right side rounded off. The pearl is split along the same line as the shell, so one half sits by each protein, and the halves are held by a short, thick linker cut out of the pearl.',
     'The two halves of the SELFTAC, each by its own protein, held by the linker: the whole mechanism in the pearl.'),
    ('rounder', '02', 'Rounder', TV2(rnd=1.0),
     'As 01, rounded further: the right-hand ends become soft lobes.',
     'The softest silhouette; closest to a pebble-smooth oyster.'),
    ('lighter', '03', 'Lightly rounded', TV2(rnd=.5),
     'As 01, rounded less, so more of the traced outline survives at the right.',
     'More protein-like; the right ends keep a little edge.'),
    ('stubby', '04', 'Stubbier linker', TV2(rnd=.8, link=(.56, .56)),
     'A shorter, fatter linker: almost a rounded square cut through the split.',
     'The boldest linker, the first detail to read at small sizes.'),
    ('long', '05', 'Longer linker', TV2(rnd=.8, link=(.9, .42)),
     'A longer linker reaching most of the way across each half.',
     'Reads more clearly as a bar joining the two halves.'),
    ('wide', '06', 'Wider split', TV2(rnd=.8, seam=.16),
     'The split between the pearl&rsquo;s halves widened, so the two halves read apart, held only by the linker.',
     'Most clearly two halves; the linker is what holds them.'),
]
