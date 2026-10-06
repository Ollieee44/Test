"""Build frontal.html, "Beyond the compact": directions from Inside Out (marks from frontal.py), on the
same sheet as refine.html."""
import frontal
from build_refine import sheet

OPTS = [
 ('inside', '00', 'Inside Out', 'The adopted mark, the base for this round. A perfect disc, two straight-lipped shells and a lid hinged open: together they read as a makeup compact.',
  'A strong silhouette, and already the o of the logotype, the favicon and the header.',
  'The compact read comes from three things: the perfect circle, the ruler-straight lips, and the lid swung up like a mirror.'),
 ('valve', '01', 'Front-on Valve', 'The oyster seen from above, as you see one on the plate: a teardrop valve with a frilled lip, growth lines fanning out from the hinge, and the pearl in the cup. No disc and no lid.',
  'Unmistakably an oyster, and nothing else. The growth lines echo nacre layers building a pearl.',
  'Not round, so as the o of the logotype it sits a little heavier than the letters. The growth lines merge below 24px.'),
 ('valvedisc', '02', 'Front-on, in the Disc', 'The disc stays the o, and the front-on valve is drawn into it as cut lines: its frilled lip and two growth lines, with the pearl in the cup.',
  'Keeps the round o and the inside-out idea, but swaps the compact&rsquo;s lid for a real shell. Reads like a struck medal or a seal.',
  'The finest of the set. Below 32px the lines close up and it falls back to a disc with a pearl.'),
 ('rough', '03', 'Shell Edge', '00 unchanged inside, but the perfect circle becomes a slightly lumpy, asymmetric rim, as a real shell has.',
  'The smallest change. The edge alone is enough to stop it reading as a manufactured object.',
  'On its own it can look like a cookie or a stone. It works best combined with ruffled lips (05).'),
 ('ruffle', '04', 'Ruffled Lips', '00 with the straight lips of both shells frilled, as an oyster&rsquo;s are. The disc stays a perfect circle.',
  'The ruffles are the most oyster-specific detail there is, and they keep the logotype&rsquo;s o perfectly round.',
  'The frills are small; at 16px the lips go back to straight lines.'),
 ('both', '05', 'Edge and Ruffles', 'Both changes together: a shell-edged rim and frilled lips around the same pearl in its cradle.',
  'The clearest fix for the compact read that still looks like 00. Organic all the way round.',
  'The least geometric option, so the o sits slightly less crisply beside the type.'),
]

if __name__ == '__main__':
    sheet(frontal, OPTS, 'Beyond the Compact', 'Beyond the compact',
          'Inside Out (00) can read as a makeup compact: a perfect disc, straight lips and a lid hinged open like a mirror. These five directions start from 00 and break that. Two look at the oyster front-on; three keep the side view and make the shell organic. Each is shown in both palettes, as the o of the logotype, at real pixel sizes and in one colour.',
          'Built by <code>oyster/brand/build_frontal.py</code>; SVG files for each option, in both palettes, are in <code>oyster/brand/</code> as <code>oyster-frontal-*.svg</code>.', 'frontal.html')
