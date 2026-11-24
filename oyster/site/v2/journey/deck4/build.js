// The v4 journey as a PowerPoint Morph deck: the page's autoplay sampled about every 0.3 s (the end card left out), every element where v4 has it,
// one "!!" name per element across slides so Morph glides it from step to step. Brand colours (Colors.pdf: the
// emerald greens, sand, gold), otherwise neutral: blank layout, theme fonts (+mj/+mn, so a template's fonts take
// over), no logo, footer or slide numbers, so slides can be pasted into a final template deck.
//   node build.js   (after export.js and prep.py; writes stage1.pptx, then post.py adds Morph)
const pptxgen = require('pptxgenjs'); const fs = require('fs');
const HERE = __dirname + '/', D = HERE + 'out/', C = D + 'c/';
const keys = JSON.parse(fs.readFileSync(D + 'keys.json', 'utf8')).keys.sort((a, b) => a.k - b.k), prep = JSON.parse(fs.readFileSync(D + 'prep.json', 'utf8'));
const PX = 13.333 / prep.W, PT = PX * 72;               // page px (1920 x 1080) to inches, to points
const UP = 1.3;                                         // labels and eyebrows a little larger than the page, for a projected slide
const COL = { ink: 'EBEBE3', mint: '67B791', pale: 'BADECD', line: '408967', label: '070D0A', ground: '1A372A' };
const HEAD = '+mj-lt', BODY = '+mn-lt';
const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE'; pres.title = 'How a SELFTAC® degrader works';
pres.theme = { headFontFace: 'Aptos Display', bodyFontFace: 'Aptos' };
const r3 = v => Math.round(v * 1000) / 1000;
const box = ([x, y, w, h]) => ({ x: r3(x * PX), y: r3(y * PX), w: r3(w * PX), h: r3(h * PX) });
const grow = ([x, y, w, h], f) => { const W = w * f, H = h * f, X = Math.min(Math.max(x + w / 2 - W / 2, 12), prep.W - 12 - W), Y = Math.min(Math.max(y + h / 2 - H / 2, 12), prep.H - 12 - H); return [X, Y, W, H]; };   // grown about its centre, kept on the slide
const ALT = { mol: 'SELFTAC® dimer', molA: 'SELFTAC® monomer', molB: 'SELFTAC® monomer', poi: 'Target protein', e3: 'E3 ligase complex', ub: 'Ubiquitin',
  proteasome: 'Proteasome', debris: 'Fragments of the degraded target protein', flash: 'The clasp opening', c: 'SELFTAC® molecule' };
const ORDER = n => n.startsWith('c') && /\d/.test(n[1]) ? 0 : ({ proteasome: 1, debris: 2, flash: 2, e3: 3, poi: 4, ub: 5, mol: 6, molA: 6, molB: 6 })[n] ?? 7;
const slug = t => t.toLowerCase().replace(/®/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
const ok = r => r[2] > 2 && r[3] > 2 && r[0] > -r[2] && r[1] > -r[3] && r[0] < prep.W && r[1] < prep.H;
keys.forEach((k, n) => {
  const s = pres.addSlide(); s.background = { color: COL.ground };
  s.addImage({ path: `${C}k${n}_bg.jpg`, x: 0, y: 0, w: 13.333, h: 7.5, objectName: '!!ground', altText: 'Background' });
  // the 3D elements, back to front
  Object.entries(prep.keys[n].els).filter(([name]) => name !== 'flash')   // the split's gold ring stays out: it sat still while the halves moved
    .sort((a, b) => ORDER(a[0]) - ORDER(b[0])).forEach(([name, r]) =>
    s.addImage({ path: `${C}k${n}_${name}.png`, ...box(r), objectName: '!!' + name, altText: ALT[name] || ALT.c }));
  // labels: dark pills with a green rule, as on the page
  const seen = {};
  k.labels.filter(l => ok(l.r)).forEach(l => {
    const plain = l.css.bg === 'rgba(0, 0, 0, 0)', id = slug(l.text) || 'plus'; seen[id] = (seen[id] || 0) + 1;
    const opts = { ...box(grow(l.r, UP)), align: 'center', valign: 'middle', margin: 0, fontFace: BODY, color: COL.ink, isTextBox: true,
      fontSize: r3(l.css.size * PT * UP), bold: +l.css.weight >= 600, charSpacing: r3(parseFloat(l.css.ls || 0) * PT * UP) || 0,
      objectName: '!!label-' + id + (seen[id] > 1 ? '-' + seen[id] : '') };
    if (!plain) Object.assign(opts, { shape: pres.ShapeType.roundRect, rectRadius: r3(l.css.radius * PX * UP), fill: { color: COL.label },
      line: { color: COL.line, width: .75 } });
    s.addText(l.text.replace('⇌', '⇌'), opts);
  });
  // the copy, where the page sets it
  const c = k.copy || keys.slice(n).find(q => q.copy).copy;   // an in-between moment keeps the next step's copy
  if (c) {
    s.addText([{ text: c.num.replace(/[^0-9]/g, '') + '  ', options: { color: COL.mint } }, { text: c.kicker.toUpperCase(), options: { color: COL.ink } }],
      { ...box([c.kR[0], c.kR[1] - 6, 700, c.kR[3] * UP]), fontFace: BODY, fontSize: r3(c.kCss.size * PT * UP), charSpacing: 1.5, margin: 0, valign: 'middle', isTextBox: true, objectName: '!!eyebrow' });
    // headline and its line of body copy in one box, so the body always follows the headline however the font wraps it
    const runs = [{ text: c.head, options: { fontFace: HEAD, fontSize: r3(c.hCss.size * PT), color: COL.ink, lineSpacingMultiple: .95, breakLine: !!c.body } }];
    if (c.body) runs.push({ text: c.body, options: { fontFace: BODY, fontSize: r3(c.pCss.size * PT * UP), color: COL.pale, paraSpaceBefore: 10 } });
    s.addText(runs, { ...box([c.hR[0], c.hR[1], c.hR[2] + 40, 1080 - 120 - c.hR[1]]), margin: 0, valign: 'top', isTextBox: true, objectName: '!!heading' });
    if (k.stop !== null && k.stop !== undefined) s.addNotes(`Step ${k.stop + 1}: ${c.num} ${c.kicker}. ${c.head}${c.body ? ' ' + c.body : ''}`);
  }
});
// each slide's Morph lasts the time since the previous frame; the steps (stops) are where a click is awaited
fs.writeFileSync(D + 'timing.json', JSON.stringify(keys.map(k => ({ dur: Math.round(k.dur || 0), stop: k.stop ?? null }))));
pres.writeFile({ fileName: HERE + 'stage1.pptx' }).then(f => console.log('wrote', f));
