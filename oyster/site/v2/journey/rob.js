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
  return mol.update(V3(-hx, 0, 0), V3(hx, 0, 0), qE(f * .3 * Math.sin(t * 1.1), f * .4 * Math.sin(t * .8)), qE(f * -.3 * Math.sin(t * 1.3), f * .4 * Math.cos(t * .9)), j);
}
// the second dimer is gone, with its label
TAGS.forEach(t => { if (t.at() === BOUNCER.g) { t.win = () => 0; t.el.style.display = 'none'; } });
{
  const frameC = frame;
  frame = function (p0) {
    const pn = clamp(p0, 0, 1);
    frameC(pn);
    BOUNCER.g.visible = false;
    if (pn > .5 && pn < .7) plus.style.opacity = 0;                    // no '+' while it joins, bounces and comes apart
    // a flash as the linker breaks at the membrane
    const fb = Math.max(0, Math.sin(Math.PI * clamp((pn - .59) / .028, 0, 1)));
    if (fb > .01) { mol.group.updateMatrixWorld(true); flash.position.copy(mol.group.localToWorld(V3(0, 0, 0))); flash.scale.setScalar(SC * (.8 + 1.2 * fb));
      flash.material.opacity = .7 * fb; flash.visible = true; flash.lookAt(camera.position); }
  };
}
