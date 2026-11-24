// Exports the v4 journey (click6) for the PowerPoint build: at each keyframe, the background (ground, flat art,
// bokeh) as one picture, every 3D element alone on a transparent ground, the labels and the copy as laid out.
//   THREE=<three@0.160.0 package dir> CHROME=<chromium> node export.js   (needs playwright-core; run harness.js first)
// Writes out/k<N>/*.png and out/keys.json; prep.py crops the pictures, build.js builds the deck.
const { chromium } = require('playwright-core'); const fs = require('fs'), path = require('path');
const HERE = __dirname + '/', OUT = HERE + 'out/', T = (process.env.THREE || '') + '/';
// The page's own autoplay ("Watch the whole journey"): each move between stops eases in and out over a set time; holds
// between moves. The deck samples it about every HOP ms, so Morph's short hops follow the animation's paths.
const STOPS = [0, .25, .335, .45, .59, .665, .728, .79, .865, .92];          // the page's stops, less the end card
const SLOW = { 4: 1.3, 5: 2.6, 6: 2.2, 7: 1.9, 8: 1.8, 9: 2.6 };
const HOLD = [250, 450, 250, 1700, 700, 450, 1300, 1600, 350, 900];
const HOP = +(process.env.HOP || 300);
const easeInOut = t => -(Math.cos(Math.PI * t) - 1) / 2;
function timeline() {
  const out = [{ k: 0, t: 0, stop: 0, dur: 0 }]; let t = 0;
  for (let i = 1; i < STOPS.length; i++) {
    t += HOLD[i - 1];
    const a = STOPS[i - 1], b = STOPS[i], d = b - a, dur = (SLOW[i] || 1) * Math.max(1700, Math.min(3600, 1400 + d * 9000)), N = Math.max(2, Math.round(dur / HOP));
    for (let j = 1; j <= N; j++) out.push({ k: a + d * easeInOut(j / N), t: t + dur * j / N, stop: j === N ? i : null, dur: dur / N });
    t += dur;
  }
  return out;
}
const W = 1920, H = 1080, PR = 2;
async function open(b) {
  const p = await b.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: PR }); const errs = [];
  p.on('pageerror', e => errs.push(e.message));
  // the page's clock is ours: every frame is drawn at its own moment on the timeline, not whenever it was captured
  await p.addInitScript(() => { const real = performance.now.bind(performance); window.__vt = null; performance.now = () => window.__vt === null ? real() : window.__vt; });
  await p.route('https://cdn.jsdelivr.net/npm/three@0.160.0/**', r => r.fulfill({ path: T + r.request().url().split('three@0.160.0/')[1], contentType: 'application/javascript' }));
  await p.route('http://site/**', r => { const n = new URL(r.request().url()).pathname.slice(1); const f = n === 'site.css' ? HERE + '../../pages/site.css' : HERE + '.harness.html';
    r.fulfill({ path: f, contentType: f.endsWith('.css') ? 'text/css' : 'text/html' }); });
  await p.goto('http://site/index.html'); await p.waitForFunction(() => window.__X, null, { timeout: 90000 });
  await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(2500);
  await p.addStyleTag({ content: '#jctl,.rail,.hint,.skip,.end{visibility:hidden!important} .jl,.beat,.beat *{transition:none!important}' });
  await p.evaluate(() => {
    const X = window.__X, R = X.renderer, orig = R.render.bind(R);     R.render = (...a) => { if (!window.__freeze) orig(...a); }; window.__draw = orig;
    const id = o => o === X.mol.group ? 'mol' : o === X.prot ? 'proteasome' : null;
    // the elements: name -> the objects drawn for it
    window.__elements = () => {
      const E = { mol: [X.mol.group], poi: [X.P.brd4], e3: [X.P.vhl, X.P.elob, X.P.eloc], ub: [...X.ubs, X.e2], proteasome: [X.prot] };
      const debris = [];
      X.scene.children.forEach((o, i) => {
        if (o === X.cg || o === X.prot || X.ubs.includes(o) || o === X.e2 || o.type === 'Sprite' || o.isLight || o.isCamera) return;
        if (o.type === 'Group' && o !== X.wall && o !== X.cell && o !== X.mol.group) E['c' + i] = [o];
        else if (o.type === 'Mesh') debris.push(o);
      });
      E.debris = debris; return E;
    };
  });
  return { p, errs };
}
(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROME || '/opt/pw-browsers/chromium-1243/chrome-linux64/chrome', args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const keys = [], plan = timeline(); console.log('frames', plan.length);
  const { p: P, errs } = await open(b), T0 = 100000;
  for (const [n, { k, t, stop, dur }] of plan.entries()) {
    const dir = OUT + 'k' + n + '/'; fs.mkdirSync(dir, { recursive: true });
    await P.evaluate(([k, vt]) => { window.__freeze = false; window.__vt = vt; window.__journey.frame(k); }, [k, T0 + t]); await P.waitForTimeout(120);
    await P.evaluate(([k, vt]) => { window.__vt = vt; window.__journey.frame(k); window.__freeze = true; }, [k, T0 + t]); await P.waitForTimeout(60);
    // what the page shows at this key: labels and copy
    const info = await P.evaluate(() => {
      const opa = el => { let o = 1; for (let n = el; n && n !== document.documentElement; n = n.parentElement) { const v = parseFloat(getComputedStyle(n).opacity); if (!isNaN(v)) o *= v; if (getComputedStyle(n).visibility === 'hidden') return 0; } return o; };
      const st = document.getElementById('stage').getBoundingClientRect();
      const rect = el => { const r = el.getBoundingClientRect(); return [r.left - st.left, r.top - st.top, r.width, r.height]; };
      const css = el => { const c = getComputedStyle(el); return { color: c.color, bg: c.backgroundColor, border: c.borderTopColor, bw: parseFloat(c.borderTopWidth), radius: parseFloat(c.borderTopLeftRadius), size: parseFloat(c.fontSize), family: c.fontFamily, weight: c.fontWeight, tt: c.textTransform, ls: c.letterSpacing, pad: [parseFloat(c.paddingLeft), parseFloat(c.paddingTop)] }; };
      const labels = [...document.querySelectorAll('.jl')].map(el => ({ text: el.innerText.replace(/\s+/g, ' ').trim(), o: opa(el), r: rect(el), css: css(el), dot: !!el.querySelector('i,.dot') })).filter(l => l.o > .5 && l.text);
      const beat = [...document.querySelectorAll('.beat')].map(b => ({ b, o: opa(b) })).sort((a, c) => c.o - a.o)[0];
      let copy = null;
      if (beat && beat.o > .5) { const k = beat.b.querySelector('.k'), h = beat.b.querySelector('h1,h2'), pp = beat.b.querySelector('p');
        copy = { num: k && k.querySelector('b') ? k.querySelector('b').textContent.trim() : '', kicker: k ? k.textContent.replace(k.querySelector('b') ? k.querySelector('b').textContent : '', '').trim() : '', kR: k ? rect(k) : null, kCss: k ? css(k) : null,
          head: h.textContent.trim(), hR: rect(h), hCss: css(h), body: pp && opa(pp) > .5 ? pp.textContent.trim() : '', pR: pp ? rect(pp) : null, pCss: pp ? css(pp) : null }; }
      return { labels, copy };
    });
    // the background: everything but the 3D elements (the bokeh stays), and no labels or copy
    const names = await P.evaluate(() => {
      const X = window.__X, E = window.__elements(), all = new Set(); Object.values(E).flat().forEach(o => all.add(o));
      window.__saved = []; all.forEach(o => { window.__saved.push([o, o.visible]); o.visible = false; });
      window.__draw(X.scene, X.camera); window.__saved.forEach(([o, v]) => o.visible = v);
      return Object.entries(E).filter(([n, os]) => os.some(o => { let vis = o.visible; for (let q = o.parent; q; q = q.parent) vis = vis && q.visible; return vis; })).map(([n]) => n);
    });
    await P.addStyleTag({ content: '.jl,.beat{visibility:hidden!important}' }).then(h => h.evaluate(e => e.id = 'hideui'));
    await P.locator('#stage').screenshot({ path: dir + 'bg.png' });
    await P.evaluate(() => document.getElementById('hideui').remove());
    // each element alone, in the scene's camera, on a clear ground
    for (const name of names) {
      const url = await P.evaluate(name => {
        const X = window.__X, R = X.renderer, E = window.__elements(), objs = E[name], keep = new Set(), anc = new Set(), saved = [];
        objs.forEach(o => { o.traverse(c => keep.add(c)); for (let q = o.parent; q; q = q.parent) anc.add(q); });
        X.scene.traverse(o => { if (keep.has(o) || anc.has(o)) return; saved.push([o, o.visible]); o.visible = false; });
        const cc = R.getClearColor(new X.THREE.Color()), ca = R.getClearAlpha(); R.setClearColor(0x000000, 0);
        window.__draw(X.scene, X.camera); const u = R.domElement.toDataURL('image/png');
        saved.forEach(([o, v]) => o.visible = v); R.setClearColor(cc, ca); return u;
      }, name);
      fs.writeFileSync(dir + name + '.png', Buffer.from(url.split(',')[1], 'base64'));
    }
    const heads = await P.evaluate(() => { const X = window.__X, T = X.THREE, st = X.stage;
      return [0, 1].map(i => { const c = new T.Box3().setFromObject(X.mol.group.children[i]).getCenter(new T.Vector3()).project(X.camera); return [(c.x + 1) / 2 * st.clientWidth, (1 - c.y) / 2 * st.clientHeight]; }); });
    if (n % 10 === 0) console.log('frame', n, k.toFixed(3));
    keys.push({ dir: 'k' + n, k, t, stop, dur, names, heads, ...info }); 
  }
  fs.writeFileSync(OUT + 'keys.json', JSON.stringify({ W, H, keys }, null, 1));
  keys.sort((x, y) => x.k - y.k);
  console.log('errors', errs); await b.close();
})();
