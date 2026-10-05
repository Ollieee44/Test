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
  // one camera move (move): out of the distance, closest at about a third, then back and across into the 'o';
  // the lid opens through the closest point and the pan starts before the pull-back ends, so nothing stops
  const T = { fade: [0, 180], move: [0, 1900], merge: [1650, 1950],
    letters: [1800, 2650], ther: [2250, 2650], glide: [2850, 3410], bg: [2990, 3410], site: 3130, end: 3450 };
  const k = (t, [a, b]) => clamp((t - a) / (b - a), 0, 1), eo = x => 1 - Math.pow(1 - x, 3);
  const lerp = (a, b, x) => a + (b - a) * x;
  const COL = ({ nacre: { out: '#CDB8C6', inn: '#EBD9E2', ring: '#8C5572' }, tidepool: { out: '#6FA79D', inn: '#DDF0EA', ring: '#06302E' } })[pal] || { out: '#CDB8C6', inn: '#EBD9E2', ring: '#8C5572' };
  const css = n => getComputedStyle(html).getPropertyValue(n).trim();
  const INK = css('--ink'), PEARL = css('--pearl');
  ov.style.setProperty('--intro-a', PAL[pal].sky[0][0]); ov.style.setProperty('--intro-b', PAL[pal].sky[0][1]);

  // ---------- the oyster: two shallow, rounded valves, a cupped bowl and a flatter lid hinged at the back ----------
  // Each valve is a round, slightly wavy outline in the horizontal plane, domed into a shell with a dished
  // nacre inside; growth rings radiate from the hinge, as on a real shell.
  const R0 = 40, ZS = 1, RIM = th => R0 * (1 + .018 * Math.sin(7 * th) + .008 * Math.sin(3 * th + 1));
  const HZ = -R0 * ZS;   // the hinge, at the back
  function valve(outD, inD) {   // outD, inD: heights of the outer and inner surfaces at the centre (negative = downwards)
    const NR = 40, NT = 120, pos = [], outer = [], inner = [];
    for (const [d, list, flip] of [[outD, outer, outD > 0], [inD, inner, inD < 0]]) {   // faces wound to point out of the shell
      const base = pos.length / 3;
      for (let i = 0; i <= NR; i++) { const r = i / NR, h = d * (1 - r * r);
        for (let j = 0; j < NT; j++) { const th = 2 * Math.PI * j / NT, R = RIM(th) * r; pos.push(R * Math.cos(th), h, R * Math.sin(th) * ZS); } }
      for (let i = 0; i < NR; i++) for (let j = 0; j < NT; j++) {
        const a = base + i * NT + j, b = base + i * NT + (j + 1) % NT, c = a + NT, e = b + NT;
        if (flip) list.push(a, b, c, b, e, c); else list.push(a, c, b, b, c, e); }
    }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    g.setIndex(outer.concat(inner)); g.addGroup(0, outer.length, 0); g.addGroup(outer.length, inner.length, 1);
    g.computeVertexNormals(); return g;
  }
  const sc = new THREE.Scene(), cam = new THREE.PerspectiveCamera(22, 1, 1, 4000);
  const RING_AT = new THREE.Vector3(0, 0, HZ);
  function shellMesh(geo) {
    const out = cmat('out', 3, RING_AT.clone()), inn = cmat('inn', 3, RING_AT.clone());
    out.uniforms.col.value.set(COL.out); out.uniforms.ring.value.set(COL.ring);
    inn.uniforms.col.value.set(COL.inn); inn.uniforms.ring.value.set(COL.inn);   // the inside is smooth nacre: no growth lines
    const m = new THREE.Mesh(geo, [out, inn]);
    const og = new THREE.BufferGeometry(); og.setAttribute('position', geo.attributes.position); og.setAttribute('normal', geo.attributes.normal);
    og.setIndex(Array.from(geo.index.array.slice(0, geo.groups[0].count)));
    const shellOnly = new THREE.Mesh(og); const o = addOutline(shellOnly, .6); shellOnly.remove(o); m.add(o);
    o.material.uniforms.color.value.set(INK); return m;
  }
  const oyster = new THREE.Group(); sc.add(oyster);
  const lower = shellMesh(valve(-18, -14.5)); oyster.add(lower);
  const hinge = new THREE.Group(); hinge.position.set(0, 0, HZ); oyster.add(hinge);
  const upper = shellMesh(valve(9, 6)); upper.position.set(0, 0, -HZ); hinge.add(upper);
  const pearlMat = new THREE.ShaderMaterial({ uniforms: { col: { value: new THREE.Color(PEARL) }, glint: { value: 0 } },
    vertexShader: `varying vec3 vN; varying vec3 vV; void main() { vec4 w = modelMatrix * vec4(position, 1.0); vN = normalize(mat3(modelMatrix) * normal); vV = normalize(cameraPosition - w.xyz); gl_Position = projectionMatrix * viewMatrix * w; }`,
    fragmentShader: `uniform vec3 col; uniform float glint; varying vec3 vN; varying vec3 vV;
      void main() { vec3 n = normalize(vN), v = normalize(vV), l = normalize(vec3(-.4, .7, .6));
        float dif = .8 + .2 * max(dot(n, l), 0.0), sp = pow(max(dot(n, normalize(l + v)), 0.0), 70.0) * (.5 + glint), rim = pow(1.0 - max(dot(n, v), 0.0), 2.5);
        gl_FragColor = vec4(col * dif + vec3(sp) + mix(col, vec3(1.0), .5) * rim * .22, 1.0);
        #include <colorspace_fragment>
      }` });
  const PEARL_R = 9, PEARL_AT = new THREE.Vector3(0, -14.5 + PEARL_R + .6, 4);
  const pearl = new THREE.Mesh(new THREE.SphereGeometry(PEARL_R, 48, 32), pearlMat); pearl.position.copy(PEARL_AT); oyster.add(pearl);
  addOutline(pearl, .5).material.uniforms.color.value.set(INK);
  const CLOSED = 0, OPEN = 68 * Math.PI / 180;   // the lid lifts towards the viewer, about the hinge at the back

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
  const VB = [21.8, -613.8, 2441], DISC = [-17.1 + 6.3571 * 50, -583.4 + 6.3571 * 51.5, 42 * 6.3571];
  const EL0 = .38, EL1 = .32;   // camera elevation: looking a little down on the oyster, so the lid and the pearl both show
  const CENTRE = new THREE.Vector3(0, -2, 0);
  const TAN = Math.tan(THREE.MathUtils.degToRad(11));
  let W = 0, H = 0, LW = 0, K = null, Dc = 0, Dm = 0, Dl = 0, TL = null;
  function layout() {
    W = innerWidth; H = innerHeight; const narrow = W < 760;
    r3.setPixelRatio(Math.min(devicePixelRatio, 2)); r3.setSize(W, H, false); cam.aspect = W / H; cam.updateProjectionMatrix();
    LW = Math.min(W * (narrow ? .84 : .62), 900); logo.style.width = LW + 'px';
    const u = LW / VB[2], lh = LW * 857.3 / VB[2];
    K = { full: [(W - LW) / 2, H * .47 - lh / 2, 1] };
    // camera distance at which the shell (86 wide, about 62 tall) spans a fraction f of the screen
    const dist = f => Math.max(2 * R0 / (f * W), 1.5 * R0 / (f * .85 * H)) * H / (2 * TAN);
    Dc = dist(narrow ? 1.25 : 1.05); Dm = dist(narrow ? .8 : .42);
    // the logotype's 'o': the oyster recedes until its pearl is exactly the logo's pearl, in size and place, so the
    // pearl carries straight through as the ink disc closes round the shell
    const s = 7.22 * 6.3571 * u / PEARL_R; Dl = H / (2 * TAN * s);
    const px = K.full[0] + (-17.1 + 6.3571 * (60.24 - 1.5) - VB[0]) * u, py = K.full[1] + (-583.4 + 6.3571 * (53.42 + 1.5) - VB[1]) * u;
    // it ends in side profile, as the logo draws it: camera level, looking along +x, so the hinge is on the left
    TL = PEARL_AT.clone().add(new THREE.Vector3(0, 0, -(px - W / 2) / s)).add(new THREE.Vector3(0, (py - H / 2) / s, 0));
  }
  let L9 = 0, Lc = 0, Ll = 0;
  const setPath = () => { L9 = Math.log(Dc * 9); Lc = Math.log(Dc); Ll = Math.log(Dl); };
  layout(); setPath(); addEventListener('resize', () => { layout(); setPath(); });
  const place = ([x, y, s]) => `translate(${x.toFixed(2)}px, ${y.toFixed(2)}px) scale(${s.toFixed(5)})`;
  const between = (A, B, g) => [lerp(A[0], B[0], g), lerp(A[1], B[1], g), Math.exp(lerp(Math.log(A[2]), Math.log(B[2]), g))];

  function render(t) {
    // the rush out: from far away to nearly filling the screen, accelerating; then it eases back as it opens
    // in: decelerating to the closest point; out: the pull-back and the pan share one easing, and the pan sets off
    // a little before the closest point, so the move turns round without stopping
    const u = k(t, T.move), sm = x => x * x * x * (x * (6 * x - 15) + 10);
    const op = ease(clamp((u - .2) / .42, 0, 1)), rc = sm(clamp((u - .45) / 0.55, 0, 1));
    const D = Math.exp(u < .34 ? lerp(L9, Lc, 1 - Math.pow(1 - u / .34, 2.2)) : lerp(Lc, Ll, sm((u - .34) / .66)));
    hinge.rotation.x = -lerp(lerp(CLOSED, OPEN, op), 24 * Math.PI / 180, rc);   // settles to the logo's 24 degrees
    // straight ahead: it comes at the viewer front-on and its lid lifts towards them to show the pearl
    // as it pulls back it turns a quarter round to side profile and levels off, landing as the logo's mark
    const rot = rc, az = lerp(0, -Math.PI / 2, rot), el = lerp(lerp(EL0, EL1, op), 0, rot);
    const tgt = CENTRE.clone().lerp(TL, rc);
    cam.position.set(tgt.x + D * Math.sin(az) * Math.cos(el), tgt.y + D * Math.sin(el), tgt.z + D * Math.cos(az) * Math.cos(el)); cam.lookAt(tgt);
    pearlMat.uniforms.glint.value = 1.3 * bump(u, .45, .9);
    sc.updateMatrixWorld(); r3.render(sc, cam);
    // merge: the ink disc fades in round the oyster (its cut-outs line up with the shells and the pearl), then the 3D goes
    const m = ease(k(t, T.merge));
    mark.style.opacity = m.toFixed(3);
    r3.domElement.style.opacity = (k(t, T.fade) * (1 - k(t, [T.merge[0] + 100, T.merge[1]]))).toFixed(3);
    // the rest of the word writes in from the left, 'therapeutics' rises in under it
    clipR.setAttribute('width', (2100 * ease(k(t, T.letters))).toFixed(1));
    letters.style.opacity = ease(k(t, [T.letters[0], T.letters[0] + 600])).toFixed(3);   // a soft fade as the letters sweep in
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
