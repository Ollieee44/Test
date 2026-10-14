"""Round thirteen: round twelve's 02 (flatter), blobbier. Each protein's own traced lobes are amplified (measured
against its own overall oval, so only the local bulges grow), with clefts pressed into its back and, in some,
a wider domain at one end; then docked as before. See proteins.exaggerate()."""
from proteins import TP, natural

N = natural(62, 68, squash=.6)
B1 = dict(lid=dict(amp=1.2, clefts=[(-115, .16, 16)]), cup=dict(amp=1.2, clefts=[(70, .16, 16)]))
B2 = dict(lid=dict(amp=2.0, clefts=[(-125, .14, 14), (-55, .12, 12)]), cup=dict(amp=2.0, clefts=[(55, .14, 14), (125, .12, 12)]))
B3 = dict(lid=dict(amp=1.0, clefts=[(-100, .26, 13)]), cup=dict(amp=1.0, clefts=[(80, .26, 13)]))
B4 = dict(lid=dict(amp=1.2, clefts=[(-90, .14, 14)], bulges=[(-160, .18, 24)]), cup=dict(amp=1.2, clefts=[(110, .14, 14)], bulges=[(20, .2, 26)]))
B5 = dict(lid=B2['lid'], cup=B4['cup'])

CONCEPTS = [
    ('blob', '01', 'Blobby', TP(bump=3.2, balance=4, blob=B1, **N),
     'Round twelve&rsquo;s 02 with each protein&rsquo;s own lobes amplified and one cleft pressed into its back.',
     'Still the same two proteins, now unmistakably lumpy, not a semicircle.'),
    ('lobed', '02', 'More lobed', TP(bump=3.2, balance=4, blob=B2, **N),
     'The lobes pushed further, with two clefts in each protein.',
     'The most like a real protein surface: domains and grooves.'),
    ('cleft', '03', 'Deep clefts', TP(bump=3.2, balance=4, blob=B3, **N),
     'One deep cleft in each, like a binding groove.',
     'A strong, simple indent per protein; reads well small.'),
    ('domain', '04', 'Wider domains', TP(bump=3.2, balance=4, blob=B4, **N),
     'A wider domain swelling at one end of each protein, with a cleft beside it.',
     'More variety of width along each half.'),
    ('mixed', '05', 'Mixed', TP(bump=3.2, balance=4, blob=B5, **N),
     'BRD4 lobed as in 02, VHL with the wider domain of 04, so the two halves differ more.',
     'Two clearly different proteins.'),
    ('smooth', '06', 'Smooth outline', TP(bump=0, balance=4, blob=B2, **N),
     '02 without the molecular bumps: the blobby outline alone.',
     'The small-size companion.'),
]
