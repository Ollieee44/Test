// ---------- v2 load-in: the fan mark holds, then its pearl becomes the clasp as the two halves close on it ----------
// The mark stays up for LOGO_MS (and until the first frame is drawn). Then, over INTRO_MS, the loader's ground fades
// and the shell shrinks away; the mark's pearl flies to where the clasp will be and turns gold; the two halves fly
// in from far behind along the line of sight to the clasp (so they grow in place, clear of the copy), close on it, and the bond clicks shut with a flash as the pearl melts into the clasp.
const LOGO_MS = 1700, INTRO_MS = 2100, pageT0 = performance.now();
const loaderEl = stage.querySelector('.loader'), claspNdc = new THREE.Vector3();
let introAnim = null, introHold = -1;
let intro = (reduce || !renderer || !loaderEl || location.hash.length > 1) ? 1 : 0, introStart = -1, drawnSig = '', firstDrawn = false;
function startIntro(now) {
  introStart = now;
  stage.classList.add('ready');
  if (intro >= 1) return;
  const src = loaderEl.querySelector('.pearl');
  if (!src) { intro = 1; return; }
  // aim the pearl at where the clasp will be once the halves have closed
  intro = 1; frame(prog); const aim = claspNdc.clone(); intro = 0; frame(prog);
  const sr = stage.getBoundingClientRect(), r = src.getBoundingClientRect(), cs = getComputedStyle(root);
  const d0 = Math.max(4, r.width), x0 = r.left - sr.left + r.width / 2, y0 = r.top - sr.top + r.height / 2;
  const x1 = (aim.x + 1) / 2 * stage.clientWidth, y1 = (1 - aim.y) / 2 * stage.clientHeight;
  const k = Math.max(26, Math.min(48, stage.clientWidth * .026)) / d0, mv = `translate(${(x1 - x0).toFixed(1)}px, ${(y1 - y0).toFixed(1)}px)`;
  const pearlCol = cs.getPropertyValue('--pearl').trim(), claspCol = cs.getPropertyValue('--clasp').trim();
  const el = document.createElement('i'); el.className = 'lpearl'; el.setAttribute('aria-hidden', 'true');
  Object.assign(el.style, { width: d0 + 'px', height: d0 + 'px', left: (x0 - d0 / 2) + 'px', top: (y0 - d0 / 2) + 'px', background: pearlCol });
  stage.appendChild(el); src.style.opacity = '0';
  // eased leg by leg: fly to the clasp (0-50%), wait there while the halves arrive (to 78%), then pop and melt into
  // the bond as it clicks shut (to 90%)
  const fly = 'cubic-bezier(.45, 0, .2, 1)', pop = 'cubic-bezier(.2, .7, .3, 1)';
  introAnim = el.animate([
    { transform: 'translate(0, 0) scale(1)', backgroundColor: pearlCol, opacity: 1, offset: 0, easing: fly },
    { transform: `${mv} scale(${k})`, backgroundColor: claspCol, opacity: 1, offset: .5, easing: 'linear' },
    { transform: `${mv} scale(${k})`, backgroundColor: claspCol, opacity: 1, offset: .78, easing: pop },
    { transform: `${mv} scale(${k * 1.7})`, backgroundColor: claspCol, opacity: 0, offset: .9 },
    { transform: `${mv} scale(${k * 1.7})`, backgroundColor: claspCol, opacity: 0, offset: 1 },
  ], { duration: INTRO_MS, easing: 'linear', fill: 'forwards' });
  introAnim.finished.then(() => el.remove(), () => el.remove());
}

// test hook: hold the load-in at ms milliseconds (screenshots)
window.__intro = ms => {
  if (!introAnim || ms === 0) {   // start over
    if (introAnim) introAnim.cancel();
    stage.querySelectorAll('.lpearl').forEach(e => e.remove());
    intro = 0; startIntro(performance.now());
  }
  introHold = ms / INTRO_MS; if (introAnim) { introAnim.pause(); introAnim.currentTime = ms; }
};

