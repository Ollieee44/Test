// ---------- site: header state, skip control, section reveals, copy button ----------
const head = document.getElementById('head'), storyEl = document.getElementById('story'), skip = document.getElementById('skip');
const navLinks = [...document.querySelectorAll('.head nav a')];
const sections = navLinks.map(a => document.querySelector(a.getAttribute('href')));
function onScroll() {
  const past = storyEl.getBoundingClientRect().bottom < innerHeight * .6;
  head.classList.toggle('solid', past);
  let cur = -1; sections.forEach((s, i) => { if (s && s.getBoundingClientRect().top < innerHeight * .4) cur = i; });
  navLinks.forEach((a, i) => a.setAttribute('aria-current', String(i === cur)));
  // the skip control stays until the story reaches its end card
  const sr = storyEl.getBoundingClientRect(), sp = -sr.top / Math.max(1, sr.height - innerHeight);
  skip.classList.toggle('gone', sp > .92);
}
addEventListener('scroll', onScroll, { passive: true }); onScroll();
const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { rootMargin: '0px 0px -10% 0px' });
document.querySelectorAll('.rv').forEach(el => io.observe(el));
document.querySelectorAll('.copy-btn').forEach(b => b.addEventListener('click', async () => {
  try { await navigator.clipboard.writeText(b.dataset.copy); b.textContent = 'Copied'; } catch (e) { b.textContent = 'Select and copy'; }
  setTimeout(() => { b.textContent = 'Copy'; }, 1800);
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
  let shut = 0, last2 = performance.now();
  (function loop2(t) {
    const dt = Math.min(.1, (t - last2) / 1000); last2 = t;
    if (visible) {
      const r = claspCanvas.getBoundingClientRect();
      // 0 while the figure is low on the screen, 1 once its centre passes 45% of the viewport height
      const goal = Math.max(0, Math.min(1, 1 - (r.top + r.height / 2 - innerHeight * .45) / (innerHeight * .45)));
      shut += (goal - shut) * (reduce ? 1 : 1 - Math.exp(-dt / .18));
      const sep = 3 + 11 * (1 - sm(shut)), joined = sm(Math.max(0, Math.min(1, (shut - .7) / .3)));
      m2.update(new THREE.Vector3(-sep, 0, 0), new THREE.Vector3(sep, 0, 0), I, I, joined);
      pivot.rotation.y = reduce ? -.25 : -.25 + .35 * Math.sin(t / 4200); pivot.rotation.x = .12;
      c2.position.set(0, 0, 96); c2.lookAt(0, 0, 0);
      r2.render(s2, c2);
    }
    requestAnimationFrame(loop2);
  })(0);
}
