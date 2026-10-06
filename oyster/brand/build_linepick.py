"""Build linepick.html: the chosen 80% pearl line fan, and its inside-out version with the drawing
enlarged to fill the disc at three rim widths (marks from linepearl.py), on the same sheet as refine.html."""
import linepearl
from build_refine import sheet

OPTS = [
 ('line-s', '01', 'Line Fan, Pearl 80%', 'The chosen mark: the fan and pearl drawn as one even line, with the 80% pearl resting in the dish.',
  'Delicate and engraved, with the ribs on show.', 'Needs 24px and up; pair it with the inside-out version for small sizes.'),
 ('io-s', '02', 'Inside Out, as it was', 'The inside-out version from the last sheet, for comparison: the drawing sits small in the middle of the disc.',
  'A round o and an app icon.', 'A wide band of solid disc round the shell makes the drawing small.'),
 ('io-s-rim7', '03', 'Inside Out, Rim 7', 'The drawing enlarged until it sits 7 units from the disc&rsquo;s edge all round (about a sixth of the radius).',
  'Comfortable: a clear solid border frames the shell, like a coin&rsquo;s rim.', 'The most border of the three, so the shell is a little smaller.'),
 ('io-s-rim5', '04', 'Inside Out, Rim 5', 'The drawing enlarged until it sits 5 units from the disc&rsquo;s edge.',
  'Balanced: the shell fills the disc and the rim still reads as a deliberate border.', 'At 16px the rim is under a pixel at the tightest point.'),
 ('io-s-rim35', '05', 'Inside Out, Rim 3.5', 'The tightest: the drawing sits 3.5 units from the disc&rsquo;s edge, about the weight of its own lines.',
  'The biggest shell and pearl, so the best of the three at small sizes. The rim matches the line weight, so the disc reads as part of the drawing.', 'With so little border the disc can look like a filled-in background rather than a frame.'),
]

if __name__ == '__main__':
    sheet(linepearl, OPTS, 'Line Fan, Inside Out', 'Line fan: inside out, tighter',
          'The 80% pearl line fan, and its inside-out version with the shell and pearl enlarged to fill the disc. The drawing is scaled to the largest size that fits, leaving an even rim of solid disc all round; three rim widths are shown, from comfortable to tight. Each is shown in both palettes, as the o of the logotype, at real pixel sizes and in one colour.',
          'Built by <code>oyster/brand/build_linepick.py</code>; SVG files are in <code>oyster/brand/</code> as <code>oyster-linepearl-io-s-rim*.svg</code> and <code>oyster-linepearl-line-s-*.svg</code>.', 'linepick.html')
