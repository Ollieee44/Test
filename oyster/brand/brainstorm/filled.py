"""Round fourteen: round thirteen's 01 (blobby) filled in, in the 3D story's protein colours (BRD4 pink or gold,
VHL lilac or mint) with an ink outline, and depth added as on the 3D models: contour rings, toon shading, a soft
gradient, or rings and shading together. See proteins._filled()."""
from proteins import TP
from blobby import B1, N

F = lambda st: TP(bump=3.2, balance=4, blob=B1, fill=st, **N)
CONCEPTS = [
    ('flat', '01', 'Flat fill', F('flat'),
     'The two proteins filled in the 3D story&rsquo;s colours, BRD4 and VHL, with the ink outline.',
     'The simplest: colour alone tells the two proteins apart.'),
    ('rings', '02', 'Contour rings', F('rings'),
     'Contour rings inside each protein at even depths, in the ring colour, as on the 3D models.',
     'The 3D story&rsquo;s signature texture, so the mark and the story match.'),
    ('toon', '03', 'Toon shading', F('toon'),
     'A shade band on the side away from the light and a lit band on the near side, from the shape itself.',
     'Reads as 3D at once, with flat colour only.'),
    ('soft', '04', 'Soft gradient', F('soft'),
     'A soft gradient across each protein, lit from the top left.',
     'The most rendered; smooth and modern.'),
    ('model', '05', 'Model', F('model'),
     'Toon shading and contour rings together: the closest to the 3D models on the site.',
     'The full 3D-story look in a mark.'),
    ('softrings', '06', 'Soft, with rings', F('softrings'),
     'The soft gradient with the contour rings over it.',
     'Rich, for large uses such as the intro or print.'),
]
