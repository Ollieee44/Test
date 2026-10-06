"""Build riffs.html, "Fan and Pearl, Riffs": variations on B1 and B3 from refs.html (marks from
riffs.py), on the same sheet as refine.html."""
import riffs
from build_refine import sheet

OPTS = [
 ('ribbed', 'B1', 'Fan and Pearl', 'The chosen starting point: the fan with its ribs, the dish and the big pearl.', 'The closest to the reference and the most instantly read.', 'A scallop, close to the Shell plc logo.'),
 ('smooth', 'B3', 'Fan and Pearl, Smooth', 'The other starting point: the same composition with a smooth fan.', 'Calm, and further from the scallop.', 'Can read as a hood or a hat.'),
 ('bold', 'R1', 'Bold Ribs', 'B1 with five deep grooves instead of nine fine ones.',
  'The clearest ribbed version at small sizes: the grooves survive at 16px.', 'Still a scallop, so the Shell plc caution stays.'),
 ('strands', 'R2', 'Pearl Strands', 'Each rib is a string of small pearls growing towards the rim: the house&rsquo;s pearl-strand linker motif, so the fan is literally built from strands of pearls.',
  'Ties the shell to the science and the rest of the brand. The strands read as ribs at a glance and as pearls up close, and they are not a scallop&rsquo;s solid ribs.',
  'The smallest pearls drop out below 32px, where it falls back to B3.'),
 ('growth', 'R3', 'Growth Lines', 'The fan&rsquo;s texture as an oyster&rsquo;s concentric growth lines instead of a scallop&rsquo;s ribs.',
  'Keeps B1&rsquo;s texture while stepping clearly away from the Shell logo. Echoes the nacre layers that build a pearl.', 'The lines can suggest a rainbow or a sunrise.'),
 ('frilled', 'R4', 'Oyster Lip', 'B3 with a gently uneven edge, as an oyster&rsquo;s is, not a scallop&rsquo;s even curve.',
  'The quietest way to make B3 an oyster rather than a generic shell.', 'Subtle: at small sizes it is B3.'),
 ('clasped', 'R5', 'Clasped Pearl', 'B3&rsquo;s pearl as two halves held by a band in the clasp colour, the house&rsquo;s hero motif.',
  'Tells the SELFTAC story, two halves made one, without adding anything to the shell.', 'The band disappears below 32px, back to a plain pearl.'),
 ('rays', 'R6', 'Rays', 'B1&rsquo;s ribs start just outside the pearl and stop short of the rim, so they read as light coming off the pearl as much as the ribs of a shell.',
  'Puts the pearl at the centre of the story, glowing. Lighter than B1 and further from the Shell logo, as the ribs never reach the edge.', 'Fine lines: it needs 24px and up.'),
 ('line', 'R7', 'Line', 'B1 drawn as one even line, with a solid pearl.',
  'Elegant and engraved, good for print, foil and large uses, and a natural companion to a solid version.', 'Too fine for favicons; pair it with B1 or B3 for small sizes.'),
 ('disc', 'R8', 'Inside Out Fan', 'B3 cut out of 00&rsquo;s disc, so the mark keeps a round o for the logotype.',
  'The best fit as the o in the logotype, and a ready-made app icon. Carries 00&rsquo;s inside-out idea forward.', 'The shell is smaller inside the disc, so it needs 24px and up.'),
]

if __name__ == '__main__':
    sheet(riffs, OPTS, 'Fan and Pearl Riffs', 'Fan and pearl: riffs',
          'Eight variations on B1 and B3, the front-on fan, dish and pearl from the second reference. Each changes one idea: what the ribs are made of, the fan&rsquo;s edge, the pearl, or how the mark sits as the o of the logotype. B1 and B3 are shown first. Each option is shown in both palettes, as the o of the logotype, at real pixel sizes and in one colour.',
          'Built by <code>oyster/brand/build_riffs.py</code>; SVG files for each option, in both palettes, are in <code>oyster/brand/</code> as <code>oyster-riffs-*.svg</code>.', 'riffs.html')
