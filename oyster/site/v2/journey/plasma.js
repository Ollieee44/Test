// ---------- the plasma version: a bloodstream beat with dimers and monomers together, and a dimer that bounces off
// the membrane while the monomers pass through ----------
// The journey's own timeline runs on WARP(p): it is held back between the gut and the barrier, which makes room for a
// new beat in the bloodstream, and the copy and rail follow the six new beats (BEATS_N, in the page's own progress).
const WARP = curve([[0, 0], [.34, .34], [.38, .4], [.5, .415], [.54, .43], [.7, .6], [1, 1]]);   // nearly still through the bloodstream beat
const BEATS_N = [[0, .17], [.17, .36], [.36, .5], [.5, .7], [.7, .86], [.86, 1]];
function extra() {
  const m = makeMolecule(THREE, DATA, Q, geom, V3(0, -1, .25)), g = new THREE.Group();
  g.add(m.group); m.group.position.copy(degC).negate(); scene.add(g); m.setColors(PAL[pal]); g.visible = false; return { m, g };
}
// the bloodstream: intact dimers and loose monomers of both kinds, around where the hero's monomers arrive
// (u, v): where each sits in the part of the screen the subject has at the hold (0 left/bottom, 1 right/top)
const CROWD = [
  { kind: 'dimer', u: .1, v: .82, s: .8, r: .45, ph: 1 },
  { kind: 'split', u: .12, v: .14, s: .78, r: .25, hx: 26, ph: 2 },
  { kind: 'dimer', u: .9, v: .16, s: .76, r: -.5, ph: 3 },
  { kind: 'split', u: .86, v: .86, s: .8, r: -.35, hx: 24, ph: 4 },
].map(c => ({ ...c, ...extra() }));
// the part of the screen the subject has (clear of the copy) at the hold, in world units: the journey's camera at
// WARP(.45), worked out the same way as in its frame, so the crowd composes on any screen shape
function holdRegion() {
  const q = WARP(.45), fov = THREE.MathUtils.degToRad(camera.fov), a = camera.aspect, narrow = a < .9;
  const dist = DIST(q) * (narrow ? Math.max(1, 1.05 / a) * .8 : 1), vh = 2 * dist * Math.tan(fov / 2), vw = vh * a;
  let ax = CAMX(q), ay = CAMY(q); if (narrow) ay -= .17 * vh; else ax -= .17 * vw;
  const R = narrow ? { x0: ax - .42 * vw, x1: ax + .42 * vw, y0: ay - .02 * vh, y1: ay + .38 * vh }
                    : { x0: ax - .12 * vw, x1: ax + .44 * vw, y0: ay - .36 * vh, y1: ay + .36 * vh };
  R.x0 = Math.max(R.x0, 130); R.y0 = Math.max(R.y0, -VESSEL_IN); R.y1 = Math.min(R.y1, VESSEL_IN);   // inside the blood vessel
  return R;
}
const VESSEL_IN = 50;                                  // the vessel's half-height (66) less a molecule's reach
const vessel = document.getElementById('jvessel'), rbc = document.getElementById('jrbc');
const at = (R, u, v) => [R.x0 + (R.x1 - R.x0) * u, R.y0 + (R.y1 - R.y0) * v];
// the dimer that tries the membrane: in the bloodstream with the others, then off toward the barrier, and back
const BOUNCER = { ...extra(), u: .42, v: .86, s: .86 };
const memX = y => X.mem + 300 - Math.sqrt(318 * 318 - y * y);          // the membrane's blood-facing surface at height y
const HALF = 34 * SC * BOUNCER.s;                                     // half the dimer's length, and a little air
function bouncer(pn, R) {
  const [B0, BY] = at(R, BOUNCER.u, BOUNCER.v), BC = memX(BY) - HALF;   // where it starts, where it meets the membrane
  let x = B0, spin = 0;
  if (pn > .5 && pn <= .585) { const t = (pn - .5) / .085; x = B0 + (BC - B0) * t * t; }              // speeds up toward it
  else if (pn > .585) { const t = clamp((pn - .585) / .13, 0, 1); x = BC - 62 * (1 - (1 - t) * (1 - t)); spin = 1.3 * (1 - (1 - t) * (1 - t)); }   // and is thrown back
  return { x, y: BY + (pn > .585 ? -10 * clamp((pn - .585) / .13, 0, 1) : 0), spin };
}
const I = new THREE.Quaternion();
const qE = (a, b) => new THREE.Quaternion().setFromEuler(new THREE.Euler(a, b, 0));
// labels that follow molecules (in the page's progress)
const PL = [...document.querySelectorAll('.jl[data-pl]')].map(el => ({ el, a: +el.dataset.a, b: +el.dataset.b, at: el.dataset.pl }));
const frameJ = frame;
frame = function (p0) {
  const pn = clamp(p0, 0, 1);
  frameJ(pn);
  // the crowd: in only for the bloodstream beat, drifting and turning slowly
  const cIn = kf(pn, [[.37, .001], [.41, 1], [.52, 1], [.56, .001]]), R = holdRegion();
  CROWD.forEach(c => {
    c.g.visible = cIn > .01; if (!c.g.visible) return;
    const [cx, cy] = at(R, c.u, c.v);
    c.g.position.set(cx + (pn - .44) * 30, cy + 4 * Math.sin(pn * 30 + c.ph), 0);
    c.g.scale.setScalar(SC * c.s * cIn); c.g.rotation.z = c.r + .25 * Math.sin(pn * 9 + c.ph);
    if (c.kind === 'dimer') c.m.update(V3(-7, 0, 0), V3(7, 0, 0), I, I, 1);
    else c.m.update(V3(-c.hx, 0, 0), V3(c.hx, 0, 0), qE(.3 * Math.sin(pn * 40 + c.ph), .4 * Math.sin(pn * 27 + c.ph)), qE(-.3 * Math.sin(pn * 33 + c.ph), .35 * Math.cos(pn * 29 + c.ph)), 0);
  });
  // the bouncer
  const bIn = kf(pn, [[.37, .001], [.41, 1], [.66, 1], [.71, .001]]), b = bouncer(pn, R);
  BOUNCER.g.visible = bIn > .01;
  if (BOUNCER.g.visible) {
    BOUNCER.g.position.set(b.x, b.y, 0); BOUNCER.g.scale.setScalar(SC * BOUNCER.s * bIn); BOUNCER.g.rotation.z = .08 * Math.sin(pn * 20) + b.spin;
    BOUNCER.m.update(V3(-7, 0, 0), V3(7, 0, 0), I, I, 1);
  }
  // the blood vessel: in from the gut's edge as the monomers leave it, out once they are inside the cell
  vessel.style.opacity = kf(pn, [[.33, 0], [.39, 1], [.68, 1], [.74, 0]]).toFixed(3);
  rbc.setAttribute('transform', `translate(${((pn - .4) * 70).toFixed(2)} 0)`);   // red cells drifting with the flow
  // copy and rail follow the six beats
  const endO = clamp((WARP(pn) - .965) / .03, 0, 1);
  document.querySelectorAll('.beat').forEach((el, i) => { const [a, z] = BEATS_N[i];
    const o = i === BEATS_N.length - 1 ? clamp((pn - a) / .03, 0, 1) * (1 - endO) : i === 0 ? clamp((z - pn) / .03, 0, 1) : clamp(Math.min((pn - a) / .03, (z - pn) / .03), 0, 1);
    el.style.opacity = o.toFixed(3); el.style.transform = 'translateY(calc(-50% + ' + ((1 - o) * 16).toFixed(1) + 'px))'; });
  document.querySelectorAll('.rail b').forEach((el, i) => { el.style.setProperty('--f', clamp((pn - BEATS_N[i][0]) / (BEATS_N[i][1] - BEATS_N[i][0]), 0, 1).toFixed(3)); el.closest('.rail > div').classList.toggle('on', pn >= BEATS_N[i][0]); });
  // labels on the crowd, the bouncer and the hero's monomers
  const ATT = {
    plasma: () => { const [x, y] = at(R, .5, 1.04); return [x, y]; }, dimer: () => { const c = CROWD[0].g.position; return [c.x, c.y - 24]; }, mono: () => { const c = CROWD[1].g.position; return [c.x, c.y - 24]; },
    bounce: () => [BOUNCER.g.position.x - 6, BOUNCER.g.position.y + 24], pass: () => { const c = cg.position; return [c.x + 34, c.y - 30]; },
  };
  PL.forEach(l => { const o = clamp(Math.min((pn - l.a) / .02, (l.b - pn) / .02), 0, 1) * (1 - endO); l.el.style.opacity = o.toFixed(3);
    if (o > 0) { let [x, y] = toScreen(...ATT[l.at]()); const hw = (l.w = l.w || l.el.offsetWidth) / 2 + 10; x = clamp(x, hw, stage.clientWidth - hw);
      l.el.style.transform = `translate(${x.toFixed(1)}px, ${y.toFixed(1)}px) translate(-50%, -50%)`; } });
};
