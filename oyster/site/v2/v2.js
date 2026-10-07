
// ---------- v2: replay each move's little loop on hover ----------
document.querySelectorAll('.move').forEach(m => {
  const play = () => { m.classList.remove('play'); void m.offsetWidth; m.classList.add('play'); };
  new IntersectionObserver((es, o) => es.forEach(e => { if (e.isIntersecting) { play(); o.disconnect(); } }), { rootMargin: '0px 0px -15% 0px' }).observe(m);
  m.addEventListener('mouseenter', play);
});
