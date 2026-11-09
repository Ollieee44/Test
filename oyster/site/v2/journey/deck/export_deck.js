// Export the journey (the oyster-tx.com version) for the PowerPoint build: reference stills of each 3D element, the
// flat illustration's pieces, the backgrounds' speckle, the logo, and the measurements of every keyframe.
//   THREE=<three@0.160.0 package dir> NODE_PATH=<dir with playwright-core> CHROME=<chromium binary> node export_deck.js
// Writes out/ (pictures) and out/keyframes.json; build_deck.js then builds the deck from them.
const { chromium } = require('playwright-core'); const fs = require('fs'), path = require('path');
const HERE = __dirname + '/', OUT = HERE + 'out/', SRC = path.join(HERE, '../otx/index.html'), CSS = path.join(HERE, '../../pages/site.css');
const T = (process.env.THREE || '') + '/';
const KEYS = [0, .05, .09, .115, .135, .152, .163, .215, .255, .296, .315, .36, .42, .5, .56, .62, .655, .68, .74, .815, .86, .895, .93, .965, .997];
const REFS = [['halfW', .33], ['halfE', .33], ['dimerG', .25], ['dimerC', .75], ['brd4', .75], ['vhl', .75], ['elob', .75], ['eloc', .75],
  ['prot', .9], ['ub0', .86], ['frag0', .985], ['frag1', .985], ['frag2', .985]];
const FLAT = [['jperson', 12, 4], ['jroute', 12, 4], ['jgut', 34, 9], ['jtract', 34, 9], ['jgutring', 34, 9], ['jbeam', 3, 4], ['jmem', 5, 3.5], ['jpill', 40, 3]];
fs.mkdirSync(OUT, { recursive: true });

// the harness: the otx page with its scene exposed as window.__X
let h = fs.readFileSync(SRC, 'utf8');
const hook = 'window.__journey = window.__story = {';
if (!h.includes(hook)) throw new Error('journey hook not found');
h = h.replace('const j = kf(p, [[.27, 1], [.31, 0], [.64, 0], [.68, 1]]);', 'const j = kf(p, [[.27, 1], [.31, 0], [.64, 0], [.68, 1]]); window.__JS = { j, p };');
h = h.replace(hook, 'window.__X = { THREE, scene, camera, get renderer() { return renderer; }, cg, inner, mol, P, prot, ubs, frags, flash, stage, frame: p => frame(p), resize: () => resize(), get j() { return window.__JS.j; }, get p() { return window.__JS.p; } };\n' + hook);
fs.writeFileSync(HERE + '.harness.html', h);

(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROME || '/opt/pw-browsers/chromium-1243/chrome-linux64/chrome', args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 1440, height: 810 } }); const errs = [];
  p.on('pageerror', e => errs.push(e.message));
  await p.route('https://cdn.jsdelivr.net/npm/three@0.160.0/**', r => r.fulfill({ path: T + r.request().url().split('three@0.160.0/')[1], contentType: 'application/javascript' }));
  await p.route('http://site/**', r => { const n = new URL(r.request().url()).pathname.slice(1); const f = n === 'site.css' ? CSS : HERE + '.harness.html';
    r.fulfill({ path: f, contentType: f.endsWith('.css') ? 'text/css' : 'text/html' }); });
  await p.goto('http://site/index.html'); await p.waitForFunction(() => window.__X && window.__JS, null, { timeout: 60000 }); await p.waitForTimeout(1500);
  await p.addScriptTag({ path: HERE + 'export_page.js' });
  // the 3D elements, each alone
  const refs = {};
  for (const [name, at] of REFS) {
    const r = await p.evaluate(([n, a]) => window.refRender(n, a), [name, at]);
    fs.writeFileSync(OUT + name + '.png', Buffer.from(r.url.split(',')[1], 'base64')); delete r.url; refs[name] = r; console.log('ref', name);
  }
  // every keyframe
  const keys = [];
  for (const k of KEYS) { keys.push(await p.evaluate(k => window.keyframe(k), k)); }
  // the flat pieces, as SVG, then drawn to PNG in a page with the theme's colours
  const vars = await p.evaluate(() => { const cs = getComputedStyle(document.documentElement); return ['--ink', '--paper', '--accent', '--muted', '--mol-a', '--mol-b', '--mol-c', '--clasp'].map(v => `${v}:${cs.getPropertyValue(v).trim()}`).join(';'); });
  const flats = {};
  for (const [id, ppu, kd] of FLAT) { flats[id] = await p.evaluate(([i, s, k]) => window.flatPiece(i, s, k), [id, ppu, kd]); }
  const starsUrl = await p.evaluate(() => getComputedStyle(document.getElementById('jstars')).backgroundImage.slice(5, -2));
  const eq = await p.evaluate(() => document.querySelector('#jeq svg').outerHTML);
  await p.close();
  const q = await b.newPage({ viewport: { width: 800, height: 600 } });
  const draw = async (svg, w, h, file) => {
    await q.setViewportSize({ width: Math.ceil(w), height: Math.ceil(h) });
    await q.setContent(`<html style="background:transparent;${vars}"><body style="margin:0;background:transparent">${svg}</body></html>`);
    await q.waitForTimeout(150); await q.screenshot({ path: file, omitBackground: true, clip: { x: 0, y: 0, width: Math.ceil(w), height: Math.ceil(h) } });
  };
  for (const [id, f] of Object.entries(flats)) { await draw(f.svg, f.w, f.h, OUT + id + '.png'); delete f.svg; console.log('flat', id, Math.round(f.w), Math.round(f.h)); }
  await draw(`<div style="width:2600px;height:1700px;background:url('${starsUrl}');background-size:520px 520px"></div>`, 2600, 1700, OUT + 'stars.png');
  await draw(eq.replace('<svg ', '<svg width="208" height="96" '), 208, 96, OUT + 'eq.png');
  const logo = fs.readFileSync(path.join(HERE, '../otx_logo.svg'), 'utf8');
  await draw(`<div style="color:#fff;width:1863px">${logo.replace('<svg ', '<svg style="width:100%;height:auto;display:block" ')}</div>`, 1863, 540, OUT + 'logo.png');
  fs.writeFileSync(OUT + 'keyframes.json', JSON.stringify({ refs, flats, keys }, null, 1));
  console.log('keyframes', keys.length, errs.length ? errs : '');
  await b.close();
})();
