// The three card illustrations (assets/card-*.png) in the new site's style: pale blue and pink brackets with a
// yellow join, on a speckled sage band. NODE_PATH=<dir with playwright-core> CHROME=<chromium> node make_icons.js
const { chromium } = require('playwright-core'); const fs = require('fs');
const W = 1080, H = 600;
let seed = 9; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
function band(cx, cy, ang, len, wid, n) {   // a diagonal band of speckle
  let s = ''; const c = Math.cos(ang), sn = Math.sin(ang);
  const cols = ['#FFFFFF', '#CFFFFF', '#96FF87', '#F7D16B', '#FFB36B', '#F0A6CA', '#CEE5F3'];
  for (let i = 0; i < n; i++) { const u = (rnd() - .5) * len, v = (rnd() + rnd() + rnd() - 1.5) * wid;
    s += `<circle cx="${(cx + u * c - v * sn).toFixed(1)}" cy="${(cy + u * sn + v * c).toFixed(1)}" r="${(1 + rnd() * 2.2).toFixed(1)}" fill="${cols[Math.floor(rnd() ** 1.6 * cols.length)]}" fill-opacity="${(.35 + rnd() * .6).toFixed(2)}"/>`; }
  return s;
}
const BL = '#CEE5F3', PK = '#F0A6CA', YL = '#F7D16B';
const blue = (x, y, s = 1) => `<path d="M ${x} ${y - 95 * s} L ${x} ${y - 30 * s} Q ${x} ${y} ${x - 30 * s} ${y} L ${x - 120 * s} ${y}" fill="none" stroke="${BL}" stroke-width="${26 * s}" stroke-linecap="round" stroke-linejoin="round"/>`;
const pink = (x, y, s = 1) => `<path d="M ${x} ${y + 95 * s} L ${x} ${y + 30 * s} Q ${x} ${y} ${x + 30 * s} ${y} L ${x + 120 * s} ${y}" fill="none" stroke="${PK}" stroke-width="${26 * s}" stroke-linecap="round" stroke-linejoin="round"/>`;
const dash = (x1, y1, x2, y2) => `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#FFFFFF" stroke-width="6" stroke-dasharray="4 14" stroke-linecap="round"/>`;
const lab = (x, y, t) => `<text x="${x}" y="${y}" fill="#E9EFED" style="font: 500 30px Consolas, 'DejaVu Sans Mono', monospace; letter-spacing: 3px">${t}</text>`;
const CARDS = {
  separate: () => band(540, 300, -.42, 1400, 70, 2600) + blue(450, 185) + pink(560, 395),
  assemble: () => band(540, 300, -.42, 1400, 90, 3000) + dash(450, 195, 560, 385) + `<circle cx="505" cy="292" r="30" fill="${YL}"/>` + blue(430, 195) + pink(580, 385),
  degrade: () => band(560, 380, -.3, 1400, 110, 3200)
    + `<path d="M 330 175 Q 330 75 450 70 L 452 70 Q 470 145 420 175 Z" fill="${BL}"/>` + blue(450, 210) + `<line x1="400" y1="210" x2="400" y2="440" stroke="#FFFFFF" stroke-opacity=".7" stroke-width="3"/>`
    + dash(450, 215, 580, 330) + `<circle cx="515" cy="272" r="30" fill="${YL}"/>`
    + pink(590, 350) + `<rect x="625" y="385" width="100" height="100" rx="22" fill="${PK}"/>`
    + `<circle cx="760" cy="335" r="18" fill="${PK}"/><circle cx="800" cy="300" r="15" fill="${PK}"/><circle cx="836" cy="270" r="13" fill="${PK}"/>`
    + `<line x1="672" y1="385" x2="672" y2="200" stroke="#FFFFFF" stroke-opacity=".7" stroke-width="3"/>` + lab(615, 190, 'TARGET') + lab(270, 470, 'E3 LIGASE'),
};
(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROME || '/opt/pw-browsers/chromium-1243/chrome-linux64/chrome' });
  const p = await b.newPage({ viewport: { width: W, height: H } });
  for (const [n, f] of Object.entries(CARDS)) {
    seed = 9;
    await p.setContent(`<body style="margin:0"><svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}"><rect width="${W}" height="${H}" fill="#3A715E"/>${f()}</svg></body>`);
    await p.screenshot({ path: __dirname + '/assets/card-' + n + '.png' }); console.log('card', n);
  }
  await b.close();
})();
