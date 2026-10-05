// Build the SELFTAC Morph deck (oyster-selftac-morph.pptx).
//
// 1. Exporter page (exporter.html, headless Chromium): the story's parts, built with the website's own
//    geometry, exported as .glb models, plus a still of each part at each slide's viewing angle.
// 2. pptxgenjs: nine keyframe slides. Each part is placed as a named picture (its still); same name on
//    every slide, so Morph pairs them.
// 3. post.py: every one of those pictures becomes an embedded 3D model (the still stays as the fallback
//    for apps without 3D support), and every slide gets the Morph transition.
//
// Run: NODE_PATH=<dir with pptxgenjs and playwright> node build.js <three.js package dir> <out dir>
const fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const pptxgen = require('pptxgenjs');
const HERE = __dirname, LANDING = path.join(HERE, '../landing');
const THREE_DIR = process.argv[2], OUT = process.argv[3] || HERE;
const ASSETS = path.join(OUT, 'assets'); fs.mkdirSync(ASSETS, { recursive: true });

const FIT = .89;              // share of a model's frame its bounding sphere fills (PowerPoint's camera below)
const W = 13.333, H = 7.5;    // LAYOUT_WIDE, inches
const X0 = 8.75, Y0 = 3.55;   // where the scene's view centre lands on the slide

// ---------- the story, as keyframes ----------
// offsets in angstroms in the screen frame (x right, y up) from each part's place in the crystal;
// yaw/pitch turn the whole scene (radians); k is inches per angstrom
const STEPS = ['Degrader', 'Split', 'Barrier', 'Rebuilt', 'Cleared', 'Again'];
const SLIDES = [
  { key: 'title', bg: 'blood', yaw: -.25, pitch: .05, k: .2, focus: 'deg', step: -1,
    parts: { halfA: [0, 0, 0], halfB: [0, 0, 0], bond: [0, 0, 0] }, glow: true },
  { key: 'size', bg: 'blood', yaw: .4, pitch: .1, k: .22, focus: 'deg', step: 0, eyebrow: '01 · The size problem',
    title: 'Protein degraders, made small enough to reach the brain',
    body: 'Degraders remove disease-causing proteins instead of blocking them. Most are too large to be taken by mouth or to enter the brain.',
    parts: { halfA: [0, 0, 0], halfB: [0, 0, 0], bond: [0, 0, 0] }, glow: true },
  { key: 'split', bg: 'blood', yaw: .15, pitch: .05, k: .15, focus: 'deg', step: 1, eyebrow: '02 · Split',
    title: 'One degrader, two small halves',
    body: 'A reversible linker lets a SELFTAC® molecule travel as two small molecules.',
    parts: { halfA: [-15, 3, 0], halfB: [15, -3, 0] } },
  { key: 'barrier', bg: 'barrier', yaw: -.1, pitch: .45, k: .1, focus: 'deg', shift: [0, -22], step: 2, eyebrow: '03 · The barrier',
    title: 'Through the cells, not between them',
    body: 'Tight junctions seal the brain’s capillaries. Each half is small enough to pass through the endothelial cells themselves.',
    parts: { halfA: [-17, -20, 0], halfB: [17, -27, 0] }, membrane: true },
  { key: 'rebuilt', bg: 'neuron', yaw: .12, pitch: .05, k: .046, focus: 'complex', step: 3, eyebrow: '04 · Rebuilt',
    title: 'Inside the neuron, the halves click back together',
    body: 'One end holds the target protein, the other an E3 ligase. The clasp closes between them.',
    parts: { halfA: [0, 0, 0], halfB: [0, 0, 0], bond: [0, 0, 0], brd4: [-7, 0, 0], vhlc: [7, 0, 0] }, glow: true },
  { key: 'tagged', bg: 'neuron', yaw: .02, pitch: .08, k: .046, focus: 'complex', step: 4, eyebrow: '05 · Cleared',
    title: 'Tagged, then destroyed',
    body: 'An E2 enzyme docks on the ligase and hands ubiquitin, one unit at a time, onto the target.',
    parts: { halfA: [0, 0, 0], halfB: [0, 0, 0], bond: [0, 0, 0], brd4: [-7, 0, 0], vhlc: [7, 0, 0], e2: 'dock', ub0: 'tag', ub1: 'tag', ub2: 'tag', ub3: 'tag' }, glow: true },
  { key: 'cleared', bg: 'neuron', yaw: -.06, pitch: .08, k: .04, focus: 'complex', shift: [-16, -14], step: 4, eyebrow: '05 · Cleared',
    title: 'The proteasome breaks the target down',
    body: 'It reads the ubiquitin chain, draws the target in and recycles it.',
    parts: { halfA: [0, 0, 0], halfB: [0, 0, 0], bond: [0, 0, 0], vhlc: [7, 0, 0], prot: 'prot', brd4: 'eaten', ub0: 'eaten', ub1: 'eaten', ub2: 'eaten', ub3: 'eaten', brd4b: 'below' }, glow: true },
  { key: 'again', bg: 'neuron', yaw: .1, pitch: .05, k: .046, focus: 'complex', step: 5, eyebrow: '06 · Again',
    title: 'Then it does it again',
    body: 'The degrader is not used up. It lets go and catches the next one, so one molecule can clear many.',
    parts: { halfA: [0, 0, 0], halfB: [0, 0, 0], bond: [0, 0, 0], vhlc: [7, 0, 0], brd4b: [-7, 0, 0] }, glow: true },
  { key: 'end', bg: 'blood', yaw: .1, pitch: .05, k: .046, focus: 'complex', step: 6, parts: {} },
];
const MODEL = { halfA: 'halfA', halfB: 'halfB', bond: 'bond', brd4: 'brd4', brd4b: 'brd4', vhlc: 'vhlc', e2: 'e2', prot: 'prot', ub0: 'ub', ub1: 'ub', ub2: 'ub', ub3: 'ub' };
const LABEL = { halfA: 'Degrader half A', halfB: 'Degrader half B', bond: 'Clasp bond', brd4: 'BRD4', brd4b: 'BRD4 second', vhlc: 'VHL complex', e2: 'E2 enzyme', prot: 'Proteasome', ub0: 'Ubiquitin 1', ub1: 'Ubiquitin 2', ub2: 'Ubiquitin 3', ub3: 'Ubiquitin 4' };

// ---------- 1. assets from the exporter page ----------
async function exportAssets() {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await b.newPage();
  const files = { '/exporter.html': [path.join(HERE, 'exporter.html'), 'text/html'], '/meshes.json': [path.join(LANDING, 'data/meshes.json'), 'application/json'], '/molecule.js': [path.join(LANDING, 'js/molecule.js'), 'text/javascript'] };
  await page.route('http://local/**', r => { const u = new URL(r.request().url()).pathname;
    if (files[u]) return r.fulfill({ contentType: files[u][1], body: fs.readFileSync(files[u][0]) });
    if (u.startsWith('/three/')) return r.fulfill({ contentType: 'text/javascript', body: fs.readFileSync(path.join(THREE_DIR, u.slice(7))) });
    r.fulfill({ status: 404 }); });
  const errs = []; page.on('pageerror', e => errs.push(e.message));
  await page.goto('http://local/exporter.html');
  await page.waitForFunction('window.READY === true', null, { timeout: 120000 }).catch(() => { throw new Error('exporter failed: ' + errs.join('; ')); });
  const info = await page.evaluate(() => API.info()), spots = await page.evaluate(() => API.spots());
  for (const k of Object.keys(info)) fs.writeFileSync(path.join(ASSETS, k + '.glb'), Buffer.from(await page.evaluate(k => API.glb(k), k), 'base64'));
  const still = async (k, yaw, pitch) => { const f = path.join(ASSETS, `${k}_${yaw.toFixed(2)}_${pitch.toFixed(2)}.png`);
    if (!fs.existsSync(f)) fs.writeFileSync(f, Buffer.from((await page.evaluate(([k, y, p]) => API.still(k, y, p), [k, yaw, pitch])).split(',')[1], 'base64'));
    return f; };
  // the brand logotype as a transparent PNG
  const lp = await b.newPage({ viewport: { width: 2441, height: 858 } });
  await lp.setContent('<style>html,body{margin:0;background:transparent}svg{display:block;width:2441px;height:auto}</style>' + fs.readFileSync(path.join(HERE, '../brand/oyster-logotype-nacre.svg'), 'utf8'));
  await lp.screenshot({ path: path.join(OUT, 'logotype.png'), omitBackground: true });
  const wall = async (o) => { const f = path.join(ASSETS, 'barrier.png');
    fs.writeFileSync(f, Buffer.from((await page.evaluate(o => API.wall(o), o)).split(',')[1], 'base64')); return f; };
  return { info, spots, still, wall, close: () => b.close() };
}

// ---------- small vector maths ----------
const add = (a, b) => a.map((v, i) => v + b[i]), sub = (a, b) => a.map((v, i) => v - b[i]), mul = (a, s) => a.map(v => v * s);
const mean = ps => mul(ps.reduce(add), 1 / ps.length);
// scene turn: R = Rx(pitch) · Ry(yaw), the same order the stills and PowerPoint use
function turn(p, yaw, pitch) {
  const [x, y, z] = p, cy = Math.cos(yaw), sy = Math.sin(yaw), cp = Math.cos(pitch), sp = Math.sin(pitch);
  const x1 = cy * x + sy * z, z1 = -sy * x + cy * z;
  return [x1, cp * y - sp * z1, sp * y + cp * z1];
}

(async () => {
  const A = await exportAssets();
  const { info, spots } = A;
  const deg = mean([info.halfA.centre, info.halfB.centre]);
  const complex = mean([info.brd4.centre, info.vhlc.centre]);
  const claspMid = mean(spots.clasp);
  // where each part sits on a slide, in the shared screen frame (before the scene turn), and its scale
  function place(s, name, spec) {
    const c = info[MODEL[name]].centre;
    if (Array.isArray(spec)) return { p: add(c, spec), s: 1 };
    const brd4 = add(info.brd4.centre, [-7, 0, 0]);
    const protAt = add(complex, [-62, -46, 0]);
    if (spec === 'dock') return { p: add(spots.vhlTop, [7 - 3, 11, 0]), s: 1 };
    if (spec === 'tag') { const i = +name.slice(2); return { p: add(add(spots.ubSpot, [-7, 0, 0]), [-1.5 * i, 3 + 6.5 * i, i % 2 ? 3 : -3]), s: .7 }; }
    if (spec === 'prot') return { p: protAt, s: 1 };
    if (spec === 'eaten') return { p: add(protAt, [14, 2, 0]), s: name === 'brd4' ? .22 : .3 };
    if (spec === 'below') return { p: add(brd4, [-30, -120, 0]), s: 1 };
  }

  const pres = new pptxgen();
  pres.layout = 'LAYOUT_WIDE';
  pres.title = 'SELFTAC, in motion'; pres.company = 'Oyster Therapeutics';
  const THEME = { name: 'Oyster Nacre', headFontFace: 'Newsreader', bodyFontFace: 'Archivo',
    colors: { dk1: '2B2230', lt1: 'FFFFFF', dk2: '65586A', lt2: 'F6EEEC', accent1: '8C5572', accent2: 'D9A443', accent3: 'B4678B', accent4: '8A73B2', accent5: 'C99BB0', accent6: 'E7C9D6', hlink: '8C5572', folHlink: '65586A' } };
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  const C = pres.SchemeColor;

  // backgrounds and the glow are images made by bg.py; the logotype is the brand export
  const BG = { blood: 'bg_blood.png', barrier: 'bg_barrier.png', neuron: 'bg_neuron.png' };
  const NOTES = {
    title: 'SELFTAC: protein degraders, made small enough to reach the brain. Click to start the story; each click morphs to the next beat.',
    size: 'A degrader has two ends: one holds the disease protein, the other recruits the cell’s disposal machinery. Joined by a linker, they are usually too big for oral dosing or the brain. The gold clasp in the middle is the SELFTAC difference.',
    split: 'SELFTAC opens at the clasp, a reversible bond, so the drug travels as two small halves.',
    barrier: 'The blood-brain barrier is sealed by tight junctions, so a drug must pass through the cells themselves. Small molecules can.',
    rebuilt: 'Inside the neuron the two halves find each other and the clasp closes, rebuilding the full degrader: one end on the target (BRD4 here), the other on the E3 ligase (VHL).',
    tagged: 'The ligase brings in an E2 enzyme, which hands ubiquitin onto the face of the target turned towards it, one unit at a time.',
    cleared: 'The proteasome reads the ubiquitin chain and breaks the target down.',
    again: 'The degrader is not used up. It lets go and catches the next target: one molecule clears many.',
    end: 'Oyster Therapeutics: oral, brain-penetrant protein degraders.',
  };
  const logotype = path.join(OUT, 'logotype.png');

  for (const s of SLIDES) {
    const slide = pres.addSlide();
    slide.background = { path: path.join(OUT, BG[s.bg]) };
    // view centre and the scene turn pivot
    let centre = s.focus === 'deg' ? deg : complex;
    if (s.shift) centre = add(centre, [...s.shift, 0]);
    const toSlide = p => { const q = turn(sub(p, centre), s.yaw, s.pitch); return [X0 + q[0] * s.k, Y0 - q[1] * s.k, q[2]]; };
    if (s.membrane) {   // the barrier, drawn as on the website, the halves passing through it
      const img = await A.wall({ yaw: s.yaw, pitch: s.pitch, k: s.k, X0, Y0, W, H, centre, wallY: deg[1] - 24, cellW: 76, wallX: 2, px: 2400 });
      slide.addImage({ path: img, x: 0, y: 0, w: W, h: H, objectName: '!!Barrier', altText: 'The blood-brain barrier: endothelial cells side by side' });
    }
    // 3D parts, drawn back to front
    const items = Object.entries(s.parts).map(([name, spec]) => { const pl = place(s, name, spec); const [x, y, z] = toSlide(pl.p);
      const side = 2 * info[MODEL[name]].radius * pl.s * s.k / FIT; return { name, x, y, z, side, model: MODEL[name] }; });
    if (s.glow) {
      const [gx, gy] = toSlide(claspMid), gs = 26 * s.k;
      slide.addImage({ path: path.join(OUT, 'glow.png'), x: gx - gs / 2, y: gy - gs / 2, w: gs, h: gs, objectName: '!!Clasp glow', altText: 'Glow around the clasp' });
    }
    items.sort((a, b) => a.z - b.z);
    for (const it of items) {
      const img = await A.still(it.model, s.yaw, s.pitch);
      slide.addImage({ path: img, x: it.x - it.side / 2, y: it.y - it.side / 2, w: it.side, h: it.side,
        objectName: '!!' + LABEL[it.name], altText: LABEL[it.name] + ' (3D model)' });
    }
    // copy
    if (s.key === 'title' || s.key === 'end') {
      const lw = s.key === 'end' ? 7.2 : 5.4, lx = s.key === 'end' ? (W - lw) / 2 : .7, ly = s.key === 'end' ? 2.3 : 2.35;
      slide.addImage({ path: logotype, x: lx, y: ly, w: lw, h: lw * 857.3 / 2441.0, objectName: '!!Logotype', altText: 'Oyster Therapeutics' });
      slide.addText(s.key === 'end' ? 'Oral, brain-penetrant protein degraders' : 'SELFTAC®, in motion', { isTextBox: true, x: lx, y: ly + lw * .3512 + .25, w: lw, h: .6,
        fontFace: 'Newsreader', fontSize: 22, color: C.text2, align: s.key === 'end' ? 'center' : 'left', margin: 0, objectName: '!!Tagline' });
    } else {
      slide.addText(s.eyebrow.toUpperCase(), { isTextBox: true, x: .7, y: 1.55, w: 4.6, h: .35, fontFace: 'IBM Plex Mono', fontSize: 11, charSpacing: 2, color: C.accent1, margin: 0, objectName: 'Eyebrow' });
      slide.addText(s.title, { isTextBox: true, x: .7, y: 1.95, w: 4.6, h: 2.1, fontFace: 'Newsreader', fontSize: 30, color: C.text1, valign: 'top', margin: 0, objectName: 'Title', lineSpacingMultiple: .95 });
      slide.addText(s.body, { isTextBox: true, x: .7, y: 4.3, w: 4.2, h: 1.5, fontFace: 'Archivo', fontSize: 15, color: C.text2, valign: 'top', margin: 0, objectName: 'Body' });
    }
    // the story rail: a pearl per beat on a strand; the rebuild beat is the gold clasp
    if (s.step >= 0 && s.step < 6) {
      slide.addShape(pres.shapes.LINE, { x: .85, y: 6.86, w: 11.6, h: 0, line: { color: '2B2230', width: .75, transparency: 70 }, objectName: '!!Rail line' });
      STEPS.forEach((label, i) => {
        const x = .7 + i * 2.32, reached = i <= s.step, clasp = i === 3, d = clasp ? .26 : .2;
        slide.addShape(pres.shapes.OVAL, { x: x + .15 - d / 2, y: 6.86 - d / 2, w: d, h: d, objectName: '!!Rail pearl ' + i,
          fill: { color: reached ? (clasp ? 'D9A443' : 'FFFFFF') : 'F6EEEC', transparency: reached ? 0 : 100 }, line: { color: '2B2230', width: 1.1, transparency: reached ? 0 : 50 } });
        slide.addText(label.toUpperCase(), { isTextBox: true, x: x + .38, y: 6.74, w: 1.8, h: .26, fontFace: 'IBM Plex Mono', fontSize: 9, charSpacing: 1.5, color: i === s.step ? C.text1 : C.text2, margin: 0, objectName: '!!Rail label ' + i });
      });
    }
    slide.addNotes(NOTES[s.key]);
  }
  await A.close();
  const out = path.join(OUT, 'stage1.pptx');
  await pres.writeFile({ fileName: out });
  const { applyTheme } = require(process.env.PPTX_SKILL + '/scripts/apply_theme.js');
  await applyTheme(out, THEME);
  // tell post.py which pictures are 3D parts, and which model file each uses
  fs.writeFileSync(path.join(OUT, 'models.json'), JSON.stringify(Object.fromEntries(Object.entries(LABEL).map(([k, v]) => ['!!' + v, { glb: path.join(ASSETS, MODEL[k] + '.glb'), radius: info[MODEL[k]].radius }]))));
  // per-slide scene turn, so post.py can write each model's rotation
  fs.writeFileSync(path.join(OUT, 'turns.json'), JSON.stringify(SLIDES.map(s => ({ yaw: s.yaw, pitch: s.pitch }))));
  console.log('stage1.pptx written');
})().catch(e => { console.error(e); process.exit(1); });
