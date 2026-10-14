"""Round sixteen: round fifteen's outlines with a few big, deep undulations instead of many lobes. Each protein's
outline is pushed in and out along its normal in exactly n smooth waves (fading out near the seam and the pearl
so the fit stays exact), then re-docked. See proteins.undulate()."""
from proteins import TP
from blobby import B1, N

U = lambda waves, fill='flat', **k: TP(bump=0, balance=4, blob=B1, fill=fill, waves=waves, **N, **k)
W5 = ((5, 5, .1, 1), (5, 5, .4, 1))
CONCEPTS = [
    ('five', '01', 'Five deep waves', U(W5),
     'Each protein&rsquo;s outer edge in five big, deep undulations; the seam and the pearl&rsquo;s pocket stay smooth and fitted.',
     'Bold and simple: a few clear lobes per protein, readable at any size.'),
    ('four', '02', 'Four broad waves', U(((4, 4, 0, 1), (4, 4, .3, 1))),
     'Four broad, gentler undulations.',
     'The calmest; closest to a smooth pebble.'),
    ('deep', '03', 'Deepest', U(((5, 6, .1, 1), (5, 6, .4, 1))),
     'Five waves, pushed deeper.',
     'The most dramatic lobes.'),
    ('lobed', '04', 'Rounded lobes', U(((5, 5, .1, 1.8), (5, 5, .4, 1.8))),
     'Five waves shaped as round lobes with tighter dips between them.',
     'More like protein domains than a wave.'),
    ('mixed', '05', 'Mixed', U(((4, 5, .1, 1.4), (6, 4, .3, 1.4))),
     'BRD4 with four big lobes, VHL with six smaller ones, so the two proteins differ.',
     'Two distinct characters.'),
    ('ref', '06', 'With lumps', U(W5, lumps=4, tint=True),
     '01 with round fifteen&rsquo;s soft lumps inside and the outline in each protein&rsquo;s own darker shade.',
     'The illustrated look of your reference, with the bigger waves.'),
    ('toon', '07', 'Toon shading', U(W5, fill='toon'),
     '01 with toon shading: a shade band on the far side, a lit band on the near.',
     'Crisp 3D in flat colour.'),
]
