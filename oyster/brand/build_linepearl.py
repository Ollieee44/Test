"""Build linepearl.html, "Line Fan, Pearl Sizes": R7 from riffs.html at five pearl sizes and inside out
(marks from linepearl.py), on the same sheet as refine.html."""
import linepearl
from build_refine import sheet

OPTS = [
 ('line-xs', '60%', 'Small Pearl', 'The pearl at 60% of R7&rsquo;s, resting in the dish. The fan dominates.',
  'The most delicate: the shell is the subject and the pearl a quiet detail.', 'The pearl is small at 16px, under two pixels; the mark reads as a shell first.'),
 ('line-s', '80%', 'Pearl 80%', 'A little smaller than R7&rsquo;s pearl, so more of the ribs show.',
  'A good balance for print and large uses, where the line work can be enjoyed.', 'Slightly less presence for the pearl at small sizes.'),
 ('line-m', '100%', 'Pearl 100% (R7)', 'R7&rsquo;s pearl. The ribs are now spaced evenly between the fan&rsquo;s straight sides, which act as the outer two, so no rib runs alongside an edge.',
  'Balanced: shell and pearl share the attention.', 'Fine lines: the line versions need 24px and up.'),
 ('line-l', '125%', 'Pearl 125%', 'A larger pearl, rising over the lower part of the fan.',
  'The pearl leads; the ribs read as a halo round it. Holds up best of the line versions at small sizes.', 'Covers the hinge and the start of the ribs, so the fan reads more as a backdrop.'),
 ('line-xl', '150%', 'Large Pearl', 'The pearl at 150%, as big as the second reference&rsquo;s.',
  'The boldest and the closest to the reference&rsquo;s proportions; the pearl is unmistakable at any size.', 'The fan becomes a frame; the shell idea is carried by its top half.'),
 ('io-s', 'IO 80%', 'Inside Out, Pearl 80%', 'The line drawing cut out of 00&rsquo;s solid disc, with the smaller pearl.',
  'A round o for the logotype and a ready-made app icon; the delicate pearl suits the engraved look.', 'The drawing is smaller inside the disc, so it needs 24px and up.'),
 ('io-m', 'IO 100%', 'Inside Out, Pearl 100%', 'The line drawing cut out of the disc, with R7&rsquo;s pearl.',
  'Like a struck medal or a seal. Carries 00&rsquo;s inside-out idea forward with the new shell.', 'Below 24px the cut lines close up and it becomes a disc with a pearl.'),
 ('io-l', 'IO 125%', 'Inside Out, Pearl 125%', 'The line drawing cut out of the disc, with the larger pearl.',
  'The strongest inside-out version at small sizes: the pearl carries it when the lines close up.', 'The pearl covers more of the drawing.'),
]

if __name__ == '__main__':
    sheet(linepearl, OPTS, 'Line Fan, Pearl Sizes', 'Line fan: pearl sizes',
          'R7, the fan and pearl drawn as one even line, at five pearl sizes from 60% to 150%, then inside out: the line drawing cut out of 00&rsquo;s solid disc at three of those sizes. The pearl always rests in the dish and grows upwards over the fan. Each is shown in both palettes, as the o of the logotype, at real pixel sizes and in one colour.',
          'Built by <code>oyster/brand/build_linepearl.py</code>; SVG files for each option, in both palettes, are in <code>oyster/brand/</code> as <code>oyster-linepearl-*.svg</code>.', 'linepearl.html')
