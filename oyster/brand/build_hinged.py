"""Build hinged.html, "Two Valves, One Hinge": open-oyster marks drawn from the client's two
references (marks from hinged.py), on the same sheet as refine.html."""
import hinged
from build_refine import sheet

OPTS = [
 ('inside', '00', 'Inside Out', 'The live mark, for reference.', 'Already the o of the logotype, the favicon and the header.', 'Reads as a makeup compact.'),
 ('frilled2', '&middot;', 'Open Oyster, Frilled', 'The last round&rsquo;s pick (02, with the eye read fixed), for comparison.',
  'Clearly open, with frilled lips and the pearl on the front lip.', 'Generic oval valves: it says shell more than it says oyster.'),
 ('upright', '01', 'Upright', 'From the second image: the upper valve stands up behind like a backdrop, the lower valve is a shallow dish, and a big pearl sits at the front. Both valves are the oyster&rsquo;s teardrop from the painting, tapering to one shared hinge.',
  'The clearest picture of two shells coming together around a pearl, and the most like a classic pearl-in-shell image, without the scallop.',
  'Tall and narrow, so as the o it is a little upright beside the letters.'),
 ('book', '02', 'Open Book', 'The two valves as near mirror images, opening from one beak like a book. The pearl sits right where they meet.',
  'The most direct picture of the SELFTAC idea: two halves, one hinge, the pearl where they come together.',
  'The pearl sits high and central, so the mark is balanced but less grounded.'),
 ('cup', '03', 'Deep Cup', 'From the painting: the lower valve is deep and seen from above, with a thick rim at the front, and the pearl rests on its front lip. The upper valve is smaller and further back, still joined at the hinge.',
  'The most like a real oyster: the painting&rsquo;s deep cup and chunky rim, with the second valve keeping the two-halves story.',
  'The upper valve is the smaller partner, so the two halves are less equal.'),
 ('bigpearl', '04', 'Big Pearl', 'The second image&rsquo;s proportions: the pearl as big as it can be, the upper valve a solid backdrop with one growth line, the dish a thin sliver in front.',
  'Bold and simple, the strongest at small sizes, with the pearl doing the talking.',
  'The solid upper valve can read as a leaf or a flame; the dish is thin below 24px.'),
]

if __name__ == '__main__':
    sheet(hinged, OPTS, 'Two Valves, One Hinge', 'Two valves, one hinge',
          'Open-oyster marks drawn from the two references: the oyster&rsquo;s own teardrop shape, deep cup and chunky rim from the painting, and the composition from the second image, an upper valve standing up behind and a big pearl at the front. A single half shell loses the two shells coming together, so every option keeps both valves, meeting at one hinge. There are no scallop ribs, which read as a scallop. Each pearl rests on its rim, not in the middle of an opening, so none reads as an eye.',
          'Built by <code>oyster/brand/build_hinged.py</code>; SVG files for each option, in both palettes, are in <code>oyster/brand/</code> as <code>oyster-hinged-*.svg</code>.', 'hinged.html')
