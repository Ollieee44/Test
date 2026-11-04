// Renders the still images for the hero mockups (img/*.png, transparent) from the v2 Science page's own 3D scene,
// with a JSON beside each giving where the parts land (0-1 across and down) for the labels.
//   python build_heroes.py --harness   (writes .harness.html: the Science page with its scene opened up)
//   THREE=<three@0.160.0 package dir> NODE_PATH=<dir with playwright-core> node render_heroes.js
//   python build_heroes.py            (writes index.html from the renders)
// Each shot holds the story at the assembled ternary complex (p0 .74), hides everything else, draws the degrader
// k times true size about the clasp (each protein moves out with the end that sits in it, then 'pull' further,
// so both ends show), and points the camera at the clasp (plus 'look') from 'dir' at 'dist'.
const { chromium } = require('playwright-core'); const fs = require('fs');
const path = require('path'), HERE = __dirname + '/', H = HERE, DIR = path.join(HERE, '../pages/') , T = (process.env.THREE || '') + '/';
const IMG = HERE + 'img/';
(async () => {
  const shots = [
    { out: IMG + 'a-centre.png', pal: 'nacre', k: 2.4, pull: 10, dist: 340, look: [14, 2, 0], dir: [0, .18, 1], w: 1440, h: 600, dpr: 2 },
    { out: IMG + 'b-split.png', pal: 'tidepool', k: 2.6, pull: 12, dist: 380, look: [14, 2, 0], dir: [-.55, .35, 1], w: 860, h: 810, dpr: 2 },
    { out: IMG + 'c-annot.png', pal: 'nacre', k: 2.4, pull: 14, dist: 360, look: [14, 0, 0], dir: [0, .1, 1], w: 1440, h: 620, dpr: 2 },
    { out: IMG + 'd-macro.png', pal: 'shellcoral', k: 2.6, pull: 10, dist: 225, look: [14, 10, 0], dir: [-.2, .22, 1], roll: 18, w: 1440, h: 810, dpr: 2 },
  ];
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 1440, height: 900 } }); const errs = [];
  p.on('pageerror', e => errs.push(e.message));
  await p.route('https://cdn.jsdelivr.net/npm/three@0.160.0/**', r => r.fulfill({ path: T + r.request().url().split('three@0.160.0/')[1], contentType: 'application/javascript' }));
  await p.route('http://site/**', r => { const n = new URL(r.request().url()).pathname.slice(1); const f = n === 'harness.html' ? H + '.harness.html' : DIR + n; r.fulfill({ path: f, contentType: f.endsWith('.css') ? 'text/css' : f.endsWith('.js') ? 'application/javascript' : 'text/html' }); });
  await p.goto('http://site/harness.html'); await p.waitForFunction(() => window.__dbg, null, { timeout: 20000 }); await p.waitForTimeout(2500);
  for (const s of shots.filter(s => !process.env.ONLY || s.out.includes(process.env.ONLY))) {
    const res = await p.evaluate(s => {
      const d = window.__dbg, V = (...a) => new d.THREE.Vector3(...a), I = new d.THREE.Quaternion();
      d.hold(s.p0 ?? .74); d.setPal(s.pal || 'nacre'); d.frame(s.p0 ?? .74);
      for (const o of [d.e2, d.prot, d.wall, d.cell, d.flash, ...d.ubs, d.P.brd4b]) o.visible = false;
      const g = s.gap ?? 12, Yn = -112;
      d.P.brd4.position.x = -g; d.P.brd4.scale.setScalar(1);
      for (const k of ['vhl', 'elob', 'eloc']) d.P[k].position.x = g;
      d.mol.group.scale.setScalar(1); d.mol.group.position.set(0, 0, 0);
      const oW = V(-g, Yn, 0), oE = V(g, Yn, 0), brk = d.mol.update(oW, oE, I, I, 1).clone();
      // the degrader drawn k times true size about the clasp; each protein moves out with the end that sits in it
      const k = s.k || 1, cW = d.S('warhead').add(oW), cE = d.S('e3lig').add(oE);
      d.mol.group.scale.setScalar(k); d.mol.group.position.copy(brk).multiplyScalar(1 - k);
      const mW = cW.clone().sub(brk).multiplyScalar(k - 1), mE = cE.clone().sub(brk).multiplyScalar(k - 1);
      d.P.brd4.position.add(mW); for (const key of ['vhl', 'elob', 'eloc']) d.P[key].position.add(mE);
      const pull = s.pull || 0; d.P.brd4.position.x -= pull; for (const key of ['vhl', 'elob', 'eloc']) d.P[key].position.x += pull;   // exploded a little so both ends of the degrader show
      const tgt = brk.clone().add(V(...(s.look || [0, 0, 0])));
      const dir = V(...(s.dir || [0, .15, 1])).normalize();
      d.camera.fov = s.fov || 26; d.camera.position.copy(tgt).addScaledVector(dir, s.dist || 260);
      const roll = (s.roll || 0) * Math.PI / 180; d.camera.up.set(Math.sin(roll), Math.cos(roll), 0); d.camera.lookAt(tgt);   // roll tilts the picture (degrees)
      const W = s.w || 1600, Hh = s.h || 1000;
      d.renderer.setPixelRatio(s.dpr || 2); d.renderer.setSize(W, Hh, false); d.camera.aspect = W / Hh; d.camera.updateProjectionMatrix();
      d.renderer.setClearColor(0x000000, 0); d.renderer.render(d.scene, d.camera);
      // where each part lands in the picture (0-1 across and down), for labels
      d.scene.updateMatrixWorld(true);
      const at = v => { const q = v.clone().project(d.camera); return [+((q.x + 1) / 2).toFixed(4), +((1 - q.y) / 2).toFixed(4)]; };
      const ctr = o => { const bx = new d.THREE.Box3().setFromObject(o); return bx.getCenter(V()); };
      const sc = v => brk.clone().add(v.clone().sub(brk).multiplyScalar(k));
      const anchors = { clasp: at(brk), target: at(ctr(d.P.brd4)), ligase: at(ctr(d.P.vhl)), elob: at(ctr(d.P.elob)), eloc: at(ctr(d.P.eloc)),
        endW: at(sc(cW)), endE: at(sc(cE)), linkW: at(sc(cW).lerp(brk, .55)), linkE: at(sc(cE).lerp(brk, .5)) };
      return { url: d.renderer.domElement.toDataURL('image/png'), anchors };
    }, s);
    fs.writeFileSync(s.out, Buffer.from(res.url.split(',')[1], 'base64')); fs.writeFileSync(s.out.replace(/\.png$/, '.json'), JSON.stringify(res.anchors)); console.log('wrote', s.out, JSON.stringify(res.anchors));
  }
  if (errs.length) console.log(errs);
  await b.close();
})();
