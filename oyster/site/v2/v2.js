
// ---------- v2: replay each move's little loop on hover ----------
document.querySelectorAll('.move').forEach(m => {
  const play = () => { m.classList.remove('play'); void m.offsetWidth; m.classList.add('play'); };
  new IntersectionObserver((es, o) => es.forEach(e => { if (e.isIntersecting) { play(); o.disconnect(); } }), { rootMargin: '0px 0px -15% 0px' }).observe(m);
  m.addEventListener('mouseenter', play);
});

// ---------- v2: if the 3D story's script could not run, say so instead of leaving the loading mark up ----------
const stageEl = document.getElementById('stage');
if (stageEl) addEventListener('load', () => {
  if (window.__story) return;
  stageEl.classList.add('ready');
  const d = document.createElement('div'); d.className = 'nogl';
  d.textContent = 'The 3D story could not load. Reload the page to try again, or skip the story.';
  stageEl.appendChild(d);
}, { once: true });
