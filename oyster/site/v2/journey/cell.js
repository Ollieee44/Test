// ---------- click-through v2: a live equilibrium in the blood, a population inside the cell, persistent protein labels ----------
// Runs after plasma.js. In the blood the crowd goes: the two monomers we follow join into the dimer and come apart again,
// on a loop, under "Monomer + Monomer ⇌ Dimer"; the dimer that fails at the barrier arrives for that beat only. Inside
// the cell, free monomers and a dimer sit around the complex, with one pair cycling in equilibrium, while our dimer forms
// the ternary complex and is degraded. Target protein, E3 ligase and ubiquitin keep large labels, with a key at the left.
// The equilibria run on the clock, so the click driver redraws while a stop holds them (click2's idle loop).
const T0 = performance.now();
const sm01 = x => x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x);
// 0 apart, 1 joined: holds apart, joins, holds joined, comes apart (period in seconds)
function eqWave(period = 4.6, ph = 0) {
  const u = ((((performance.now() - T0) / 1000 + ph) % period) + period) % period / period;
  return u < .16 ? 0 : u < .4 ? sm01((u - .16) / .24) : u < .64 ? 1 : u < .88 ? 1 - sm01((u - .64) / .24) : 0;
}
const winOf = (a, b, f = .02) => pn => clamp(Math.min((pn - a) / f, (b - pn) / f), 0, 1);

// ---- the blood: no crowd; the bouncer comes in for the barrier beat ----
TAGS.forEach(t => { if (t.at() !== BOUNCER.g) { t.el.style.display = 'none'; t.win = () => 0; } else t.win = winOf(.515, .583, .015); });
// ---- inside the cell ----
const CELL = [
  { kind: 'dimer', dx: -80, y: 70, s: .7, r: .55, ph: 1, out: .845 },
  { kind: 'split', dx: -76, y: -58, s: .68, r: -.3, hx: 24, ph: 2, out: .845 },
  { kind: 'split', dx: 86, y: 84, s: .66, r: .25, hx: 20, ph: 3, out: .9 },
  { kind: 'eq', dx: 84, y: -8, s: .68, r: -.45, ph: 1.7, out: .9 },
].map(c => ({ ...c, ...extra() }));
// in as the monomers cross; the ones left of the complex leave before the camera pans to the proteasome, the rest after
const cellIn = pn => clamp((pn - .665) / .035, 0, 1);
CELL.forEach(c => { const cellWin = c.win = pn => cellIn(pn) * clamp((c.out - pn) / .02, 0, 1);
  if (c.kind === 'dimer') c.tags = [tag('Dimer', 'sm', () => c.g, cellWin)];
  else if (c.kind === 'split') c.tags = [0, 1].map(i => tag('Monomer', 'sm', () => c.m.group.children[i], cellWin));
  else c.tags = [tag('Monomers', 'sm', () => c.g, cellWin)];
  c.tags.forEach(t => TAGS.push(t));
});
// ---- the equilibrium labels in the blood ----
function label2(text, cls) { const el = document.createElement('span'); el.className = 'jl ' + cls; el.innerHTML = text; el.setAttribute('aria-hidden', 'true');
  stage.insertBefore(el, document.getElementById('copy')); return el; }
const EQ_LBL = label2('Monomer + Monomer <b>⇌</b> Dimer', 'big eqf'), STATE = label2('Monomers', 'big');
// ---- persistent labels on the proteins and ubiquitin, beside each one, and a key at the left ----
const KEY = [['Target protein', '#F0A6CA', () => P.brd4, winOf(.715, .945)], ['E3 ligase', '#CEE5F3', () => P.vhl, winOf(.715, .985)],
  ['Ubiquitin', '#B9A6F5', () => ubs[2], pn => winOf(.848, .945)(pn) * (ubs[2].visible ? 1 : 0)]];
KEY.forEach(([t, col, at, win]) => { const k = tag(t, 'key', at, win, 14); k.side = 'right'; k.el.style.setProperty('--dot', col); TAGS.push(k); });
document.querySelectorAll('.jl[data-x]').forEach(el => { if (/^(Target protein|E3 ligase)$/.test(el.textContent.trim())) el.style.display = 'none'; });
const keyBox = document.createElement('div'); keyBox.className = 'jkey'; keyBox.setAttribute('aria-label', 'Key');
keyBox.innerHTML = '<span class="jkey-t">Key</span>' + KEY.map(([t, col]) => `<span class="jkey-r"><i style="background:${col}"></i>${t}</span>`).join('')
  + '<span class="jkey-r"><i class="sel"></i>SELFTAC<sup>®</sup> degrader</span>';
stage.insertBefore(keyBox, document.getElementById('copy'));

const frameP = frame;
frame = function (p0) {
  const pn = clamp(p0, 0, 1);
  // inside the cell: the population, drifting a little; one pair cycling
  const t = (performance.now() - T0) / 1000;
  CELL.forEach(c => { const cIn = c.win(pn);
    c.g.visible = cIn > .01; if (!c.g.visible) return;
    c.g.position.set(X.complex + c.dx + 3 * Math.sin(t * .7 + c.ph), c.y + 4 * Math.sin(t * .55 + c.ph * 2), 0);
    c.g.scale.setScalar(SC * c.s * cIn); c.g.rotation.z = c.r + .12 * Math.sin(t * .4 + c.ph);
    if (c.kind === 'dimer') { if (!c.built) { c.m.update(V3(-7, 0, 0), V3(7, 0, 0), I, I, 1); c.built = true; } }
    else if (c.kind === 'split') c.m.update(V3(-c.hx, 0, 0), V3(c.hx, 0, 0), qE(.25 * Math.sin(t + c.ph), .35 * Math.sin(t * .8 + c.ph)), qE(-.25 * Math.sin(t * .9 + c.ph), .3 * Math.cos(t * .7 + c.ph)), 0);
    else { const e = eqWave(5.2, c.ph), hx = 22 - 15 * e, f = 1 - e;
      c.m.update(V3(-hx, 0, 0), V3(hx, 0, 0), qE(f * .25 * Math.sin(t + c.ph), f * .35 * Math.sin(t * .8 + c.ph)), qE(f * -.25 * Math.sin(t * .9), f * .3 * Math.cos(t * .7)), e);
      const st = e > .5 ? 'Dimer' : 'Monomers'; if (c.tags[0].el.textContent !== st) c.tags[0].el.textContent = st; }
  });
  frameP(pn);
  const endO = clamp((WARP(pn) - .965) / .03, 0, 1);
  CROWD.forEach(c => { c.g.visible = false; });
  // the bouncer: only for the barrier beat
  const bA = kf(pn, [[.5, .001], [.535, 1]]);
  if (BOUNCER.g.visible) { BOUNCER.g.scale.multiplyScalar(bA); BOUNCER.g.visible = bA > .01; }
  // our two monomers, joining and parting in the blood
  const w = clamp(Math.min((pn - .405) / .03, (.525 - pn) / .03), 0, 1);
  let s = 0;
  if (w > 0) {
    s = eqWave() * w;
    const q = WARP(pn), free = 1 - s, hx = 12 - 5 * s;
    mol.update(V3(-hx, 0, 0), V3(hx, 0, 0), qE(free * .32 * Math.sin(q * 47), free * .42 * Math.sin(q * 31)), qE(free * -.3 * Math.sin(q * 43), free * .4 * Math.cos(q * 35)), s);
    plus.style.opacity = (+plus.style.opacity * (1 - sm01(s * 1.6))).toFixed(3);
  }
  const lw = w * (1 - endO), c0 = cg.localToWorld(V3(0, 0, 0));
  EQ_LBL.style.opacity = STATE.style.opacity = lw.toFixed(3);
  if (lw > 0) {
    const [ex, ey] = toScreen(c0.x, c0.y + 30), [sx, sy] = toScreen(c0.x, c0.y - 26);
    const hw = (EQ_LBL.w = EQ_LBL.w || EQ_LBL.offsetWidth) / 2 + 10, exc = clamp(ex, hw, stage.clientWidth - hw);   // kept on screen
    EQ_LBL.style.transform = `translate(${exc.toFixed(1)}px, ${ey.toFixed(1)}px) translate(-50%, -50%)`;
    const st = s > .5 ? 'Dimer' : 'Monomers'; if (STATE.textContent !== st) STATE.textContent = st;
    STATE.style.transform = `translate(${sx.toFixed(1)}px, ${sy.toFixed(1)}px) translate(-50%, -50%)`;
  }
  keyBox.style.opacity = (winOf(.715, .99)(pn) * (1 - endO)).toFixed(3);
};
// the click driver's idle loop asks for a redraw while a stop holds a live equilibrium
window.__liveAt = p => (p > .4 && p < .53) || (p > .66 && p < .99);
