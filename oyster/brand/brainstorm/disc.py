"""Round eighteen: round seventeen's 08 (Akoya) and 09 (Rose mother-of-pearl) on a near-black filled disc, as the earlier
Inside Out logo sat in its disc. Clasped only. Variations on how the mark sits in the disc: roomy, tight, breaking out
past the edge, and with a fine pearl ring inside the rim."""
from nacre import T

DISC = '#1B1720'

def on_disc(fn, scale=.78, ring=False, clip=True):
    """The mark scaled about the centre on a near-black disc. clip=False lets the mark break out past the rim."""
    def g(ns, split=False):
        inner = fn(ns, False)
        m = f'<g transform="translate({50 - 50 * scale:.2f} {50 - 50 * scale:.2f}) scale({scale})">{inner}</g>'
        rim = f'<circle cx="50" cy="50" r="44.5" fill="none" stroke="#E9DCE4" stroke-width=".8" opacity=".7"/>' if ring else ''
        if clip:
            m = f'<clipPath id="{ns}dc"><circle cx="50" cy="50" r="48"/></clipPath><g clip-path="url(#{ns}dc)">{m}</g>'
        return f'<circle cx="50" cy="50" r="48" fill="{DISC}"/>{rim}{m}'
    g.clasped_only = True
    return g

AK, RO = T('nacre:akoya'), T('nacre:rose')
CONCEPTS = [
    ('', 'Akoya on the disc', 'Round seventeen&rsquo;s 08: white and rose nacre with silver bands, an Akoya pearl.', None),
    ('ak-roomy', 'A1', 'Roomy', on_disc(AK, .74), 'The mark centred with clear space round it.', 'Calm, like a cameo.'),
    ('ak-tight', 'A2', 'Tight', on_disc(AK, .9), 'The mark filling the disc, its lobes close to the rim.', 'Bolder; more mark, less disc.'),
    ('ak-break', 'A3', 'Breaking out', on_disc(AK, 1.04, clip=False), 'The mark larger than the disc, its lobes pushing past the edge.', 'The most dynamic; the oyster escapes its frame.'),
    ('ak-ring', 'A4', 'Ringed', on_disc(AK, .74, ring=True), 'Roomy, with a fine pearl ring inside the rim.', 'Jewellery-like; a pearl set in a mount.'),
    ('', 'Rose mother-of-pearl on the disc', 'Round seventeen&rsquo;s 09: rose, lilac and mint bands, a pearl with a green overtone.', None),
    ('ro-roomy', 'R1', 'Roomy', on_disc(RO, .74), 'The mark centred with clear space round it.', 'The iridescence glows against the dark.'),
    ('ro-tight', 'R2', 'Tight', on_disc(RO, .9), 'The mark filling the disc.', 'Bolder; more mark, less disc.'),
    ('ro-break', 'R3', 'Breaking out', on_disc(RO, 1.04, clip=False), 'The mark larger than the disc, its lobes pushing past the edge.', 'The most dynamic.'),
    ('ro-ring', 'R4', 'Ringed', on_disc(RO, .74, ring=True), 'Roomy, with a fine pearl ring inside the rim.', 'A pearl set in a mount.'),
]
