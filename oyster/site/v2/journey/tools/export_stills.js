// Fills export/selftac-journey-v4/4-stills (poster + every step, desktop 1920x1080 and phone 390x844 @2x, as JPG) and
// 5-video (crossfade slideshows of those stills). Run after export_package.py:  node tools/export_stills.js
// Needs playwright-core (CHROME=<chromium path> if it isn't the default), Python with Pillow, and ffmpeg.
const { chromium } = require('playwright-core'), http = require('http'), fs = require('fs'), path = require('path'), { execSync } = require('child_process');
const OUT = path.join(__dirname, '../export/selftac-journey-v4/'), PORT = 8765;
const TYPES = { '.html': 'text/html', '.js': 'application/javascript', '.css': 'text/css', '.woff2': 'font/woff2' };
const server = http.createServer((q, r) => { let f = path.join(OUT, decodeURIComponent(q.url.split('?')[0])); if (f.endsWith('/')) f += 'index.html';
  fs.readFile(f, (e, b) => { if (e) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream' }); r.end(b); }); });
(async () => {
  await new Promise(ok => server.listen(PORT, ok));
  const b = await chromium.launch({ executablePath: process.env.CHROME || undefined, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  for (const [name, vp, dsf] of [['desktop', { width: 1920, height: 1080 }, 1], ['phone', { width: 390, height: 844 }, 2]]) {
    const p = await b.newPage({ viewport: vp, deviceScaleFactor: dsf });
    await p.goto(`http://127.0.0.1:${PORT}/2-self-contained/`); await p.waitForFunction(() => window.__journey, null, { timeout: 90000 });
    await p.addStyleTag({ content: '#jctl{visibility:hidden!important}' }); await p.waitForTimeout(4000);
    const total = +(await p.textContent('#jcount')).split('/')[1];
    for (let i = 1; i <= total; i++) {
      if (i > 1) { await p.evaluate(() => document.getElementById('jnext').click()); await p.waitForTimeout(9000); }
      const f = `${OUT}4-stills/${name}-step-${String(i).padStart(2, '0')}.png`; await p.screenshot({ path: f });
      if (i === 1) fs.copyFileSync(f, `${OUT}4-stills/${name}-poster.png`);
      console.log(name, i, '/', total);
    }
    await p.close();
  }
  await b.close(); server.close();
  execSync(`python3 -c "from PIL import Image;import glob,os\nfor f in glob.glob('${OUT}4-stills/*.png'): Image.open(f).convert('RGB').save(f[:-4]+'.jpg',quality=88,optimize=True,progressive=True); os.remove(f)"`);
  for (const name of ['desktop', 'phone']) {
    const ins = [], fl = []; let prev = '0:v';
    for (let i = 1; i <= 11; i++) ins.push(`-loop 1 -t 4 -i ${OUT}4-stills/${name}-step-${String(i).padStart(2, '0')}.jpg`);
    for (let k = 1; k <= 10; k++) { fl.push(`[${prev}][${k}:v]xfade=transition=fade:duration=1:offset=${k * 3}[v${k}]`); prev = 'v' + k; }
    execSync(`ffmpeg -y -loglevel error ${ins.join(' ')} -filter_complex "${fl.join(';')}" -map "[v10]" -c:v libx264 -pix_fmt yuv420p -crf 23 -preset slow -movflags +faststart ${OUT}5-video/selftac-journey-slideshow-${name}.mp4`);
  }
  console.log('done');
})();
