// ---------- pages: palette (kept from page to page), header, menu, reveals, copy button ----------
const root = document.documentElement, reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const storyEl = document.getElementById('story'), head = document.getElementById('head'), skip = document.getElementById('skip');
const menuBtn = document.querySelector('.menu-btn'), themeMeta = document.querySelector('meta[name="theme-color"]');
const palBtns = [...document.querySelectorAll('.pal button')], paln = document.getElementById('paln');
const PAL_KEY = 'oyster-palette';
root.lang = 'en';

// every page opens at its top (or at the #section its link names): the browser, and the viewer around
// an artifact, would otherwise keep the scroll position of the page you came from
try { history.scrollRestoration = 'manual'; } catch (e) {}
const toStart = () => {
  const target = location.hash.length > 1 && document.getElementById(location.hash.slice(1));
  if (target) target.scrollIntoView({ behavior: 'instant' }); else scrollTo({ top: 0, left: 0, behavior: 'instant' });
};
// (once more when everything has loaded, unless you have started scrolling yourself by then)
let userMoved = false;
['wheel', 'touchstart', 'keydown', 'pointerdown'].forEach(t => addEventListener(t, () => { userMoved = true; }, { once: true, passive: true }));
toStart(); requestAnimationFrame(toStart); addEventListener('load', () => { if (!userMoved) toStart(); }, { once: true });
addEventListener('pageshow', e => { if (e.persisted) toStart(); });

// the palette shows in the switch, the browser chrome and the address bar, and rides along on every
// link to another page (and in storage) so the next page opens in the same one
function showPal(k) {
  root.setAttribute('data-palette', k);
  palBtns.forEach(b => b.setAttribute('aria-pressed', String(b.dataset.pal === k)));
  if (paln) paln.textContent = NAMES[k] || '';
  if (themeMeta) themeMeta.content = getComputedStyle(root).getPropertyValue('--paper').trim();
  try { localStorage.setItem(PAL_KEY, k); } catch (e) {}
  try { history.replaceState(null, '', '?palette=' + k + location.hash); } catch (e) {}
  document.querySelectorAll('a[href]').forEach(a => {
    const m = a.getAttribute('href').match(/^([a-z]+\.html)(?:\?[^#]*)?(#.*)?$/);
    if (m) a.setAttribute('href', m[1] + '?palette=' + k + (m[2] || ''));
  });
}
palBtns.forEach(b => b.addEventListener('click', () => { showPal(b.dataset.pal); bgWall.refresh(); }));

// header: see-through over the story (or at the very top of a page), solid once you scroll on
let scrollQueued = false;
function onScroll() {
  if (scrollQueued) return; scrollQueued = true;
  requestAnimationFrame(() => {
    scrollQueued = false;
    let past = scrollY > 8;
    if (storyEl) {
      const sr = storyEl.getBoundingClientRect(); past = sr.bottom < innerHeight * .6;
      if (skip) skip.classList.toggle('gone', -sr.top / Math.max(1, sr.height - innerHeight) > .92);   // the skip control stays until the story reaches its end card
    }
    head.classList.toggle('solid', past || head.classList.contains('open'));
  });
}
addEventListener('scroll', onScroll, { passive: true }); addEventListener('resize', onScroll);

// phones: the page links fold into a menu
function setMenu(open) { head.classList.toggle('open', open); menuBtn.setAttribute('aria-expanded', String(open)); onScroll(); }
if (menuBtn) {
  menuBtn.addEventListener('click', () => setMenu(!head.classList.contains('open')));
  addEventListener('keydown', e => { if (e.key === 'Escape' && head.classList.contains('open')) { setMenu(false); menuBtn.focus(); } });
  matchMedia('(min-width: 901px)').addEventListener('change', e => { if (e.matches) setMenu(false); });
}

const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { rootMargin: '0px 0px -10% 0px' });
document.querySelectorAll('.rv').forEach(el => io.observe(el));
document.querySelectorAll('.copy-btn').forEach(b => b.addEventListener('click', async () => {
  const status = document.getElementById('copyStatus');
  try { await navigator.clipboard.writeText(b.dataset.copy); b.textContent = 'Copied'; if (status) status.textContent = 'Email address copied'; }
  catch (e) { b.textContent = 'Select and copy'; if (status) status.textContent = 'Copying failed: select the address and copy it'; }
  setTimeout(() => { b.textContent = 'Copy'; if (status) status.textContent = ''; }, 1800);
}));
