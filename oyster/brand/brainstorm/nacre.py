"""Round seventeen: round sixteen's 02 (four broad waves) with the textures and shading of earlier rounds, and a set of
mother-of-pearl colourways: the proteins as iridescent nacre (colour bands, a fibrous sheen from turbulence, highlight
and shade) and the pearl photographic (body gradient, overtone, rim, specular). See proteins._filled(),
proteins._nacre_fill() and proteins.NACRE."""
from proteins import TP
from blobby import B1, N

W4 = ((4, 4, 0, 1), (4, 4, .3, 1))
T = lambda fill, **k: TP(bump=0, balance=4, blob=B1, fill=fill, waves=W4, **N, **k)
CONCEPTS = [
    ('', 'Textures and shading', 'Round sixteen&rsquo;s 02, four broad waves, in the 3D story&rsquo;s colours, with each depth treatment from earlier rounds.', None),
    ('flat', '01', 'Flat', T('flat'), 'Flat fill and ink outline, for reference.', 'The base.'),
    ('rings', '02', 'Contour rings', T('rings'), 'Rings at even depths inside each protein, as on the 3D models.', 'Matches the 3D story.'),
    ('toon', '03', 'Toon shading', T('toon'), 'A shade band away from the light, a lit band toward it.', 'Crisp 3D in flat colour.'),
    ('soft', '04', 'Soft gradient', T('soft'), 'A soft gradient lit from the top left.', 'Smooth and rendered.'),
    ('model', '05', 'Model', T('model'), 'Toon shading with contour rings: the 3D models&rsquo; look.', 'The full 3D-story look.'),
    ('softrings', '06', 'Soft, with rings', T('softrings'), 'The soft gradient with rings over it.', 'Rich, for large uses.'),
    ('lumps', '07', 'Lumps, tinted outline', T('flat', lumps=4, tint=True), 'Soft lumps inside and an outline in each protein&rsquo;s own darker shade, as in your reference.', 'Illustrative and soft.'),
    ('', 'Mother-of-pearl colourways', 'The proteins as iridescent nacre, each banded at its own angle with a fibrous sheen, a highlight and shade; the pearl photographic, with its overtone and highlight. Named after real pearls. These colours are fixed, so they look the same on either palette.', None),
    ('akoya', '08', 'Akoya', T('nacre:akoya'), 'White and rose with cool silver bands, an Akoya pearl with a pink overtone.', 'Classic and clean.'),
    ('rose', '09', 'Rose mother-of-pearl', T('nacre:rose'), 'Rose, lilac and mint bands, a pearl with a green overtone.', 'The most iridescent of the light ones.'),
    ('southsea', '10', 'Golden South Sea', T('nacre:southsea'), 'Warm gold and cream, a golden pearl.', 'Warm and premium; close to the clasp gold.'),
    ('tahitian', '11', 'Tahitian', T('nacre:tahitian'), 'Dark slate with peacock green and aubergine, a dark pearl with a green overtone.', 'Dramatic; strongest on light backgrounds.'),
    ('abalone', '12', 'Abalone', T('nacre:abalone'), 'Blue, teal and violet bands, a pale pearl.', 'Ties in with the Tidepool teal.'),
]
