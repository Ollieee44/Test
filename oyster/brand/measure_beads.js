// Measures each mark's ink bounds in its 0-100 viewBox and writes beads_ink.json for build_beads.py.
// Run with Playwright: node measure_beads.js
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => { const b = await chromium.launch({ executablePath: process.env.CHROME || undefined });
  const p = await b.newPage();
  await p.goto('file://' + path.join(__dirname, 'beads.html')); await p.waitForTimeout(500);
  const r = await p.evaluate(() => { const out = {};
    for (const s of document.querySelectorAll('symbol')) {
      const ns = 'http://www.w3.org/2000/svg', svg = document.createElementNS(ns, 'svg');
      svg.setAttribute('viewBox', '0 0 100 100'); svg.setAttribute('width', 100); svg.setAttribute('height', 100);
      svg.style.position = 'absolute'; svg.style.left = '0'; svg.style.top = '0';
      svg.innerHTML = s.innerHTML; document.body.appendChild(svg);
      const base = svg.getScreenCTM().inverse(); let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
      svg.querySelectorAll('path, circle').forEach(el => {
        if (el.closest('mask')) return;
        const m = base.multiply(el.getScreenCTM()), L = el.getTotalLength();
        for (let i = 0; i <= 600; i++) { const q = el.getPointAtLength(L * i / 600), t = new DOMPoint(q.x, q.y).matrixTransform(m);
          x0 = Math.min(x0, t.x); y0 = Math.min(y0, t.y); x1 = Math.max(x1, t.x); y1 = Math.max(y1, t.y); } });
      out[s.id] = [x0, y0, x1, y1].map(v => +v.toFixed(2)); svg.remove(); }
    return out; });
  fs.writeFileSync(path.join(__dirname, 'beads_ink.json'), JSON.stringify(r, null, 1)); console.log(r); await b.close(); })();
