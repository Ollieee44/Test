// Oyster slide template v2: the brand guide's Colors.pdf palette (Abyss and Kelp greens, Sea Foam, gold and the soft
// accents) in the oyster-tx.com layout language, as PowerPoint slide layouts plus a sample deck that uses every one.
//   PPTX_SKILL=<pptx skill dir> node build_template.js   (after make_assets.py)
// Fonts are PowerPoint's own, so nothing needs installing: Georgia for headings, Arial for body text, Consolas for the
// small uppercase labels.
const pptxgen = require('pptxgenjs');
const { applyTheme } = require(process.env.PPTX_SKILL + '/scripts/apply_theme.js');
const A = __dirname + '/assets/';
const SZ = require('./assets/sizes.json'), ar = n => SZ[n][1] / SZ[n][0];

// the palette (Colors.pdf)
const P = { abyss0: '070D0A', abyss: '1A372A', forest: '2E6149', kelp: '408967', kelp2: '67B791', mint: 'BADECD', seafoam: 'EBEBE3',
  g3D: '3D3D3D', g66: '666666', g85: '858585', gC2: 'C2C2C2', gEB: 'EBEBEB', white: 'FFFFFF',
  gold: 'DCA84E', bronze: '99803C', pink: 'F0A6CA', mauve: 'A2839E', sage: '8AB0AB', teal: '3F7965', ice: 'CEE5F3', slate: '90A9B7' };
const THEME = {
  name: 'Oyster Therapeutics',
  headFontFace: 'Georgia', bodyFontFace: 'Arial',
  colors: { dk1: P.abyss, lt1: P.white, dk2: P.forest, lt2: P.seafoam,
    accent1: P.kelp, accent2: P.gold, accent3: P.kelp2, accent4: P.mauve, accent5: P.sage, accent6: P.pink,
    hlink: P.kelp, folHlink: P.bronze },
};
const MONO = 'Consolas', HEAD = THEME.headFontFace;
module.exports = { P, THEME };
if (require.main !== module) return;

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE';                       // 13.333 x 7.5 in
pres.title = 'Oyster Therapeutics template';
pres.author = 'Oyster Therapeutics';
pres.company = 'Oyster Therapeutics';
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;
const LOGO_AR = ar('logo-white.png'), MARK_AR = ar('mark-white.png');

// ---------- shared pieces ----------
const ph = (name, type, x, y, w, h, opts, prompt) => ({ placeholder: { options: { name, type, x, y, w, h, margin: 0, ...(type === 'title' ? { align: 'left' } : {}), ...opts }, text: prompt } });
// the brand guide's gradient edge down the left of every content page
const edge = { image: { path: A + 'edge.png', x: 0, y: 0, w: .13, h: 7.5 } };
const mark = (dark, x = .6, y = .5, h = .3) => ({ image: { path: A + (dark ? 'mark-white.png' : 'mark-abyss.png'), x, y, w: h / MARK_AR, h } });
const footer = dark => [
  mark(dark, .6, 7.0, .2),
  { text: { text: 'OYSTER THERAPEUTICS', options: { x: .9, y: 6.98, w: 4, h: .24, fontFace: MONO, fontSize: 8, charSpacing: 2, color: dark ? P.mint : P.forest, margin: 0, valign: 'middle' } } },
];
const num = (dark, x = 12.13) => ({ x, y: 6.98, w: .6, h: .24, fontFace: MONO, fontSize: 8, color: dark ? P.mint : P.forest, align: 'right' });
// content slides: the title sits high and compact so the slide is left for the content
const title = color => ph('title', 'title', .6, .34, 12.1, .62, { fontFace: HEAD, fontSize: 26, color, valign: 'top' }, 'Slide title');
const subtitle = color => ph('subtitle', 'body', .6, .98, 12.1, .36, { fontSize: 14, color, valign: 'top' }, 'Subtitle or one-line takeaway');

// ---------- slide layouts ----------
pres.defineSlideMaster({ title: 'Oyster Title', background: { path: A + 'complex-title.png' }, objects: [
  { image: { path: A + 'logo-white.png', x: .6, y: .6, w: 2.3, h: 2.3 * LOGO_AR } },
  ph('title', 'title', .6, 2.2, 7.4, 2.3, { fontFace: HEAD, fontSize: 48, color: C.background1, valign: 'bottom', lineSpacingMultiple: .95 }, 'Presentation title'),
  ph('subtitle', 'body', .6, 4.75, 7.2, .9, { fontSize: 20, color: P.gold, valign: 'top' }, 'Subtitle or date'),
  ph('meta', 'body', .6, 6.75, 8, .3, { fontFace: MONO, fontSize: 10, charSpacing: 2, color: P.mint, valign: 'middle' }, 'AUDIENCE · PRESENTER · CONFIDENTIAL'),
] });
pres.defineSlideMaster({ title: 'Oyster Contents', background: { color: P.abyss }, objects: [
  mark(true),
  ph('title', 'title', .6, 1.25, 6, .45, { fontSize: 16, color: P.sage, valign: 'bottom' }, 'Contents:'),
  ...footer(true),
], slideNumber: num(true) });
pres.defineSlideMaster({ title: 'Oyster Section', background: { color: P.abyss }, objects: [
  mark(true),
  ph('number', 'body', .6, 2.45, 3, .5, { fontFace: MONO, fontSize: 20, color: P.kelp2, valign: 'bottom' }, '01'),
  ph('title', 'title', .6, 3.05, 11.5, 1.4, { fontFace: HEAD, fontSize: 44, color: C.background1, valign: 'top' }, 'Section title'),
  ph('intro', 'body', .6, 4.6, 8.4, 1.0, { fontSize: 16, color: P.mint, valign: 'top' }, 'One or two lines on what this section covers'),
  ...footer(true),
], slideNumber: num(true) });
pres.defineSlideMaster({ title: 'Oyster Statement', background: { color: P.abyss }, objects: [
  edge, mark(true),
  ph('label', 'body', .6, 1.6, 8, .3, { fontFace: MONO, fontSize: 11, charSpacing: 2, color: P.gold, valign: 'middle' }, 'LABEL'),
  ph('title', 'title', .6, 2.05, 11.4, 3.2, { fontFace: HEAD, fontSize: 38, color: C.background1, valign: 'top', lineSpacingMultiple: 1.05 }, 'A single, large statement'),
  ph('attribution', 'body', .6, 5.5, 8, .5, { fontSize: 14, color: P.mint, valign: 'top' }, 'Source or attribution'),
  ...footer(true),
], slideNumber: num(true) });
const titleOnly = (name, bg, dark) => pres.defineSlideMaster({ title: name, background: { color: bg }, objects: [
  edge, title(dark ? P.white : P.abyss), subtitle(dark ? P.kelp2 : P.kelp), ...footer(dark),
], slideNumber: num(dark) });
titleOnly('Oyster Title Only', P.white, false);
titleOnly('Oyster Title Only Sea Foam', P.seafoam, false);
titleOnly('Oyster Title Only Dark', P.abyss, true);
pres.defineSlideMaster({ title: 'Oyster Blank', background: { color: P.white }, objects: [edge, ...footer(false)], slideNumber: num(false) });
pres.defineSlideMaster({ title: 'Oyster Title and Content', background: { color: P.white }, objects: [
  edge, title(P.abyss), subtitle(P.kelp),
  ph('body', 'body', .6, 1.65, 12.1, 5.0, { fontSize: 16, color: P.abyss, valign: 'top', paraSpaceAfter: 8 }, 'Body text'),
  ...footer(false),
], slideNumber: num(false) });
pres.defineSlideMaster({ title: 'Oyster Two Column', background: { color: P.white }, objects: [
  edge,
  ph('title', 'title', .6, .34, 5.9, .62, { fontFace: HEAD, fontSize: 26, color: P.abyss, valign: 'top' }, 'Slide title'),
  ph('subtitle', 'body', .6, .98, 5.9, .36, { fontSize: 14, color: P.kelp, valign: 'top' }, 'Subtitle'),
  ph('body', 'body', .6, 1.65, 5.9, 5.0, { fontSize: 16, color: P.abyss, valign: 'top', paraSpaceAfter: 8 }, 'Body text'),
  { rect: { x: 7.0, y: 0, w: 6.333, h: 7.5, fill: { color: P.abyss } } },
  ph('picture', 'pic', 7.0, 0, 6.333, 7.5, { color: C.background1 }, 'Picture'),
  ...footer(false),
], slideNumber: num(true) });
// the brand guide's own page: a narrow left column for the heading, a dashed rule, the content to its right
pres.defineSlideMaster({ title: 'Oyster Divided', background: { color: P.seafoam }, objects: [
  edge, mark(false),
  ph('title', 'title', .6, 1.2, 2.75, 2.4, { fontFace: HEAD, fontSize: 26, color: P.abyss, valign: 'top' }, 'Slide title'),
  ph('subtitle', 'body', .6, 3.7, 2.75, 1.4, { fontSize: 14, color: P.kelp, valign: 'top' }, 'Subtitle'),
  { line: { x: 3.7, y: .5, w: 0, h: 6.25, line: { color: P.g85, width: .75, dashType: 'dash' } } },
  ph('body', 'body', 4.1, 1.2, 8.6, 5.45, { fontSize: 16, color: P.abyss, valign: 'top', paraSpaceAfter: 8 }, 'Body text'),
  ...footer(false),
], slideNumber: num(false) });
pres.defineSlideMaster({ title: 'Oyster Image', background: { color: P.abyss }, objects: [
  ph('picture', 'pic', 0, 0, 13.333, 7.5, { color: C.background1 }, 'Full-bleed picture'),
  { rect: { x: .6, y: 4.95, w: 6.4, h: 1.8, fill: { color: P.abyss, transparency: 12 }, rectRadius: 0 } },
  ph('label', 'body', .9, 5.2, 5.8, .3, { fontFace: MONO, fontSize: 11, charSpacing: 2, color: P.gold, valign: 'middle' }, 'LABEL'),
  ph('caption', 'body', .9, 5.6, 5.8, 1.0, { fontFace: HEAD, fontSize: 22, color: C.background1, valign: 'top' }, 'Caption'),
] });
pres.defineSlideMaster({ title: 'Oyster Closing', background: { color: P.abyss }, objects: [
  { image: { path: A + 'logo-white.png', x: 4.77, y: 1.85, w: 3.8, h: 3.8 * LOGO_AR } },
  ph('title', 'title', 1.4, 3.35, 10.53, 1.2, { fontFace: HEAD, fontSize: 32, color: C.background1, align: 'center', valign: 'top' }, 'Closing line'),
  ph('contact', 'body', 2.4, 4.75, 8.53, .9, { fontSize: 14, color: P.mint, align: 'center', valign: 'top' }, 'Contact details'),
] });

// ---------- the sample deck ----------
const sec = t => pres.addSection({ title: t });
const add = (master, section) => pres.addSlide({ masterName: master, sectionTitle: section });
const T = (s, name, text, o = {}) => s.addText(text, { placeholder: name, ...o });
const SELFTAC = 'SELFTAC®';
// a contents list in the brand guide's style: mono number, serif item, dotted rule under each; the current item in white
const contentsRows = (s, items, cur, y0 = 1.95, rowH = .58) => items.forEach((it, i) => {
  const y = y0 + i * rowH, on = i === cur;
  s.addText(String(i + 1).padStart(2, '0'), { x: .6, y, w: .9, h: rowH, isTextBox: true, fontFace: MONO, fontSize: 14, color: P.sage, margin: 0, valign: 'middle', objectName: 'Number ' + (i + 1) });
  s.addText(it, { x: 1.85, y, w: 10.8, h: rowH, isTextBox: true, fontFace: HEAD, fontSize: 20, color: on ? P.white : P.sage, margin: 0, valign: 'middle', objectName: 'Item ' + (i + 1) });
  s.addShape(pres.shapes.LINE, { x: .6, y: y + rowH, w: 12.13, h: 0, line: { color: P.sage, width: .5, dashType: 'sysDot', transparency: 40 }, objectName: 'Rule ' + (i + 1) });
});

sec('Opening');
let s = add('Oyster Title', 'Opening');
T(s, 'title', 'Targeted protein degradation beyond conventional limits');
T(s, 'subtitle', 'Company overview · 2026');
T(s, 'meta', 'OYSTER THERAPEUTICS · CONFIDENTIAL');
s.addNotes('Title layout. The background is the SELFTAC ternary complex from the journey animation on the Abyss Green ground.');
s = add('Oyster Contents', 'Opening');
T(s, 'title', 'Contents:');
contentsRows(s, ['The idea', 'The problem', `Our solution: the ${SELFTAC} platform`, 'Pipeline', 'Team'], 0);
s.addNotes('Contents layout: number, item and dotted rule are composed on the slide (copy a row to add one). Set the current item in white.');
s = add('Oyster Statement', 'Opening');
T(s, 'label', 'THE IDEA');
T(s, 'title', [{ text: 'The function of a full degrader. ', options: {} }, { text: 'The distribution of a small molecule.', options: { color: P.gold } }]);
T(s, 'attribution', `${SELFTAC} platform`);

sec('Problem');
s = add('Oyster Section', 'Problem');
T(s, 'number', '02'); T(s, 'title', 'The problem'); T(s, 'intro', 'Why first-generation protein degraders are limited.');
s = add('Oyster Title Only', 'Problem');
T(s, 'title', 'Each type of degrader brings its own trade-off'); T(s, 'subtitle', 'First-generation degraders');
[['Bifunctional degraders', ['MODULAR', 'BULKY'], 'Modular components, but their large size limits oral bioavailability and penetration into tissues like the brain.'],
 ['Molecular glues', ['DRUG-LIKE', 'SERENDIPITOUS'], 'Smaller, with more favourable drug-like properties, but without the same rational, modular design approach.']].forEach(([t, tags, body], i) => {
  const x = .6 + i * 6.12;
  s.addShape(pres.shapes.RECTANGLE, { x, y: 1.75, w: 5.95, h: 4.7, fill: { color: P.seafoam }, objectName: 'Card ' + (i + 1) });
  s.addText(t, { x: x + .4, y: 2.15, w: 5.2, h: .6, isTextBox: true, fontFace: HEAD, fontSize: 24, color: C.text1, margin: 0, objectName: 'Card title ' + (i + 1) });
  tags.forEach((g, j) => s.addText(g, { x: x + .4 + j * 1.85, y: 2.95, w: 1.7, h: .36, shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: .18, fill: { color: j ? P.pink : P.ice },
    fontFace: MONO, fontSize: 10, charSpacing: 1.5, color: C.text1, align: 'center', valign: 'middle', margin: 0, objectName: 'Tag ' + g }));
  s.addText(body, { x: x + .4, y: 3.65, w: 5.2, h: 2.4, isTextBox: true, fontSize: 16, color: C.text1, margin: 0, valign: 'top', objectName: 'Card text ' + (i + 1) });
});
s.addNotes('Title Only layout with two comparison cards on Sea Foam, composed on the slide.');

sec('Our solution');
s = add('Oyster Section', 'Our solution');
T(s, 'number', '03'); T(s, 'title', `Our solution: the ${SELFTAC} platform`); T(s, 'intro', 'Degraders that travel as small molecules and self-assemble where they are needed.');
s = add('Oyster Two Column', 'Our solution');
T(s, 'title', 'Rebuilt inside the cell'); T(s, 'subtitle', 'The ternary complex');
T(s, 'body', [{ text: 'One end holds the target protein, the other an E3 ligase.', options: { bullet: true, breakLine: true } },
  { text: 'The cell tags the target with ubiquitin and the proteasome breaks it down.', options: { bullet: true, breakLine: true } },
  { text: 'The degrader is not used up: it lets go and finds the next one.', options: { bullet: true } }]);
s.addImage({ placeholder: 'picture', path: A + 'complex-panel.png', w: 6.333, h: 7.5, altText: 'Ternary complex: target protein above, E3 ligase below, the SELFTAC degrader between, its clasp in gold' });
s.addNotes('Two Column layout: a full-height picture on the right, on an Abyss Green panel.');
s = add('Oyster Divided', 'Our solution');
T(s, 'title', 'Protein degradation, unlocked'); T(s, 'subtitle', 'Four things the platform changes');
[['High oral bioavailability', 'Make oral degraders the expectation, not the exception.'], ['Routine CNS penetration', 'Open the brain to protein degrader therapeutics.'],
 ['Faster discovery', 'Turn iterative chemistry into modular design with reusable components.'], ['New technology', 'Integrate emerging E3 ligases as they arrive.']].forEach(([t, b], i) => {
  const y = 1.2 + i * 1.38;
  s.addText('0' + (i + 1), { x: 4.1, y, w: .8, h: .45, isTextBox: true, fontFace: MONO, fontSize: 14, color: P.kelp, margin: 0, valign: 'top', objectName: 'Number ' + (i + 1) });
  s.addText(t, { x: 5.0, y: y - .04, w: 7.7, h: .5, isTextBox: true, fontFace: HEAD, fontSize: 22, color: C.text1, margin: 0, valign: 'top', objectName: 'Feature ' + (i + 1) });
  s.addText(b, { x: 5.0, y: y + .5, w: 7.7, h: .45, isTextBox: true, fontSize: 15, color: P.g3D, margin: 0, valign: 'top', objectName: 'Feature text ' + (i + 1) });
  if (i < 3) s.addShape(pres.shapes.LINE, { x: 4.1, y: y + 1.17, w: 8.6, h: 0, line: { color: P.g85, width: .5, dashType: 'sysDot' }, objectName: 'Rule ' + (i + 1) });
});
s.addNotes("Divided layout, after the brand guide's own pages: the heading in a narrow column, a dashed rule, the content to its right.");

sec('Pipeline');
s = add('Oyster Title Only Dark', 'Pipeline');
T(s, 'title', 'Discovery programmes'); T(s, 'subtitle', 'Pipeline');
const hd = t => ({ text: t, options: { fontFace: MONO, fontSize: 10, color: P.sage, charSpacing: 1.5 } });
const cl = (t, o = {}) => ({ text: t, options: { fontSize: 16, color: P.white, ...o } });
const stage = on => ({ text: on ? '●' : '○', options: { fontSize: 16, color: on ? P.gold : P.sage, align: 'center' } });
s.addTable([[hd('THERAPEUTIC AREA'), hd('TARGETS'), hd('DISCOVERY'), hd('LEAD OPTIMISATION'), hd('PRECLINICAL'), hd('CLINICAL')],
  [cl('Oncology', { fontFace: HEAD, fontSize: 20 }), cl('Undisclosed', { color: P.mint }), stage(1), stage(0), stage(0), stage(0)],
  [cl('Central nervous system', { fontFace: HEAD, fontSize: 20 }), cl('Undisclosed', { color: P.mint }), stage(1), stage(0), stage(0), stage(0)]],
  { x: .6, y: 1.9, w: 12.13, colW: [3.4, 2.2, 1.63, 1.63, 1.63, 1.64], rowH: [.6, .95, .95], valign: 'middle', margin: [0, .1, 0, 0],
    border: [{ type: 'none' }, { type: 'none' }, { pt: .75, color: P.forest }, { type: 'none' }], fill: { color: P.abyss, transparency: 100 }, objectName: 'Pipeline table' });
s.addText('● stage reached   ○ to come', { x: .6, y: 4.75, w: 6, h: .3, isTextBox: true, fontFace: MONO, fontSize: 10, color: P.sage, margin: 0, objectName: 'Pipeline key' });
s.addNotes('Title Only (dark) layout with a native table; gold marks the stage reached.');
s = add('Oyster Title Only Sea Foam', 'Pipeline');
T(s, 'title', 'Charts take the palette'); T(s, 'subtitle', 'Illustrative data');
s.addChart(pres.charts.BAR, [{ name: 'Free brain AUC', labels: ['Small-molecule benchmark', `${SELFTAC} monomer B`, `${SELFTAC} monomer A`, 'Full degrader'], values: [80, 71, 64, 8] }], {
  x: .6, y: 1.6, w: 7.6, h: 5.1, barDir: 'bar', chartColors: [P.sage, P.gold, P.gold, P.kelp], invertedColors: [P.sage, P.gold, P.gold, P.kelp], catAxisOrientation: 'maxMin',
  showValue: true, dataLabelPosition: 'outEnd', dataLabelColor: P.abyss, dataLabelFontSize: 12, dataLabelFontFace: '+mn-lt', showLegend: false,
  catAxisLabelColor: P.abyss, catAxisLabelFontSize: 12, catAxisLabelFontFace: '+mn-lt', valAxisHidden: true, valGridLine: { style: 'none' }, catGridLine: { style: 'none' },
  catAxisLineShow: false, objectName: 'Example chart' });
s.addText([{ text: 'Use the theme', options: { fontFace: HEAD, fontSize: 22, color: P.abyss, breakLine: true } },
  { text: 'Kelp for the data, gold for the one thing to look at, sage for comparators. Text is Arial, labels Consolas.', options: { fontSize: 15, color: P.g3D } }],
  { x: 8.8, y: 1.75, w: 3.9, h: 2.2, isTextBox: true, margin: 0, valign: 'top', paraSpaceAfter: 8, objectName: 'Chart note' });
s.addNotes('Illustrative values only.');
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
T(s, 'title', [{ text: 'Targeted protein degradation ', options: {} }, { text: 'beyond conventional limits.', options: { color: P.gold } }]);
T(s, 'contact', 'info@oystertx.com  ·  London, United Kingdom  ·  oyster-tx.com');

(async () => {
  const f = __dirname + '/oyster-template-v2.pptx';
  await pres.writeFile({ fileName: f }); await applyTheme(f, THEME); console.log('wrote', f);
})();
