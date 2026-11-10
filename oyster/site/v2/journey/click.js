// ---------- the click-through version: Next / Back step between the story's key moments ----------
// The page does not scroll; each step plays the journey from one stop to the next (eased, its length in proportion to
// the distance) and holds there. Arrow keys and the space bar step too, and the rail's pearls jump to a beat.
(() => {
  const STOPS = [0, .145, .25, .335, .45, .585, .665, .79, .865, .92, .998];
  const BEAT_STOP = [0, 2, 4, 5, 7, 8];                  // the first stop of each of the six beats (the rail)
  BEATS_N[4][1] = BEATS_N[5][0] = .84;                   // the degradation copy is in by the time the tags land (stop 9)
  const J = window.__journey, next = document.getElementById('jnext'), back = document.getElementById('jback'), count = document.getElementById('jcount');
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let at = 0, p = 0, anim = null;
  const ease = t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  function show() {
    count.textContent = `${at + 1} / ${STOPS.length}`;
    back.disabled = at === 0;
    next.querySelector('span').textContent = at === STOPS.length - 1 ? 'Start again' : 'Next';
  }
  function go(i) {
    i = Math.max(0, Math.min(STOPS.length - 1, i));
    if (i === STOPS.length - 1 && at === STOPS.length - 1 && i === at) return;
    const from = p, to = STOPS[i], dur = reduce ? 0 : Math.max(900, Math.min(3400, Math.abs(to - from) * 9000)), t0 = performance.now();
    at = i; show(); if (anim) cancelAnimationFrame(anim);
    const tick = now => { const t = dur ? Math.min(1, (now - t0) / dur) : 1; p = from + (to - from) * ease(t); J.frame(p); if (t < 1) anim = requestAnimationFrame(tick); else anim = null; };
    anim = requestAnimationFrame(tick);
  }
  next.addEventListener('click', () => go(at === STOPS.length - 1 ? 0 : at + 1));
  back.addEventListener('click', () => go(at - 1));
  addEventListener('keydown', e => {
    if (e.target.closest && e.target.closest('input, textarea')) return;
    if (['ArrowRight', 'ArrowDown', 'PageDown', ' '].includes(e.key)) { e.preventDefault(); go(at === STOPS.length - 1 ? 0 : at + 1); }
    if (['ArrowLeft', 'ArrowUp', 'PageUp'].includes(e.key)) { e.preventDefault(); go(at - 1); }
  });
  document.querySelectorAll('.rail > div').forEach((d, i) => { d.setAttribute('role', 'button'); d.tabIndex = 0; d.setAttribute('aria-label', 'Go to ' + d.textContent.trim());
    const jump = () => go(BEAT_STOP[i]); d.addEventListener('click', jump); d.addEventListener('keydown', e => { if (e.key === 'Enter') jump(); }); });
  document.getElementById('rail').removeAttribute('aria-hidden');
  // "Watch again" on the end card goes back to the first stop
  document.querySelectorAll('#end a').forEach(a => a.addEventListener('click', e => { e.preventDefault(); go(0); }));
  J.frame(0); show();
})();
