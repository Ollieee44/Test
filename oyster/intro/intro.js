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

  // timeline (ms): the closed oyster rushes out towards the viewer, pulls back as it opens on its pearl, then
  // recedes into the screen until it sits exactly in the logotype's 'o'; the ink disc closes round it, the word
  // writes in, and the logotype settles into the header
  const T = { fade: [0, 250], fly: [0, 1000], open: [950, 1900], recede: [2000, 2750], merge: [2450, 2850],
    letters: [2650, 3150], ther: [2950, 3350], glide: [3450, 4250], bg: [3650, 4250], site: 3850, end: 4300 };
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
  const PEARL_AT = new THREE.Vector3(62, -52, 0), PEARL_R = 9.5;
  const pearl = new THREE.Mesh(new THREE.SphereGeometry(PEARL_R, 48, 32), pearlMat); pearl.position.copy(PEARL_AT); oyster.add(pearl);
  addOutline(pearl, .5).material.uniforms.color.value.set(INK);
  const CLOSED = -.06, OPEN = 24 * Math.PI / 180;   // the logo's pose: the upper shell lifted 24 degrees

  // ---------- the logotype: its 'o' is the same open oyster cut out of an ink disc ----------
  const logo = document.getElementById('ilogo'), disc = document.getElementById('ioDisc'), mark = document.getElementById('ioMark');
  const clipR = document.getElementById('ioClipR'), letters = document.getElementById('ioLetters'), ther = document.getElementById('ioTher');
  const head = document.querySelector('.head .wm');
  document.getElementById('ipearl').remove();
  // the 'o' fully drawn: shell cut-out, hollow and small pearl in place, disc in ink; only its opacity animates
  document.getElementById('ioCut').setAttribute('transform', 'translate(51.5 50) scale(0.76) translate(-50.5 -47.5)');
  document.getElementById('ioHole').setAttribute('r', '10.26'); document.getElementById('ioPearl').setAttribute('r', '7.22');
  disc.style.fill = INK;
  // logotype units (viewBox 21.8 -613.8 2441 857.3): the 'o' disc centre, and logotype units per shell unit
  const VB = [21.8, -613.8, 2441], DISC = [-17.1 + 6.3571 * 50, -583.4 + 6.3571 * 51.5], PER_SHELL = 6.3571 * .76;
  // the disc centre in shell coordinates is (50.5, 47.5): in the scene that is this point
  const DISC_W = new THREE.Vector3(50.5 - 51, -47.5 + 58, 0);
  const TAN = Math.tan(THREE.MathUtils.degToRad(11));
  let W = 0, H = 0, LW = 0, K = null, Dc = 0, Dm = 0, Dl = 0, TL = null;
  function layout() {
    W = innerWidth; H = innerHeight; const narrow = W < 760;
    r3.setPixelRatio(Math.min(devicePixelRatio, 2)); r3.setSize(W, H, false); cam.aspect = W / H; cam.updateProjectionMatrix();
    LW = Math.min(W * (narrow ? .84 : .62), 900); logo.style.width = LW + 'px';
    const u = LW / VB[2], lh = LW * 857.3 / VB[2];
    K = { full: [(W - LW) / 2, H * .47 - lh / 2, 1] };
    // camera distance at which the shell (86 wide, about 62 tall) spans a fraction f of the screen
    const dist = f => Math.max(86 / (f * W), 62 / (f * .85 * H)) * H / (2 * TAN);
    Dc = dist(narrow ? 1.35 : 1.1); Dm = dist(narrow ? .78 : .4);
    // the logotype's 'o': its shells are PER_SHELL * u px per shell unit; at that scale the camera sits square on
    // and aims so that the disc centre lands on the 'o' on screen
    const s = PER_SHELL * u; Dl = H / (2 * TAN * s);
    const ox = K.full[0] + (DISC[0] - VB[0]) * u, oy = K.full[1] + (DISC[1] - VB[1]) * u;
    TL = new THREE.Vector3(DISC_W.x - (ox - W / 2) / s, DISC_W.y + (oy - H / 2) / s, 0);
  }
  layout(); addEventListener('resize', layout);
  const place = ([x, y, s]) => `translate(${x.toFixed(2)}px, ${y.toFixed(2)}px) scale(${s.toFixed(5)})`;
  const between = (A, B, g) => [lerp(A[0], B[0], g), lerp(A[1], B[1], g), Math.exp(lerp(Math.log(A[2]), Math.log(B[2]), g))];
  const logLerp = (a, b, x) => Math.exp(lerp(Math.log(a), Math.log(b), x));
  const CENTRE = new THREE.Vector3(0, -4, 0);

  function render(t) {
    // the rush out: from far away to nearly filling the screen, accelerating; then it eases back as it opens
    const fly = k(t, T.fly), fe = fly * fly * (3 - 2 * fly) * .4 + fly * fly * fly * .6, op = ease(k(t, T.open)), rc = ease(k(t, T.recede));
    let D = logLerp(Dc * 9, Dc, fe); D = logLerp(D, Dm, op); D = logLerp(D, Dl, rc);
    hinge.rotation.z = lerp(CLOSED, OPEN, op);
    // a three-quarter view while it flies, turning square on as it opens and recedes
    const az = lerp(lerp(.55, .2, fe), 0, Math.max(op * .6, rc)), el = lerp(lerp(.38, .2, fe), 0, Math.max(op * .5, rc));
    const tgt = CENTRE.clone().lerp(TL, rc);
    cam.position.set(tgt.x + D * Math.sin(az) * Math.cos(el), tgt.y + D * Math.sin(el), tgt.z + D * Math.cos(az) * Math.cos(el)); cam.lookAt(tgt);
    pearlMat.uniforms.glint.value = 1.3 * bump(t, 1500, 2200);
    sc.updateMatrixWorld(); r3.render(sc, cam);
    // merge: the ink disc fades in round the oyster (its cut-outs line up with the shells and the pearl), then the 3D goes
    const m = ease(k(t, T.merge));
    mark.style.opacity = m.toFixed(3);
    r3.domElement.style.opacity = (k(t, T.fade) * (1 - k(t, [T.merge[0] + 150, T.merge[1] + 100]))).toFixed(3);
    // the rest of the word writes in from the left, 'therapeutics' rises in under it
    clipR.setAttribute('width', (2100 * ease(k(t, T.letters))).toFixed(1));
    letters.style.opacity = k(t, [T.letters[0], T.letters[0] + 150]).toFixed(3);
    const thIn = ease(k(t, T.ther)); ther.style.opacity = (thIn * (1 - k(t, [T.glide[0], T.glide[0] + 350]))).toFixed(3);
    ther.setAttribute('transform', `translate(0 ${(30 * (1 - thIn)).toFixed(1)})`);
    // the logotype then shrinks into the header wordmark (same drawing, same frame) as the story fades in under it
    let pose = K.full;
    if (t >= T.glide[0]) {
      if (!K.head) { const h = head.getBoundingClientRect(); K.head = [h.left, h.top, h.width / LW]; }
      pose = between(K.full, K.head, ease(k(t, T.glide)));
    }
    logo.style.transform = place(pose);
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
