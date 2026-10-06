// ---------- intro (fan mark): the clam opens face-on, its lid stands up as the fan, and it lands in the logotype's 'o' ----------
// Plays once on load (about 3.5 s) and hands over to the scroll story. Skip, or any attempt to scroll, jumps to the
// final glide. Reduced motion, no WebGL, or a page that loads already scrolled: straight to the landing page.
// The oyster is built from the mark itself (GEO, written by build_fan.py): both valves have the fan's outline, hinged
// at the back; at the end the lid stands upright facing the camera, which looks down at the mark's low angle, so the
// 3D lies on the line-cut disc's drawing as the disc fades in round it.
(() => {
  const GEO = /*GEO*/null;
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
  if (window.__startPal && window.__startPal !== pal) { const b = document.querySelector('.pal button[data-pal="' + window.__startPal + '"]'); if (b) b.click(); }
  if (reduce || !renderer || scrollY > 10) { finish(); return; }
  try { r3 = new THREE.WebGLRenderer({ canvas: document.getElementById('introGl'), antialias: true, alpha: true }); } catch (e) { finish(); return; }

  // timeline (ms): the closed clam rushes in from the left and above, opens as it comes closest, its lid rising to
  // stand upright; the pearl forms in the cup; as it pulls back it swings round to face us and drops to the mark's
  // low angle, landing in the 'o'; the line-cut disc closes round it, the word writes in, the logotype settles
  const T = { fade: [0, 180], move: [0, 2100], merge: [1850, 2150],
    letters: [2000, 2850], ther: [2450, 2850], glide: [3050, 3610], bg: [3050, 3610], site: 3560, end: 3650 };
  const k = (t, [a, b]) => clamp((t - a) / (b - a), 0, 1);
  const lerp = (a, b, x) => a + (b - a) * x;
  const COL = ({ nacre: { out: '#CDB8C6', inn: '#EBD9E2', ring: '#8C5572' }, tidepool: { out: '#7DB8AC', inn: '#DCEFE8', ring: '#2F6F69' } })[pal] || { out: '#CDB8C6', inn: '#EBD9E2', ring: '#8C5572' };
  const css = n => getComputedStyle(html).getPropertyValue(n).trim();
  const INK = css('--ink'), PEARL = css('--pearl');
  const paperC = new THREE.Color(css('--paper') || '#EFE6E1'), LIGHTSITE = (paperC.r + paperC.g + paperC.b) / 3 > .45;
  const STAGE = LIGHTSITE ? ['#3B2F42', '#241C29'] : ['#0B3A38', '#04201F'], LOGO0 = LIGHTSITE ? css('--paper') : INK, LINE = LIGHTSITE ? '#806A86' : '#4E9A91';
  const RIBC = LIGHTSITE ? '#8C5572' : '#0F4C4A';   // the lid's rib lines: the colour the logo's cut lines show through
  ov.style.setProperty('--intro-a', STAGE[0]); ov.style.setProperty('--intro-b', STAGE[1]);
  const mixHex = (a, b, x) => '#' + new THREE.Color(a).lerp(new THREE.Color(b), x).getHexString();

  // ---------- the clam: two fan-shaped valves hinged at the back ----------
  // One 3D unit is five reference units (the mark's drawing units). A valve lies along +z from the hinge at the
  // origin; phi is the angle from the valve's centre line, 0 straight out, +90 along the hinge to the right.
  const U = 1 / 5, D2R = Math.PI / 180;
  const edgeAt = phi => { const i = clamp((phi / D2R + 90) / 3, 0, 60), a = Math.floor(i), b = Math.min(60, a + 1); return lerp(GEO.edge[a], GEO.edge[b], i - a) * U; };
  const LEN = edgeAt(0);                       // hinge to lip
  const bulge = s => Math.pow(Math.max(0, 4 * s * (1 - s)), .75);   // 0 at the hinge and at the lip
  function valve(dOut, dIn, sx) {   // dOut, dIn: how far the outer and inner surfaces bow out (negative: downwards)
    const NR = 44, NT = 96, pos = [], outer = [], inner = [];
    for (const [d, list, up] of [[dOut, outer, dOut > 0], [dIn, inner, dIn < 0]]) {   // faces wound to point out of the shell
      const base = pos.length / 3;
      for (let i = 0; i <= NR; i++) { const s = i / NR;
        for (let j = 0; j <= NT; j++) { const phi = (-90 + 180 * j / NT) * D2R, r = s * edgeAt(phi);
          pos.push(r * Math.sin(phi) * sx, d * bulge(s), r * Math.cos(phi)); } }
      for (let i = 0; i < NR; i++) for (let j = 0; j < NT; j++) {
        const a = base + i * (NT + 1) + j, b = a + 1, c = a + NT + 1, e = c + 1;
        if (up) list.push(a, c, b, b, c, e); else list.push(a, b, c, b, e, c); }
    }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    g.setIndex(outer.concat(inner)); g.addGroup(0, outer.length, 0); g.addGroup(outer.length, inner.length, 1);
    g.computeVertexNormals(); return g;
  }
  // flat-shaded nacre with lines in the valve's own frame: growth rings round the hinge (outside), or the fan's
  // ribs (inside the lid, where the logo draws them), with a soft rim like the story's contour material
  const fanVS = `varying vec3 vN; varying vec3 vL; varying vec3 vV;
    void main() { vec4 w = modelMatrix * vec4(position, 1.0); vL = position; vN = normalize(mat3(modelMatrix) * normal); vV = normalize(cameraPosition - w.xyz); gl_Position = projectionMatrix * viewMatrix * w; }`;
  const fanFS = `uniform vec3 col; uniform vec3 ring; uniform float mode; uniform float sx; uniform float len; uniform float ribs[7];
    varying vec3 vN; varying vec3 vL; varying vec3 vV;
    void main() {
      vec3 n = normalize(vN); float line = 0.0; float r = length(vec2(vL.x / sx, vL.z));
      if (mode > 1.5) {   // ribs: lines at the logo's rib angles, starting a third of the way out
        float phi = degrees(atan(vL.x / sx, vL.z));
        for (int i = 0; i < 7; i++) { float d = abs(phi - ribs[i]) * r * .0174533; float w = fwidth(d); line = max(line, 1.0 - smoothstep(.35, .35 + 1.6 * w, d)); }
        line *= smoothstep(len * .3, len * .36, r);
      } else if (mode > .5) {   // growth rings round the hinge
        float d = r / 4.5; float f = abs(fract(d) - .5); float w = fwidth(d); line = smoothstep(.5 - 1.6 * w, .5 - .4 * w, f) * .55;
      }
      float lit = .82 + .18 * max(dot(n, normalize(vec3(.4, .7, .6))), 0.0);
      float rim = pow(1.0 - max(dot(n, normalize(vV)), 0.0), 2.2);
      vec3 c = col * lit; c = mix(c, ring, line); c = mix(c, ring, rim * .3);
      gl_FragColor = vec4(c, 1.0);
      #include <colorspace_fragment>
    }`;
  const fanMat = (col, ring, mode, sx) => new THREE.ShaderMaterial({ vertexShader: fanVS, fragmentShader: fanFS,
    uniforms: { col: { value: new THREE.Color(col) }, ring: { value: new THREE.Color(ring) }, mode: { value: mode }, sx: { value: sx }, len: { value: LEN },
      ribs: { value: GEO.ribs } }, side: THREE.FrontSide });
  function shellMesh(geo, innerMode, sx) {
    const m = new THREE.Mesh(geo, [fanMat(COL.out, COL.ring, 1, sx), fanMat(COL.inn, innerMode === 2 ? RIBC : COL.inn, innerMode, sx)]);
    const og = new THREE.BufferGeometry(); og.setAttribute('position', geo.attributes.position); og.setAttribute('normal', geo.attributes.normal);
    og.setIndex(Array.from(geo.index.array.slice(0, geo.groups[0].count)));
    const shellOnly = new THREE.Mesh(og); const o = addOutline(shellOnly, .9); shellOnly.remove(o); m.add(o);
    o.material.uniforms.color.value.set(LINE); return m;
  }
  const sc = new THREE.Scene(), cam = new THREE.PerspectiveCamera(22, 1, 1, 6000);
  const oyster = new THREE.Group(); sc.add(oyster);
  const SXL = 1.09;                                         // the lower valve is a little wider, as the logo's dish is
  const lower = shellMesh(valve(-12, -8, SXL), 0, SXL); oyster.add(lower);
  const lid = new THREE.Group(); oyster.add(lid);           // the hinge is the origin
  const upper = shellMesh(valve(7, 4.6, 1), 2, 1); lid.add(upper);
  const pearlMat = new THREE.ShaderMaterial({ uniforms: { col: { value: new THREE.Color(PEARL) }, glint: { value: 0 } },
    vertexShader: `varying vec3 vN; varying vec3 vV; void main() { vec4 w = modelMatrix * vec4(position, 1.0); vN = normalize(mat3(modelMatrix) * normal); vV = normalize(cameraPosition - w.xyz); gl_Position = projectionMatrix * viewMatrix * w; }`,
    fragmentShader: `uniform vec3 col; uniform float glint; varying vec3 vN; varying vec3 vV;
      void main() { vec3 n = normalize(vN), v = normalize(vV), l = normalize(vec3(-.4, .7, .6));
        float dif = .8 + .2 * max(dot(n, l), 0.0), sp = pow(max(dot(n, normalize(l + v)), 0.0), 70.0) * (.5 + glint), rim = pow(1.0 - max(dot(n, v), 0.0), 2.5);
        gl_FragColor = vec4(col * dif + vec3(sp) + mix(col, vec3(1.0), .5) * rim * .22, 1.0);
        #include <colorspace_fragment>
      }` });
  const PEARL_R = GEO.pearlRef * U;
  const pearl = new THREE.Mesh(new THREE.SphereGeometry(PEARL_R, 48, 32), pearlMat); oyster.add(pearl);
  addOutline(pearl, .8).material.uniforms.color.value.set(LINE);
  // the pearl rests in the cup near the hinge, as the logo has it, just in front of the standing lid
  const PZ = 10.5, PEARL_AT = new THREE.Vector3(0, -8 * bulge(PZ / LEN) + PEARL_R - .4, PZ);
  pearl.position.copy(PEARL_AT);
  const EL = 10 * D2R;                                      // the mark's view: a little above, looking down 10 degrees (the dish's ellipse)
  const OPEN = 90 * D2R + EL;                               // the lid stands upright, tipped back to face the camera

  // ---------- the logotype: its 'o' is the same clam, cut out of a disc as lines ----------
  const logo = document.getElementById('ilogo'), mark = document.getElementById('ioMark');
  const clipR = document.getElementById('ioClipR'), letters = document.getElementById('ioLetters'), ther = document.getElementById('ioTher');
  const head = document.querySelector('.head .wm');
  logo.style.color = LOGO0;
  const VB = logo.getAttribute('viewBox').split(' ').map(Number);
  // a point of the mark's drawing (its 0-100 box) in logotype units
  const toLT = ([x, y]) => [-17.1 + 6.3571 * (x - 1.5), -583.4 + 6.3571 * (y + 1.5)];
  let W = 0, H = 0, LW = 0, K = null, Dc = 0, Dl = 0, TL = null;
  const TAN = Math.tan(THREE.MathUtils.degToRad(11));
  function layout() {
    W = innerWidth; H = innerHeight; const narrow = W < 760;
    r3.setPixelRatio(Math.min(devicePixelRatio, 2)); r3.setSize(W, H, false); cam.aspect = W / H; cam.updateProjectionMatrix();
    LW = Math.min(W * (narrow ? .84 : .62), 900); logo.style.width = LW + 'px';
    const u = LW / VB[2], lh = LW * VB[3] / VB[2];
    K = { full: [(W - LW) / 2, H * .47 - lh / 2, 1] };
    // closest: the open clam (about 86 wide with the dish, about 108 tall as the lid swings up past the camera) fills most of the screen
    Dc = Math.max(86 / .78 / W, 108 / (.8 * H)) * H / (2 * TAN);
    // the end: one 3D unit is five reference units, k mark units each, 6.3571 logotype units each, u pixels each
    const s = 5 * GEO.k * 6.3571 * u; Dl = H / (2 * TAN * s);
    // aim so the hinge lands on the logo's hinge: the camera's right is +x, its up is (0, cos EL, -sin EL)
    const [hx, hy] = toLT(GEO.hinge), sx = K.full[0] + (hx - VB[0]) * u - W / 2, sy = K.full[1] + (hy - VB[1]) * u - H / 2;
    TL = new THREE.Vector3(-sx / s, 0, 0).add(new THREE.Vector3(0, Math.cos(EL), -Math.sin(EL)).multiplyScalar(sy / s));
  }
  let L9 = 0, Lc = 0, Ll = 0;
  const setPath = () => { L9 = Math.log(Dc * 9); Lc = Math.log(Dc); Ll = Math.log(Dl); };
  layout(); setPath(); addEventListener('resize', () => { layout(); setPath(); });
  const place = ([x, y, s]) => `translate(${x.toFixed(2)}px, ${y.toFixed(2)}px) scale(${s.toFixed(5)})`;
  const between = (A, B, g) => [lerp(A[0], B[0], g), lerp(A[1], B[1], g), Math.exp(lerp(Math.log(A[2]), Math.log(B[2]), g))];
  const CENTRE = new THREE.Vector3(0, 6, LEN * .42);       // the middle of the clam as it opens

  function render(t) {
    // one camera move: in from the distance to the closest point at about a third, then back into the 'o'; the lid
    // opens through the closest point, and the swing round to face it starts before the pull-back ends
    const u = k(t, T.move), sm = x => x * x * x * (x * (6 * x - 15) + 10);
    const op = ease(clamp((u - .16) / .44, 0, 1)), rc = sm(clamp((u - .4) / .6, 0, 1));
    const D = Math.exp(u < .34 ? lerp(L9, Lc, 1 - Math.pow(1 - u / .34, 2.2)) : lerp(Lc, Ll, sm((u - .34) / .66)));
    lid.rotation.x = -OPEN * op;
    // the pearl forms in the cup as the lid lifts: it would show through the closed shell, so it grows from nothing
    pearl.scale.setScalar(Math.max(.001, ease(clamp((op - .25) / .5, 0, 1))));
    // three-quarter from the left and well above at first, so the clam reads as a shell; face-on and low at the end
    const az = lerp(-34 * D2R, 0, rc), el = lerp(lerp(38 * D2R, 22 * D2R, op), EL, rc);
    const tgt = CENTRE.clone().lerp(TL, rc);
    cam.position.set(tgt.x + D * Math.sin(az) * Math.cos(el), tgt.y + D * Math.sin(el), tgt.z + D * Math.cos(az) * Math.cos(el)); cam.lookAt(tgt);
    pearlMat.uniforms.glint.value = 1.3 * bump(u, .45, .9);
    sc.updateMatrixWorld(); r3.render(sc, cam);
    // merge: the line-cut disc fades in round the clam (its lines lie on the lid's ribs and the dish), then the 3D goes
    const m = ease(k(t, T.merge));
    mark.style.opacity = m.toFixed(3);
    r3.domElement.style.opacity = (k(t, T.fade) * (1 - k(t, [T.merge[0] + 100, T.merge[1]]))).toFixed(3);
    clipR.setAttribute('width', (2100 * ease(k(t, T.letters))).toFixed(1));
    letters.style.opacity = ease(k(t, [T.letters[0], T.letters[0] + 600])).toFixed(3);
    const thIn = ease(k(t, T.ther)); ther.style.opacity = (thIn * (1 - k(t, [T.glide[0], T.glide[0] + 350]))).toFixed(3);
    ther.setAttribute('transform', `translate(0 ${(30 * (1 - thIn)).toFixed(1)})`);
    let pose = K.full;
    if (t >= T.glide[0]) {
      if (!K.head) { const hb = head.getBoundingClientRect(); K.head = [hb.left, hb.top, hb.width / LW]; }
      pose = between(K.full, K.head, ease(k(t, T.glide)));
    }
    logo.style.transform = place(pose);
    const lit = ease(k(t, T.bg)), lc = mixHex(LOGO0, INK, ease(clamp((lit - .3) / .4, 0, 1)));
    logo.style.color = lc;
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
