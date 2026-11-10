// ---------- click-through v2: a live equilibrium in the blood, a population inside the cell, persistent protein labels ----------
// Runs after plasma.js. The blood and the cell hold the same small population (a dimer, a free pair of monomers, a pair
// cycling in equilibrium). In the blood the two monomers we follow join into the dimer and come apart again, on a loop,
// under "Monomer + Monomer ⇌ Dimer"; the dimer that fails at the barrier arrives for that beat only. Inside the cell our
// dimer forms the ternary complex and is degraded. Target protein, E3 ligase and ubiquitin keep large labels beside them.
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
// ---- the same population in the blood and inside the cell: an intact dimer, a free pair of monomers and a pair that
// keeps joining and parting, beside the molecule we follow (cycling in the blood, forming the complex in the cell) ----
const blWin = winOf(.405, .53, .03), cellIn = pn => clamp((pn - .665) / .035, 0, 1);
const POP = [
  // the blood: around our pair (offsets from it, in world units), inside the vessel and clear of the copy
  { at: 'blood', kind: 'dimer', dx: -70, y: -12, s: .74, r: .4, ph: 1, win: blWin },
  { at: 'blood', kind: 'split', dx: -30, y: -34, s: .72, r: -.25, hx: 22, ph: 2.4, win: blWin },
  { at: 'blood', kind: 'eq', dx: -66, y: 44, s: .74, r: -.35, ph: .6, win: blWin },
  // the cell: around the complex; the ones left of it leave before the camera pans to the proteasome
  { at: 'cell', kind: 'dimer', dx: -80, y: 70, s: .7, r: .55, ph: 1, win: pn => cellIn(pn) * clamp((.845 - pn) / .02, 0, 1) },
  { at: 'cell', kind: 'split', dx: -76, y: -58, s: .68, r: -.3, hx: 24, ph: 2, win: pn => cellIn(pn) * clamp((.845 - pn) / .02, 0, 1) },
  { at: 'cell', kind: 'eq', dx: 86, y: 70, s: .68, r: -.45, ph: 1.7, win: pn => cellIn(pn) * clamp((.9 - pn) / .02, 0, 1) },
].map(c => ({ ...c, ...extra() }));
POP.forEach(c => { const d0 = c.at === 'cell' ? 1000 : 900, d = d0 + { dimer: 0, split: 450, eq: 900 }[c.kind];   // after the focal labels
  if (c.kind === 'dimer') c.tags = [tag('Dimer', 'sm', () => c.g, c.win)];
  else if (c.kind === 'split') c.tags = [0, 1].map(i => tag('Monomer', 'sm', () => c.m.group.children[i], c.win));
  else c.tags = [tag('Monomers', 'sm', () => c.g, c.win)];
  c.tags.forEach(t => { t.seq = d; TAGS.push(t); });
});
// ---- the equilibrium labels in the blood ----
function label2(text, cls) { const el = document.createElement('span'); el.className = 'jl ' + cls; el.innerHTML = text; el.setAttribute('aria-hidden', 'true');
  stage.insertBefore(el, document.getElementById('copy')); return el; }
const EQ_LBL = label2('Monomer + Monomer <b>⇌</b> Dimer', 'big eqf'), STATE = label2('Monomers', 'big');
// ---- persistent labels on the proteins and ubiquitin, beside each one; the target's and ubiquitin's go as they enter the proteasome ----
const KEY = [['Target protein', '#F0A6CA', () => P.brd4, winOf(.715, .912, .015)], ['E3 ligase', '#CEE5F3', () => P.vhl, pn => winOf(.715, stage.clientWidth < 760 ? .905 : .985)(pn)],   // on a phone the complex leaves the screen
  ['Ubiquitin', '#B9A6F5', () => ubs[2], pn => winOf(.848, .912, .015)(pn) * (ubs[2].visible ? 1 : 0)]];
KEY.forEach(([t, col, at, win], i) => { const k = tag(t, 'key', at, win, 14); k.side = 'right'; k.seq = [0, 500, 0][i]; k.el.style.setProperty('--dot', col); TAGS.push(k); });
document.querySelectorAll('.jl[data-x]').forEach(el => { if (/^(Target protein|E3 ligase|Ternary complex)$/.test(el.textContent.trim())) el.style.display = 'none'; });
// ---- red cells that drift under the copy fade out, so the text always reads ----
const RBC = [...rbc.children].map(g => { const m = /translate\(([-\d.]+) ([-\d.]+)\)/.exec(g.getAttribute('transform')); return { g, x: +m[1], y: +m[2], o: 1 }; });
const beats = [...document.querySelectorAll('.beat')];
function clearCopy(pn) {
  if (+vessel.style.opacity <= 0) return;
  const rs = beats.filter(b => +b.style.opacity > .01).map(b => b.getBoundingClientRect()), s0 = stage.getBoundingClientRect(), drift = (pn - .4) * 70;
  RBC.forEach(r => { const [x, y] = toScreen(r.x + drift, r.y); let o = 1;
    rs.forEach(b => { const dx = Math.max(b.left - s0.left - x, x - (b.right - s0.left), 0), dy = Math.max(b.top - s0.top - y, y - (b.bottom - s0.top), 0);
      o = Math.min(o, clamp((Math.hypot(dx, dy) - 40) / 30, 0, 1)); });
    if (Math.abs(o - r.o) > .01) { r.o = o; r.g.style.opacity = o.toFixed(2); } });
}

const frameP = frame;
frame = function (p0) {
  const pn = clamp(p0, 0, 1);
  // the populations, drifting a little; the pair in equilibrium joins and parts on the clock
  const t = (performance.now() - T0) / 1000, h0 = cg.localToWorld(V3(0, 0, 0));
  POP.forEach(c => { const cIn = c.win(pn);
    c.g.visible = cIn > .01; if (!c.g.visible) return;
    const ox = c.at === 'cell' ? X.complex : h0.x, oy = c.at === 'cell' ? 0 : h0.y;
    c.g.position.set(ox + c.dx + 3 * Math.sin(t * .7 + c.ph), oy + c.y + 4 * Math.sin(t * .55 + c.ph * 2), 0);
    c.g.scale.setScalar(SC * c.s * cIn); c.g.rotation.z = c.r + .12 * Math.sin(t * .4 + c.ph);
    if (c.kind === 'dimer') { if (!c.built) { c.m.update(V3(-7, 0, 0), V3(7, 0, 0), I, I, 1); c.built = true; } }
    else if (c.kind === 'split') c.m.update(V3(-c.hx, 0, 0), V3(c.hx, 0, 0), qE(.25 * Math.sin(t + c.ph), .35 * Math.sin(t * .8 + c.ph)), qE(-.25 * Math.sin(t * .9 + c.ph), .3 * Math.cos(t * .7 + c.ph)), 0);
    else { const e = eqWave(5.2, c.ph), hx = 22 - 15 * e, f = 1 - e;
      c.m.update(V3(-hx, 0, 0), V3(hx, 0, 0), qE(f * .25 * Math.sin(t + c.ph), f * .35 * Math.sin(t * .8 + c.ph)), qE(f * -.25 * Math.sin(t * .9), f * .3 * Math.cos(t * .7)), e);
      const st = e > .5 ? 'Dimer' : 'Monomers'; if (c.tags[0].el.textContent !== st) c.tags[0].el.textContent = st; }
  });
  frameP(pn);
  // in the gut the pair turns across its path to leave side by side: its "Monomers" label moves from under it to beside it
  const jm = document.getElementById('jmono');
  if (jm && +jm.style.opacity > 0) { const q = WARP(pn), sh = kf(q, [[.18, .001], [.21, .45], [.31, .45], [.42, 1]]), c = cg.localToWorld(V3(0, 0, 0)), r = Math.min(1, Math.abs(cg.rotation.z) / (Math.PI / 2));
    const [bx, by] = toScreen(c.x, c.y - 17 * sh * SC), [rx, ry] = toScreen(c.x + 15 * sh * SC, c.y), hw = jm.offsetWidth / 2;
    jm.style.transform = `translate(${(bx + (rx + hw - bx) * r).toFixed(1)}px, ${(by + (ry - by) * r).toFixed(1)}px) translate(-50%, -50%)`; }
  const endO = clamp((WARP(pn) - .965) / .03, 0, 1);
  clearCopy(pn);
  CROWD.forEach(c => { c.g.visible = false; });
  // the bouncer: only for the barrier beat
  const bA = kf(pn, [[.5, .001], [.535, 1]]);
  // once the barrier beat is over it steps back (smaller, higher in the vessel), clear of the larger copy
  const bBack = kf(pn, [[.615, 0], [.66, 1]]);
  if (BOUNCER.g.visible) { BOUNCER.g.scale.multiplyScalar(bA * (1 - .3 * bBack)); BOUNCER.g.position.y += 7 * bBack; BOUNCER.g.visible = bA > .01; }
  // our two monomers, joining and parting in the blood
  const w = clamp(Math.min((pn - .405) / .03, (.525 - pn) / .03), 0, 1);
  let s = 0;
  if (w > 0) {
    s = eqWave() * w;
    const q = WARP(pn), free = 1 - s, hx = 12 - 5 * s;
    mol.update(V3(-hx, 0, 0), V3(hx, 0, 0), qE(free * .32 * Math.sin(q * 47), free * .42 * Math.sin(q * 31)), qE(free * -.3 * Math.sin(q * 43), free * .4 * Math.cos(q * 35)), s);
    plus.style.opacity = (+plus.style.opacity * (1 - sm01(s * 1.6))).toFixed(3);
  }
  const lw = w * (1 - endO), c0 = h0;
  EQ_LBL.style.opacity = STATE.style.opacity = lw.toFixed(3);
  if (lw > 0) {
    const [ex, ey] = toScreen(c0.x, c0.y + 30), [sx, sy] = toScreen(c0.x, c0.y - 26);
    const hw = (EQ_LBL.w = EQ_LBL.w || EQ_LBL.offsetWidth) / 2 + 10, exc = clamp(ex, hw, stage.clientWidth - hw);   // kept on screen
    EQ_LBL.style.transform = `translate(${exc.toFixed(1)}px, ${ey.toFixed(1)}px) translate(-50%, -50%)`;
    const st = s > .5 ? 'Dimer' : 'Monomers'; if (STATE.textContent !== st) STATE.textContent = st;
    STATE.style.transform = `translate(${sx.toFixed(1)}px, ${sy.toFixed(1)}px) translate(-50%, -50%)`;
  }
  staggerLabels();
};
// ---- labels in the busy spots come in one after another, in reading order: each waits its turn (ms) from the moment
// its own window opens, and pops in. Named by their text for the journey's own labels, by .seq for the ones made here ----
const REDUCE = matchMedia('(prefers-reduced-motion: reduce)').matches;
const byText = (txt, d) => [...document.querySelectorAll('.jl')].filter(el => el.textContent.replace(/\s+/g, ' ').trim() === txt).map(el => ({ el, d }));
const SEQ = [
  { el: EQ_LBL, d: 0 }, { el: STATE, d: 400 },                                        // the bloodstream: the equilibrium, then the crowd
  ...byText('Cell membrane · blood-brain barrier', 0), ...byText('Dimer: too large to penetrate', 300),   // the barrier
  ...byText('Target cell', 700), ...byText('Monomers pass through', 1200),
  ...byText('Proteasome', 700),                                                        // tagging: ubiquitin first, then where it leads
  ...TAGS.filter(t => t.seq !== undefined).map(t => ({ el: t.el, d: t.seq })),
].map(s => ({ ...s, t0: 0 }));
let busyUntil = 0;
function staggerLabels() {
  const now = performance.now();
  SEQ.forEach(s => { const base = +s.el.style.opacity || 0;
    if (base <= .01) { s.t0 = 0; return; }
    if (!s.t0) { s.t0 = now; busyUntil = Math.max(busyUntil, now + s.d + 450); }
    const f = REDUCE ? 1 : clamp((now - s.t0 - s.d) / 320, 0, 1);
    if (f >= 1) return;
    s.el.style.opacity = (base * f).toFixed(3);
    if (f > 0) s.el.style.transform += ` scale(${(.82 + .18 * (1 - Math.pow(1 - f, 3))).toFixed(3)})`;   // a small pop as it lands
  });
}
// the click driver's idle loop asks for a redraw while a stop holds a live equilibrium, or labels are still coming in
window.__liveAt = p => (p > .4 && p < .53) || (p > .66 && p < .99) || performance.now() < busyUntil;
