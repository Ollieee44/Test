// ---------- site: header state, skip control, section reveals, copy button ----------
const head = document.getElementById('head'), storyEl = document.getElementById('story'), skip = document.getElementById('skip');
const navLinks = [...document.querySelectorAll('.head nav a')];
const sections = navLinks.map(a => document.querySelector(a.getAttribute('href')));
document.documentElement.lang = 'en';
const themeMeta = document.querySelector('meta[name="theme-color"]');
// one batch of layout reads per frame at most, then the writes
let scrollQueued = false;
function onScroll() {
  if (scrollQueued) return; scrollQueued = true;
  requestAnimationFrame(() => {
    scrollQueued = false;
    const sr = storyEl.getBoundingClientRect(), tops = sections.map(s => s ? s.getBoundingClientRect().top : Infinity);
    const past = sr.bottom < innerHeight * .6, sp = -sr.top / Math.max(1, sr.height - innerHeight);
    let cur = -1; tops.forEach((t, i) => { if (t < innerHeight * .4) cur = i; });
    head.classList.toggle('solid', past);
    navLinks.forEach((a, i) => a.setAttribute('aria-current', String(i === cur)));
    skip.classList.toggle('gone', sp > .92);   // the skip control stays until the story reaches its end card
  });
}
addEventListener('scroll', onScroll, { passive: true }); addEventListener('resize', onScroll); onScroll();
// the browser chrome follows the palette
const syncTheme = () => { if (themeMeta) themeMeta.content = getComputedStyle(document.documentElement).getPropertyValue('--paper').trim(); };
new MutationObserver(syncTheme).observe(document.documentElement, { attributes: true, attributeFilter: ['data-palette'] }); syncTheme();
const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { rootMargin: '0px 0px -10% 0px' });
document.querySelectorAll('.rv').forEach(el => io.observe(el));
document.querySelectorAll('.copy-btn').forEach(b => b.addEventListener('click', async () => {
  const status = document.getElementById('copyStatus');
  try { await navigator.clipboard.writeText(b.dataset.copy); b.textContent = 'Copied'; if (status) status.textContent = 'Email address copied'; }
  catch (e) { b.textContent = 'Select and copy'; if (status) status.textContent = 'Copying failed: select the address and copy it'; }
  setTimeout(() => { b.textContent = 'Copy'; if (status) status.textContent = ''; }, 1800);
}));

// ---------- the live clasp: the two halves close as the section scrolls into view ----------
const claspCanvas = document.getElementById('claspGl');
if (claspCanvas && renderer) {
  const r2 = new THREE.WebGLRenderer({ canvas: claspCanvas, antialias: true, alpha: true });
  const s2 = new THREE.Scene(), c2 = new THREE.PerspectiveCamera(24, 1, 1, 1000);
  const m2 = makeMolecule(THREE, DATA, Q, geom, new THREE.Vector3(0, -1, .25));
  const pivot = new THREE.Group(); pivot.add(m2.group); m2.group.position.copy(m2.centre).negate(); s2.add(pivot);
  m2.setColors(PAL[pal]);
  document.querySelectorAll('.pal button').forEach(b => b.addEventListener('click', () => m2.setColors(PAL[pal])));
  let visible = false; new IntersectionObserver(e => { visible = e[0].isIntersecting; }).observe(claspCanvas);
  const size2 = () => { const w = claspCanvas.clientWidth, h = claspCanvas.clientHeight; r2.setPixelRatio(Math.min(devicePixelRatio, 2)); r2.setSize(w, h, false); c2.aspect = w / h; c2.updateProjectionMatrix(); };
  addEventListener('resize', size2); size2();
  const I = new THREE.Quaternion(), sm = t => t * t * (3 - 2 * t);
  // where the figure sits is read on scroll and resize, not every frame: 0 while it is low on the
  // screen, 1 once its centre passes 45% of the viewport height
  let goal = 0;
  const measure2 = () => { const r = claspCanvas.getBoundingClientRect(); goal = Math.max(0, Math.min(1, 1 - (r.top + r.height / 2 - innerHeight * .45) / (innerHeight * .45))); };
  addEventListener('scroll', measure2, { passive: true }); addEventListener('resize', measure2); measure2();
  // it moves only with the scroll (no autoplaying loop): the halves close and the model turns a little
  // as the section comes up, and the scene stops redrawing once it has settled
  let shut = 0, last2 = performance.now(), drawn = -1;
  (function loop2(t) {
    const dt = Math.min(.1, (t - last2) / 1000); last2 = t;
    if (visible) {
      shut += (goal - shut) * (reduce ? 1 : 1 - Math.exp(-dt / .18));
      if (Math.abs(goal - shut) < 1e-4) shut = goal;
      if (shut !== drawn) {
        const sep = 3 + 11 * (1 - sm(shut)), joined = sm(Math.max(0, Math.min(1, (shut - .7) / .3)));
        m2.update(new THREE.Vector3(-sep, 0, 0), new THREE.Vector3(sep, 0, 0), I, I, joined);
        pivot.rotation.y = -.25 + (reduce ? 0 : .3 * (1 - shut)); pivot.rotation.x = .12;
        c2.position.set(0, 0, 96); c2.lookAt(0, 0, 0);
        r2.render(s2, c2); drawn = shut;
      }
    }
    requestAnimationFrame(loop2);
  })(0);
  document.querySelectorAll('.pal button').forEach(b => b.addEventListener('click', () => { drawn = -1; }));
}
