// ---------- intro: the oyster opens, its pearl becomes the 'o', the logotype forms and settles into the header ----------
// Plays once on load (about 5 s) and hands over to the scroll story. Skip, or any attempt to scroll, jumps to the
// final glide. Reduced motion, no WebGL, or a page that loads already scrolled: straight to the landing page.
(() => {
  const ov = document.getElementById('intro'), skipBtn = document.getElementById('introSkip'), html = document.documentElement;
  if (!ov) return;
  let finished = false;
  const finish = () => {
    if (finished) return; finished = true;
    html.classList.add('intro-end'); html.classList.remove('intro');
    ov.remove(); if (skipBtn) skipBtn.remove();
    if (r3) { r3.dispose(); r3.forceContextLoss(); }
    setTimeout(() => html.classList.remove('intro-end'), 1200);
  };
  let r3 = null;
  if (reduce || !renderer || scrollY > 10) { finish(); return; }
  try { r3 = new THREE.WebGLRenderer({ canvas: document.getElementById('introGl'), antialias: true, alpha: true }); } catch (e) { finish(); return; }

  // timeline (ms)
  const T = { fade: [0, 450], open: [350, 1750], lift: [1700, 2600], disc: [2450, 3050], carve: [2700, 3350], letters: [3000, 3750], ther: [3400, 3950], glide: [4100, 5000], bg: [4300, 5000], site: 4450, end: 5050 };
  const k = (t, [a, b]) => clamp((t - a) / (b - a), 0, 1), eo = x => 1 - Math.pow(1 - x, 3);
  const lerp = (a, b, x) => a + (b - a) * x;
  const COL = ({ nacre: { out: '#CDB8C6', inn: '#F6ECF0', ring: '#8C5572' }, tidepool: { out: '#6FA79D', inn: '#DDF0EA', ring: '#06302E' } })[pal] || { out: '#CDB8C6', inn: '#F6ECF0', ring: '#8C5572' };
  const css = n => getComputedStyle(html).getPropertyValue(n).trim();
  const INK = css('--ink'), PEARL = css('--pearl');
  ov.style.setProperty('--intro-a', PAL[pal].sky[0][0]); ov.style.setProperty('--intro-b', PAL[pal].sky[0][1]);

  // ---------- the oyster, sculpted from the logo's two shell shapes ----------
  // Each shell's outline is the logo path; across its length the shell bulges into a rounded belly whose depth
  // follows the outline's height, and the open face is gently dished (the nacre inside).
  const bez = (a, b, c, d, t) => { const u = 1 - t; return [0, 1].map(i => u * u * u * a[i] + 3 * u * u * t * b[i] + 3 * u * t * t * c[i] + t * t * t * d[i]); };
  function outline(start, segs) { const pts = [start]; let cur = start;
    for (const s of segs) { if (s.length === 1) { pts.push(s[0]); cur = s[0]; } else { for (let i = 1; i <= 20; i++) pts.push(bez(cur, s[0], s[1], s[2], i / 20)); cur = s[2]; } }
    pts.push(start); return pts; }
  const LOWER = outline([10, 60], [[[10, 58], [12, 57], [14, 57]], [[84, 57]], [[90, 57], [93, 60], [92, 64]], [[88, 80], [70, 90], [48, 90]], [[27, 90], [11, 78], [10, 60]]]);
  const UPPER = outline([12, 53], [[[12, 51], [13, 50], [15, 50]], [[84, 50]], [[90, 50], [93, 47], [91, 44]], [[85, 34], [66, 29], [46, 30]], [[27, 31], [13, 40], [12, 53]]]);
  function span(poly, x) { const ys = [];
    for (let i = 0; i < poly.length - 1; i++) { const [x0, y0] = poly[i], [x1, y1] = poly[i + 1]; if (x0 !== x1 && (x0 - x) * (x1 - x) <= 0) ys.push(y0 + (y1 - y0) * (x - x0) / (x1 - x0)); }
    return ys.length ? [Math.min(...ys), Math.max(...ys)] : null; }
  function shell(poly, bellyDown, depth) {
    const xs = poly.map(p => p[0]), x0 = Math.min(...xs), x1 = Math.max(...xs), N = 80, M = 56, pos = [], outer = [], inner = [];
    for (let i = 0; i <= N; i++) {
      const x = lerp(x0, x1, (1 - Math.cos(Math.PI * i / N)) / 2), s = span(poly, clamp(x, x0 + 1e-3, x1 - 1e-3)) || [0, 0];
      const flat = bellyDown ? s[0] : s[1], d = bellyDown ? s[1] - s[0] : s[0] - s[1], w = depth * Math.abs(d);
      for (let j = 0; j < M; j++) { const th = 2 * Math.PI * j / M, sn = Math.sin(th);
        pos.push(x, -(th <= Math.PI ? flat + d * sn : flat - .16 * d * sn), w * Math.cos(th)); } }
    for (let i = 0; i < N; i++) for (let j = 0; j < M; j++) { const a = i * M + j, b = i * M + (j + 1) % M, c = a + M, e = b + M;
      (j < M / 2 ? outer : inner).push(a, c, b, b, c, e); }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    g.setIndex(outer.concat(inner)); g.addGroup(0, outer.length, 0); g.addGroup(outer.length, inner.length, 1);
    g.computeVertexNormals();
    // keep the faces pointing outwards (the outline pushes along the normals)
    const n = g.attributes.normal, p = g.attributes.position, mid = Math.floor(N / 2) * M + Math.floor(M / 4);
    if (n.getY(mid) * (bellyDown ? -1 : 1) < 0) { const ix = g.index.array; for (let q = 0; q < ix.length; q += 3) { const t = ix[q + 1]; ix[q + 1] = ix[q + 2]; ix[q + 2] = t; } g.computeVertexNormals(); }
    return g;
  }
  const sc = new THREE.Scene(), cam = new THREE.PerspectiveCamera(22, 1, 1, 4000);
  const HINGE = new THREE.Vector3(12, -53, 0);
  function shellMesh(geo) {
    const out = cmat('out', 3.2, HINGE.clone()), inn = cmat('inn', 3.2, HINGE.clone());
    out.uniforms.col.value.set(COL.out); out.uniforms.ring.value.set(COL.ring);
    inn.uniforms.col.value.set(COL.inn); inn.uniforms.ring.value.set(COL.inn);   // the inside is smooth nacre: no growth lines
    const m = new THREE.Mesh(geo, [out, inn]); const o = addOutline(m, .7); o.material.uniforms.color.value.set(INK); return m;
  }
  const oyster = new THREE.Group(); sc.add(oyster); oyster.position.set(-51, 58, 0);   // centre the shells on the origin
  const lower = shellMesh(shell(LOWER, true, .72)); oyster.add(lower);
  const hinge = new THREE.Group(); hinge.position.copy(HINGE); oyster.add(hinge);
  const upper = shellMesh(shell(UPPER, false, .78)); upper.position.copy(HINGE).negate(); hinge.add(upper);
  const pearlMat = new THREE.ShaderMaterial({ uniforms: { col: { value: new THREE.Color(PEARL) }, glint: { value: 0 } },
    vertexShader: `varying vec3 vN; varying vec3 vV; void main() { vec4 w = modelMatrix * vec4(position, 1.0); vN = normalize(mat3(modelMatrix) * normal); vV = normalize(cameraPosition - w.xyz); gl_Position = projectionMatrix * viewMatrix * w; }`,
    fragmentShader: `uniform vec3 col; uniform float glint; varying vec3 vN; varying vec3 vV;
      void main() { vec3 n = normalize(vN), v = normalize(vV), l = normalize(vec3(-.4, .7, .6));
        float dif = .8 + .2 * max(dot(n, l), 0.0), sp = pow(max(dot(n, normalize(l + v)), 0.0), 70.0) * (.5 + glint), rim = pow(1.0 - max(dot(n, v), 0.0), 2.5);
        gl_FragColor = vec4(col * dif + vec3(sp) + mix(col, vec3(1.0), .5) * rim * .22, 1.0);
        #include <colorspace_fragment>
      }` });
  const PEARL_AT = new THREE.Vector3(62, -51, 0), PEARL_R = 9.5;
  const pearl = new THREE.Mesh(new THREE.SphereGeometry(PEARL_R, 48, 32), pearlMat); pearl.position.copy(PEARL_AT); oyster.add(pearl);
  addOutline(pearl, .5).material.uniforms.color.value.set(INK);
  const CLOSED = -.07, OPEN = 24 * Math.PI / 180;   // the logo's pose: the upper shell lifted 24 degrees about the hinge

  // ---------- the logotype, large and centred, then into the header ----------
  const logo = document.getElementById('ilogo'), disc = document.getElementById('ioDisc'), mark = document.getElementById('ioMark');
  const cut = document.getElementById('ioCut'), hole = document.getElementById('ioHole'), smallPearl = document.getElementById('ioPearl');
  const clipR = document.getElementById('ioClipR'), letters = document.getElementById('ioLetters'), ther = document.getElementById('ioTher');
  const pdiv = document.getElementById('ipearl'), head = document.querySelector('.head .wm');
  let W = 0, H = 0, L = null;
  function layout() {
    W = innerWidth; H = innerHeight; const narrow = W < 760;
    r3.setPixelRatio(Math.min(devicePixelRatio, 2)); r3.setSize(W, H, false); cam.aspect = W / H; cam.updateProjectionMatrix();
    const lw = Math.min(W * (narrow ? .84 : .62), 900), lh = lw * 857.3 / 2441;
    logo.style.width = lw + 'px'; L = { x: (W - lw) / 2, y: H * .47 - lh * .5, w: lw };
    // the oyster fills about a third of the width (more on phones), a little below centre
    const frac = narrow ? .62 : .3, D = (86 / frac) / (2 * Math.tan(THREE.MathUtils.degToRad(11)) * cam.aspect);
    cam.userData.D = D;
  }
  layout(); addEventListener('resize', layout);
  const hex = c => new THREE.Color(c), mixHex = (a, b, x) => '#' + hex(a).lerp(hex(b), x).getHexString();
  let glideFrom = null, pearlFrom = null, discTo = null;
  function screenOf(v) { const p = v.clone().project(cam); return [(p.x + 1) / 2 * W, (1 - p.y) / 2 * H]; }

  function render(t) {
    // 3D: fade in, turn to face front while the upper shell lifts to the logo's pose; the pearl glints as it is revealed
    const o = eo(k(t, T.open)), f = k(t, T.fade), lift = ease(k(t, T.lift));
    hinge.rotation.z = lerp(CLOSED, OPEN, ease(k(t, T.open)));
    const az = lerp(.62, 0, o), el = lerp(.32, .04, o), D = cam.userData.D * lerp(1.08, 1, o);
    cam.position.set(D * Math.sin(az) * Math.cos(el), D * Math.sin(el) - 4, D * Math.cos(az) * Math.cos(el)); cam.lookAt(0, -4, 0);
    pearlMat.uniforms.glint.value = 1.4 * bump(t, 1300, 1900);
    oyster.scale.setScalar(lerp(.94, 1, f) * lerp(1, .82, lift)); oyster.position.y = 58 - 10 * lift;
    pearl.visible = t < T.lift[0];
    r3.domElement.style.opacity = (f * (1 - k(t, [T.lift[0] + 150, T.lift[1] - 100]))).toFixed(3);
    sc.updateMatrixWorld(); r3.render(sc, cam);
    // the logotype's position, and where its 'o' disc sits on screen
    logo.style.transform = glideFrom ? '' : `translate(${L.x}px, ${L.y}px)`;
    if (!discTo) { const r = disc.getBoundingClientRect(); discTo = [r.left + r.width / 2, r.top + r.height / 2, r.width / 2]; }
    // the pearl leaves the shell as a flat-shaded disc, rises and swings left into the 'o', growing to its size
    if (t >= T.lift[0] && !pearlFrom) { const c = PEARL_AT.clone(); oyster.localToWorld(c); const e = c.clone().add(new THREE.Vector3().setFromMatrixColumn(cam.matrixWorld, 0).multiplyScalar(PEARL_R * oyster.scale.x));
      const s0 = screenOf(c), s1 = screenOf(e); pearlFrom = [s0[0], s0[1], Math.hypot(s1[0] - s0[0], s1[1] - s0[1])]; }
    if (pearlFrom) {
      const [x0, y0, r0] = pearlFrom, [x1, y1, r1] = discTo;
      const x = lerp(x0, x1, lift), y = lerp(y0, y1, lift) - Math.sin(Math.PI * lift) * H * .08, r = lerp(r0, r1, eo(lift));
      pdiv.style.transform = `translate(${x}px, ${y}px) scale(${(2 * r / 100).toFixed(4)})`;
      pdiv.style.opacity = (1 - k(t, [T.disc[0], T.disc[0] + 250])).toFixed(3);
    } else pdiv.style.opacity = 0;
    // the disc turns from pearl to ink, then the open shell is carved out of it and a small pearl settles in the hollow
    mark.style.opacity = k(t, [T.disc[0], T.disc[0] + 200]).toFixed(3);
    disc.style.fill = mixHex(PEARL, INK, ease(k(t, T.disc)));
    const cv = eo(k(t, T.carve));
    cut.setAttribute('transform', `translate(51.5 50) scale(${(.76 * cv).toFixed(4)}) translate(-50.5 -47.5)`);
    hole.setAttribute('r', (10.26 * cv).toFixed(3)); smallPearl.setAttribute('r', (7.22 * eo(k(t, [T.carve[0] + 200, T.carve[1] + 100]))).toFixed(3));
    // 'yster' writes in from the left, 'therapeutics' rises in under it
    clipR.setAttribute('width', (2100 * ease(k(t, T.letters))).toFixed(1));
    letters.style.opacity = k(t, [T.letters[0], T.letters[0] + 150]).toFixed(3);
    const th = ease(k(t, T.ther)) * (1 - k(t, [T.glide[0], T.glide[0] + 350]));
    ther.style.opacity = th.toFixed(3); ther.setAttribute('transform', `translate(0 ${(30 * (1 - ease(k(t, T.ther)))).toFixed(1)})`);
    // glide: the logotype shrinks into the header wordmark (same drawing, same frame) while the story fades in under it
    if (t >= T.glide[0]) {
      if (!glideFrom) { const h = head.getBoundingClientRect(); glideFrom = { x: L.x, y: L.y, s: h.width / L.w, tx: h.left, ty: h.top }; }
      const g = ease(k(t, T.glide)), G = glideFrom;
      logo.style.transform = `translate(${lerp(G.x, G.tx, g)}px, ${lerp(G.y, G.ty, g)}px) scale(${lerp(1, G.s, g)})`;
    }
    ov.querySelector('.ibg').style.opacity = (1 - ease(k(t, T.bg))).toFixed(3);
    if (skipBtn) { const so = 1 - k(t, [T.glide[0], T.glide[0] + 300]); skipBtn.style.opacity = so.toFixed(3); skipBtn.style.visibility = so > 0 ? '' : 'hidden'; }
    if (t >= T.site && html.classList.contains('intro')) { html.classList.add('intro-end'); html.classList.remove('intro'); }
  }

  let t0 = performance.now(), held = false;
  const jump = () => { const t = performance.now() - t0; if (t < T.glide[0] - 60) t0 = performance.now() - (T.glide[0] - 60); };
  if (skipBtn) skipBtn.addEventListener('click', jump);
  addEventListener('wheel', jump, { passive: true }); addEventListener('touchmove', jump, { passive: true });
  addEventListener('keydown', e => { if ([' ', 'ArrowDown', 'PageDown', 'End', 'Enter', 'Escape'].includes(e.key)) jump(); });
  function tick() { if (finished || held) return; const t = performance.now() - t0; render(t); if (t >= T.end) finish(); else requestAnimationFrame(tick); }
  requestAnimationFrame(tick);
  // test hook: hold the intro at time t (ms)
  window.__intro = { at: t => { held = true; render(t); }, T };
})();
