// Build the PowerPoint version of the journey (the oyster-tx.com version): one slide per keyframe, every element
// placed where the web animation has it, with one "!!" name across slides so Morph glides, scales and turns it from
// slide to slide. The copy, labels, rail and end card are native, editable text and shapes.
//   node build_deck.js            (after export_deck.js and prep_deck.py; writes stage1.pptx, then post_deck.py)
// Fonts: the closest that ship with PowerPoint. Georgia for Newsreader (headings), Aptos for Geist (body),
// Consolas for Geist Mono and Monomaniac One (labels, step numbers).
const pptxgen = require('pptxgenjs'); const fs = require('fs');
const HERE = __dirname + '/', D = HERE + 'out/', C = D + 'c/';
const data = JSON.parse(fs.readFileSync(D + 'prep.json', 'utf8'));
const { refs, flats, keys, crops } = data;
const PX = 13.333 / 1440;                      // page px (1440 x 810 viewport) to inches
const PT = 13.333 * 72 / 1440;                 // page px to points (0.667)
const F = { head: 'Georgia', body: 'Aptos', mono: 'Consolas' };
const INK = 'F5FFFC', MINT = '30FCBA', GOLD = 'F7D16B', MUTED = 'A8D8C6';

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE';
pres.title = 'SELFTAC journey';
pres.author = 'Oyster Therapeutics';
pres.theme = { headFontFace: F.head, bodyFontFace: F.body };

const r2 = v => Math.round(v * 1000) / 1000;
const tr = o => Math.max(0, Math.min(100, Math.round((1 - o) * 100)));
const box = (x, y, w, h) => ({ x: r2(x * PX), y: r2(y * PX), w: r2(Math.max(1, w) * PX), h: r2(Math.max(1, h) * PX) });

// a 3D element: placed by its anchor, scaled and turned by its frame's unit x (see export_page.js)
function place3d(slide, name, e, o) {
  const ref = refs[e.img], c = crops[e.img];
  const lr = Math.hypot(...ref.v), lk = Math.hypot(...e.v); if (!lr || !lk) return;
  const f = lk / lr, d = Math.atan2(e.v[1], e.v[0]) - Math.atan2(ref.v[1], ref.v[0]);
  const ox = c.w / 2 - (ref.A[0] - c.x0), oy = c.h / 2 - (ref.A[1] - c.y0);
  const cx = e.A[0] + f * (ox * Math.cos(d) - oy * Math.sin(d)), cy = e.A[1] + f * (ox * Math.sin(d) + oy * Math.cos(d));
  const w = c.w * f, h = c.h * f, deg = ((d * 180 / Math.PI) % 360 + 360) % 360;
  slide.addImage({ path: C + e.img + '.png', ...box(cx - w / 2, cy - h / 2, w, h), rotate: r2(deg), transparency: tr(o), objectName: '!!' + name, altText: ALT[name.replace(/\d+$/, '')] || name });
}
const ALT = { halfW: 'SELFTAC half that binds the target protein', halfE: 'SELFTAC half that binds the E3 ligase', dimerG: 'SELFTAC dimer', dimerC: 'SELFTAC degrader, joined',
  brd4: 'Target protein (BRD4)', vhl: 'E3 ligase (VHL)', elob: 'Elongin B', eloc: 'Elongin C', prot: 'Proteasome', ub: 'Ubiquitin', frag: 'Fragment of the target protein' };
// a flat piece: its world rectangle through the page's world-to-screen matrix
function placeFlat(slide, id, k, o, alt) {
  const f = flats[id], [x0, y0, x1, y1] = f.rect, w = k.world;
  slide.addImage({ path: C + id + '.png', ...box(w.k * x0 + w.tx, -w.k * y1 + w.ty, w.k * (x1 - x0), w.k * (y1 - y0)), transparency: tr(o), objectName: '!!' + id, altText: alt });
}
function placePill(slide, k, o) {
  const [px, py, rot, s] = k.pill, f = flats.jpill, [x0, y0, x1, y1] = f.rect, w = k.world;
  const ww = w.k * s * (x1 - x0), hh = w.k * s * (y1 - y0), cx = w.k * (px + (x0 + x1) / 2 * s) + w.tx, cy = -w.k * (py + (y0 + y1) / 2 * s) + w.ty;
  slide.addImage({ path: C + 'jpill.png', ...box(cx - ww / 2, cy - hh / 2, ww, hh), rotate: r2(((-rot % 360) + 360) % 360), transparency: tr(o), objectName: '!!pill', altText: 'Capsule' });
}

const ORDER3D_BACK = ['prot', ...Array.from({ length: 18 }, (_, i) => 'frag' + i), 'dimerG', 'dimerC', 'halfW', 'halfE'];
const ORDER3D_FRONT = ['vhl', 'elob', 'eloc', 'brd4', 'ub0', 'ub1', 'ub2', 'ub3'];
const FLAT_ORDER = [['jbeam', 'Absorption from the gut'], ['jmem', 'Cell membrane and blood-brain barrier'], ['jperson', 'A person, in profile'], ['jroute', 'Route of the capsule'],
  ['jgut', 'Gut inset'], ['jtract', 'Gastrointestinal tract'], ['jgutring', '']];
const slug = s => s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

keys.forEach((k, si) => {
  const s = pres.addSlide();
  s.background = { path: C + k.ground + '.png' };
  // the speckle, drifting with the camera
  s.addImage({ path: C + 'stars.png', ...box(k.stars[0] - 300, k.stars[1] - 300, crops.stars.w, crops.stars.h), transparency: 10, objectName: '!!stars', altText: 'Speckled background' });
  // the flat illustration
  FLAT_ORDER.forEach(([id, alt]) => { const o = k.flatO[id]; if (o > .03) placeFlat(s, id, k, o, alt); });
  if (k.flatO.jpill > .03) placePill(s, k, k.flatO.jpill);
  // the 3D elements
  const sceneO = k.sceneO;
  ORDER3D_BACK.forEach(n => { if (k.els[n]) place3d(s, n, k.els[n], sceneO); });
  ORDER3D_FRONT.forEach(n => { if (k.els[n]) place3d(s, n, k.els[n], sceneO); });
  // the bond's flash
  if (k.flash && k.flash.o > .05) {
    const r = k.flash.r;
    s.addShape(pres.shapes.OVAL, { ...box(k.flash.A[0] - r, k.flash.A[1] - r, 2 * r, 2 * r), fill: { type: 'none' }, line: { color: GOLD, width: 2.5, transparency: tr(k.flash.o) }, objectName: '!!flash' });
  }
  // labels (and the reversible arrows, and the + between the monomers)
  k.labels.forEach(l => {
    const [x, y, w, h] = l.r, name = '!!lbl-' + (l.id || slug(l.text));
    if (l.id === 'jeq') { s.addImage({ path: C + 'eq.png', ...box(x, y, w, h), objectName: name, altText: 'Reversible arrows' }); return; }
    if (l.id === 'jplus') { s.addText('+', { ...box(x - 8, y - 6, w + 16, h + 12), isTextBox: true, fontFace: F.head, fontSize: 24, color: INK, align: 'center', valign: 'middle', margin: 0, objectName: name }); return; }
    s.addText(l.text.toUpperCase(), { ...box(x - 2, y, w + 4, h), isTextBox: true, shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: .04, fill: { color: '0C5C40', transparency: 45 },
      fontFace: F.mono, fontSize: 7.5, charSpacing: 1.2, color: l.cls.includes('hi') ? MINT : INK, align: 'center', valign: 'middle', margin: 0, objectName: name });
  });
  // the copy: step number and name, headline, line
  if (k.copy) {
    const c = k.copy;
    s.addText([{ text: c.num + '  ', options: { color: '8AC3B1' } }, { text: c.kicker.toUpperCase(), options: { color: INK } }],
      { ...box(c.kR[0], c.kR[1] - 4, 420, c.kR[3] + 8), isTextBox: true, fontFace: F.mono, fontSize: 10, bold: true, margin: 0, valign: 'middle', objectName: '!!copyK' + c.i });
    s.addText(c.head, { ...box(c.hR[0], c.hR[1], c.hR[2] * 1.12, c.hR[3] * 1.1), isTextBox: true, fontFace: F.head, fontSize: Math.round(c.hSize * PT), color: 'FFFFFF', margin: 0, valign: 'top', paraSpaceAfter: 0, lineSpacingMultiple: .95, objectName: '!!copyH' + c.i });
    s.addText(c.body, { ...box(c.pR[0], c.pR[1], c.pR[2] * 1.08, c.pR[3] * 1.15), isTextBox: true, fontFace: F.body, fontSize: Math.max(10, Math.round(c.pSize * PT)), color: 'D6EFE6', margin: 0, valign: 'top', objectName: '!!copyB' + c.i });
  }
  // the rail: a pearl per step, filled once it is reached, the fourth (the clasp closing) in gold
  if (!k.end) k.rail.forEach((d, i) => {
    const [sx, sy, sw, sh] = d.sR, cy = sy - 13, dia = i === 3 ? 13 : 11;
    if (i < k.rail.length - 1) {
      const nx = k.rail[i + 1].sR[0];
      s.addShape(pres.shapes.LINE, { ...box(sx + dia + 5, cy, nx - sx - dia - 10, 0), line: { color: k.rail[i + 1].on ? MINT : INK, width: 1, transparency: k.rail[i + 1].on ? 0 : 75 }, objectName: '!!railL' + i });
    }
    s.addShape(pres.shapes.OVAL, { ...box(sx, cy - dia / 2, dia, dia), fill: d.on ? { color: i === 3 ? GOLD : 'FFFFFF' } : { type: 'none' }, line: { color: d.on ? (i === 3 ? GOLD : 'FFFFFF') : INK, width: 1, transparency: d.on ? 0 : 50 }, objectName: '!!railC' + i });
    s.addText(d.label.toUpperCase(), { ...box(sx, sy, 140, sh), isTextBox: true, fontFace: F.mono, fontSize: 8, bold: true, charSpacing: .6, color: INK, margin: 0, valign: 'middle', objectName: '!!railT' + i });
  });
  // the end card
  if (k.end) {
    const e = k.end;
    s.addImage({ path: C + 'logo.png', ...box(e.logo[0], e.logo[1], e.logo[2], e.logo[2] * crops.logo.h / crops.logo.w), objectName: '!!logo', altText: 'Oyster Therapeutics logo' });
    const parts = e.tagText.split('beyond');
    s.addText([{ text: parts[0], options: { color: 'FFFFFF' } }, { text: 'beyond' + parts[1], options: { color: MINT } }],
      { ...box(e.tag[0] + e.tag[2] / 2 - 600, e.tag[1], 1200, e.tag[3] * 1.15), isTextBox: true, fontFace: F.head, fontSize: Math.round(e.tagSize * PT), align: 'center', valign: 'middle', margin: 0, objectName: '!!tag' });
    s.addText('Watch again', { ...box(e.btn[0], e.btn[1], e.btn[2], e.btn[3]), shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: .08, fill: { color: 'FFFFFF', transparency: 83 },
      line: { color: 'FFFFFF', transparency: 88, width: .75 }, fontFace: F.body, fontSize: 10, color: 'FFFFFF', align: 'center', valign: 'middle', margin: 0, hyperlink: { slide: 1, tooltip: 'Back to the start' }, objectName: '!!again' });
    s.addText(e.ecrText, { ...box(e.ecr[0] - 30, e.ecr[1], e.ecr[2] + 60, e.ecr[3] * 1.3), isTextBox: true, fontFace: F.body, fontSize: 8, color: MUTED, align: 'center', valign: 'top', margin: 0, objectName: '!!credit' });
  }
  s.addNotes(`Keyframe ${si + 1} of ${keys.length} (journey progress ${k.p}). ${k.copy ? k.copy.head + ' ' + k.copy.body : ''}`);
});

// timings for post_deck.py: each Morph lasts in proportion to the scroll it covers
const timing = keys.map((k, i) => { if (i === 0) return null; const dp = k.p - keys[i - 1].p; return Math.round(Math.max(700, Math.min(2200, dp * 26000))); });
fs.writeFileSync(D + 'timing.json', JSON.stringify(timing));
pres.writeFile({ fileName: HERE + 'stage1.pptx' }).then(f => console.log('wrote', f, keys.length, 'slides'));
