"""Build openpick.html: the two chosen open-oyster marks (02 and 05 from threequarter.html), before and
after the fix for the eye read, on the same sheet as refine.html."""
import threequarter
from build_refine import sheet

OPTS = [
 ('frilled', '02', 'Frilled, as it was', 'The pearl sat in the middle of an almond-shaped opening, which in one colour read as an eye.',
  'Unmistakably an oyster, open and offering its pearl.', 'A round pearl centred in an almond is a pupil in an eye, most of all in one colour.'),
 ('frilled2', '02', 'Frilled, fixed', 'The cup&rsquo;s opening is pulled back and tipped, and the pearl moves forward onto the front lip, off-centre, so it breaks the cup&rsquo;s outline instead of sitting inside it.',
  'Reads as a pearl being offered, in colour and in one colour. The pearl is a little larger, which helps at small sizes.',
  'The pearl now reaches the right-hand edge, so it sits closer to the y in the logotype.'),
 ('low', '05', 'Lower angle, as it was', 'The same eye read, with the pearl centred in a thinner almond.',
  'The most open and generous pose.', 'The thinner opening made the eye read stronger.'),
 ('low2', '05', 'Lower angle, fixed', 'The same fix: the opening pulled back, the pearl forward and to the right on the front lip.',
  'The pearl sits proud at the front of a wide-open shell, the clearest &ldquo;offering&rdquo; of the two.',
  'Wider than it is tall, so as the o it sits a little low and wide beside the letters.'),
]

if __name__ == '__main__':
    sheet(threequarter, OPTS, 'Open Oyster Picks', 'Open oyster: 02 and 05',
          'The two chosen open-oyster marks, each shown as it was and with the eye read fixed. The fix is the same for both: the cup&rsquo;s opening moves back and loses its symmetric almond shape, and the pearl moves forward onto the front lip, off-centre, so it breaks the cup&rsquo;s outline instead of sitting in the middle of it like a pupil. Each is shown in both palettes, as the o of the logotype, at real pixel sizes and in one colour.',
          'Built by <code>oyster/brand/build_openpick.py</code>; SVG files are in <code>oyster/brand/</code> as <code>oyster-threequarter-frilled2-*.svg</code> and <code>oyster-threequarter-low2-*.svg</code>.', 'openpick.html')
