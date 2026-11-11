// ---------- Rob's edits: one dimer at the barrier ----------
// After the bloodstream the two monomers we follow join into the dimer, which heads for the membrane, bounces off it (too
// large to penetrate), comes apart at its reversible linker, and the two monomers cross side by side. No second dimer.
// heroOverride runs inside the journey's frame, straight after it places the molecule, so every label follows it.
const smR = x => x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x);
const HERO_HALF = 18;                                                  // from its centre to its leading end (the dimer sits off-centre)
function heroOverride(pn, brk) {
  if (pn < .5 || pn > .68) return brk;
  const xJ = cg.position.x, yJ = cg.position.y, rotJ = cg.rotation.z;  // where the journey has it (handed back by .68)
  const xB = HERO_X(WARP(.5)), xC = memX(0) - HERO_HALF, xK = xC - 26;  // in the blood; touching the membrane; knocked back
  const join = smR((pn - .5) / .03), gone = smR((pn - .592) / .022);   // joins up; then comes apart
  let x;
  if (pn < .53) x = xB;
  else if (pn < .566) { const t = (pn - .53) / .036; x = xB + (xC - xB) * t * t; }                       // speeding up toward it
  else if (pn < .59) { const t = (pn - .566) / .024; x = xC - (xC - xK) * (1 - (1 - t) * (1 - t)); }    // knocked back
  else if (pn < .612) x = xK;
  else x = xK + (xJ - xK) * smR((pn - .612) / .05);                                                      // the monomers go through
  const back = smR((pn - .655) / .025);                                // hand back to the journey's own path
  cg.position.set(x + (xJ - x) * back, yJ * back, 0);
  const wob = pn > .566 && pn < .6 ? .22 * Math.sin((pn - .566) / .034 * Math.PI) : 0;                  // the knock
  cg.rotation.z = (-Math.PI / 2 * smR((pn - .594) / .02) + wob) * (1 - back) + rotJ * back;
  const j = join * (1 - gone), hxJ = HX(WARP(pn)) - (typeof CMP === 'number' ? CMP : 0);
  let hx = 12 - 5 * j; if (gone > 0) hx = 7 + 6 * gone;               // apart, then joined, then apart again
  hx = hx + (hxJ - hx) * smR((pn - .64) / .04);
  const f = (1 - j) * (1 - back) * .6, t = pn * 40;
  const b = mol.update(V3(-hx, 0, 0), V3(hx, 0, 0), qE(f * .3 * Math.sin(t * 1.1), f * .4 * Math.sin(t * .8)), qE(f * -.3 * Math.sin(t * 1.3), f * .4 * Math.cos(t * .9)), j);
  if (gone < .35) ROB_BRK.copy(b);                                     // the linker, while it still holds: where the flash goes
  return b;
}
const ROB_BRK = V3(0, 0, 0);
// no oscillating Monomers/Dimer word under the pair in the blood (the formula above it stays)
STATE.style.display = 'none';
// the second dimer is gone, with its label
TAGS.forEach(t => { if (t.at() === BOUNCER.g) { t.win = () => 0; t.el.style.display = 'none'; } });
{
  const frameC = frame;
  frame = function (p0) {
    const pn = clamp(p0, 0, 1);
    frameC(pn);
    declutter();
    BOUNCER.g.visible = false;
    if (pn > .5 && pn < .7) plus.style.opacity = 0;                    // no '+' while it joins, bounces and comes apart
    // a flash as the linker breaks at the membrane
    const fb = Math.max(0, Math.sin(Math.PI * clamp((pn - .59) / .028, 0, 1)));   // the break
    // a small flash on the linker as it breaks, sized like the break in the gut
    if (fb > .01) { mol.group.updateMatrixWorld(true); flash.position.copy(mol.group.localToWorld(ROB_BRK.clone()));
      flash.scale.setScalar(SC * (.6 + 1.1 * clamp((pn - .59) / .028, 0, 1))); flash.material.opacity = .6 * fb; flash.visible = true; flash.lookAt(camera.position); }
  };
}
// labels never sit on one another or on the molecule we follow: after each frame a label over one of its two halves is moved
// just clear of it (up or down, whichever is shorter), then any label overlapping one above it is nudged down clear of it
function declutter() {
  const obs = [];
  if (cg.visible) mol.group.children.slice(0, 2).forEach(ch => { const bx = new THREE.Box3().setFromObject(ch); if (bx.isEmpty()) return; let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9;
    for (const cx of [bx.min.x, bx.max.x]) for (const cy of [bx.min.y, bx.max.y]) for (const cz of [bx.min.z, bx.max.z]) {
      vtmp.set(cx, cy, cz).project(camera); const sx = (vtmp.x + 1) / 2 * stage.clientWidth, sy = (1 - vtmp.y) / 2 * stage.clientHeight;
      x0 = Math.min(x0, sx); x1 = Math.max(x1, sx); y0 = Math.min(y0, sy); y1 = Math.max(y1, sy); }
    const s0 = stage.getBoundingClientRect(); obs.push({ left: x0 + s0.left, right: x1 + s0.left, top: y0 + s0.top, bottom: y1 + s0.top }); });
  const rs = [...document.querySelectorAll('.jl')].filter(e => e.style.display !== 'none' && +e.style.opacity > .05)
    .map(e => ({ e, r: e.getBoundingClientRect() }));
  rs.forEach(o => { const b = o.r; let dy = 0;
    obs.forEach(a => { if (b.left < a.right + 4 && b.right > a.left - 4 && b.top + dy < a.bottom + 4 && b.bottom + dy > a.top - 4) {
      const up = a.top - 4 - b.bottom, down = a.bottom + 4 - b.top; dy = Math.abs(up) < Math.abs(down) ? up : down; } });
    if (dy) { o.e.style.transform += ` translate(0, ${dy.toFixed(1)}px)`; o.r = { left: b.left, right: b.right, top: b.top + dy, bottom: b.bottom + dy }; } });
  rs.sort((a, b) => a.r.top - b.r.top);
  for (let i = 1; i < rs.length; i++) {
    let b = rs[i].r, dy = 0;
    for (let k = 0; k < i; k++) { const a = rs[k].r;
      if (b.left < a.right + 6 && b.right > a.left - 6 && b.top + dy < a.bottom + 5 && b.bottom + dy > a.top) dy = a.bottom + 5 - b.top; }
    if (dy > 0) { rs[i].e.style.transform += ` translate(0, ${dy.toFixed(1)}px)`; rs[i].r = { left: b.left, right: b.right, top: b.top + dy, bottom: b.bottom + dy }; }
  }
}
