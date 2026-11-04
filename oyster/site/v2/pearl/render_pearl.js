// Renders the stills for the SELFTAC pearl variations (img/*.png, transparent, plus a JSON of where the parts land)
// from the v2 Science page's own 3D scene, all in the Tidepool palette, with the join of the reversible linker drawn
// as one realistic pearl (nacre: cream with an angle-dependent sheen, growth rings, two highlights).
//   python ../heroes/build_heroes.py --harness      (the Science page with its scene opened up)
//   THREE=<three@0.160.0 package dir> NODE_PATH=<dir with playwright-core> node render_pearl.js [name ...]
//   python build_pearl.py
// Each shot loads the scene fresh, holds the story at the assembled ternary complex (p0 .74), draws the degrader k
// times true size about the join (the proteins move out with it, then `pull` further), and styles it:
//   mol      'rings' (the traced ends) | 'pods' (plain glossy pods threaded on the strand)
//   proteins 'contour' (as on the site) | 'flat' | 'ghost' (see-through) | 'line' (blueprint) | 'none'
//   line     true: the degrader drawn as line-work too, so only the pearl is rendered
const { chromium } = require('playwright-core'); const fs = require('fs'), path = require('path');
const HERE = __dirname + '/', IMG = HERE + 'img/', HARNESS = path.join(HERE, '../heroes/.harness.html'), PAGES = path.join(HERE, '../pages/'), T = (process.env.THREE || '') + '/';
const DIAG = { k: 2.6, pull: 10, dist: 225, look: [14, 10, 0], dir: [-.2, .22, 1], roll: 18, w: 1440, h: 810, dy: 90 };
const SHOTS = [
  { name: 'v1-detailed', ...DIAG, mol: 'rings', proteins: 'contour' },
  { name: 'v2-pods', ...DIAG, mol: 'pods', proteins: 'contour' },
  { name: 'v3-silhouette', ...DIAG, mol: 'pods', proteins: 'flat' },
  { name: 'v4-ghost', ...DIAG, mol: 'pods', proteins: 'ghost' },
  { name: 'v5-blueprint', ...DIAG, mol: 'pods', proteins: 'line', line: true },
  // the same drawing as 05 with the camera pulled back so the whole complex is in frame (for the vector asset)
  { name: 'v5-asset', ...DIAG, dy: 0, dist: 420, look: [18, 12, 0], w: 1800, h: 1200, mol: 'pods', proteins: 'line', line: true },
  { name: 'v6-callouts', dy: 110, k: 2.4, pull: 16, dist: 330, look: [16, 2, 0], dir: [0, .12, 1], roll: 0, w: 1440, h: 810, mol: 'pods', proteins: 'line', line: true },
  { name: 'v7-strand', k: 2.6, pull: 10, dist: 130, look: [-16, 5, 0], dir: [-.15, .25, 1], roll: 12, w: 1440, h: 810, mol: 'pods', proteins: 'none', pearlScale: 1.25 },
  { name: 'v8-macro', dy: 110, k: 2.6, pull: 10, dist: 58, look: [-12, 1, 0], dir: [-.35, .3, 1], roll: -4, w: 1440, h: 810, mol: 'pods', proteins: 'contour', fov: 30 },
];
(async () => {
  const only = process.argv.slice(2);
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  for (const s0 of SHOTS.filter(s => !only.length || only.includes(s.name))) {
    const s = { ...s0, exportData: !!process.env.EXPORT };
    const p = await b.newPage({ viewport: { width: 1440, height: 900 } }); const errs = [];
    p.on('pageerror', e => errs.push(e.message));
    await p.route('https://cdn.jsdelivr.net/npm/three@0.160.0/**', r => r.fulfill({ path: T + r.request().url().split('three@0.160.0/')[1], contentType: 'application/javascript' }));
    await p.route('http://site/**', r => { const n = new URL(r.request().url()).pathname.slice(1); const f = n === 'harness.html' ? HARNESS : PAGES + n;
      r.fulfill({ path: f, contentType: f.endsWith('.css') ? 'text/css' : f.endsWith('.js') ? 'application/javascript' : 'text/html' }); });
    await p.goto('http://site/harness.html'); await p.waitForFunction(() => window.__dbg, null, { timeout: 30000 }); await p.waitForTimeout(2000);
    const res = await p.evaluate(s => {
      const d = window.__dbg, THREE = d.THREE, V = (...a) => new THREE.Vector3(...a), I = new THREE.Quaternion();
      d.hold(.74); d.setPal('tidepool'); d.frame(.74);
      for (const o of [d.e2, d.prot, d.wall, d.cell, d.flash, ...d.ubs, d.P.brd4b]) o.visible = false;
      const g = 12, Yn = -112, k = s.k;
      d.P.brd4.position.x = -g; d.P.brd4.scale.setScalar(1); for (const key of ['vhl', 'elob', 'eloc']) d.P[key].position.x = g;
      const oW = V(-g, Yn, 0), oE = V(g, Yn, 0), brk = d.mol.update(oW, oE, I, I, 1).clone();
      const cW = d.S('warhead').add(oW), cE = d.S('e3lig').add(oE);
      d.mol.group.scale.setScalar(k); d.mol.group.position.copy(brk).multiplyScalar(1 - k);
      d.P.brd4.position.add(cW.clone().sub(brk).multiplyScalar(k - 1)).add(V(-s.pull, 0, 0));
      for (const key of ['vhl', 'elob', 'eloc']) d.P[key].position.add(cE.clone().sub(brk).multiplyScalar(k - 1)).add(V(s.pull, 0, 0));

      // ---- colours: Tidepool, and the blueprint's line colour ----
      const LIGHT = new THREE.Color('#EAF3EF'), BG = new THREE.Color('#0C4341');
      const protKeys = ['brd4', 'vhl', 'elob', 'eloc'];
      const meshOf = key => d.P[key].children[0], outlineOf = key => meshOf(key).children[0];
      protKeys.forEach(key => {
        const m = meshOf(key), u = m.material.uniforms, o = outlineOf(key);
        if (s.proteins === 'none') d.P[key].visible = false;
        if (s.proteins === 'flat') u.ring.value.copy(u.col.value);
        if (s.proteins === 'ghost') { m.material.transparent = true; m.material.depthWrite = false; u.alpha.value = .22; o.material.transparent = true; o.material.depthWrite = false; o.material.uniforms.alpha.value = .55; m.renderOrder = 1; }
        if (s.proteins === 'line') { u.col.value.copy(BG); u.ring.value.copy(LIGHT); o.material.uniforms.color.value.copy(LIGHT); }
      });

      // ---- the degrader ----
      const ch = d.mol.group.children, heads = [ch[0], ch[1]], lineMat = heads[0].children[0].material;
      const add = (geo, mat, pos, quat, outline = true) => { const m = new THREE.Mesh(geo, mat); m.position.copy(pos); if (quat) m.quaternion.copy(quat);
        if (outline) { const o = new THREE.Mesh(geo, lineMat); o.renderOrder = -1; m.add(o); } d.mol.group.add(m); return m; };
      if (s.mol === 'pods') [ch[7], ch[8]].forEach((t, i) => { const h = heads[i]; h.visible = false;
        const pth = t.geometry.parameters.path, u = i === 0 ? 0 : 1, end = pth.getPointAt(u), dir = pth.getTangentAt(u).normalize();
        h.geometry.computeBoundingSphere(); const r = h.geometry.boundingSphere.radius;
        add(new THREE.CapsuleGeometry(r * .33, r * .55, 12, 28), h.material, end.clone().addScaledVector(dir, (i === 0 ? -1 : 1) * r * .2), new THREE.Quaternion().setFromUnitVectors(V(0, 1, 0), dir)); });
      if (s.line) {   // the degrader as line-work: fills take the ground, outlines and strand take the line colour
        const flat = c => { const mm = heads[0].material.clone(); mm.uniforms = THREE.UniformsUtils.clone(heads[0].material.uniforms); mm.uniforms.col.value.copy(c); mm.uniforms.ink.value.copy(LIGHT); mm.uniforms.gloss.value = 0; return mm; };
        const ends = [heads[0].material, heads[1].material];
        d.mol.group.children.forEach(o => { if (o.isMesh && ends.includes(o.material)) o.material = flat(BG); });
        ch[7].material = ch[8].material = flat(LIGHT);
        lineMat.uniforms.color.value.copy(LIGHT);
      }

      // ---- the pearl: nacre, cream with a sheen that shifts with angle, growth rings, two highlights ----
      const VS = `varying vec3 vN; varying vec3 vV; varying vec3 vP;
        void main() { mat4 m = modelMatrix;
          #ifdef USE_INSTANCING
          m = m * instanceMatrix;
          #endif
          vec4 w = m * vec4(position, 1.0); vN = normalize(mat3(m) * normal); vV = normalize(cameraPosition - w.xyz); vP = position;
          gl_Position = projectionMatrix * viewMatrix * w; }`;
      const FS = `uniform vec3 base; uniform vec3 deep; uniform vec3 env; uniform float sheen; varying vec3 vN; varying vec3 vV; varying vec3 vP;
        float h(vec3 p) { return fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453); }
        float nz(vec3 p) { vec3 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
          return mix(mix(mix(h(i), h(i + vec3(1, 0, 0)), f.x), mix(h(i + vec3(0, 1, 0)), h(i + vec3(1, 1, 0)), f.x), f.y),
                     mix(mix(h(i + vec3(0, 0, 1)), h(i + vec3(1, 0, 1)), f.x), mix(h(i + vec3(0, 1, 1)), h(i + vec3(1, 1, 1)), f.x), f.y), f.z); }
        void main() {
          vec3 n = normalize(vN), v = normalize(vV), l = normalize(vec3(-.45, .8, .55)), l2 = normalize(vec3(.7, .15, .7));
          float ndv = max(dot(n, v), 0.0), fres = pow(1.0 - ndv, 2.0);
          vec3 q = normalize(vP) * 2.4;
          float t = nz(q * 3.0) * .5 + nz(q * 11.0) * .3 + nz(q * 37.0) * .2;
          float rings = .5 + .5 * sin((q.y * 1.4 + t * .9) * 14.0);
          float diff = .62 + .38 * max(dot(n, l), 0.0);
          vec3 c = base * diff * (.985 + .025 * t + .015 * rings);
          c = mix(c, deep, fres * .45);
          float film = fres * 1.4 + t * .22 + rings * .06 + n.y * .15;
          vec3 iri = .5 + .5 * cos(6.2832 * (film + vec3(.0, .34, .68)));
          c = mix(c, c * (.72 + .55 * iri), sheen * (.25 + .55 * fres));
          c = mix(c, env, pow(1.0 - ndv, 3.0) * .4 * clamp(.6 - n.y, 0.0, 1.0));
          c += vec3(1.0) * pow(max(dot(n, normalize(l + v)), 0.0), 260.0) * .85;
          c += vec3(1.0) * pow(max(dot(n, normalize(l + v)), 0.0), 14.0) * .12;
          c += vec3(1.0, .97, .93) * pow(max(dot(n, normalize(l2 + v)), 0.0), 40.0) * .22;
          gl_FragColor = vec4(c, 1.0);
          #include <colorspace_fragment>
        }`;
      const nacre = (sheen) => new THREE.ShaderMaterial({ vertexShader: VS, fragmentShader: FS, uniforms: {
        base: { value: new THREE.Color('#F1E9E2') }, deep: { value: new THREE.Color('#B8ADA6') }, env: { value: new THREE.Color('#3E8079') }, sheen: { value: sheen } } });
      // the small pearls on the strand get the same nacre, more quietly; the clasp beads and bond give way to one pearl
      ch[2].material = nacre(.45);
      [ch[4], ch[5], ch[9]].forEach(o => { o.visible = false; });
      const bondAt = ch[9].position.clone(), pr = Math.max(2.3, ch[9].scale.y / 2 + .9) * (s.pearlScale || 1);
      const pearl = add(new THREE.SphereGeometry(pr, 96, 64), nacre(1), bondAt, null, !!s.line);
      if (s.line) pearl.children[0].material = lineMat;
      ch[6].material.color.set('#F4EEE6'); ch[6].material.opacity = s.line ? .35 : .5; ch[6].scale.setScalar(pr * 4.2);   // a soft halo of pearl light

      // ---- camera ----
      const tgt = brk.clone().add(V(...s.look)), dir = V(...s.dir).normalize();
      d.camera.fov = s.fov || 26; d.camera.position.copy(tgt).addScaledVector(dir, s.dist);
      const roll = (s.roll || 0) * Math.PI / 180; d.camera.up.set(Math.sin(roll), Math.cos(roll), 0); d.camera.lookAt(tgt);
      d.renderer.setPixelRatio(2); d.renderer.setSize(s.w, s.h, false); d.camera.aspect = s.w / s.h;
      // dy: move the picture down that many pixels inside the frame (clear of the header), with nothing cut off
      if (s.dy) d.camera.setViewOffset(s.w, s.h, 0, -s.dy, s.w, s.h); else d.camera.clearViewOffset();
      d.camera.updateProjectionMatrix();
      d.renderer.setClearColor(0x000000, 0); d.scene.updateMatrixWorld(true); d.renderer.render(d.scene, d.camera);
      const at = v => { const q = v.clone().project(d.camera); return [+((q.x + 1) / 2).toFixed(4), +((1 - q.y) / 2).toFixed(4)]; };
      const ctr = o => new THREE.Box3().setFromObject(o).getCenter(V());
      const sc = v => brk.clone().add(v.clone().sub(brk).multiplyScalar(k));
      const pearlEdge = brk.clone().add(d.camera.up.clone().multiplyScalar(pr * k));
      // ---- data pass for the vector export (EXPORT=1): which object owns each pixel and the proteins' contour value ----
      let data = null;
      if (s.exportData) {
        const W = s.w * 2, H = s.h * 2;
        const objs = [];
        [['brd4', 'BRD4 (target protein)'], ['vhl', 'VHL (E3 ligase)'], ['elob', 'Elongin B'], ['eloc', 'Elongin C']].forEach(([key, name]) => {
          const m = d.P[key].children[0]; objs.push({ o: m, name, kind: 'protein', centre: m.material.uniforms.centre.value.clone(), spacing: m.material.uniforms.spacing.value }); });
        const pods = d.mol.group.children.filter(o => o.isMesh && o.geometry.type === 'CapsuleGeometry');
        pods.forEach((m, i) => objs.push({ o: m, name: i === 0 ? 'Target-binding end' : 'Ligase-binding end', kind: 'pod' }));
        objs.push({ o: ch[7], name: 'Linker strand, target side', kind: 'strand' }, { o: ch[8], name: 'Linker strand, ligase side', kind: 'strand' });
        objs.push({ o: ch[2], name: 'Linker pearls', kind: 'pearls' }, { o: pearl, name: 'The pearl', kind: 'pearl' });
        const keep = new Set(objs.map(e => e.o));
        d.scene.traverse(o => { if ((o.isMesh || o.isSprite || o.isLine || o.isPoints) && !keep.has(o)) o.visible = false; });
        const dVS = `varying vec3 vL; void main() { vL = position; mat4 m = modelMatrix;
          #ifdef USE_INSTANCING
          m = m * instanceMatrix;
          #endif
          gl_Position = projectionMatrix * viewMatrix * m * vec4(position, 1.0); }`;
        const dFS = `uniform float oid; uniform vec3 centre; uniform float spacing; varying vec3 vL;
          void main() { float dd = spacing > 0.0 ? length(vL - centre) / spacing : 0.0; gl_FragColor = vec4(oid, dd, 0.0, 1.0); }`;
        objs.forEach((e, i) => { e.o.visible = true; e.o.material = new THREE.ShaderMaterial({ vertexShader: dVS, fragmentShader: dFS, side: THREE.FrontSide,
          uniforms: { oid: { value: i + 1 }, centre: { value: e.centre || V() }, spacing: { value: e.spacing || 0 } } }); });
        const rt = new THREE.WebGLRenderTarget(W, H, { type: THREE.FloatType, minFilter: THREE.NearestFilter, magFilter: THREE.NearestFilter });
        d.renderer.setPixelRatio(1); d.renderer.setSize(W, H, false);
        d.renderer.setRenderTarget(rt); d.renderer.setClearColor(0x000000, 0); d.renderer.clear(); d.renderer.render(d.scene, d.camera);
        const buf = new Float32Array(W * H * 4); d.renderer.readRenderTargetPixels(rt, 0, 0, W, H, buf); d.renderer.setRenderTarget(null);
        const out = new Uint8Array(W * H * 3);
        for (let i = 0, j = 0; i < W * H; i++, j += 3) { out[j] = Math.round(buf[i * 4]); const q = Math.min(65535, Math.round(buf[i * 4 + 1] * 256)); out[j + 1] = q >> 8; out[j + 2] = q & 255; }
        let bin = ''; for (let i = 0; i < out.length; i += 32768) bin += String.fromCharCode.apply(null, out.subarray(i, i + 32768));
        // pearls as true circles: centre and radius in picture pixels (1440 x 810)
        const px = w => { const q = w.clone().project(d.camera); return [(q.x + 1) / 2 * s.w, (1 - q.y) / 2 * s.h]; };
        const circ = (centre, r) => { const [x, y] = px(centre), [x2, y2] = px(centre.clone().addScaledVector(d.camera.up, r)); return { x, y, r: Math.hypot(x2 - x, y2 - y) }; };
        const small = []; const mI = new THREE.Matrix4(), pos = V(), qq = new THREE.Quaternion(), scl = V();
        for (let i = 0; i < ch[2].count; i++) { ch[2].getMatrixAt(i, mI); mI.premultiply(ch[2].matrixWorld).decompose(pos, qq, scl); small.push(circ(pos.clone(), scl.x)); }
        const pw = pearl.getWorldPosition(V()), pScale = pearl.getWorldScale(V()).x;
        const order = objs.map((e, i) => ({ i, dist: new THREE.Box3().setFromObject(e.o).getCenter(V()).distanceTo(d.camera.position) })).sort((a, b) => b.dist - a.dist).map(e => e.i + 1);
        data = { b64: btoa(bin), meta: { w: W, h: H, scale: 2, objects: objs.map((e, i) => ({ id: i + 1, name: e.name, kind: e.kind })), backToFront: order,
          pearls: small, pearl: circ(pw, pr * pScale) } };
      }
      return { data, url: d.renderer.domElement.toDataURL('image/png'), anchors: { pearl: at(brk), pearlTop: at(pearlEdge), target: at(ctr(d.P.brd4)), ligase: at(ctr(d.P.vhl)),
        endW: at(sc(cW)), endE: at(sc(cE)), linkW: at(sc(cW).lerp(brk, .5)), linkE: at(sc(cE).lerp(brk, .5)) } };
    }, s);
    if (res.data) { fs.mkdirSync(HERE + 'vector', { recursive: true }); fs.writeFileSync(HERE + 'vector/' + s.name + '-data.bin', Buffer.from(res.data.b64, 'base64'));
      fs.writeFileSync(HERE + 'vector/' + s.name + '-meta.json', JSON.stringify(res.data.meta, null, 1)); console.log('wrote vector data for', s.name); await p.close(); continue; }
    fs.writeFileSync(IMG + s.name + '.png', Buffer.from(res.url.split(',')[1], 'base64')); fs.writeFileSync(IMG + s.name + '.json', JSON.stringify(res.anchors));
    console.log('wrote', s.name, errs.length ? errs : '');
    await p.close();
  }
  await b.close();
})();
