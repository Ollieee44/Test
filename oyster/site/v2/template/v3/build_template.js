// Oyster slide template v3: the oyster-tx.com feel in the Colors.pdf palette. Depth instead of flat fills: glowing
// Abyss grounds with a drift of speckles (kept out from under each layout's text), the brand's textured greens, glass cards, rounded picture frames, soft
// shadows; a clean sans throughout (Aptos, PowerPoint's own) in place of a serif, with mono labels led by a gold dot.
//   PPTX_SKILL=<pptx skill dir> NODE_PATH=<dir with pptxgenjs> node build_template.js   (after make_assets.py)
const pptxgen = require('pptxgenjs');
const { applyTheme } = require(process.env.PPTX_SKILL + '/scripts/apply_theme.js');
const A = __dirname + '/assets/';
const SZ = require('./assets/sizes.json'), ar = n => SZ[n][1] / SZ[n][0];

const P = { abyss0: '070D0A', abyss: '1A372A', forest: '2E6149', kelp: '408967', kelp2: '67B791', mint: 'BADECD', seafoam: 'EBEBE3',
  g3D: '3D3D3D', g66: '666666', g85: '858585', gC2: 'C2C2C2', gEB: 'EBEBEB', white: 'FFFFFF',
  gold: 'DCA84E', bronze: '99803C', pink: 'F0A6CA', mauve: 'A2839E', sage: '8AB0AB', teal: '3F7965', ice: 'CEE5F3', slate: '90A9B7' };
const THEME = {
  name: 'Oyster Therapeutics',
  headFontFace: 'Aptos Display', bodyFontFace: 'Aptos',
  colors: { dk1: P.abyss, lt1: P.white, dk2: P.forest, lt2: P.seafoam,
    accent1: P.kelp, accent2: P.gold, accent3: P.kelp2, accent4: P.mauve, accent5: P.sage, accent6: P.pink,
    hlink: P.kelp, folHlink: P.bronze },
};
const MONO = 'Aptos Mono', HEAD = THEME.headFontFace;
module.exports = { P, THEME, MONO };
if (require.main !== module) return;

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE';                       // 13.333 x 7.5 in
pres.title = 'Oyster Therapeutics template';
pres.author = 'Oyster Therapeutics';
pres.company = 'Oyster Therapeutics';
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;
const LOGO_AR = ar('logo-on-dark.png'), MARK_AR = ar('mark-white.png');
const bg = f => ({ path: A + f });
// a layout's rect objects can't be rounded, so rounded shapes and dots go in as empty shaped text objects
const rrect = (x, y, w, h, o) => ({ text: { text: '', options: { x, y, w, h, shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: o.r ?? .2, fill: o.fill, line: o.line, shadow: o.shadow, margin: 0 } } });
const dot = (x, y, d = .1) => ({ text: { text: '', options: { x, y, w: d, h: d, shape: pres.shapes.OVAL, fill: { color: P.gold }, line: { type: 'none' }, margin: 0 } } });

// ---------- shared pieces ----------
const ph = (name, type, x, y, w, h, opts, prompt) => ({ placeholder: { options: { name, type, x, y, w, h, margin: 0, ...(type === 'title' ? { align: 'left' } : {}), ...opts }, text: prompt } });
const mark = (dark, x = .6, y = .5, h = .42) => ({ image: { path: A + (dark ? 'mark-on-dark.png' : 'mark-on-light.png'), x, y, w: h / MARK_AR, h } });
const monoMark = (dark, x, y, h) => ({ image: { path: A + (dark ? 'mark-white.png' : 'mark-black.png'), x, y, w: h / MARK_AR, h } });
// a label: a gold dot, then small mono capitals (the website's section labels)
const label = (dark, x, y, w = 8, prompt = 'LABEL') => [
  dot(x, y + .1),
  ph('label', 'body', x + .22, y, w, .3, { fontFace: MONO, fontSize: 11, charSpacing: 2.5, color: dark ? P.mint : P.forest, valign: 'middle' }, prompt),
];
const footer = dark => [
  monoMark(dark, .6, 6.98, .22),
  { text: { text: 'OYSTER THERAPEUTICS', options: { x: .9, y: 6.97, w: 3, h: .24, fontFace: MONO, fontSize: 8, charSpacing: 2.5, color: dark ? P.mint : P.forest, margin: 0, valign: 'middle' } } },
  // the page number sits in a small pill, like the website's controls
  rrect(12.13, 6.92, .6, .34, { r: .17, fill: { color: dark ? P.white : P.abyss, transparency: dark ? 86 : 93 }, line: { type: 'none' } }),
];
const num = dark => ({ x: 12.13, y: 6.92, w: .6, h: .34, fontFace: MONO, fontSize: 9, color: dark ? P.white : P.abyss, align: 'center', valign: 'middle' });
const shadow = () => ({ type: 'outer', blur: 18, offset: 4, angle: 90, color: '1A372A', opacity: .14 });
// frosted glass: a dark tint that quietens the speckles behind it, with a fine light edge
const glass = (x, y, w, h) => rrect(x, y, w, h, { fill: { color: P.abyss, transparency: 25 }, line: { color: P.white, transparency: 75, width: .75 } });
// content slides: a compact title band at the top, so the slide is left for the content
const title = color => ph('title', 'title', .6, .34, 12.1, .62, { fontFace: HEAD, fontSize: 30, color, valign: 'top' }, 'Slide title');
const subtitle = color => ph('subtitle', 'body', .6, .98, 12.1, .36, { fontSize: 15, color, valign: 'top' }, 'Subtitle or one-line takeaway');

// ---------- slide layouts ----------
pres.defineSlideMaster({ title: 'Oyster Title', background: bg('ground-title.jpg'), objects: [
  { image: { path: A + 'logo-on-dark.png', x: .6, y: .6, w: 2.7, h: 2.7 * LOGO_AR } },
  ph('title', 'title', .6, 2.0, 8.8, 2.7, { fontFace: HEAD, fontSize: 56, color: C.background1, valign: 'bottom', lineSpacingMultiple: .9 }, 'Presentation title'),
  ph('subtitle', 'body', .6, 4.95, 7.6, .8, { fontSize: 20, color: P.seafoam, valign: 'top' }, 'Subtitle or date'),
  dot(.6, 6.66),
  ph('meta', 'body', .82, 6.56, 8, .3, { fontFace: MONO, fontSize: 10, charSpacing: 2.5, color: P.mint, valign: 'middle' }, 'AUDIENCE · PRESENTER · CONFIDENTIAL'),
] });
pres.defineSlideMaster({ title: 'Oyster Contents', background: bg('ground-contents.jpg'), objects: [
  mark(true),
  ph('title', 'title', .6, 1.55, 3.6, 1.0, { fontFace: HEAD, fontSize: 40, color: C.background1, valign: 'top' }, 'Contents'),
  ...footer(true),
], slideNumber: num(true) });
pres.defineSlideMaster({ title: 'Oyster Section', background: bg('ground-section.jpg'), objects: [
  mark(true),
  ph('number', 'body', 7.6, .35, 5.2, 3.1, { fontFace: HEAD, fontSize: 200, color: P.kelp2, align: 'right', valign: 'top' }, '01'),
  ph('title', 'title', .6, 3.75, 11.0, 1.4, { fontFace: HEAD, fontSize: 50, color: C.background1, valign: 'bottom' }, 'Section title'),
  ph('intro', 'body', .6, 5.2, 8.4, .9, { fontSize: 18, color: P.seafoam, valign: 'top' }, 'One or two lines on what this section covers'),
  ...footer(true),
], slideNumber: num(true) });
pres.defineSlideMaster({ title: 'Oyster Statement', background: bg('ground-statement.jpg'), objects: [
  mark(true),
  ...label(true, .6, 1.55),
  ph('title', 'title', .6, 2.05, 11.6, 3.3, { fontFace: HEAD, fontSize: 44, color: C.background1, valign: 'top', lineSpacingMultiple: .96 }, 'A single, large statement'),
  ph('attribution', 'body', .6, 5.6, 8, .5, { fontSize: 16, color: P.mint, valign: 'top' }, 'Source or attribution'),
  ...footer(true),
], slideNumber: num(true) });
const titleOnly = (name, ground, dark) => pres.defineSlideMaster({ title: name, background: bg(ground), objects: [
  title(dark ? P.white : P.abyss), subtitle(dark ? P.mint : P.kelp), ...footer(dark),
], slideNumber: num(dark) });
titleOnly('Oyster Title Only', 'ground-white.jpg', false);
titleOnly('Oyster Title Only Sea Foam', 'ground-light.jpg', false);
titleOnly('Oyster Title Only Dark', 'ground-quiet.jpg', true);
pres.defineSlideMaster({ title: 'Oyster Blank', background: bg('ground-white.jpg'), objects: [...footer(false)], slideNumber: num(false) });
pres.defineSlideMaster({ title: 'Oyster Title and Content', background: bg('ground-light.jpg'), objects: [
  title(P.abyss), subtitle(P.kelp),
  rrect(.6, 1.65, 12.13, 4.95, { fill: { color: P.white }, line: { type: 'none' }, shadow: shadow() }),
  ph('body', 'body', 1.0, 2.0, 11.3, 4.3, { fontSize: 18, color: P.abyss, valign: 'top', paraSpaceAfter: 10 }, 'Body text'),
  ...footer(false),
], slideNumber: num(false) });
pres.defineSlideMaster({ title: 'Oyster Two Column', background: bg('ground-quiet.jpg'), objects: [
  ...label(true, .6, .6),
  ph('title', 'title', .6, 1.05, 5.7, 1.5, { fontFace: HEAD, fontSize: 34, color: C.background1, valign: 'top' }, 'Slide title'),
  ph('subtitle', 'body', .6, 2.6, 5.7, .5, { fontSize: 16, color: P.mint, valign: 'top' }, 'Subtitle'),
  ph('body', 'body', .6, 3.3, 5.7, 3.3, { fontSize: 16, color: P.seafoam, valign: 'top', paraSpaceAfter: 8 }, 'Body text'),
  rrect(6.85, .55, 5.93, 6.2, { r: .3, fill: { color: P.white, transparency: 90 }, line: { color: P.white, transparency: 78, width: .75 } }),
  ph('picture', 'pic', 6.95, .65, 5.73, 6.0, { color: C.background1 }, 'Picture'),
  ...footer(true),
], slideNumber: num(true) });
// the brand guide's own page: a dark column for the heading, the content beside it
pres.defineSlideMaster({ title: 'Oyster Divided', background: bg('ground-light.jpg'), objects: [
  { image: { path: A + 'panel-deep.jpg', x: 0, y: 0, w: 3.7, h: 7.5 } },
  mark(true),
  ph('title', 'title', .6, 1.3, 2.75, 2.6, { fontFace: HEAD, fontSize: 30, color: C.background1, valign: 'top' }, 'Slide title'),
  ph('subtitle', 'body', .6, 4.0, 2.75, 1.4, { fontSize: 15, color: P.mint, valign: 'top' }, 'Subtitle'),
  ph('body', 'body', 4.1, 1.2, 8.6, 5.45, { fontSize: 17, color: P.abyss, valign: 'top', paraSpaceAfter: 8 }, 'Body text'),
  monoMark(true, .6, 6.98, .22),
  { text: { text: 'OYSTER THERAPEUTICS', options: { x: .9, y: 6.97, w: 2.6, h: .24, fontFace: MONO, fontSize: 8, charSpacing: 2.5, color: P.mint, margin: 0, valign: 'middle' } } },
  rrect(12.13, 6.92, .6, .34, { r: .17, fill: { color: P.abyss, transparency: 93 }, line: { type: 'none' } }),
], slideNumber: num(false) });
const cardX = i => .6 + i * 4.11;
pres.defineSlideMaster({ title: 'Oyster Three Cards', background: bg('ground-cards.jpg'), objects: [
  ...label(true, .6, .6),
  ph('title', 'title', .6, 1.05, 12.1, .8, { fontFace: HEAD, fontSize: 34, color: C.background1, valign: 'top' }, 'Slide title'),
  ...[0, 1, 2].flatMap(i => [
    glass(cardX(i), 2.25, 3.89, 4.35),
    { text: { text: '0' + (i + 1), options: { x: cardX(i) + .35, y: 2.6, w: 1, h: .4, fontFace: MONO, fontSize: 14, color: P.gold, margin: 0 } } },
    ph('card' + (i + 1) + 'Title', 'body', cardX(i) + .35, 3.25, 3.2, 1.0, { fontFace: HEAD, fontSize: 24, color: C.background1, valign: 'top' }, 'Card title'),
    ph('card' + (i + 1) + 'Body', 'body', cardX(i) + .35, 4.35, 3.2, 2.0, { fontSize: 15, color: P.seafoam, valign: 'top' }, 'Card text'),
  ]),
  ...footer(true),
], slideNumber: num(true) });
pres.defineSlideMaster({ title: 'Oyster Image', background: { color: P.abyss }, objects: [
  ph('picture', 'pic', 0, 0, 13.333, 7.5, { color: C.background1 }, 'Full-bleed picture'),
  // (no card behind the caption: a picture on the slide would sit over anything the layout draws)
  dot(.95, 5.2),
  ph('label', 'body', 1.17, 5.1, 5.5, .3, { fontFace: MONO, fontSize: 11, charSpacing: 2.5, color: P.mint, valign: 'middle' }, 'LABEL'),
  ph('caption', 'body', .95, 5.55, 5.8, 1.0, { fontFace: HEAD, fontSize: 24, color: C.background1, valign: 'top' }, 'Caption'),
] });
pres.defineSlideMaster({ title: 'Oyster Closing', background: bg('ground-closing.jpg'), objects: [
  { image: { path: A + 'logo-on-dark.png', x: 4.37, y: 1.6, w: 4.6, h: 4.6 * LOGO_AR } },
  ph('title', 'title', 1.2, 3.25, 10.93, 1.3, { fontFace: HEAD, fontSize: 40, color: C.background1, align: 'center', valign: 'top' }, 'Closing line'),
  ph('contact', 'body', 2.4, 4.8, 8.53, .9, { fontSize: 16, color: P.seafoam, align: 'center', valign: 'top' }, 'Contact details'),
] });

// ---------- the sample deck ----------
const sec = t => pres.addSection({ title: t });
const add = (master, section) => pres.addSlide({ masterName: master, sectionTitle: section });
const T = (s, name, text, o = {}) => s.addText(text, { placeholder: name, ...o });
const SELFTAC = 'SELFTAC®';
const contentsRows = (s, items, cur) => items.forEach((it, i) => {
  const y = 1.55 + i * .9, on = i === cur;
  s.addText('0' + (i + 1), { x: 4.7, y, w: .9, h: .9, isTextBox: true, fontFace: MONO, fontSize: 14, color: on ? P.gold : P.sage, margin: 0, valign: 'middle', objectName: 'Number ' + (i + 1) });
  s.addText(it, { x: 5.7, y, w: 7.0, h: .9, isTextBox: true, fontFace: HEAD, fontSize: 26, color: on ? P.white : P.sage, margin: 0, valign: 'middle', objectName: 'Item ' + (i + 1) });
  s.addShape(pres.shapes.LINE, { x: 4.7, y: y + .9, w: 8.03, h: 0, line: { color: P.sage, width: .5, dashType: 'sysDot', transparency: 30 }, objectName: 'Rule ' + (i + 1) });
});

sec('Opening');
let s = add('Oyster Title', 'Opening');
T(s, 'title', [{ text: 'Targeted protein degradation ', options: {} }, { text: 'beyond conventional limits', options: { color: P.mint } }]);
T(s, 'subtitle', 'Company overview · 2026');
T(s, 'meta', 'OYSTER THERAPEUTICS · CONFIDENTIAL');
s = add('Oyster Contents', 'Opening');
T(s, 'title', 'Contents');
contentsRows(s, ['The idea', 'The problem', `Our solution: the ${SELFTAC} platform`, 'Pipeline', 'Team'], 0);
s.addNotes('Contents layout: number, item and dotted rule are composed on the slide (copy a row to add one). The current item is white with a gold number.');
s = add('Oyster Statement', 'Opening');
T(s, 'label', 'THE IDEA');
T(s, 'title', [{ text: 'The function of a full degrader. ', options: {} }, { text: 'The distribution of a small molecule.', options: { color: P.gold } }]);
T(s, 'attribution', `${SELFTAC} platform`);

sec('Problem');
s = add('Oyster Section', 'Problem');
T(s, 'number', '02'); T(s, 'title', 'The problem'); T(s, 'intro', 'Why first-generation protein degraders are limited.');
s = add('Oyster Title Only Sea Foam', 'Problem');
T(s, 'title', 'Each type of degrader brings its own trade-off'); T(s, 'subtitle', 'First-generation degraders');
[['Bifunctional degraders', ['MODULAR', 'BULKY'], 'Modular components, but their large size limits oral bioavailability and penetration into tissues like the brain.'],
 ['Molecular glues', ['DRUG-LIKE', 'SERENDIPITOUS'], 'Smaller, with more favourable drug-like properties, but without the same rational, modular design approach.']].forEach(([t, tags, body], i) => {
  const x = .6 + i * 6.17;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.75, w: 5.96, h: 4.75, fill: { color: P.white }, rectRadius: .2, shadow: shadow(), objectName: 'Card ' + (i + 1) });
  s.addText(t, { x: x + .45, y: 2.2, w: 5.1, h: .6, isTextBox: true, fontFace: HEAD, fontSize: 28, color: C.text1, margin: 0, objectName: 'Card title ' + (i + 1) });
  tags.forEach((g, j) => s.addText(g, { x: x + .45 + j * 1.9, y: 3.05, w: 1.75, h: .38, shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: .19, fill: { color: j ? P.pink : P.ice },
    fontFace: MONO, fontSize: 10, charSpacing: 1.5, color: C.text1, align: 'center', valign: 'middle', margin: 0, objectName: 'Tag ' + g }));
  s.addText(body, { x: x + .45, y: 3.8, w: 5.1, h: 2.3, isTextBox: true, fontSize: 17, color: P.g3D, margin: 0, valign: 'top', objectName: 'Card text ' + (i + 1) });
});

sec('Our solution');
s = add('Oyster Section', 'Our solution');
T(s, 'number', '03'); T(s, 'title', `Our solution: the ${SELFTAC} platform`); T(s, 'intro', 'Degraders that travel as small molecules and self-assemble where they are needed.');
s = add('Oyster Three Cards', 'Our solution');
T(s, 'label', 'HOW IT WORKS'); T(s, 'title', 'Separate, assemble, degrade');
[['Separate', 'Degraders start as two small molecular halves that can cross the blood-brain barrier.'],
 ['Assemble', 'Inside the cell the halves clasp back together at a reversible linker.'],
 ['Degrade', 'Once assembled it works like a full degrader, and the cell clears the target protein.']].forEach(([t, b], i) => { T(s, 'card' + (i + 1) + 'Title', t); T(s, 'card' + (i + 1) + 'Body', b); });
s = add('Oyster Two Column', 'Our solution');
T(s, 'label', 'THE TERNARY COMPLEX'); T(s, 'title', 'Rebuilt inside the cell'); T(s, 'subtitle', 'One molecule holds the target to the ligase');
T(s, 'body', [{ text: 'One end holds the target protein, the other an E3 ligase.', options: { bullet: true, breakLine: true } },
  { text: 'The cell tags the target with ubiquitin and the proteasome breaks it down.', options: { bullet: true, breakLine: true } },
  { text: 'The degrader is not used up: it lets go and finds the next one.', options: { bullet: true } }]);
s.addImage({ placeholder: 'picture', path: A + 'complex-panel.png', w: 5.73, h: 6.0, sizing: { type: 'cover', w: 5.73, h: 6.0 }, altText: 'Ternary complex: target protein above, E3 ligase below, the SELFTAC degrader between, its clasp in gold' });
s.addNotes('Two Column layout: the picture sits in a rounded frame on a glass panel.');
s = add('Oyster Divided', 'Our solution');
T(s, 'title', 'Protein degradation, unlocked'); T(s, 'subtitle', 'Four things the platform changes');
[['High oral bioavailability', 'Make oral degraders the expectation, not the exception.'], ['Routine CNS penetration', 'Open the brain to protein degrader therapeutics.'],
 ['Faster discovery', 'Turn iterative chemistry into modular design with reusable components.'], ['New technology', 'Integrate emerging E3 ligases as they arrive.']].forEach(([t, b], i) => {
  const y = 1.2 + i * 1.38;
  s.addText('0' + (i + 1), { x: 4.1, y: y + .04, w: .8, h: .45, isTextBox: true, fontFace: MONO, fontSize: 14, color: P.kelp, margin: 0, valign: 'top', objectName: 'Number ' + (i + 1) });
  s.addText(t, { x: 5.0, y: y - .04, w: 7.7, h: .5, isTextBox: true, fontFace: HEAD, fontSize: 24, color: C.text1, margin: 0, valign: 'top', objectName: 'Feature ' + (i + 1) });
  s.addText(b, { x: 5.0, y: y + .52, w: 7.7, h: .45, isTextBox: true, fontSize: 16, color: P.g3D, margin: 0, valign: 'top', objectName: 'Feature text ' + (i + 1) });
  if (i < 3) s.addShape(pres.shapes.LINE, { x: 4.1, y: y + 1.17, w: 8.6, h: 0, line: { color: P.g85, width: .5, dashType: 'sysDot' }, objectName: 'Rule ' + (i + 1) });
});

sec('Pipeline');
s = add('Oyster Title Only Dark', 'Pipeline');
T(s, 'title', 'Discovery programmes'); T(s, 'subtitle', 'Pipeline');
const hd = t => ({ text: t, options: { fontFace: MONO, fontSize: 10, color: P.sage, charSpacing: 1.5 } });
const cl = (t, o = {}) => ({ text: t, options: { fontSize: 16, color: P.white, ...o } });
const stage = on => ({ text: on ? '●' : '○', options: { fontSize: 16, color: on ? P.gold : P.sage, align: 'center' } });
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: .6, y: 1.75, w: 12.13, h: 3.3, fill: { color: P.white, transparency: 92 }, line: { color: P.white, transparency: 80, width: .75 }, rectRadius: .2, objectName: 'Glass panel' });
s.addTable([[hd('THERAPEUTIC AREA'), hd('TARGETS'), hd('DISCOVERY'), hd('LEAD OPTIMISATION'), hd('PRECLINICAL'), hd('CLINICAL')],
  [cl('Oncology', { fontFace: HEAD, fontSize: 22 }), cl('Undisclosed', { color: P.mint }), stage(1), stage(0), stage(0), stage(0)],
  [cl('Central nervous system', { fontFace: HEAD, fontSize: 22 }), cl('Undisclosed', { color: P.mint }), stage(1), stage(0), stage(0), stage(0)]],
  { x: 1.0, y: 2.0, w: 11.33, colW: [3.4, 2.0, 1.48, 1.48, 1.48, 1.49], rowH: [.6, 1.0, 1.0], valign: 'middle', margin: [0, .1, 0, 0],
    border: [{ type: 'none' }, { type: 'none' }, { pt: .75, color: P.forest }, { type: 'none' }], fill: { color: P.abyss, transparency: 100 }, objectName: 'Pipeline table' });
s.addText('● stage reached   ○ to come', { x: .6, y: 5.3, w: 6, h: .3, isTextBox: true, fontFace: MONO, fontSize: 10, color: P.sage, margin: 0, objectName: 'Pipeline key' });
s.addNotes('Title Only (dark) layout: a glass panel with a native table on it; gold marks the stage reached.');
s = add('Oyster Title Only', 'Pipeline');
T(s, 'title', 'Numbers that carry the story'); T(s, 'subtitle', 'Illustrative figures');
[['$60M', 'Series A2 raised to take SELFTAC® to the clinic'], ['2', 'small halves that cross the blood-brain barrier'], ['1', 'degrader, reused target after target']].forEach(([n, l], i) => {
  const x = .6 + i * 4.11;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.9, w: 3.89, h: 3.9, fill: { color: P.seafoam }, rectRadius: .2, objectName: 'Stat card ' + (i + 1) });
  s.addText([{ text: n, options: {} }, { text: '.', options: { color: P.gold } }], { x: x + .4, y: 2.3, w: 3.2, h: 1.6, isTextBox: true, fontFace: HEAD, fontSize: 72, color: P.kelp, margin: 0, valign: 'bottom', objectName: 'Stat ' + (i + 1) });
  s.addText(l, { x: x + .4, y: 4.1, w: 3.1, h: 1.3, isTextBox: true, fontSize: 17, color: P.abyss, margin: 0, valign: 'top', objectName: 'Stat label ' + (i + 1) });
});
s.addNotes('Title Only layout with stat cards; the gold full stop on big figures is the house touch.');
s = add('Oyster Title Only Sea Foam', 'Pipeline');
T(s, 'title', 'Charts take the palette'); T(s, 'subtitle', 'Illustrative data');
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: .6, y: 1.65, w: 8.1, h: 4.95, fill: { color: P.white }, rectRadius: .2, shadow: shadow(), objectName: 'Chart card' });
s.addChart(pres.charts.BAR, [{ name: 'Free brain AUC', labels: ['Small-molecule benchmark', `${SELFTAC} monomer B`, `${SELFTAC} monomer A`, 'Full degrader'], values: [80, 71, 64, 8] }], {
  x: .9, y: 1.9, w: 7.5, h: 4.45, barDir: 'bar', chartColors: [P.sage, P.gold, P.gold, P.kelp], invertedColors: [P.sage, P.gold, P.gold, P.kelp], catAxisOrientation: 'maxMin', barGapWidthPct: 60,
  showValue: true, dataLabelPosition: 'outEnd', dataLabelColor: P.abyss, dataLabelFontSize: 13, dataLabelFontFace: '+mn-lt', showLegend: false,
  catAxisLabelColor: P.abyss, catAxisLabelFontSize: 13, catAxisLabelFontFace: '+mn-lt', valAxisHidden: true, valGridLine: { style: 'none' }, catGridLine: { style: 'none' },
  catAxisLineShow: false, objectName: 'Example chart' });
s.addText([{ text: 'Use the theme', options: { fontFace: HEAD, fontSize: 24, color: P.abyss, breakLine: true } },
  { text: 'Kelp for the data, gold for the one thing to look at, sage for comparators.', options: { fontSize: 16, color: P.g3D } }],
  { x: 9.2, y: 1.75, w: 3.5, h: 2.4, isTextBox: true, margin: 0, valign: 'top', paraSpaceAfter: 8, objectName: 'Chart note' });
s.addNotes('Illustrative values only. Charts sit on a white card on the Sea Foam ground.');
s = add('Oyster Title and Content', 'Pipeline');
T(s, 'title', 'Next steps'); T(s, 'subtitle', 'Title and Content layout');
T(s, 'body', [{ text: 'Confirm library activity with a clear mechanism of action', options: { bullet: true, breakLine: true } },
  { text: 'Expand the library and build structure-activity relationships', options: { bullet: true, breakLine: true } },
  { text: 'Show oral brain exposure above the free DC₅₀', options: { bullet: true } }]);

sec('Close');
s = add('Oyster Image', 'Close');
s.addImage({ placeholder: 'picture', path: A + 'complex-hero.png', w: 13.333, h: 7.5, altText: 'The SELFTAC ternary complex on the Abyss Green ground' });
T(s, 'label', `${SELFTAC} · TERNARY COMPLEX`); T(s, 'caption', 'One molecule holds the target to the ligase.');
s = add('Oyster Closing', 'Close');
T(s, 'title', [{ text: 'Targeted protein degradation ', options: {} }, { text: 'beyond conventional limits.', options: { color: P.mint } }]);
T(s, 'contact', 'info@oystertx.com  ·  London, United Kingdom  ·  oyster-tx.com');

(async () => {
  const f = __dirname + '/oyster-template-v3.pptx';
  await pres.writeFile({ fileName: f }); await applyTheme(f, THEME); console.log('wrote', f);
})();
