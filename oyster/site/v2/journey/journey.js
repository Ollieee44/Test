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
const m2 = makeMolecule(THREE, DATA, Q, geom, V3(0, -1, .25)), g2 = new THREE.Group();
g2.add(m2.group); m2.group.position.copy(degC).negate(); g2.scale.setScalar(SC); scene.add(g2);
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
  applyBase(); const c = PAL[pal]; m2.setColors(c);
  root.style.setProperty('--mol-a', c.warhead); root.style.setProperty('--mol-b', c.e3lig); root.style.setProperty('--mol-c', c.clasp);
};

// ---------- the timeline ----------
const BEATS = [[0, .17], [.17, .42], [.42, .6], [.6, .8], [.8, 1]];
const CAMX = curve([[0, 14], [.12, 14], [.22, X.dimer + 44], [.38, X.dimer + 46], [.5, X.mem + 6], [.62, X.complex - 6], [.79, X.complex], [.88, (X.complex + X.prot) / 2 + 12], [.95, X.prot - 18], [1, 320]]);
const CAMY = curve([[0, 4], [.12, 4], [.22, 0], [.58, 0], [.66, -4], [.86, -4], [.95, -6], [1, 0]]);
const DIST = curve([[0, 440], [.12, 440], [.22, 370], [.38, 370], [.5, 440], [.62, 560], [.79, 560], [.9, 560], [.95, 600], [1, 1500]]);
const HX = curve([[.2, 12], [.44, 12], [.56, 30], [.6, 30], [.67, GAPJ]]);   // half-separation of the hero
const HERO_X = curve([[0, X.mono], [.42, X.mono], [.6, X.inside], [.68, X.complex], [1, X.complex]]);

// ---------- the flat layer (SVG, world units in the z = 0 plane) and the labels ----------
const svgNS = 'http://www.w3.org/2000/svg', world = document.getElementById('jworld');
const pill = document.getElementById('jpill'), beam = document.getElementById('jbeam'), membrane = document.getElementById('jmem'), person = document.getElementById('jperson');
const plus = document.getElementById('jplus');
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

  // ---- 01 oral dosing: the capsule goes in by mouth
  const pp = ease(clamp((p - .025) / .1, 0, 1));
  const px = 74 + (19 - 74) * pp, py = 64 + (43 - 64) * pp - 10 * Math.sin(Math.PI * pp);
  pill.setAttribute('transform', `translate(${px.toFixed(2)} ${py.toFixed(2)}) rotate(${(-18 + 18 * pp).toFixed(1)}) scale(${(1 - .7 * pp).toFixed(3)})`);
  pill.style.opacity = (1 - clamp((pp - .86) / .14, 0, 1)).toFixed(3);
  person.style.opacity = kf(p, [[.13, 1], [.19, 0]]).toFixed(3);   // gone before the copy changes over
  // the gut's absorption, a warm beam carrying the molecules to the membrane
  beam.style.opacity = (kf(p, [[.08, 0], [.17, 1], [.56, 1], [.64, 0]])).toFixed(3);
  membrane.style.opacity = (kf(p, [[.3, 0], [.42, 1], [.56, 1], [.64, .28], [.95, .28], [1, .55]])).toFixed(3);   // back once the halves are through, clear of the copy

  // ---- 02 the equilibrium: the dimer splits and rejoins while the pair of monomers joins and splits again
  const s2 = kf(p, [[.12, .001], [.18, 1], [.5, 1], [.56, .001]]);
  g2.visible = s2 > .01; g2.scale.setScalar(SC * s2); g2.position.set(X.dimer, 0, 0); g2.rotation.z = .1 * Math.sin(p * 14);
  const j2 = 1, f2 = 0, hx2 = 7;   // the dimer stays whole; the equilibrium is the arrows between it and the monomers
  m2.update(V3(-hx2, 0, 0), V3(hx2, 0, 0), new THREE.Quaternion().setFromEuler(new THREE.Euler(f2 * .3 * Math.sin(p * 41), f2 * .4 * Math.sin(p * 29), 0)),
    new THREE.Quaternion().setFromEuler(new THREE.Euler(f2 * -.3 * Math.sin(p * 37), f2 * .35 * Math.cos(p * 33), 0)), j2);

  // ---- the hero SELFTAC: monomers in the equilibrium, across the membrane, upright and rejoined in the cell
  const sh = kf(p, [[.12, .001], [.18, 1]]);
  cg.position.set(HERO_X(p), 0, 0); cg.scale.setScalar(SC * sh); cg.visible = sh > .01;
  cg.rotation.z = kf(p, [[.44, 0], [.58, -Math.PI / 2]]);
  const j = kf(p, [[.64, 0], [.68, 1]]);
  const free = (1 - j) * clamp((.66 - p) / .05, 0, 1), hx = p < .2 ? 12 : HX(p);
  const rW = new THREE.Quaternion().setFromEuler(new THREE.Euler(free * .32 * Math.sin(p * 47), free * .42 * Math.sin(p * 31), 0));
  const rE = new THREE.Quaternion().setFromEuler(new THREE.Euler(free * -.3 * Math.sin(p * 43), free * .4 * Math.cos(p * 35), 0));
  const brk = mol.update(V3(-hx, 0, 0), V3(hx, 0, 0), rW, rE, j);
  // the proteins come in: the target from above, the ligase from below
  const tIn = kf(p, [[.58, 1], [.66, 0]]);
  P.brd4.position.set(-GAPJ - 110 * tIn, 0, 0); P.brd4.scale.setScalar(1);
  ['vhl', 'elob', 'eloc'].forEach(key => { P[key].position.set(GAPJ + 130 * tIn, 0, 0); P[key].visible = p > .57; });
  P.brd4.visible = p > .57;
  cg.updateMatrixWorld(true);
  // the bond clicking shut in the complex
  const fx = bump(p, .655, .7); flash.position.copy(mol.group.localToWorld(brk.clone())); flash.scale.setScalar(SC * (1 + 3 * clamp((p - .655) / .045, 0, 1)));
  flash.material.opacity = fx * .9; flash.visible = fx > .01; flash.lookAt(camera.position);

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
