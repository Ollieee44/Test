"""The handoff package for v4 (click6): everything a web developer needs to put the SELFTAC journey on a Webflow site
(or anywhere else). Writes export/selftac-journey-v4/:
  1-hosted-page/        the production page (no in-page editor; a small bridge for the host page) + site.css; the 3D
                        library and fonts come from public CDNs (jsDelivr, Google Fonts)
  2-self-contained/     the same page with no third-party requests: three.js and the fonts bundled beside it
  3-webflow-snippets/   paste-in embeds: full screen, fixed height, a button that opens it in an overlay, step events
  4-stills/             (filled by tools/export_stills.js) a poster and every step, desktop and phone
  5-video/              (filled by tools/export_stills.js) crossfade slideshows of the stills
  README.md             copied from tools/export_README.md: every option, hosting, text, accessibility, credits
Usage: python export_package.py <three package dir> <fonts node_modules dir>
       then node tools/export_stills.js (it serves the folder itself; needs playwright-core and ffmpeg)
4-stills/ and 5-video/ are kept across rebuilds; delete them to force fresh ones."""
import json, os, re, shutil, sys
D = os.path.dirname(os.path.abspath(__file__)) + '/../'
THREE, FONTS = sys.argv[1:3]
OUT = D + 'export/selftac-journey-v4/'
for d in ('1-hosted-page', '2-self-contained', '3-webflow-snippets'): shutil.rmtree(OUT + d, ignore_errors=True)
for d in ('1-hosted-page', '2-self-contained/vendor/three/build', '2-self-contained/vendor/three/examples/jsm/geometries',
          '2-self-contained/vendor/three/examples/jsm/math', '2-self-contained/fonts', '3-webflow-snippets', '4-stills', '5-video'):
    os.makedirs(OUT + d, exist_ok=True)

page = open(D + 'click6/index.html', encoding='utf8').read()
editor = open(D + 'editor.js', encoding='utf8').read()
assert page.count(editor) == 1

# the host bridge: tells a parent page which step is showing; takes next / back / play / goto from it; ?step=N starts there
BRIDGE = r"""
// ---------- host bridge (for a page that embeds this one in an iframe) ----------
// Sends {source: 'selftac-journey', type: 'ready' | 'step', step, total} to the parent page as the step changes, and
// takes {source: 'selftac-journey-host', command: 'next' | 'back' | 'play' | 'goto', step} from it. ?step=N in the
// address opens at step N.
{
  const count = document.getElementById('jcount'), next = document.getElementById('jnext'), back = document.getElementById('jback'), play = document.getElementById('jplay');
  const state = () => { const [a, b] = (count.textContent || '1 / 1').split('/').map(s => parseInt(s, 10)); return { step: a || 1, total: b || 1 }; };
  const send = (type, extra = {}) => { if (window.parent !== window) window.parent.postMessage({ source: 'selftac-journey', type, ...state(), ...extra }, '*'); };
  const goto = n => { const s = state().step; if (s < n) { next.click(); setTimeout(() => goto(n), 70); } else if (s > n) { back.click(); setTimeout(() => goto(n), 70); } };
  let last = count.textContent;
  new MutationObserver(() => { if (count.textContent !== last) { last = count.textContent; send('step'); } }).observe(count, { childList: true, characterData: true, subtree: true });
  window.addEventListener('message', e => { const d = e.data; if (!d || d.source !== 'selftac-journey-host') return;
    if (d.command === 'next') next.click(); else if (d.command === 'back') back.click(); else if (d.command === 'play') play.click();
    else if (d.command === 'goto' && d.step) goto(+d.step); });
  const q = +new URLSearchParams(location.search).get('step'); if (q > 1) setTimeout(() => goto(q), 600);
  send('ready');
}
"""
prod = page.replace(editor, BRIDGE)
prod = prod.replace("<title>SELFTAC Journey Rob's Edits v4</title>", '<title>How a SELFTAC® degrader works · Oyster Therapeutics</title>', 1)
assert '<title>How a SELFTAC® degrader works' in prod
open(OUT + '1-hosted-page/index.html', 'w', encoding='utf8').write(prod)
shutil.copy(D + '../pages/site.css', OUT + '1-hosted-page/site.css')

# self-contained: the CDN URLs pointed at local copies
sc = prod.replace('https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js', './vendor/three/build/three.module.js')
sc = sc.replace('https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/', './vendor/three/examples/jsm/')
sc = re.sub(r'<link rel="preconnect" href="https://(fonts\.googleapis\.com|fonts\.gstatic\.com|cdn\.jsdelivr\.net)"[^>]*>\n?', '', sc)
sc = re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/css2\?[^"]*">', '<link rel="stylesheet" href="./fonts/fonts.css">', sc)
assert 'https://' not in re.sub(r'https://(www\.w3\.org|oyster-tx\.com)[^"\'\s)]*', '', sc.split('<script type="application/json"')[0]), 'a third-party URL is left in the head'
open(OUT + '2-self-contained/index.html', 'w', encoding='utf8').write(sc)
shutil.copy(D + '../pages/site.css', OUT + '2-self-contained/site.css')
for f in ('build/three.module.js', 'examples/jsm/geometries/RoundedBoxGeometry.js', 'examples/jsm/math/MeshSurfaceSampler.js', 'LICENSE'):
    shutil.copy(THREE + '/' + f, OUT + '2-self-contained/vendor/three/' + f)
FF = [('Geist', '@fontsource/geist-sans/files/geist-sans-latin-{w}-normal.woff2', (400, 500, 600)),
      ('Geist Mono', '@fontsource/geist-mono/files/geist-mono-latin-{w}-normal.woff2', (400, 500)),
      ('Monomaniac One', '@fontsource/monomaniac-one/files/monomaniac-one-latin-{w}-normal.woff2', (400,))]
css = ['/* The page\'s fonts, served locally (all SIL Open Font License 1.1; see LICENSES.txt). Latin subset. */']
for fam, pat, ws in FF:
    for w in ws:
        src = pat.format(w=w); name = os.path.basename(src); shutil.copy(FONTS + '/' + src, OUT + '2-self-contained/fonts/' + name)
        css.append(f"@font-face {{ font-family: '{fam}'; font-style: normal; font-weight: {w}; font-display: swap; src: url('./{name}') format('woff2'); }}")
shutil.copy(FONTS + '/@fontsource-variable/newsreader/files/newsreader-latin-opsz-normal.woff2', OUT + '2-self-contained/fonts/newsreader-latin-opsz-normal.woff2')
css.append("@font-face { font-family: 'Newsreader'; font-style: normal; font-weight: 200 800; font-display: swap; src: url('./newsreader-latin-opsz-normal.woff2') format('woff2-variations'); }")
open(OUT + '2-self-contained/fonts/fonts.css', 'w').write('\n'.join(css) + '\n')
open(OUT + '2-self-contained/LICENSES.txt', 'w').write('''Third-party parts of this folder
three.js r160 (vendor/three) - MIT License, see vendor/three/LICENSE. https://threejs.org
Geist, Geist Mono (Vercel), Monomaniac One, Newsreader (Production Type) - SIL Open Font License 1.1, via Fontsource
  https://fontsource.org - https://openfontlicense.org
Protein structures drawn from PDB 5T35 (Gadd et al., Nat. Chem. Biol. 2017) and 1UBQ (Vijay-Kumar et al., J. Mol. Biol.
  1987), via the RCSB Protein Data Bank (data CC0). The proteasome is a stand-in shape from PDB 6MSB (Dong et al., Nature
  2019). The SELFTAC degrader is drawn generically: its two halves are invented ring systems, not a real molecule.
''')

# the Webflow snippets
SN = {
'A-full-screen.html': '''<!-- SELFTAC journey: full-screen section. Paste into a Webflow Embed element placed in a section set to 100vh
     (or 100svh), full width, no padding. Replace the src with where you host 1-hosted-page or 2-self-contained. -->
<div style="position:relative;width:100%;height:100vh;height:100svh;overflow:hidden;background:#1A372A">
  <iframe src="https://YOUR-HOST/selftac-journey/" title="How a SELFTAC® degrader works"
    style="position:absolute;inset:0;width:100%;height:100%;border:0;display:block"
    loading="lazy" allow="fullscreen" allowfullscreen></iframe>
</div>
''',
'B-fixed-height.html': '''<!-- SELFTAC journey: a fixed-height panel inside a page (desktop 720px, phones 640px). The page lays itself out for any
     size: wide screens put the copy on the left; narrow ones put it on a card below the animation. -->
<style>
  .selftac-embed { position: relative; width: 100%; height: 720px; border-radius: 16px; overflow: hidden; background: #1A372A; }
  @media (max-width: 760px) { .selftac-embed { height: 640px; border-radius: 0; } }
  .selftac-embed iframe { position: absolute; inset: 0; width: 100%; height: 100%; border: 0; display: block; }
</style>
<div class="selftac-embed">
  <iframe src="https://YOUR-HOST/selftac-journey/" title="How a SELFTAC® degrader works" loading="lazy" allow="fullscreen" allowfullscreen></iframe>
</div>
''',
'C-button-opens-overlay.html': '''<!-- SELFTAC journey: a button that opens it full screen over the page, closed with the X or Escape. Nothing loads until
     the button is pressed. Style the button to match the site; keep the class names. -->
<button type="button" class="selftac-open">See how SELFTAC® works</button>
<div class="selftac-overlay" role="dialog" aria-modal="true" aria-label="How a SELFTAC® degrader works" hidden>
  <button type="button" class="selftac-close" aria-label="Close">&times;</button>
</div>
<style>
  .selftac-overlay { position: fixed; inset: 0; z-index: 9999; background: #1A372A; }
  .selftac-overlay[hidden] { display: none; }
  .selftac-overlay iframe { position: absolute; inset: 0; width: 100%; height: 100%; border: 0; }
  .selftac-close { position: absolute; top: 14px; right: 14px; z-index: 2; width: 44px; height: 44px; border-radius: 22px; border: 0;
    background: rgba(255,255,255,.16); color: #fff; font: 28px/44px sans-serif; cursor: pointer; }
  .selftac-close:focus-visible { outline: 2px solid #DCA84E; outline-offset: 2px; }
</style>
<script>
(() => {
  const SRC = 'https://YOUR-HOST/selftac-journey/';
  const open = document.querySelector('.selftac-open'), ov = document.querySelector('.selftac-overlay'), close = ov.querySelector('.selftac-close');
  let last = null;
  const show = () => { last = document.activeElement; if (!ov.querySelector('iframe')) { const f = document.createElement('iframe');
      f.src = SRC; f.title = 'How a SELFTAC® degrader works'; f.allow = 'fullscreen'; ov.appendChild(f); }
    ov.hidden = false; document.documentElement.style.overflow = 'hidden'; close.focus(); };
  const hide = () => { ov.hidden = true; document.documentElement.style.overflow = ''; if (last) last.focus(); };
  open.addEventListener('click', show); close.addEventListener('click', hide);
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && !ov.hidden) hide(); });
})();
</script>
''',
'D-step-events-and-controls.html': '''<!-- SELFTAC journey: listening to it and driving it from the host page (optional; works with A, B or C).
     The embedded page tells the host which step is showing ({source:'selftac-journey', type:'ready'|'step', step, total})
     and takes commands ({source:'selftac-journey-host', command:'next'|'back'|'play'|'goto', step}). Use it for analytics
     or for the site's own buttons. Give the iframe id="selftac-frame". -->
<script>
(() => {
  const ORIGIN = 'https://YOUR-HOST';   // where the journey is hosted: only its messages are trusted
  window.addEventListener('message', e => {
    if (e.origin !== ORIGIN || !e.data || e.data.source !== 'selftac-journey') return;
    const { type, step, total } = e.data;
    // e.g. analytics: one event per step reached
    if (type === 'step') { window.dataLayer = window.dataLayer || []; window.dataLayer.push({ event: 'selftac_step', step, total }); }
  });
  // e.g. the site's own "next" button: document.querySelector('.my-next').onclick = () => send('next');
  window.selftacSend = (command, step) => document.getElementById('selftac-frame')
    .contentWindow.postMessage({ source: 'selftac-journey-host', command, step }, ORIGIN);
})();
</script>
<!-- Deep link: https://YOUR-HOST/selftac-journey/?step=7 opens at step 7. -->
''',
}
for n, t in SN.items(): open(OUT + '3-webflow-snippets/' + n, 'w').write(t)
shutil.copy(D + 'tools/export_README.md', OUT + 'README.md')
json.dump({'built_from': 'oyster/site/v2/journey/click6/index.html', 'steps': 11}, open(OUT + 'package.json', 'w'), indent=1)
print('wrote', OUT)
for root, _, files in os.walk(OUT):
    for f in files: p = os.path.join(root, f); print(f'  {os.path.relpath(p, OUT)}  {os.path.getsize(p) // 1024} KB')
