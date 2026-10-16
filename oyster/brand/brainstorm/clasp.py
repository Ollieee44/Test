"""Round twenty-one: round nineteen's 05 (Model with the traced ring) with other ways for the pearl to tell the SELFTAC
story: two halves that clasp back together, the clasp in gold as on the site. Clasped only. See proteins.pearl_alt()."""
from nacre import T

def C(pearl=None):
    fn = T('model', island=(2.2, 1), **({'pearl': pearl} if pearl else {})); fn.clasped_only = True; return fn

CONCEPTS = [
    ('ref', '01', '05, as it was', C(),
     'Round nineteen&rsquo;s 05 for reference: the pearl split along the seam, the linker cut out of it as negative space.', ''),
    ('bridge', '02', 'Gold bridge', C('bridge'),
     'The two halves held a little apart, joined by a solid gold bond across the gap: the clasp drawn in, not cut out.',
     'The clasp becomes the one gold thing in the mark, as it is on the site.'),
    ('glow', '03', 'Glowing clasp', C('glow'),
     'As 02, with the soft glow the site&rsquo;s clasp has while it is closed.',
     'Says &ldquo;the bond is active&rdquo;; warmer, more alive.'),
    ('twotone', '04', 'Two halves, two tones', C('twotone'),
     'As 02, but each half of the pearl in its own tone, one per protein, so they read as two different molecules.',
     'Makes the heterobifunctional point: two different halves, one clasp.'),
    ('clasp', '05', 'Clasp glyph', C('clasp'),
     'The site&rsquo;s clasp glyph as the pearl: two gold pearls, one against each protein, joined by a thick bond.',
     'The most on-brand; ties the mark to every section label on the site.'),
    ('strand', '06', 'Pearl strand', C('strand'),
     'The site&rsquo;s pearl strand running through the pocket from one protein to the other, the two gold clasp pearls at its middle.',
     'Shows each half reaching into its protein; busiest at small sizes.'),
    ('jigsaw', '07', 'Knob and socket', C('jigsaw'),
     'The halves joined by a knob on one and a socket in the other, like jigsaw pieces: they fit only one way, and click together.',
     'Says self-assembly: the halves are made to find each other.'),
    ('venn', '08', 'Overlap', C('venn'),
     'Two pearls, one per protein, overlapping in the middle; the overlap is gold.',
     'The clasp is where the halves meet: simple and readable small.'),
]
