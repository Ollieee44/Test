"""Build refs.html, "From the References": marks drawn closely from each of the client's two reference
images on its own (marks from refs.py), on the same sheet as refine.html."""
import refs
from build_refine import sheet

OPTS = [
 ('inside', '00', 'Inside Out', 'The live mark, for reference.', 'Already the o of the logotype, the favicon and the header.', 'Reads as a makeup compact.'),
 ('half', 'A1', 'Half Shell', 'From the painting: one half shell seen three-quarter, the hinge&rsquo;s point at the left and the broad end up at the right. The cup is deep, its rim thick at the front and thin at the back, its inner wall darker round the back, and the pearl rests low in the cup.',
  'The closest to the painting: unmistakably an oyster, with the pearl held in its cup. The tinted inner wall gives it depth, which keeps it from reading as an eye.',
  'One shell only, so it loses the two halves coming together. The tint needs a second tone; in one colour it prints as a lighter ink.'),
 ('rough', 'A2', 'Half Shell, Rough Rim', 'A1 with the painting&rsquo;s chipped, uneven rim.',
  'The rough rim is the most oyster-specific detail in the painting, and it reads even at 24px.', 'A little busier at large sizes; the chips need to be redrawn by hand for print.'),
 ('shadow', 'A3', 'Half Shell, with Shadow', 'A2 resting on its cast shadow, as the shell sits on the sand in the painting.',
  'Grounds the shell and gives it weight, like an object on a table rather than a symbol.', 'The shadow widens the mark to the left and drops out at small sizes, so it suits large uses.'),
 ('ribbed', 'B1', 'Fan and Pearl', 'From the second image, front-on: the upper valve stands up as a fan behind, its ribs radiating from a hinge hidden behind the pearl, a shallow dish lies in front, and the big pearl rests in it.',
  'The closest to the second image, and the most instantly read pearl-in-shell picture. Both shells are there, coming together around the pearl.',
  'The ribbed fan is a scallop, not an oyster, and it is close to the Shell plc logo. Worth a trademark check before going further.'),
 ('scalloped', 'B2', 'Fan and Pearl, Scalloped Edge', 'B1 with the ribs carried only by the fan&rsquo;s scalloped edge, for a cleaner icon.',
  'Simpler than B1 and still clearly a shell. Holds up better at small sizes.', 'Still a scallop&rsquo;s silhouette, with the same Shell plc caution.'),
 ('smooth', 'B3', 'Fan and Pearl, Smooth', 'The same front-on composition with a smooth fan and no ribs.',
  'Keeps the composition of the second image while stepping away from the scallop. The calmest of the three.', 'Without ribs the fan is less obviously a shell and can read as a hood or a hat.'),
]

if __name__ == '__main__':
    sheet(refs, OPTS, 'From the References', 'From the references',
          'Marks drawn closely from each reference on its own, with no blending. A is the painting: a single half shell seen three-quarter, deep cup, thick rim and the pearl in the cup. B is the second image: front-on, the upper valve standing up as a fan, a shallow dish in front and a big pearl resting in it. As you noted, the half shell loses the two shells coming together; B keeps them. Each is shown in both palettes, as the o of the logotype, at real pixel sizes and in one colour.',
          'Built by <code>oyster/brand/build_refs.py</code>; SVG files for each option, in both palettes, are in <code>oyster/brand/</code> as <code>oyster-refs-*.svg</code>.', 'refs.html')
