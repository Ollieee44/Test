"""Build Website v2 (v2/pages/): the multi-page site (../build_pages.py) taken further.

- The new fan mark (11.7 in the Mark Catalogue) is the 'o' of every logotype, and appears on its own as the
  stage's loading mark, the divider between bands, the corner of every card on hover, the footer and the favicon.
- The 3D story is longer (1650vh, 1300vh on phones) and glides more (a longer smoothing time). It compiles every
  shader before the first frame, redraws only when something moved, and opens on the fan mark until the first
  frame is ready, so the Science page no longer stutters as it loads.
- Every page has more to read: the three moves and the figures on Home, a comparison and the terms on Science,
  the areas and stage key on Pipeline, joining on Team, the backers and milestones on Investors, ways to get in
  touch on Contact.
- Everything you can press moves on hover (v2.css), and nothing moves under prefers-reduced-motion.

Run ../build_site.py and ../build_palettes.py first. v1 (../pages/) is left as it is."""
import json, os, re, sys, urllib.parse
D = os.path.dirname(os.path.abspath(__file__)) + '/'
S = D + '../'
sys.path.insert(0, S + '../brand')
import linepearl
OUT = D + 'pages/'
os.makedirs(OUT, exist_ok=True)
src = open(S + 'palettes.html').read()

def between(s, a, b):
    i = s.index(a); return s[i + len(a):s.index(b, i + len(a))]
def once(s, old, new):
    assert old in s, old[:70]
    return s.replace(old, new, 1)

# ---------- the fan mark ----------
NAME = 'io-s-rim35'                     # 11.7: the line fan and 80% pearl inside out, rim 3.5
MARK_RE = re.compile(r'<g transform="translate\(-17\.1 -583\.4\) scale\(6\.3571\)"><g transform="translate\(-1\.5 1\.5\)">.*?</g></g>', re.S)
n_ids = [0]
def uid():
    n_ids[0] += 1; return f'fan{n_ids[0]}-'
def mark_parts(ns):
    masks, sym = linepearl.build(ns)
    return masks[NAME], sym[NAME].replace('style="fill:var(--p1)"', 'class="pearl" style="fill:var(--pearl)"')
def fanify(h):
    """Every old mark in the page becomes the fan mark, each with its own mask ids."""
    def swap(m):
        mask, body = mark_parts(uid())
        return f'<g transform="translate(-17.1 -583.4) scale(6.3571)"><defs>{mask}</defs><g transform="translate(-1.5 1.5)">{body}</g></g>'
    return MARK_RE.sub(swap, h)
def fm(cls='fm'):
    mask, body = mark_parts(uid())
    return f'<svg class="{cls}" viewBox="8 9.5 84 84" aria-hidden="true" fill="currentColor"><defs>{mask}</defs><g transform="translate(-1.5 1.5)">{body}</g></svg>'
def svg(name, cls, mid):
    s = open(S + '../brand/' + name).read()
    s = s.replace('x-mInside', mid).replace('fill="#2B2230"', 'fill="currentColor"').replace('fill="#C99BB0"', 'style="fill:var(--pearl)"')
    return fanify(s.replace('<svg ', f'<svg class="{cls}" translate="no" role="img" aria-label="Oyster Therapeutics" ', 1))
ICON = 'data:image/svg+xml,' + urllib.parse.quote(fm('').replace('class="" ', 'xmlns="http://www.w3.org/2000/svg" ').replace(' aria-hidden="true"', '')
                                                  .replace('fill="currentColor"', 'fill="#2B2230"').replace('fill:var(--pearl)', 'fill:#C99BB0'))
CG = '<svg class="cg" viewBox="0 0 30 12" aria-hidden="true"><line x1="6" y1="6" x2="24" y2="6"/><circle cx="6" cy="6" r="4.6"/><circle cx="24" cy="6" r="4.6"/></svg>'
ARROW = '<span class="arr"><svg viewBox="0 0 14 14" aria-hidden="true"><path d="M2 7h10M8 3l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></span>'
DOWN = '<svg viewBox="0 0 14 14" aria-hidden="true"><path d="M2 7h10M8 3l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
TM = lambda s: re.sub(r'(?<!<span translate="no">)SELFTAC&reg;', '<span translate="no">SELFTAC&reg;</span>', s)
RULE = lambda: f'<div class="markrule" aria-hidden="true">{fm()}</div>\n'
def eyebrow(t): return f'<p class="eyebrow rv">{CG}{t}</p>'

# ---------- shared stylesheet and script ----------
css = between(src, '<style>', '</style>') + '\n' + open(S + 'multipage.css').read() + '\n' + open(D + 'v2.css').read()
open(OUT + 'site.css', 'w').write(css.strip() + '\n')
module = between(src, '<script type="module">', '</script>')
names = between(module, 'const NAMES = ', ', paln =')
walls = re.search(r'var WALLS = .*?;\n', module).group(0)
wall = open(S + 'wallpaper.js').read()
wall = once(wall, "function readCol() { var tide = root.getAttribute('data-palette') === 'tidepool'; return tide ? { a: hexToRgb('#F2B84B'), b: hexToRgb('#7FC4B0'), ink: hexToRgb('#EAF3EF') } : { a: hexToRgb('#C99BB0'), b: hexToRgb('#B8A7C9'), ink: hexToRgb('#2B2230') }; }",
            walls + "  function readCol() { var w = WALLS[root.getAttribute('data-palette')] || WALLS.nacre; return { a: hexToRgb(w.a), b: hexToRgb(w.b), ink: hexToRgb(w.ink) }; }")
wall = once(wall, 'ended = storyEl.getBoundingClientRect().bottom < innerHeight * .5;', 'ended = !storyEl || storyEl.getBoundingClientRect().bottom < innerHeight * .5;')
wall = once(wall, "\ndocument.querySelectorAll('.pal button').forEach(b => b.addEventListener('click', () => bgWall.refresh()));", '')
js = ('const NAMES = ' + names + ';\n' + open(S + 'multipage.js').read() + open(D + 'v2.js').read() + '\n' + wall + '''
// open in the palette from the link, else the one used last, else Nacre (a click, so the 3D story follows too)
(() => {
  let k = new URLSearchParams(location.search).get('palette');
  if (!NAMES[k]) { try { k = localStorage.getItem(PAL_KEY); } catch (e) { k = null; } }
  if (!NAMES[k]) k = 'nacre';
  const b = palBtns.find(x => x.dataset.pal === k); if (b) b.click(); else showPal(k);
  onScroll();
})();
''')
open(OUT + 'site.js', 'w').write(js)

# ---------- page frame ----------
PAGES = [('science', 'Science', 'How a SELFTAC&reg; molecule splits, crosses the blood-brain barrier and clasps back together inside the neuron.'),
         ('pipeline', 'Pipeline', 'Drug discovery in oncology and diseases of the central nervous system.'),
         ('team', 'Team', 'The leadership and the Board of Directors.'),
         ('investors', 'Investors', '&pound;25m Series A, led by Syncona alongside Oxford Science Enterprises.'),
         ('news', 'News', 'Appointments and financing.'),
         ('contact', 'Contact', 'Partnerships, investors and careers.')]
paldots = re.search(r'<div class="pal dots".*?</div>(?=</header>)', src, re.S).group(0)
MENU = '<button type="button" class="menu-btn" aria-expanded="false" aria-controls="nav" aria-label="Menu"><span></span><span></span></button>'
def header(cur):
    nav = ''.join(f'<a href="{s}.html"' + (' aria-current="page"' if s == cur else '') + f'>{n}</a>' for s, n, _ in PAGES)
    return (f'<header class="head" id="head"><a class="home" href="index.html" aria-label="Oyster Therapeutics, home">{svg("oyster-wordmark-nacre.svg", "wm", "wmMask")}</a>'
            f'<nav id="nav" aria-label="Main">{nav}</nav>{paldots}{MENU}</header>\n')
def strand(cur):
    dots = ''.join(f'<li><a href="{s}.html"' + (' aria-current="page"' if s == cur else '') + f'><span>{n}</span></a></li>' for s, n, _ in PAGES)
    slugs = [s for s, _, _ in PAGES]
    nxt = PAGES[(slugs.index(cur) + 1) % len(PAGES)]
    return (f'<nav class="next band" aria-label="Pages"><div class="wrap"><ol class="strandnav">{dots}</ol>'
            f'<a class="nextlink" href="{nxt[0]}.html"><span><small>Next</small><b>{nxt[1]}</b></span>{ARROW}</a></div></nav>\n')
credit = re.search(r'<p class="credit">.*?</p>', open(S + 'sections.html').read(), re.S).group(0)
def footer():
    return (f'<footer class="foot"><div class="wrap"><div class="foot-top">'
            f'<a class="foot-home" href="index.html" aria-label="Oyster Therapeutics, home">{svg("oyster-logotype-nacre.svg", "lt2", "lt2Mask")}</a>'
            '<ul>' + ''.join(f'<li><a href="{s}.html">{n}</a></li>' for s, n, _ in PAGES) + '</ul>'
            '<ul><li><a href="mailto:info@oystertx.com">info@oystertx.com</a></li><li><a href="https://uk.linkedin.com/company/kesmalea-therapeutics" target="_blank" rel="noopener">LinkedIn</a></li>'
            '<li><p>London, United Kingdom</p></li></ul></div>'
            f'{credit}<p class="legal">&copy; 2026 Oyster Therapeutics. Formerly Kesmalea Therapeutics.</p>'
            f'<p class="foot-mark">{fm()}<span>Oral, brain-penetrant protein degraders</span></p></div></footer>\n')
HEAD = '''<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="icon" href="{icon}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>{extra}
<meta name="theme-color" content="#EFE6E1">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=swap">
<link rel="stylesheet" href="site.css">
'''
def page(slug, title, desc, main, after='', skipto='#main', extra='', with_strand=True):
    h = HEAD.format(title=title, icon=ICON, desc=re.sub('<[^>]+>|&[a-z]+;', lambda m: {'&reg;': '®', '&pound;': '£'}.get(m.group(0), ''), desc), extra=extra)
    h += ('<canvas id="bgArt" aria-hidden="true"></canvas>\n'
          f'<a class="sr-only" href="{skipto}">Skip to content</a>\n' + header(slug) + '<main id="main">\n' + main
          + (RULE() + strand(slug) if with_strand else '') + '</main>\n' + footer() + after + '<script type="module" src="site.js"></script>\n')
    h = TM(fanify(h))
    open(OUT + slug + '.html', 'w').write(h)

sec = open(S + 'sections.html').read().replace('<!--CG-->', CG).replace('<!--ARROW-->', ARROW)
def block(sid):
    return re.search(r'<(section|footer) class="[^"]*" id="' + sid + r'">.*?</\1>', sec, re.S).group(0)
def as_page(b):
    b = re.sub(r'class="([^"]*)band"', r'class="\1band phero"', b, count=1)
    return re.sub(r'<h2 class="(say|sr-only)([^"]*)">(.*?)</h2>', r'<h1 class="\1\2">\3</h1>', b, count=1, flags=re.S)
def band(sid, inner, cls=''):
    return f'<section class="band {cls}" id="{sid}"><div class="wrap">{inner}</div></section>\n'
def card(k, title, body, cls='', more=''):
    return f'<article class="card rv {cls}">{fm()}<span class="k">{k}</span><h3>{title}</h3>{body}{more}</article>'

# ---------- home ----------
# three moves, each a small picture that plays once in view and again on hover
PIC_SPLIT = ('<svg class="pic" viewBox="0 0 320 180" aria-hidden="true"><g class="l"><rect class="ha" x="70" y="72" width="56" height="36" rx="18"/><circle class="cp" cx="140" cy="90" r="9"/></g>'
             '<line class="bd bd1" x1="140" y1="90" x2="180" y2="90"/><g class="r"><circle class="cp" cx="180" cy="90" r="9"/><rect class="hb" x="194" y="72" width="56" height="36" rx="18"/></g></svg>')
PIC_CROSS = ('<svg class="pic" viewBox="0 0 320 180" aria-hidden="true"><rect class="wl" x="20" y="72" width="88" height="36" rx="14"/><rect class="wl" x="116" y="72" width="88" height="36" rx="14"/>'
             '<rect class="wl" x="212" y="72" width="88" height="36" rx="14"/><g class="pair"><rect class="ha" x="128" y="78" width="26" height="18" rx="9"/><circle class="cp" cx="160" cy="87" r="6"/>'
             '<circle class="cp" cx="176" cy="94" r="6"/><rect class="hb" x="168" y="84" width="26" height="18" rx="9" transform="translate(14 0)"/></g></svg>')
PIC_CLASP = ('<svg class="pic" viewBox="0 0 320 180" aria-hidden="true"><circle class="gl" cx="160" cy="90" r="34"/><g class="cl"><rect class="ha" x="82" y="72" width="56" height="36" rx="18"/><circle class="cp" cx="151" cy="90" r="9"/></g>'
             '<line class="bd" x1="151" y1="90" x2="169" y2="90"/><g class="cr"><circle class="cp" cx="169" cy="90" r="9"/><rect class="hb" x="182" y="72" width="56" height="36" rx="18"/></g></svg>')
moves = ''.join(f'<li class="move rv">{pic}<span class="k">{k}</span><h3>{t}</h3><p>{d}</p></li>' for pic, k, t, d in [
    (PIC_SPLIT, 'Split', 'One degrader, two small halves.', 'A reversible linker lets a SELFTAC&reg; molecule travel as two small molecules.'),
    (PIC_CROSS, 'Cross', 'Through the barrier, one half at a time.', 'Each half is small enough to be taken by mouth and to pass through the cells of the blood-brain barrier.'),
    (PIC_CLASP, 'Clasp', 'Rebuilt inside the neuron.', 'The halves click back together at the clasp, and the full degrader clears its target.')])
figs = ''.join(f'<li class="rv"><b>{b}</b><span>{t}</span></li>' for b, t in [
    ('&pound;25m', 'Series A financing in 2022, led by Syncona alongside Oxford Science Enterprises.'),
    ('2', 'Therapeutic areas in discovery: oncology and the central nervous system.'),
    ('1', 'Degrader rebuilt from two small halves, inside the cell that needs it.')])
cards = ''.join(f'<li class="rv"><a href="{s}.html">{fm()}<span class="k">{n}</span><b>{"How SELFTAC&reg; works" if s == "science" else n}</b><p>{d}</p>{ARROW}</a></li>'
                for s, n, d in PAGES)
news = re.findall(r'<li class="rv">.*?</li>', block('news'), re.S)[:2]
home = (f'<section class="hero" id="top">{svg("oyster-logotype-nacre.svg", "lt", "ltMask")}'
        '<h1>Protein degraders, made small enough to reach the brain.</h1>'
        f'<div class="ctas"><a class="btn" href="science.html"><span>See how SELFTAC&reg; works</span>{DOWN}</a><a class="btn ghost" href="pipeline.html"><span>Our pipeline</span>{DOWN}</a></div>'
        '<div class="hint" aria-hidden="true"><i></i></div></section>\n'
        + block('vision') + '\n'
        + band('moves', eyebrow('The idea') + '<h2 class="say rv">Split to travel, clasp to work.</h2><ol class="moves">' + moves + '</ol>'
               '<p class="ctas rv" style="justify-content:flex-start;margin-top:40px"><a class="btn" href="science.html"><span>Watch it in 3D</span>' + DOWN + '</a></p>')
        + RULE()
        + band('figures', eyebrow('Oyster in figures') + '<h2 class="say rv">A young company with one clear idea.</h2><ul class="figs">' + figs + '</ul>')
        + band('explore', eyebrow('Explore') + '<h2 class="say rv">From the science to the people behind it.</h2><ul class="explore">' + cards + '</ul>')
        + band('latest', eyebrow('Latest') + '<h2 class="say rv">News from Oyster</h2><ol class="items">' + ''.join(news) + '</ol>'
               '<p class="rv" style="margin-top:28px"><a class="uline" href="news.html" style="color:var(--ink)">All news</a></p>'))
page('index', 'Website v2', 'Oral, brain-penetrant protein degraders. SELFTAC&reg; molecules enter as two small halves and clasp back together inside the cell.', home, with_strand=False)

# ---------- science ----------
story = re.search(r'<section class="story" id="story".*?</div>\s*</div>\s*</section>', src, re.S).group(0)
story = story.replace('href="#vision">Skip to Oyster', 'href="#why">Skip the story').replace('<a href="#vision">Discover Oyster</a>', '<a href="#why">Why it works</a>')
story = once(story, '<canvas id="gl" aria-hidden="true"></canvas>', f'<canvas id="gl" aria-hidden="true"></canvas><div class="loader" aria-hidden="true">{fm()}<span>Loading the molecules</span></div>')
site_js = open(S + 'site.js').read()
clasp = site_js[site_js.index('// ---------- the live clasp'):]
a = module.index('// ---------- site: header state'); b = module.index('\nwindow.__story = {')
module = module[:a] + clasp + module[b:]
# a longer glide behind the scroll
module = once(module, '1 - Math.exp(-dt / .22)', '1 - Math.exp(-dt / .3)')
# the load-in (loadin.js): the fan mark's pearl becomes the clasp as the halves close on it, only at the top of the story
module = once(module, '\nfunction frame(p0) {', '\n' + open(D + 'loadin.js').read() + 'function frame(p0) {')
module = once(module, '  const joined = kf(p, [[.16, 1], [.2, 0], [.6, 0], [.665, 1]]);\n',
              '  const joined = kf(p, [[.16, 1], [.2, 0], [.6, 0], [.665, 1]]);\n'
              '  // load-in: the halves fly in from far behind and close on the pearl (only at the top of the story)\n'
              '  const ia = 1 - clamp(p0 / .05, 0, 1), ei = ease(clamp((intro - .2) / .6, 0, 1));\n'
              '  const hxI = hx + ia * (1 - ei) * 8, joinedI = joined * (1 - ia * (1 - clamp((intro - .8) / .08, 0, 1)));\n'
              '  const away = mol.centre.clone().sub(camera.position).normalize().multiplyScalar(ia * (1 - ei) * 160);   // straight back along the line of sight\n')
module = once(module, 'const oW = new THREE.Vector3(-hx, hy, 0), oE = new THREE.Vector3(hx, hy, 0);', 'const oW = new THREE.Vector3(-hxI, hy, 0).add(away), oE = new THREE.Vector3(hxI, hy, 0).add(away);')
module = once(module, 'free * .5 * Math.sin(spin * .9), 0));', 'free * .5 * Math.sin(spin * .9) + ia * (1 - ei) * .9, 0));')
module = once(module, 'free * .45 * Math.cos(spin * 1.2), 0));', 'free * .45 * Math.cos(spin * 1.2) - ia * (1 - ei) * .9, 0));')
module = once(module, 'const brk = mol.update(oW, oE, rW, rE, joined);', 'const brk = mol.update(oW, oE, rW, rE, joinedI);')
module = once(module, 'const fx = bump(p, .655, .69); flash.position.copy(brk); flash.scale.setScalar(1 + 3 * clamp((p - .655) / .035, 0, 1));',
              'const fs = bump(p, .655, .69), fi = ia * bump(intro, .8, 1), fx = Math.max(fs, fi); flash.position.copy(brk);\n'
              '  flash.scale.setScalar(1 + 3 * (fi > fs ? clamp((intro - .8) / .2, 0, 1) : clamp((p - .655) / .035, 0, 1)));')
module = once(module, "document.getElementById('hint').style.opacity = 1 - clamp(p / .02, 0, 1);",
              "document.getElementById('hint').style.opacity = 1 - clamp(p / .02, 0, 1);\n  claspNdc.copy(brk).project(camera);   // where the load-in's pearl lands")
# redraw only when the picture changes; the load-in starts once the mark has been up long enough and a frame is ready
module = once(module, '  if (storyOn) { frame(prog); if (renderer) renderer.render(scene, camera); }',
              "  const now = performance.now();\n"
              "  if (introStart < 0 && firstDrawn && now - pageT0 > (intro >= 1 ? 0 : LOGO_MS)) startIntro(now);\n"
              "  if (introHold >= 0) intro = introHold; else if (introStart >= 0 && intro < 1) intro = Math.min(1, (now - introStart) / INTRO_MS);\n"
              "  const sig = prog.toFixed(5) + '|' + spin.toFixed(4) + '|' + pal + '|' + intro.toFixed(4) + '|' + stage.clientWidth + 'x' + stage.clientHeight;\n"
              "  if (storyOn && sig !== drawnSig) { frame(prog); if (renderer) renderer.render(scene, camera); drawnSig = sig; firstDrawn = true; }")
module = once(module, '\nrequestAnimationFrame(loop);\n',
              "\n// every shader is built before the first frame, so nothing hitches when a new part of the story comes into view\n"
              "if (renderer) { try { renderer.compile(scene, camera); } catch (e) {} }\n"
              "requestAnimationFrame(loop);\n")
for gone in ('makeBg(', 'const NAMES', 'const head ='):
    assert gone not in module, gone
meshes = re.search(r'<script type="application/json" id="meshes">.*?</script>', src, re.S).group(0)
importmap = re.search(r'<script type="importmap">.*?</script>', src, re.S).group(0)
versus = ('<div class="versus">'
          + card('Most degraders', 'One large molecule.', '<p>Degraders remove disease-causing proteins instead of blocking them, but most are large.</p>'
                 '<ul><li>Hard to take by mouth</li><li>Rarely reach the brain</li><li>Travel as one large molecule throughout</li></ul>')
          + card('SELFTAC&reg;', 'Two small halves, one degrader.', '<p>The degrader is split at a reversible linker and travels as two small molecules.</p>'
                 '<ul><li>Small enough to be taken by mouth</li><li>Small enough to cross the blood-brain barrier</li><li>Rebuilt inside the cell, where it acts</li></ul>', 'hi')
          + '</div>')
TERMS = [('Protein degrader', 'A molecule that removes a protein rather than blocking it, by handing it to the cell&rsquo;s own disposal system.'),
         ('Target protein', 'The disease-causing protein to be removed. In the story it is BRD4, from the crystal structure 5T35.'),
         ('E3 ligase', 'The enzyme that marks proteins for disposal. In the story it is VHL, held with Elongin B and C.'),
         ('Ternary complex', 'The three-part assembly of target, degrader and E3 ligase. It brings the target close enough to be tagged.'),
         ('Ubiquitin', 'A small protein tag. A chain of ubiquitin on the target is the signal to destroy it.'),
         ('Proteasome', 'The barrel-shaped machine that breaks tagged proteins down.'),
         ('Blood-brain barrier', 'The sealed lining of the brain&rsquo;s blood vessels, which keeps most large molecules out.'),
         ('The clasp', 'Our name for the reversible linker where the two SELFTAC&reg; halves meet and close.')]
terms = '<dl class="terms">' + ''.join(f'<div class="rv"><dt>{t}</dt><dd>{d}</dd></div>' for t, d in TERMS) + '</dl>'
science = (story + '\n' + block('why') + '\n'
           + band('versus', eyebrow('The difference') + '<h2 class="say rv">The same degrader, made small enough to travel.</h2>' + versus)
           + RULE()
           + band('terms', eyebrow('Terms') + '<h2 class="say rv">The words behind the story.</h2>' + terms))
# the import map goes in the head, ahead of the preloads: Safari and Firefox ignore an import map that comes after
# any module has started loading, and the story's script then cannot find three.js at all
page('science', 'Science | Oyster Therapeutics', PAGES[0][2], science,
     after=meshes + '\n<script type="module">' + module + '</script>\n', skipto='#why',
     extra='\n<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>\n' + importmap +
           '\n<link rel="modulepreload" href="https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js">'
           '\n<link rel="modulepreload" href="https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/geometries/RoundedBoxGeometry.js">')

# ---------- pipeline ----------
stagekey = '<ul class="stagekey">' + ''.join(f'<li class="rv"><b>{t}</b><span>{d}</span></li>' for t, d in [
    ('Discovery', 'Finding and making the first molecules that work on a target. Where both programmes are today.'),
    ('Lead optimisation', 'Refining the best molecules for potency, safety and how they behave in the body.'),
    ('Preclinical', 'The studies needed before a medicine can be given to people.'),
    ('Clinical', 'Trials in people.')]) + '</ul>'
areas = ('<div class="areas">'
         + card('Oncology', 'Removing what drives a cancer.', '<p>Many proteins that drive cancer have no pocket a conventional drug can block. A degrader only needs to hold on long enough to hand the protein over, so it can reach targets that blocking cannot.</p>')
         + card('Central nervous system', 'Reaching the brain by mouth.', '<p>Medicines for the brain must cross the blood-brain barrier, which most degraders are too large to do. Travelling as two small halves is how a SELFTAC&reg; degrader is designed to get there.</p>', 'hi')
         + '</div>')
pipe = as_page(block('pipeline')).replace('</div>\n</section>', stagekey + '</div>\n</section>', 1)
page('pipeline', 'Pipeline | Oyster Therapeutics', PAGES[1][2], pipe + band('areas', eyebrow('Why these areas') + '<h2 class="say rv">Two areas where removing a protein matters most.</h2>' + areas))

# ---------- team ----------
join = band('join', '<div class="join">' + '<div>' + eyebrow('Join us') + '<h2 class="say rv">Chemists, biologists and builders who want to see the clasp close.</h2>'
            '<p class="lede rv">We are a small team in London. If you would like to work with us, write to us with what you do.</p></div>'
            '<p class="rv"><a class="btn" href="contact.html"><span>Get in touch</span>' + DOWN + '</a></p></div>')
page('team', 'Team | Oyster Therapeutics', PAGES[2][2], as_page(block('team')) + RULE() + join)

# ---------- investors ----------
backers = ('<div class="backers">'
           + '<article class="card rv">' + fm() + '<a href="https://www.synconaltd.com/" target="_blank" rel="noopener"><span class="k">Lead investor</span><h3>Syncona</h3>'
             '<p>A London-listed life science investor that founds, builds and funds companies.</p>' + ARROW + '</a></article>'
           + '<article class="card rv">' + fm() + '<a href="https://www.oxfordscienceenterprises.com/" target="_blank" rel="noopener"><span class="k">Investor</span><h3>Oxford Science Enterprises</h3>'
             '<p>An investor in companies built on science from the University of Oxford.</p>' + ARROW + '</a></article></div>')
miles = '<ol class="miles">' + ''.join(f'<li class="rv"><time datetime="{dt}">{d}</time><b>{t}</b><span>{x}</span></li>' for dt, d, t, x in [
    ('2022', '2022', '&pound;25m Series A', 'Led by Syncona with Oxford Science Enterprises, to advance the SELFTAC&reg; platform.'),
    ('2024-11-06', 'November 2024', 'Robert Johnson appointed CEO', 'To lead a new class of oral, CNS-penetrant protein degraders.'),
    ('2025-05-13', 'May 2025', 'Tim Clackson joins the Board', 'Three decades building oncology companies.')]) + '</ol>'
inv = as_page(block('investors'))
page('investors', 'Investors | Oyster Therapeutics', PAGES[3][2], inv
     + band('backers', eyebrow('Our backers') + '<h2 class="say rv">Specialist investors in life science.</h2>' + backers)
     + band('milestones', eyebrow('Milestones') + '<h2 class="say rv">From financing to a full board.</h2>' + miles))

# ---------- news ----------
page('news', 'News | Oyster Therapeutics', PAGES[4][2], as_page(block('news').replace('href="#investors"', 'href="investors.html"'))
     + band('follow', eyebrow('Follow') + '<h2 class="say rv">News as it happens.</h2>'
            '<p class="lede rv">We post news on LinkedIn first. To hear by email, ask to join the list.</p>'
            '<p class="ctas rv" style="justify-content:flex-start;margin-top:32px"><a class="btn" href="https://uk.linkedin.com/company/kesmalea-therapeutics" target="_blank" rel="noopener"><span>Follow on LinkedIn</span>' + DOWN + '</a>'
            '<a class="btn ghost" href="mailto:info@oystertx.com?subject=Sign%20me%20up%20for%20Oyster%20news"><span>Ask to join the list</span>' + DOWN + '</a></p>'))

# ---------- contact ----------
contact = block('contact')
contact = re.sub(r'\s*<div class="sign rv">.*?</div>|\s*<p class="credit">.*?</p>|\s*<p class="legal">.*?</p>', '', contact, flags=re.S)
contact = contact.replace('<footer class="foot" id="contact">', '<section class="contact band" id="contact">').replace('</footer>', '</section>')
reach = '<div class="reach">' + ''.join(card(k, t, f'<p>{d}</p>', more=f'<a class="uline" href="mailto:info@oystertx.com?subject={urllib.parse.quote(s)}">Write to us about {k.lower()}</a>')
                                        for k, t, d, s in [
    ('Partnerships', 'Work with us on a target.', 'For companies interested in what a degrader that reaches the brain could do for their programmes.', 'Partnership enquiry'),
    ('Investors', 'Follow our progress.', 'For investors who would like to hear about Oyster and the SELFTAC&reg; platform.', 'Investor enquiry'),
    ('Careers', 'Join the team.', 'For chemists, biologists and others who would like to work with us in London.', 'Careers enquiry')]) + '</div>'
contact = contact.replace('<div class="cols rv">', reach + '<div class="cols rv">', 1)
page('contact', 'Contact | Oyster Therapeutics', PAGES[5][2], as_page(contact))

for f in sorted(os.listdir(OUT)):
    print(f, os.path.getsize(OUT + f) // 1024, 'KB')
