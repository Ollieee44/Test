"""Build threequarter.html, "Open Oyster": the open clamshell seen from a slight angle (marks from
threequarter.py), on the same sheet as refine.html."""
import threequarter
from build_refine import sheet

OPTS = [
 ('inside', '00', 'Inside Out', 'The adopted mark, the base for this round: a disc, a straight-lipped lid hinged open, and the pearl in its cradle.',
  'A strong silhouette, and already the o of the logotype, the favicon and the header.',
  'Seen side-on with a flat lid in a perfect circle, it reads as a makeup compact.'),
 ('open', '01', 'Open Oyster', 'The open shell from a slight angle: the lower valve is a bowl we look down into, the upper valve tips back from the hinge on the left so we see its hollow inside, and the pearl rests in the cup in 00&rsquo;s cradle.',
  'Depth is what a compact lacks: both valves are visibly hollow, so it reads as a shell straight away. Simple enough for small sizes.',
  'With smooth edges it can also suggest a ring box or a bowl; the frills in 02 settle that.'),
 ('frilled', '02', 'Open Oyster, Frilled', '01 with ruffled, uneven lips on both valves, as a real oyster has.',
  'Unmistakably an oyster, open and offering its pearl. The frills give it warmth without fuss.',
  'The frills merge into a rough edge below 32px, which still reads as a shell. In one colour the pearl in its cup can read as an eye; a thicker cradle ring or the pearl&rsquo;s highlight would fix that.'),
 ('backed', '03', 'Shell Behind', 'The upper valve stands up behind, seen from the outside: solid, with growth lines. Only the lower cup is open, holding the pearl.',
  'The solid back valve gives a heavier, more confident silhouette and a natural frame for the pearl.',
  'The growth lines disappear below 32px.'),
 ('disc', '04', 'Open Oyster, in the Disc', '00&rsquo;s idea kept: the disc stays the o of the logotype, with the frilled open oyster cut into it as an outline.',
  'Keeps the round o and the inside-out idea, now with a shell that reads as a shell.',
  'The finest drawing of the set; below 32px it closes up into a disc with a pearl.'),
 ('low', '05', 'Lower Angle', 'Closer to front-on: the bowl is a thinner ellipse and the upper valve leans further back, showing more of its inside. The pearl sits proud at the front.',
  'The most open and generous pose, with the pearl front and centre.',
  'Wider than it is tall, so as the o it sits a little low and wide beside the letters.'),
]

if __name__ == '__main__':
    sheet(threequarter, OPTS, 'Open Oyster', 'Open oyster',
          'The open clamshell, seen from a slight angle. What makes 00 look like a makeup compact is its flat lid in a perfect circle; these show depth instead. We look into both valves, which are hollow (cut out, as 00&rsquo;s shells are), the rims are frilled, and the pearl rests in the lower cup in 00&rsquo;s cradle. Each is shown in both palettes, as the o of the logotype, at real pixel sizes and in one colour.',
          'Built by <code>oyster/brand/build_threequarter.py</code>; SVG files for each option, in both palettes, are in <code>oyster/brand/</code> as <code>oyster-threequarter-*.svg</code>.', 'threequarter.html')
