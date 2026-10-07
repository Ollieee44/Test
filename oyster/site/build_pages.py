"""Build the multi-page site (pages/): the six-palette site (palettes.html) split into one page per
section. The 3D SELFTAC story and the live clasp are the Science page; Home, Pipeline, Team, Investors,
News and Contact each open the way the story does (a full first screen, the clasp-glyph label, a big serif
line) over the ternary complex wallpaper, and end on a pearl strand of every page and a link to the next.
All pages share pages/oyster.css and pages/oyster.js; only the Science page loads three.js and the meshes.
The palette chosen on one page carries to the next (?palette=<id> on every link, and local storage).

Run build_site.py and build_palettes.py first: the styles, story script, palette switch and wallpaper are
taken from palettes.html so the pages match it exactly."""
import json, os, re
D = os.path.dirname(os.path.abspath(__file__)) + '/'
OUT = D + 'pages/'
os.makedirs(OUT, exist_ok=True)
src = open(D + 'palettes.html').read()

def between(s, a, b, start=0):
    i = s.index(a, start); j = s.index(b, i + len(a)); return s[i + len(a):j]
def once(s, old, new):
    assert old in s, old[:70]
    return s.replace(old, new, 1)
def svg(name, cls, uid):
    s = open(D + '../brand/' + name).read()
    s = s.replace('x-mInside', uid).replace('fill="#2B2230"', 'fill="currentColor"').replace('fill="#C99BB0"', 'style="fill:var(--pearl)"')
    return s.replace('<svg ', f'<svg class="{cls}" translate="no" role="img" aria-label="Oyster Therapeutics" ', 1)
CG = '<svg class="cg" viewBox="0 0 30 12" aria-hidden="true"><line x1="6" y1="6" x2="24" y2="6"/><circle cx="6" cy="6" r="4.6"/><circle cx="24" cy="6" r="4.6"/></svg>'
ARROW = '<span class="arr"><svg viewBox="0 0 14 14" aria-hidden="true"><path d="M2 7h10M8 3l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></span>'
TM = lambda s: re.sub(r'(?<!<span translate="no">)SELFTAC&reg;', '<span translate="no">SELFTAC&reg;</span>', s)

# ---------- shared stylesheet and script ----------
css = between(src, '<style>', '</style>') + '\n' + open(D + 'multipage.css').read()
open(OUT + 'oyster.css', 'w').write(css.strip() + '\n')

module = between(src, '<script type="module">', '</script>')
names = between(module, 'const NAMES = ', ', paln =')
walls = re.search(r'var WALLS = .*?;\n', module).group(0)
wall = open(D + 'wallpaper.js').read()
wall = once(wall, "function readCol() { var tide = root.getAttribute('data-palette') === 'tidepool'; return tide ? { a: hexToRgb('#F2B84B'), b: hexToRgb('#7FC4B0'), ink: hexToRgb('#EAF3EF') } : { a: hexToRgb('#C99BB0'), b: hexToRgb('#B8A7C9'), ink: hexToRgb('#2B2230') }; }",
            walls + "  function readCol() { var w = WALLS[root.getAttribute('data-palette')] || WALLS.nacre; return { a: hexToRgb(w.a), b: hexToRgb(w.b), ink: hexToRgb(w.ink) }; }")
# no story on the page: the wallpaper is up from the start
wall = once(wall, 'ended = storyEl.getBoundingClientRect().bottom < innerHeight * .5;', 'ended = !storyEl || storyEl.getBoundingClientRect().bottom < innerHeight * .5;')
wall = once(wall, "\ndocument.querySelectorAll('.pal button').forEach(b => b.addEventListener('click', () => bgWall.refresh()));", '')
js = ('const NAMES = ' + names + ';\n' + open(D + 'multipage.js').read() + '\n' + wall + '''
// open in the palette from the link, else the one used last, else Nacre (a click, so the 3D story follows too)
(() => {
  let k = new URLSearchParams(location.search).get('palette');
  if (!NAMES[k]) { try { k = localStorage.getItem(PAL_KEY); } catch (e) { k = null; } }
  if (!NAMES[k]) k = 'nacre';
  const b = palBtns.find(x => x.dataset.pal === k); if (b) b.click(); else showPal(k);
  onScroll();
})();
''')
open(OUT + 'oyster.js', 'w').write(js)

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
    """Every page as a pearl on one strand, then a big link to the next page (Science follows the last)."""
    dots = ''.join(f'<li><a href="{s}.html"' + (' aria-current="page"' if s == cur else '') + f'><span>{n}</span></a></li>' for s, n, _ in PAGES)
    slugs = [s for s, _, _ in PAGES]
    nxt = PAGES[(slugs.index(cur) + 1) % len(PAGES)] if cur in slugs else PAGES[0]
    return (f'<nav class="next band" aria-label="Pages"><div class="wrap"><ol class="strandnav">{dots}</ol>'
            f'<a class="nextlink" href="{nxt[0]}.html"><span><small>Next</small><b>{nxt[1]}</b></span>{ARROW}</a></div></nav>\n')

credit = re.search(r'<p class="credit">.*?</p>', open(D + 'sections.html').read(), re.S).group(0)
FOOT = (f'<footer class="foot"><div class="wrap"><div class="foot-top">'
        f'<a class="foot-home" href="index.html" aria-label="Oyster Therapeutics, home">{svg("oyster-logotype-nacre.svg", "lt2", "lt2Mask")}</a>'
        '<ul>' + ''.join(f'<li><a href="{s}.html">{n}</a></li>' for s, n, _ in PAGES) + '</ul>'
        '<ul><li><a href="mailto:info@oystertx.com">info@oystertx.com</a></li><li><a href="https://uk.linkedin.com/company/kesmalea-therapeutics" target="_blank" rel="noopener">LinkedIn</a></li>'
        '<li><p>London, United Kingdom</p></li></ul></div>'
        f'{credit}<p class="legal">&copy; 2026 Oyster Therapeutics. Formerly Kesmalea Therapeutics.</p></div></footer>\n')

HEAD = '''<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>{extra}
<meta name="theme-color" content="#EFE6E1">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=swap">
<link rel="stylesheet" href="oyster.css">
'''
def page(slug, title, desc, main, after='', skipto='#main', extra=''):
    h = HEAD.format(title=title, desc=re.sub('<[^>]+>|&[a-z]+;', lambda m: {'&reg;': '®', '&pound;': '£'}.get(m.group(0), ''), desc), extra=extra)
    h += ('<canvas id="bgArt" aria-hidden="true"></canvas>\n'
          f'<a class="sr-only" href="{skipto}">Skip to content</a>\n' + header(slug) + '<main id="main">\n' + main + strand(slug) + '</main>\n' + FOOT + after +
          '<script type="module" src="oyster.js"></script>\n')
    open(OUT + slug + '.html', 'w').write(TM(h))
    return h

# ---------- the sections, one per page ----------
sec = open(D + 'sections.html').read().replace('<!--CG-->', CG).replace('<!--ARROW-->', ARROW)
def block(sid):
    m = re.search(r'<(section|footer) class="[^"]*" id="' + sid + r'">.*?</\1>', sec, re.S); return m.group(0)
def as_page(b):
    """A section as the opening of its own page: the first-screen band, and its statement as the page's h1."""
    b = re.sub(r'class="([^"]*)band"', r'class="\1band phero"', b, count=1)
    b = re.sub(r'<h2 class="(say|sr-only)([^"]*)">(.*?)</h2>', r'<h1 class="\1\2">\3</h1>', b, count=1, flags=re.S)
    return b

page('pipeline', 'Pipeline | Oyster Therapeutics', PAGES[1][2], as_page(block('pipeline')))
page('team', 'Team | Oyster Therapeutics', PAGES[2][2], as_page(block('team')))
page('investors', 'Investors | Oyster Therapeutics', PAGES[3][2], as_page(block('investors')))
page('news', 'News | Oyster Therapeutics', PAGES[4][2], as_page(block('news').replace('href="#investors"', 'href="investors.html"')))
contact = block('contact')
contact = re.sub(r'\s*<div class="sign rv">.*?</div>|\s*<p class="credit">.*?</p>|\s*<p class="legal">.*?</p>', '', contact, flags=re.S)
contact = contact.replace('<footer class="foot" id="contact">', '<section class="contact band" id="contact">').replace('</footer>', '</section>')
page('contact', 'Contact | Oyster Therapeutics', PAGES[5][2], as_page(contact))

# ---------- home: the story's end card as the front door, the vision, and a card per page ----------
cards = ''.join(f'<li class="rv"><a href="{s}.html"><span class="k">{i + 1:02d} &middot; {n}</span><b>{"How SELFTAC&reg; works" if s == "science" else n}</b><p>{d}</p>{ARROW}</a></li>'
                for i, (s, n, d) in enumerate(PAGES))
down = '<svg viewBox="0 0 14 14" aria-hidden="true"><path d="M2 7h10M8 3l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
home = (f'<section class="hero" id="top">{svg("oyster-logotype-nacre.svg", "lt", "ltMask")}'
        '<h1>Protein degraders, made small enough to reach the brain.</h1>'
        f'<div class="ctas"><a class="btn" href="science.html"><span>See how SELFTAC&reg; works</span>{down}</a><a class="btn ghost" href="pipeline.html"><span>Our pipeline</span></a></div>'
        '<div class="hint" aria-hidden="true"><i></i></div></section>\n'
        + block('vision') +
        f'\n<section class="band" id="explore"><div class="wrap"><p class="eyebrow rv">{CG}Explore</p><h2 class="say rv">One idea, from the science to the people behind it.</h2>'
        f'<ul class="explore">{cards}</ul></div></section>\n')
h = page('index', 'Oyster Therapeutics', 'Oral, brain-penetrant protein degraders. SELFTAC&reg; molecules enter as two small halves and clasp back together inside the cell.', home)
# the home page has its own strand and cards, so it ends on the footer
open(OUT + 'index.html', 'w').write(TM(h.replace(strand('index'), '')))

# ---------- science: the 3D story, then the live clasp ----------
story = re.search(r'<section class="story" id="story".*?</div>\s*</div>\s*</section>', src, re.S).group(0)
story = story.replace('href="#vision">Skip to Oyster', 'href="#why">Skip the story').replace('<a href="#vision">Discover Oyster</a>', '<a href="#why">Why it works</a>')
assert 'href="#vision"' not in story, 'story still links to #vision'
why = block('why')
# the story module without the one-page site code (header, reveals, wallpaper, palette switch: those are in
# oyster.js now), keeping the live clasp, which draws with the story's renderer and molecule
site_js = open(D + 'site.js').read()
clasp = site_js[site_js.index('// ---------- the live clasp'):]
a = module.index('// ---------- site: header state'); b = module.index('\nwindow.__story = {')
module = module[:a] + clasp + module[b:]
for gone in ('makeBg(', 'const NAMES', 'const head ='):
    assert gone not in module, gone
meshes = re.search(r'<script type="application/json" id="meshes">.*?</script>', src, re.S).group(0)
importmap = re.search(r'<script type="importmap">.*?</script>', src, re.S).group(0)
page('science', 'Science | Oyster Therapeutics', PAGES[0][2], story + '\n' + why + '\n',
     after=meshes + '\n' + importmap + '\n<script type="module">' + module + '</script>\n', skipto='#why',
     extra='\n<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>')

for f in sorted(os.listdir(OUT)):
    print(f, os.path.getsize(OUT + f) // 1024, 'KB')
