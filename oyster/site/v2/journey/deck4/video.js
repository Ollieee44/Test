// The v4 journey as video: the page's autoplay drawn frame by frame on a controlled clock (so it is smooth however slow
// the machine), piped straight into ffmpeg. Two cuts from one pass: with the copy (as the web page shows it) and clean
// (animation and labels only, for a slide with its own text). Holds at each step long enough to read. No end card.
//   THREE=<three@0.160.0 package dir> CHROME=<chromium> NODE_PATH=<playwright-core> node video.js [fps]   (run harness.js first)
const { chromium } = require('playwright-core'); const fs = require('fs'), { spawn } = require('child_process');
const HERE = __dirname + '/', T = (process.env.THREE || '') + '/', FPS = +(process.argv[2] || 30), W = 1920, H = 1080;
const STOPS = [0, .25, .335, .45, .59, .665, .728, .79, .865, .92];
const SLOW = { 4: 1.3, 5: 2.6, 6: 2.2, 7: 1.9, 8: 1.8, 9: 2.6 };
const HOLD = [1800, 1800, 1500, 3200, 2200, 2000, 2800, 3000, 2000, 3500];   // reading time at each step (ms)
const easeInOut = t => -(Math.cos(Math.PI * t) - 1) / 2;
// p at time t (ms): hold at each stop, then the page's eased move to the next
const segs = []; let T0 = 0;
STOPS.forEach((s, i) => { segs.push({ t0: T0, t1: T0 + HOLD[i], a: s, b: s }); T0 += HOLD[i];
  if (i + 1 < STOPS.length) { const d = STOPS[i + 1] - s, dur = (SLOW[i + 1] || 1) * Math.max(1700, Math.min(3600, 1400 + d * 9000)); segs.push({ t0: T0, t1: T0 + dur, a: s, b: STOPS[i + 1], move: true }); T0 += dur; } });
const pAt = t => { const g = segs.find(g => t < g.t1) || segs[segs.length - 1]; return g.move ? g.a + (g.b - g.a) * easeInOut(Math.min(1, (t - g.t0) / (g.t1 - g.t0))) : g.a; };
const ff = file => spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '18',
  '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-r', String(FPS), file], { stdio: ['pipe', 'inherit', 'inherit'] });
const put = (proc, buf) => new Promise(r => proc.stdin.write(buf) ? r() : proc.stdin.once('drain', r));
(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROME || '/opt/pw-browsers/chromium-1243/chrome-linux64/chrome', args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: W, height: H } }); const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.addInitScript(() => { const real = performance.now.bind(performance); window.__vt = null; performance.now = () => window.__vt === null ? real() : window.__vt; });
  await p.route('https://cdn.jsdelivr.net/npm/three@0.160.0/**', r => r.fulfill({ path: T + r.request().url().split('three@0.160.0/')[1], contentType: 'application/javascript' }));
  await p.route('http://site/**', r => { const n = new URL(r.request().url()).pathname.slice(1); const f = n === 'site.css' ? HERE + '../../pages/site.css' : HERE + '.harness.html';
    r.fulfill({ path: f, contentType: f.endsWith('.css') ? 'text/css' : 'text/html' }); });
  await p.goto('http://site/index.html'); await p.waitForFunction(() => window.__X, null, { timeout: 90000 });
  await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(2500);
  await p.addStyleTag({ content: '#jctl,.rail,.hint,.skip,.end{visibility:hidden!important} .jl,.beat,.beat *{transition:none!important} body.clean .beat{visibility:hidden!important}' });
  const full = ff(HERE + 'selftac-journey-v4.mp4'), clean = ff(HERE + 'selftac-journey-v4-clean.mp4');
  const N = Math.round(T0 / 1000 * FPS); console.log('frames', N, 'seconds', (T0 / 1000).toFixed(1));
  for (let i = 0; i < N; i++) {
    const t = i * 1000 / FPS;
    await p.evaluate(([k, vt]) => { document.body.classList.remove('clean'); window.__vt = vt; window.__journey.frame(k); }, [pAt(t), 100000 + t]);
    await put(full, await p.screenshot({ type: 'jpeg', quality: 95 }));
    await p.evaluate(() => document.body.classList.add('clean'));
    await put(clean, await p.screenshot({ type: 'jpeg', quality: 95 }));
    if (i % 150 === 0) console.log('frame', i, '/', N);
  }
  full.stdin.end(); clean.stdin.end();
  await Promise.all([full, clean].map(pr => new Promise(r => pr.on('close', r))));
  console.log('done errors', errs); await b.close();
})();
