// ---------- the journey: the SELFTAC story told left to right as the page scrolls ----------
// Oral dosing, the dimer and its monomers in equilibrium, across the membrane, the ternary complex, degradation.
// World units are the scene's (angstroms). x runs left to right along the journey and y is up. The camera only
// pans and zooms, looking straight down -z, so the z = 0 plane maps to the screen by a translation and a scale:
// the flat illustration (the person, the absorption beam, the membrane) is drawn in that plane in an SVG layer
// under the canvas, and the labels are placed in it too, so all of it stays locked to the 3D as the camera moves.
wall.visible = false; cell.visible = false; P.brd4b.visible = false; e2.visible = false;
const X = { person: 0, dimer: 150, mono: 238, mem: 345, inside: 420, complex: 470, prot: 640 };
const SC = 1.25;                       // the molecules' and the complex's scale
const GAPJ = 12;                       // the proteins sit this far out from the degrader in the complex
const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const degC = S('warhead').add(S('e3lig')).multiplyScalar(.5);

// the complex: the degrader and its two proteins in one group, centred on the degrader; turned upright inside
// the cell so the target protein is above and the ligase below, as on the slide
const cg = new THREE.Group(), inner = new THREE.Group(); cg.add(inner); scene.add(cg);
inner.position.copy(degC).negate(); cg.scale.setScalar(SC);
inner.add(mol.group); ['brd4', 'vhl', 'elob', 'eloc'].forEach(k => inner.add(P[k]));
// a second SELFTAC, the dimer of the equilibrium
// the proteasome stands upright, as on the slide
const qProt = new THREE.Quaternion(), eProt = new THREE.Euler(0, 0, Math.PI / 2, 'ZYX');
// fragments of the target, falling out of the proteasome
const frags = [];
for (let i = 0; i < 18; i++) {
  const mat = cmat('brd4', 1.1); mats.push(mat);
  const m = new THREE.Mesh(new THREE.IcosahedronGeometry(1.5 + (i % 3) * .55, 2), mat); addOutline(m, .28); scene.add(m);
  frags.push({ m, dx: (((i * 37) % 19) / 19 - .5) * 90, dy: 30 + ((i * 53) % 23) * 2.6, d: (i % 6) * .012, r: i * 1.7 });
}
// where the ubiquitin tags sit on the target: the far side of BRD4 from the degrader (the top, once upright)
const ubLocal = (() => { const g = P.brd4.children[0].geometry, pos = g.attributes.position, v = V3(); let best = null, bs = -1e9;
  for (let i = 0; i < pos.count; i++) { v.fromBufferAttribute(pos, i).applyQuaternion(Q); const s = -v.x + .35 * v.z + .2 * v.y; if (s > bs) { bs = s; best = v.clone(); } } return best; })();

// ---------- palette: the capsule takes the two halves' colours ----------
const applyBase = applyPalette;
applyPalette = function () {
  applyBase(); const c = PAL[pal];
  root.style.setProperty('--mol-a', c.warhead); root.style.setProperty('--mol-b', c.e3lig); root.style.setProperty('--mol-c', c.clasp);
};

// ---------- the timeline ----------
const BEATS = [[0, .17], [.17, .42], [.42, .6], [.6, .8], [.8, 1]];
const CAMX = curve([[0, 14], [.12, 14], [.16, 8], [.22, 0], [.31, 0], [.42, X.mono - 30], [.5, X.mem + 6], [.62, X.complex - 6], [.79, X.complex], [.88, (X.complex + X.prot) / 2 + 12], [.95, X.prot - 18], [1, 320]]);
const CAMY = curve([[0, 4], [.12, 4], [.22, -25], [.31, -25], [.42, 0], [.58, 0], [.66, -4], [.86, -4], [.95, -6], [1, 0]]);
const DIST = curve([[0, 440], [.12, 440], [.16, 400], [.22, 130], [.31, 130], [.42, 370], [.5, 440], [.62, 560], [.79, 560], [.9, 560], [.95, 600], [1, 1500]]);
// the hero: a dimer released in the gut (at y -25), which dissociates there into its two monomers, then leaves
const HX = curve([[.27, 7], [.31, 13], [.44, 13], [.56, 30], [.6, 30], [.67, GAPJ]]);   // half-separation
const HERO_X = curve([[0, 0], [.31, 0], [.42, X.mono], [.6, X.inside], [.68, X.complex], [1, X.complex]]);
const HERO_Y = curve([[0, -25], [.31, -25], [.42, 0], [1, 0]]);

// ---------- the flat layer (SVG, world units in the z = 0 plane) and the labels ----------
const svgNS = 'http://www.w3.org/2000/svg', world = document.getElementById('jworld');
const route = document.getElementById('jroute'), routeLen = route.getTotalLength(), gutRing = document.getElementById('jgutring');
const pill = document.getElementById('jpill'), beam = document.getElementById('jbeam'), membrane = document.getElementById('jmem'), person = document.getElementById('jperson');
const plus = document.getElementById('jplus'), gut = document.getElementById('jgut'), tract = document.getElementById('jtract');
const dynL = ['jdimer', 'jmono', 'jeq'].map(id => document.getElementById(id));
const LABELS = [...document.querySelectorAll('.jl[data-x]')].map(el => ({ el, x: +el.dataset.x, y: +el.dataset.y, a: +el.dataset.a, b: +el.dataset.b }));
const vtmp = V3();
function toScreen(x, y) { vtmp.set(x, y, 0).project(camera); return [(vtmp.x + 1) / 2 * stage.clientWidth, (1 - vtmp.y) / 2 * stage.clientHeight]; }
const winO = (p, a, b, f = .02) => clamp(Math.min((p - a) / f, (b - p) / f), 0, 1);

function frame(p0) {
  const p = clamp(p0, 0, 1);
  // ---- camera: copy on the left on wide screens (the subject sits right of centre); on a card below on phones
  const narrow = camera.aspect < .9, fov = THREE.MathUtils.degToRad(camera.fov);
  const dist = DIST(p) * (narrow ? Math.max(1, 1.05 / camera.aspect) * .8 : 1);
  const vh = 2 * dist * Math.tan(fov / 2), vw = vh * camera.aspect, settle = 1 - clamp((p - .955) / .04, 0, 1);
  let ax = CAMX(p), ay = CAMY(p);
  if (narrow) ay -= .17 * vh * settle; else ax -= .17 * vw * settle;
  camera.position.set(ax, ay, dist); camera.lookAt(ax, ay, 0); camera.updateMatrixWorld();
  const k = stage.clientHeight / vh, tx = stage.clientWidth / 2 - ax * k, ty = stage.clientHeight / 2 + ay * k;
  world.setAttribute('transform', `matrix(${k.toFixed(5)} 0 0 ${(-k).toFixed(5)} ${tx.toFixed(2)} ${ty.toFixed(2)})`);

  // ---- 01 oral dosing: the capsule goes in by mouth, then down the throat along the dotted route into the gut
  const pp = ease(clamp((p - .02) / .08, 0, 1)), pr = ease(clamp((p - .1) / .055, 0, 1));
  let px, py, rot, pls;
  if (pr <= 0) { px = 74 + (18 - 74) * pp; py = 64 + (42 - 64) * pp - 10 * Math.sin(Math.PI * pp); rot = -18 + 18 * pp; pls = 1 - .45 * pp; }
  else {   // the route is drawn y-down inside the person, so its points flip into the world
    const L = routeLen * pr, a = route.getPointAtLength(L), b = route.getPointAtLength(Math.min(routeLen, L + .5));
    px = a.x; py = -a.y; rot = Math.atan2(-(b.y - a.y), b.x - a.x) * 180 / Math.PI; pls = .55 - .15 * pr;
  }
  pill.setAttribute('transform', `translate(${px.toFixed(2)} ${py.toFixed(2)}) rotate(${rot.toFixed(1)}) scale(${pls.toFixed(3)})`);
  pill.style.opacity = (1 - clamp((p - .152) / .012, 0, 1)).toFixed(3);
  route.style.opacity = kf(p, [[.085, 0], [.105, 1]]).toFixed(3);
  gutRing.style.opacity = bump(p, .148, .175).toFixed(3);   // the gut answers as the capsule arrives
  person.style.opacity = kf(p, [[.15, 1], [.21, 0]]).toFixed(3);   // the body goes as the camera zooms into the gut
  gut.style.opacity = kf(p, [[.33, 1], [.37, 0]]).toFixed(3);   // gone before it would sit behind the copy
  tract.style.opacity = kf(p, [[.19, 1], [.22, .3], [.34, .3], [.38, 1]]).toFixed(3);   // quieter while the molecule is in front of it
  // the gut's absorption, a warm beam carrying the molecules to the membrane
  beam.style.opacity = (kf(p, [[.3, 0], [.38, 1], [.56, 1], [.64, 0]])).toFixed(3);   // absorption, once there are monomers
  membrane.style.opacity = (kf(p, [[.3, 0], [.42, 1], [.56, 1], [.64, .28], [.95, .28], [1, .55]])).toFixed(3);   // back once the halves are through, clear of the copy

  // ---- 02 in the gut: the capsule releases a dimer, which dissociates at its reversible linker into two monomers;
  // then the hero monomers leave the gut, are absorbed, cross the membrane, and rejoin upright in the cell
  const sh = kf(p, [[.18, .001], [.21, .45], [.31, .45], [.42, 1]]);
  cg.position.set(HERO_X(p), HERO_Y(p), 0); cg.scale.setScalar(SC * sh); cg.visible = sh > .01;
  cg.rotation.z = kf(p, [[.44, 0], [.58, -Math.PI / 2]]) + (p < .31 ? .12 * Math.sin(p * 30) : 0);
  const j = kf(p, [[.27, 1], [.31, 0], [.64, 0], [.68, 1]]);
  const free = (1 - j) * clamp((.66 - p) / .05, 0, 1), hx = p < .27 ? 7 : HX(p);
  const rW = new THREE.Quaternion().setFromEuler(new THREE.Euler(free * .32 * Math.sin(p * 47), free * .42 * Math.sin(p * 31), 0));
  const rE = new THREE.Quaternion().setFromEuler(new THREE.Euler(free * -.3 * Math.sin(p * 43), free * .4 * Math.cos(p * 35), 0));
  const brk = mol.update(V3(-hx, 0, 0), V3(hx, 0, 0), rW, rE, j);
  // the proteins come in: the target from above, the ligase from below
  const tIn = kf(p, [[.58, 1], [.66, 0]]);
  P.brd4.position.set(-GAPJ - 110 * tIn, 0, 0); P.brd4.scale.setScalar(1);
  ['vhl', 'elob', 'eloc'].forEach(key => { P[key].position.set(GAPJ + 130 * tIn, 0, 0); P[key].visible = p > .57; });
  P.brd4.visible = p > .57;
  cg.updateMatrixWorld(true);
  // the bond: a flash as it breaks in the gut, and again as it clicks shut in the complex
  const fb = bump(p, .27, .31), fj = bump(p, .655, .7), fx = Math.max(fb, fj);
  flash.position.copy(mol.group.localToWorld(brk.clone()));
  flash.scale.setScalar(SC * sh * (fb > fj ? .7 + 1.4 * clamp((p - .27) / .04, 0, 1) : 1 + 3 * clamp((p - .655) / .045, 0, 1)));   // a finer flash for the break
  flash.material.opacity = (fb > fj ? .6 : .9) * fx; flash.visible = fx > .01; flash.lookAt(camera.position);

  // ---- 05 degradation: ubiquitin tags the target, it goes into the proteasome, and comes out in pieces
  const PROT = V3(X.prot, 6, 0), ps = kf(p, [[.8, .001], [.85, 1.15], [.97, 1.15], [1, 1]]);
  prot.visible = ps > .01; prot.position.copy(PROT); prot.scale.setScalar(ps);
  eProt.set(p * 3, 0, Math.PI / 2, 'ZYX'); prot.quaternion.setFromEuler(eProt);
  const go = kf(p, [[.86, 0], [.92, 1]]);
  if (go > 0) {
    // the holder scales about its origin, so the protein's centre is kept on the proteasome as it shrinks
    const sc = 1 - .82 * clamp((go - .55) / .45, 0, 1), home = V3(-GAPJ, 0, 0), into = inner.worldToLocal(PROT.clone()).sub(S('brd4').multiplyScalar(sc));
    P.brd4.position.lerpVectors(home, into, go); P.brd4.scale.setScalar(sc);
    P.brd4.visible = p < .935;
  }
  P.brd4.updateMatrixWorld(true);
  ubs.forEach((u, i) => {
    const t0 = .8 + i * .012, on = clamp((p - t0) / .012, 0, 1);
    const spot = P.brd4.localToWorld(ubLocal.clone().add(V3(-2 - 3 * i, (i % 2 ? 3 : -3), 4)));
    u.position.copy(spot).add(V3(0, 26 * (1 - ease(on)), 0)); u.scale.setScalar(.42 * SC * P.brd4.scale.x);
    u.visible = on > .01 && P.brd4.visible;
  });
  const fo = clamp((p - .915) / .06, 0, 1);
  frags.forEach(f => { const t = clamp((fo - f.d) / (1 - f.d), 0, 1);
    f.m.visible = t > 0 && p < 1.01; f.m.position.set(PROT.x + f.dx * ease(t), PROT.y - 30 - f.dy * ease(t), 0); f.m.rotation.set(f.r + t * 3, t * 2, 0); f.m.scale.setScalar(SC * .8 * Math.min(1, t * 4)); });

  // ---- ground: the blood's colours outside the membrane, the cell's inside it
  const sky = PAL[pal].sky, ks = ease(clamp((p - .47) / .1, 0, 1));
  const mix = (a, b, t) => '#' + new THREE.Color(a).lerp(new THREE.Color(b), t).getHexString();
  stage.style.setProperty('--sky-a', mix(sky[0][0], sky[2][0], ks)); stage.style.setProperty('--sky-b', mix(sky[0][1], sky[2][1], ks));

  // ---- copy, rail, labels, end card
  const endO = clamp((p - .965) / .03, 0, 1);
  document.querySelectorAll('.beat').forEach((b, i) => { const [a, z] = BEATS[i];
    const o = i === BEATS.length - 1 ? clamp((p - a) / .03, 0, 1) * (1 - endO) : i === 0 ? clamp((z - p) / .03, 0, 1) : clamp(Math.min((p - a) / .03, (z - p) / .03), 0, 1);
    b.style.opacity = o.toFixed(3); b.style.transform = 'translateY(calc(-50% + ' + ((1 - o) * 16).toFixed(1) + 'px))'; });
  document.querySelectorAll('.rail b').forEach((b, i) => { b.style.setProperty('--f', clamp((p - BEATS[i][0]) / (BEATS[i][1] - BEATS[i][0]), 0, 1).toFixed(3)); b.closest('.rail > div').classList.toggle('on', p >= BEATS[i][0]); });
  plus.style.opacity = (winO(p, .19, .64) * (1 - j)).toFixed(3);   // '+' between the two monomers, riding with them
  // the dimer, then the monomers, named under the molecule in the gut, with the reversible arrows above it
  const hc = cg.localToWorld(V3(0, 0, 0)), dyn = [[winO(p, .215, .29), -15], [winO(p, .3, .44), -17], [winO(p, .255, .34), 15]];
  dynL.forEach((el, i) => { const [o, dy] = dyn[i]; el.style.opacity = (o * (1 - endO)).toFixed(3);
    if (o > 0) { const [x, y] = toScreen(hc.x, hc.y + dy * sh * SC); el.style.transform = `translate(${x.toFixed(1)}px, ${y.toFixed(1)}px) translate(-50%, -50%)`; } });
  if (+plus.style.opacity > 0) { const c = cg.localToWorld(V3(0, 0, 0)); const [x, y] = toScreen(c.x, c.y); plus.style.transform = `translate(${x.toFixed(1)}px, ${y.toFixed(1)}px) translate(-50%, -50%)`; }
  LABELS.forEach(l => { const o = winO(p, l.a, l.b) * (1 - endO); l.el.style.opacity = o.toFixed(3);
    if (o > 0) { let [x, y] = toScreen(l.x, l.y); const hw = (l.w = l.w || l.el.offsetWidth) / 2 + 10;   // kept on screen, with a margin
      x = clamp(x, hw, stage.clientWidth - hw); l.el.style.transform = `translate(${x.toFixed(1)}px, ${y.toFixed(1)}px) translate(-50%, -50%)`; } });
  const end = document.getElementById('end'); end.style.opacity = endO; end.style.pointerEvents = endO > .9 ? 'auto' : 'none';
  document.getElementById('copy').style.opacity = 1 - endO;
  canvas.style.opacity = (1 - .85 * endO).toFixed(3); document.getElementById('jsvg').style.opacity = (1 - .85 * endO).toFixed(3);
  document.getElementById('hint').style.opacity = 1 - clamp(p / .02, 0, 1);
}

// ---------- scroll: a smoothed progress through the pinned journey ----------
const story = document.getElementById('story');
function target() { const r = story.getBoundingClientRect(); return clamp(-r.top / (r.height - innerHeight), 0, 1); }
let goalNow = target(), storyOn = true;
function measure() { goalNow = target(); storyOn = story.getBoundingClientRect().bottom > 0; }
addEventListener('scroll', measure, { passive: true }); addEventListener('resize', measure);
let prog = goalNow, last = performance.now(), hold = false, drawnSig = '';
function resize() { const w = stage.clientWidth, h = stage.clientHeight; if (renderer) { renderer.setPixelRatio(Math.min(devicePixelRatio, 2)); renderer.setSize(w, h, false); } camera.aspect = w / h; camera.updateProjectionMatrix(); drawnSig = ''; }
addEventListener('resize', resize); resize(); applyPalette();
document.querySelectorAll('.pal button').forEach(b => b.addEventListener('click', () => { drawnSig = ''; }));
function loop(t) {
  const dt = Math.min(.1, (t - last) / 1000); last = t;
  const goal = hold ? prog : goalNow; prog += (goal - prog) * (reduce ? 1 : 1 - Math.exp(-dt / .3)); if (Math.abs(goal - prog) < 1e-5) prog = goal;
  const sig = prog.toFixed(5) + '|' + pal + '|' + stage.clientWidth + 'x' + stage.clientHeight;
  if (storyOn && sig !== drawnSig) { frame(prog); if (renderer) renderer.render(scene, camera); drawnSig = sig; }
  requestAnimationFrame(loop);
}
if (renderer) { try { renderer.compile(scene, camera); } catch (e) {} }
requestAnimationFrame(loop);
// test hook: hold the journey at progress p (0-1)
window.__journey = window.__story = { frame: p => { hold = true; prog = p; frame(p); if (renderer) renderer.render(scene, camera); drawnSig = ''; }, setPal: v => { pal = v; applyPalette(); } };
