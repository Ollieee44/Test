// Prints print.html to selftac-pearl-heroes.pdf (A3 landscape, vector type, the renders at full resolution).
//   NODE_PATH=<dir with playwright-core> node print_pearl_pdf.js
const { chromium } = require('playwright-core'); const path = require('path');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 1587, height: 1123 } });
  await p.goto('file://' + path.join(__dirname, 'print.html'), { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready); await p.emulateMedia({ media: 'print' });
  await p.evaluate(() => document.querySelectorAll('.frame').forEach(f => f.style.setProperty('--s', (f.clientWidth / 1440).toFixed(5))));
  await p.waitForTimeout(800);
  await p.pdf({ path: path.join(__dirname, 'selftac-pearl-heroes.pdf'), width: '420mm', height: '297mm', printBackground: true, preferCSSPageSize: true });
  await b.close(); console.log('selftac-pearl-heroes.pdf');
})();
