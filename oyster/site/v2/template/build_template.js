// Oyster slide template: the new site's design language as PowerPoint slide layouts, plus a suggested deck that uses
// every one. Built with pptxgenjs on a theme (colours and fonts) applied after writing.
//   NODE_PATH=<dir with pptxgenjs> node build_template.js   (after make_assets.py and make_icons.js)
// Fonts ship with PowerPoint and stand in for the site's: Georgia for its serif headlines, Aptos for Geist,
// Consolas for its mono and pixel labels.
const pptxgen = require('pptxgenjs');
const { applyTheme } = require(process.env.PPTX_SKILL + '/scripts/apply_theme.js');
const A = __dirname + '/assets/';
const SZ = require('./assets/sizes.json'), ar = n => SZ[n][1] / SZ[n][0];   // a picture's height over its width

const THEME = {
  name: 'Oyster Therapeutics',
  headFontFace: 'Georgia', bodyFontFace: 'Aptos',
  colors: { dk1: '295143', lt1: 'FFFFFF', dk2: '158B63', lt2: 'F5FFFC',
    accent1: '30FCBA', accent2: 'F0A6CA', accent3: 'CEE5F3', accent4: 'F7D16B', accent5: '158B63', accent6: '3A715E',
    hlink: '158B63', folHlink: '3A715E' },
};
const MONO = 'Consolas';
const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE';                       // 13.333 x 7.5 in
pres.title = 'Oyster Therapeutics template';
pres.author = 'Oyster Therapeutics';
pres.company = 'Oyster Therapeutics';
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;
// colours with no theme slot: the dimmed step number and the soft body text on dark grounds
const SOFT = 'D6EFE6', DIM = '8AC3B1', MUTED = 'A8D8C6';
const LOGO_AR = ar('logo-white.png');

// ---------- shared pieces ----------
// titles are left-aligned, as on the site, unless a layout says otherwise (PowerPoint centres them by default)
const ph = (name, type, x, y, w, h, opts, prompt) => ({ placeholder: { options: { name, type, x, y, w, h, margin: 0, ...(type === 'title' ? { align: 'left' } : {}), ...opts }, text: prompt } });
const eyebrow = (color, y = .62) => ph('eyebrow', 'body', .6, y, 8, .3, { fontFace: MONO, fontSize: 11, bold: true, charSpacing: 2, color, valign: 'middle' }, 'SECTION LABEL');
const footer = (dark) => [
  { image: { path: A + (dark ? 'mark-white.png' : 'mark-ink.png'), x: .6, y: 6.93, w: .32 / ar('mark-white.png'), h: .32 } },
  { text: { text: 'OYSTER THERAPEUTICS', options: { x: 1.05, y: 6.93, w: 4, h: .32, fontFace: MONO, fontSize: 9, charSpacing: 2, color: dark ? MUTED : C.text1, margin: 0, valign: 'middle' } } },
];
const num = dark => ({ x: 12.13, y: 6.93, w: .6, h: .32, fontFace: MONO, fontSize: 9, color: dark ? MUTED : C.text1, align: 'right' });

// ---------- slide layouts ----------
pres.defineSlideMaster({ title: 'Oyster Title', background: { path: A + 'ground-emerald.png' }, objects: [
  { image: { path: A + 'logo-white.png', x: .6, y: .55, w: 2.4, h: 2.4 * LOGO_AR } },
  ph('title', 'title', .6, 2.2, 11.4, 2.5, { fontFace: THEME.headFontFace, fontSize: 54, color: C.background1, valign: 'bottom', lineSpacingMultiple: .92 }, 'Presentation title'),
  ph('subtitle', 'body', .6, 4.95, 8.6, 1.0, { fontSize: 18, color: C.background1, valign: 'top' }, 'Subtitle or one-line summary'),
  ph('meta', 'body', .6, 6.75, 8, .35, { fontFace: MONO, fontSize: 10, charSpacing: 2, color: SOFT, valign: 'middle' }, 'DATE · AUDIENCE · PRESENTER'),
] });
pres.defineSlideMaster({ title: 'Oyster Section', background: { path: A + 'ground-emerald.png' }, objects: [
  ph('number', 'body', .6, 2.35, 3, .6, { fontFace: MONO, fontSize: 26, bold: true, color: DIM, valign: 'bottom' }, '01'),
  ph('title', 'title', .6, 3.0, 11.5, 1.5, { fontFace: THEME.headFontFace, fontSize: 48, color: C.background1, valign: 'top' }, 'Section title'),
  ph('intro', 'body', .6, 4.6, 8.4, 1.1, { fontSize: 16, color: SOFT, valign: 'top' }, 'One or two lines on what this section covers'),
  ...footer(true),
], slideNumber: num(true) });
pres.defineSlideMaster({ title: 'Oyster Statement', background: { path: A + 'ground-deep.png' }, objects: [
  eyebrow(C.accent1, 1.55),
  ph('title', 'title', .6, 2.0, 11.6, 3.3, { fontFace: THEME.headFontFace, fontSize: 40, color: C.background1, valign: 'top', lineSpacingMultiple: .98 }, 'A single, large statement'),
  ph('attribution', 'body', .6, 5.6, 8, .5, { fontSize: 14, color: MUTED, valign: 'top' }, 'Source or attribution'),
  ...footer(true),
], slideNumber: num(true) });
const content = (title, dark) => pres.defineSlideMaster({ title, background: dark ? { path: A + 'ground-deep.png' } : { color: 'FFFFFF' }, objects: [
  eyebrow(dark ? C.accent1 : C.text2),
  ph('title', 'title', .6, .95, 12.1, .95, { fontFace: THEME.headFontFace, fontSize: 32, color: dark ? C.background1 : C.text1, valign: 'top' }, 'Slide title'),
  ph('body', 'body', .6, 2.2, 7.8, 4.4, { fontSize: 16, color: dark ? C.background1 : C.text1, valign: 'top', paraSpaceAfter: 8 }, 'Body text'),
  ...footer(dark),
], slideNumber: num(dark) });
content('Oyster Content Dark', true);
content('Oyster Content Light', false);
pres.defineSlideMaster({ title: 'Oyster Two Column', background: { color: 'FFFFFF' }, objects: [
  eyebrow(C.text2),
  ph('title', 'title', .6, .95, 5.8, 1.6, { fontFace: THEME.headFontFace, fontSize: 32, color: C.text1, valign: 'top' }, 'Slide title'),
  ph('body', 'body', .6, 2.75, 5.8, 3.85, { fontSize: 16, color: C.text1, valign: 'top', paraSpaceAfter: 8 }, 'Body text'),
  { rect: { x: 6.9, y: .6, w: 5.83, h: 6.0, fill: { color: '3A715E' }, rectRadius: 0 } },
  ph('picture', 'pic', 6.9, .6, 5.83, 6.0, { color: C.background1 }, 'Picture'),
  ...footer(false),
], slideNumber: num(false) });
const cardX = i => .6 + i * 4.11;
pres.defineSlideMaster({ title: 'Oyster Three Cards', background: { path: A + 'ground-deep.png' }, objects: [
  eyebrow(C.accent1),
  ph('title', 'title', .6, .95, 12.1, .95, { fontFace: THEME.headFontFace, fontSize: 32, color: C.background1, valign: 'top' }, 'Slide title'),
  ...[0, 1, 2].flatMap(i => [
    { rect: { x: cardX(i), y: 2.15, w: 3.89, h: 4.55, fill: { color: 'FFFFFF' }, rectRadius: .12 } },
    { image: { path: A + 'ground-sage.png', x: cardX(i) + .12, y: 2.27, w: 3.65, h: 2.03 } },
    ph('card' + (i + 1) + 'Picture', 'pic', cardX(i) + .12, 2.27, 3.65, 2.03, { color: C.background1 }, 'Card picture'),
    ph('card' + (i + 1) + 'Title', 'body', cardX(i) + .3, 4.48, 3.3, .5, { fontFace: THEME.headFontFace, fontSize: 24, color: C.text1, valign: 'top' }, 'Card title'),
    ph('card' + (i + 1) + 'Body', 'body', cardX(i) + .3, 5.05, 3.3, 1.5, { fontSize: 14, color: C.text1, valign: 'top' }, 'Card text'),
  ]),
  ...footer(true),
], slideNumber: num(true) });
const featX = i => .6 + i * 3.08;
pres.defineSlideMaster({ title: 'Oyster Four Features', background: { path: A + 'ground-emerald.png' }, objects: [
  eyebrow(C.background1),
  ph('title', 'title', .6, .95, 12.1, .95, { fontFace: THEME.headFontFace, fontSize: 32, color: C.background1, valign: 'top' }, 'Slide title'),
  ...[0, 1, 2, 3].flatMap(i => [
    { rect: { x: featX(i), y: 2.3, w: 2.9, h: 4.25, fill: { color: 'FFFFFF', transparency: 88 }, line: { color: 'FFFFFF', transparency: 80, width: .75 }, rectRadius: .12 } },
    { text: { text: '0' + (i + 1), options: { x: featX(i) + .25, y: 2.5, w: 1, h: .35, fontFace: MONO, fontSize: 12, bold: true, color: DIM, margin: 0 } } },
    ph('feature' + (i + 1) + 'Title', 'body', featX(i) + .25, 3.05, 2.45, 1.0, { fontFace: THEME.headFontFace, fontSize: 21, color: C.background1, valign: 'top' }, 'Feature'),
    ph('feature' + (i + 1) + 'Body', 'body', featX(i) + .25, 4.2, 2.45, 2.1, { fontSize: 14, color: SOFT, valign: 'top' }, 'One or two lines'),
  ]),
  ...footer(true),
], slideNumber: num(true) });
pres.defineSlideMaster({ title: 'Oyster Image', background: { path: A + 'ground-emerald.png' }, objects: [
  ph('picture', 'pic', 0, 0, 13.333, 7.5, { color: C.background1 }, 'Full-bleed picture'),
  { rect: { x: .6, y: 4.95, w: 6.6, h: 1.85, fill: { color: '0F3A2D', transparency: 22 }, rectRadius: .12 } },
  ph('eyebrow', 'body', .9, 5.18, 6, .3, { fontFace: MONO, fontSize: 11, bold: true, charSpacing: 2, color: C.accent1, valign: 'middle' }, 'LABEL'),
  ph('caption', 'body', .9, 5.6, 6.0, 1.05, { fontFace: THEME.headFontFace, fontSize: 22, color: C.background1, valign: 'top' }, 'Caption'),
] });
const titleOnly = (title, dark) => pres.defineSlideMaster({ title, background: dark ? { path: A + 'ground-deep.png' } : { color: 'FFFFFF' }, objects: [
  eyebrow(dark ? C.accent1 : C.text2),
  ph('title', 'title', .6, .95, 12.1, .95, { fontFace: THEME.headFontFace, fontSize: 32, color: dark ? C.background1 : C.text1, valign: 'top' }, 'Slide title'),
  ...footer(dark),
], slideNumber: num(dark) });
titleOnly('Oyster Title Only Dark', true);
titleOnly('Oyster Title Only Light', false);
pres.defineSlideMaster({ title: 'Oyster Closing', background: { path: A + 'ground-emerald.png' }, objects: [
  { image: { path: A + 'logo-white.png', x: 4.67, y: 1.9, w: 4.0, h: 4.0 * LOGO_AR } },
  ph('title', 'title', 1.4, 3.45, 10.53, 1.3, { fontFace: THEME.headFontFace, fontSize: 32, color: C.background1, align: 'center', valign: 'top' }, 'Closing line'),
  ph('contact', 'body', 2.4, 4.95, 8.53, 1.0, { fontSize: 14, color: SOFT, align: 'center', valign: 'top' }, 'Contact details'),
] });

// ---------- the suggested deck ----------
const sec = t => pres.addSection({ title: t });
const add = (master, section) => pres.addSlide({ masterName: master, sectionTitle: section });
const T = (s, name, text, o = {}) => s.addText(text, { placeholder: name, ...o });
const SELFTAC = 'SELFTAC®';

sec('Opening');
let s = add('Oyster Title', 'Opening');
T(s, 'title', [{ text: 'Targeted protein degradation ', options: { breakLine: true } }, { text: 'beyond conventional limits', options: { color: C.accent1 } }]);
T(s, 'subtitle', 'We develop smaller protein degrader therapeutics to reach new biological targets and bigger populations. First stop: neurodegenerative disease.');
T(s, 'meta', 'COMPANY OVERVIEW · 2026');
s.addNotes('Title layout. The second line of the title is set in the theme accent (mint) by hand, as on the website.');
s = add('Oyster Statement', 'Opening');
T(s, 'eyebrow', 'THE IDEA');
T(s, 'title', [{ text: 'The function of a full degrader. ', options: {} }, { text: 'The distribution of a small molecule.', options: { color: C.accent1 } }]);
T(s, 'attribution', `${SELFTAC} platform`);

sec('Problem');
s = add('Oyster Section', 'Problem');
T(s, 'number', '01'); T(s, 'title', 'The problem'); T(s, 'intro', 'Why first-generation protein degraders are limited.');
s = add('Oyster Title Only Light', 'Problem');
T(s, 'eyebrow', 'FIRST-GENERATION DEGRADERS'); T(s, 'title', 'Each type of degrader brings its own trade-off');
[['Bifunctional degraders', ['MODULAR', 'BULKY'], 'Modular components, but their large size limits oral bioavailability and penetration into tissues like the brain.'],
 ['Molecular glues', ['DRUG-LIKE', 'SERENDIPITOUS'], 'Smaller, with more favourable drug-like properties, but without the same rational, modular design approach.']].forEach(([t, tags, body], i) => {
  const x = .6 + i * 6.12;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 2.2, w: 5.95, h: 4.35, fill: { color: 'F5FFFC' }, line: { color: '295143', transparency: 80, width: .75 }, rectRadius: .12, objectName: 'Card ' + (i + 1) });
  s.addText(t, { x: x + .4, y: 2.55, w: 5.2, h: .6, isTextBox: true, fontFace: THEME.headFontFace, fontSize: 26, color: C.text1, margin: 0, objectName: 'Card title ' + (i + 1) });
  tags.forEach((g, j) => s.addText(g, { x: x + .4 + j * 1.75, y: 3.35, w: 1.6, h: .38, shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: .19, fill: { color: j ? 'F0A6CA' : 'CEE5F3' },
    fontFace: MONO, fontSize: 10, bold: true, charSpacing: 1.5, color: C.text1, align: 'center', valign: 'middle', margin: 0, objectName: 'Tag ' + g }));
  s.addText(body, { x: x + .4, y: 4.05, w: 5.2, h: 2.1, isTextBox: true, fontSize: 16, color: C.text1, margin: 0, valign: 'top', objectName: 'Card text ' + (i + 1) });
});
s.addNotes('Title Only (light) layout with two comparison cards composed on the slide.');

sec('Our solution');
s = add('Oyster Section', 'Our solution');
T(s, 'number', '02'); T(s, 'title', `Our solution: the ${SELFTAC} platform`); T(s, 'intro', 'Degraders that travel as small molecules and self-assemble where they are needed.');
s = add('Oyster Three Cards', 'Our solution');
T(s, 'eyebrow', 'HOW IT WORKS'); T(s, 'title', 'Separate, assemble, degrade');
[['separate', 'Separate', 'Degraders start as two small molecular components that can cross the blood-brain barrier.'],
 ['assemble', 'Assemble', 'The two small molecules cross the gut wall, cell membranes and the blood-brain barrier.'],
 ['degrade', 'Degrade', 'Once assembled, it behaves like a standard PROTAC and the cell clears the target protein.']].forEach(([f, t, b], i) => {
  s.addImage({ placeholder: 'card' + (i + 1) + 'Picture', path: A + 'card-' + f + '.png', w: 3.65, h: 2.03, altText: t + ' illustration' });
  T(s, 'card' + (i + 1) + 'Title', t); T(s, 'card' + (i + 1) + 'Body', b);
});
s = add('Oyster Two Column', 'Our solution');
T(s, 'eyebrow', 'THE TERNARY COMPLEX'); T(s, 'title', 'Rebuilt inside the cell');
T(s, 'body', [{ text: 'One end holds the target protein, the other an E3 ligase.', options: { breakLine: true } },
  { text: 'The cell tags the target with ubiquitin and the proteasome breaks it down.', options: { breakLine: true } },
  { text: 'The degrader is not used up: it lets go and finds the next one.', options: {} }]);
s.addImage({ placeholder: 'picture', path: A + 'complex-panel.png', w: 5.83, h: 6.0, altText: 'Ternary complex: target protein above, E3 ligase below, the SELFTAC degrader between' });
s.addNotes('Two Column layout. The picture placeholder sits on a sage panel; a transparent picture (as here) shows the panel behind it.');
s = add('Oyster Four Features', 'Our solution');
T(s, 'eyebrow', 'KEY FEATURES'); T(s, 'title', 'Protein degradation, unlocked');
[['High oral bioavailability', 'Make oral degraders the expectation, not the exception.'], ['Routine CNS penetration', 'Open the brain to protein degrader therapeutics.'],
 ['Faster discovery', 'Turn iterative chemistry into modular design with reusable components.'], ['New technology', 'Integrate emerging E3 ligases as they arrive.']].forEach(([t, b], i) => {
  T(s, 'feature' + (i + 1) + 'Title', t); T(s, 'feature' + (i + 1) + 'Body', b);
});
s = add('Oyster Title Only Dark', 'Our solution');
T(s, 'eyebrow', 'PIPELINE'); T(s, 'title', 'Discovery programmes');
const hd = t => ({ text: t, options: { fontFace: MONO, fontSize: 11, bold: true, color: MUTED, charSpacing: 1.5 } });
const cl = (t, o = {}) => ({ text: t, options: { fontSize: 16, color: 'FFFFFF', ...o } });
const stage = on => ({ text: on ? '●' : '○', options: { fontSize: 16, color: on ? 'F7D16B' : MUTED, align: 'center' } });
s.addTable([[hd('THERAPEUTIC AREA'), hd('TARGETS'), hd('DISCOVERY'), hd('LEAD OPTIMISATION'), hd('PRECLINICAL'), hd('CLINICAL')],
  [cl('Oncology', { fontFace: THEME.headFontFace, fontSize: 20 }), cl('Undisclosed', { color: SOFT }), stage(1), stage(0), stage(0), stage(0)],
  [cl('Central nervous system', { fontFace: THEME.headFontFace, fontSize: 20 }), cl('Undisclosed', { color: SOFT }), stage(1), stage(0), stage(0), stage(0)]],
  { x: .6, y: 2.4, w: 12.13, colW: [3.4, 2.2, 1.63, 1.63, 1.63, 1.64], rowH: [.6, .95, .95], valign: 'middle', margin: [0, .1, 0, 0],
    border: [{ type: 'none' }, { type: 'none' }, { pt: .75, color: '6F8F83' }, { type: 'none' }], fill: { color: '295143', transparency: 100 }, objectName: 'Pipeline table' });
s.addText('● stage reached   ○ to come', { x: .6, y: 5.25, w: 6, h: .35, isTextBox: true, fontFace: MONO, fontSize: 10, color: MUTED, margin: 0, objectName: 'Pipeline key' });
s.addNotes('Title Only (dark) layout with a native table; pearls mark the stage reached, gold for the current stage.');

sec('Team');
s = add('Oyster Section', 'Team');
T(s, 'number', '03'); T(s, 'title', 'Team'); T(s, 'intro', 'Medicinal chemists and company builders with a record of turning science into medicines.');
s = add('Oyster Title Only Light', 'Team');
T(s, 'eyebrow', 'LEADERSHIP'); T(s, 'title', 'The people behind the platform');
[['RJ', 'Robert Johnson', 'Chief Executive Officer', 'Previously CEO of Adrestia Therapeutics, acquired by Insmed in 2023.'],
 ['HF', 'Harry Finch, PhD', 'Founder & Chief Scientific Officer', 'Medicinal chemist whose research founded the SELFTAC® platform.']].forEach(([m, n, r, b], i) => {
  const x = .6 + i * 6.12;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 2.2, w: 5.95, h: 2.6, fill: { color: 'F5FFFC' }, line: { color: '295143', transparency: 80, width: .75 }, rectRadius: .12, objectName: 'Person card ' + (i + 1) });
  s.addText(m, { x: x + .35, y: 2.55, w: 1.1, h: 1.1, shape: pres.shapes.OVAL, fill: { color: i ? 'F0A6CA' : 'CEE5F3' }, fontFace: THEME.headFontFace, fontSize: 22, color: C.text1, align: 'center', valign: 'middle', margin: 0, objectName: 'Monogram ' + m });
  s.addText(n, { x: x + 1.75, y: 2.55, w: 3.9, h: .5, isTextBox: true, fontFace: THEME.headFontFace, fontSize: 22, color: C.text1, margin: 0, objectName: 'Name ' + (i + 1) });
  s.addText(r.toUpperCase(), { x: x + 1.75, y: 3.08, w: 3.9, h: .32, isTextBox: true, fontFace: MONO, fontSize: 10, bold: true, charSpacing: 1.2, color: C.text2, margin: 0, objectName: 'Role ' + (i + 1) });
  s.addText(b, { x: x + 1.75, y: 3.5, w: 3.9, h: 1.1, isTextBox: true, fontSize: 14, color: C.text1, margin: 0, valign: 'top', objectName: 'Bio ' + (i + 1) });
});
s.addNotes('Replace the monograms with photos cropped to a circle (Picture Format > Crop to Shape > Oval) if you have them.');

sec('Close');
s = add('Oyster Image', 'Close');
s.addImage({ placeholder: 'picture', path: A + 'complex-hero.png', w: 13.333, h: 7.5, altText: 'The SELFTAC ternary complex on the emerald ground' });
T(s, 'eyebrow', 'SELFTAC® · TERNARY COMPLEX'); T(s, 'caption', 'One molecule holds the target to the ligase.');
s.addNotes('Image layout: a full-bleed picture with a caption panel over its lower left.');
s = add('Oyster Closing', 'Close');
T(s, 'title', [{ text: 'Targeted protein degradation ', options: {} }, { text: 'beyond conventional limits.', options: { color: C.accent1 } }]);
T(s, 'contact', 'info@oystertx.com  ·  London, United Kingdom  ·  oyster-tx.com');

(async () => {
  const f = __dirname + '/oyster-template.pptx';
  await pres.writeFile({ fileName: f }); await applyTheme(f, THEME); console.log('wrote', f);
})();
