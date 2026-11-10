// ---------- the click-through version: Next / Back step between the story's key moments ----------
// The page does not scroll; each step plays the journey from one stop to the next (eased, its length in proportion to
// the distance) and holds there. Arrow keys and the space bar step too, and the rail's pearls jump to a beat.
(() => {
  const STOPS = [0, .145, .25, .335, .45, .612, .665, .79, .865, .92, .998];
  const BEAT_STOP = [0, 2, 4, 5, 7, 8];                  // the first stop of each of the six beats (the rail)
  BEATS_N[4][1] = BEATS_N[5][0] = .84;                   // the degradation copy is in by the time the tags land (stop 9)
  const J = window.__journey, next = document.getElementById('jnext'), back = document.getElementById('jback'), count = document.getElementById('jcount');
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let at = 0, p = 0, anim = null, playing = false, playToken = 0;
  const play = document.getElementById('jplay'), playLabel = play.querySelector('span');
  // a click answers at once and settles into the stop; autoplay glides in and out
  const easeOut = t => 1 - Math.pow(1 - t, 3), easeInOut = t => -(Math.cos(Math.PI * t) - 1) / 2;
  function show() {
    count.textContent = `${at + 1} / ${STOPS.length}`;
    back.disabled = at === 0;
    next.querySelector('span').textContent = at === STOPS.length - 1 ? 'Start again' : 'Next';
  }
  // go to stop i; resolves when the move has played (or at once if there is nowhere to go)
  function go(i, glide = false) {
    i = Math.max(0, Math.min(STOPS.length - 1, i));
    if (i === at && Math.abs(p - STOPS[i]) < 1e-6) return Promise.resolve();
    let done; const finished = new Promise(r => { done = r; });
    const from = p, to = STOPS[i], d = Math.abs(to - from), ease = glide ? easeInOut : easeOut;
    // unhurried moves: autoplay 1.6-3.4 s, a click 1.1-2.6 s, longer for longer journeys
    const dur = reduce ? 0 : glide ? Math.max(1600, Math.min(3400, 1300 + d * 9000)) : Math.max(1100, Math.min(2600, 900 + d * 7000)), t0 = performance.now();
    at = i; show(); if (anim) cancelAnimationFrame(anim);
    // only the progress moves here; the journey's loop draws it, once per screen refresh
    const tick = now => { const t = dur ? Math.min(1, (now - t0) / dur) : 1; p = from + (to - from) * ease(t); J.goTo(p); if (t < 1) anim = requestAnimationFrame(tick); else { anim = null; done(); } };
    anim = requestAnimationFrame(tick);
    return finished;
  }
  // the whole journey: every stop in turn, holding at each long enough to read (longer where the copy changes)
  const HOLD = [300, 150, 550, 300, 800, 200, 550, 650, 450, 400];   // a brief pause at each stop (longest where the copy changes)
  const wait = ms => new Promise(r => setTimeout(r, ms));
  function setPlaying(on) { playing = on; play.classList.toggle('on', on); play.setAttribute('aria-pressed', String(on));
    playLabel.textContent = on ? 'Pause' : at === STOPS.length - 1 ? 'Watch again' : at === 0 ? 'Watch the whole journey' : 'Play from here'; }
  async function playAll() {
    const token = ++playToken; setPlaying(true);
    if (at === STOPS.length - 1) { await go(0); if (token !== playToken) return; await wait(700); }
    while (at < STOPS.length - 1) {
      await wait(HOLD[at] || 1600); if (token !== playToken) return;
      await go(at + 1, true); if (token !== playToken) return;
    }
    setPlaying(false);
  }
  function stopPlay() { if (playing) { playToken++; setPlaying(false); } }
  play.addEventListener('click', () => { if (playing) stopPlay(); else playAll(); });
  next.addEventListener('click', () => { stopPlay(); go(at === STOPS.length - 1 ? 0 : at + 1).then(() => setPlaying(false)); });
  back.addEventListener('click', () => { stopPlay(); go(at - 1).then(() => setPlaying(false)); });
  addEventListener('keydown', e => {
    if (e.target.closest && e.target.closest('input, textarea')) return;
    if (['ArrowRight', 'ArrowDown', 'PageDown', ' '].includes(e.key)) { if (e.target === play) return; e.preventDefault(); stopPlay(); go(at === STOPS.length - 1 ? 0 : at + 1).then(() => setPlaying(false)); }
    if (['ArrowLeft', 'ArrowUp', 'PageUp'].includes(e.key)) { e.preventDefault(); stopPlay(); go(at - 1).then(() => setPlaying(false)); }
  });
  document.querySelectorAll('.rail > div').forEach((d, i) => { d.setAttribute('role', 'button'); d.tabIndex = 0; d.setAttribute('aria-label', 'Go to ' + d.textContent.trim());
    const jump = () => { stopPlay(); go(BEAT_STOP[i]).then(() => setPlaying(false)); }; d.addEventListener('click', jump); d.addEventListener('keydown', e => { if (e.key === 'Enter') jump(); }); });
  document.getElementById('rail').removeAttribute('aria-hidden');
  // "Watch again" on the end card goes back to the first stop
  document.querySelectorAll('#end a').forEach(a => a.addEventListener('click', e => { e.preventDefault(); playAll(); }));   // Watch again plays it through
  J.frame(0); show(); setPlaying(false);
})();
