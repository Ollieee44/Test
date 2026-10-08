"""Build brand/brainstorm.html, "Oyster Mark Brainstorm": new brandmark concepts (concepts.py) that tell the
SELFTAC story with the oyster's own anatomy. Each shown clasped and split in Nacre and Tidepool, at small
sizes, and locked up with the logotype in place of the current mark. Usage: python3 build_brainstorm.py"""
import os, re
import concepts as C
D = os.path.dirname(os.path.abspath(__file__)) + '/'
SITE = D + '../../intro/fan-site.html'
PAL = {'nacre': 'color:#2B2230;background:#EFE6E1;--clasp:#D9A443', 'tidepool': 'color:#EAF3EF;background:#0F4C4A;--clasp:#F27D62'}
LT = re.search(r'<svg class="lt"[^>]*>.*?</svg>', open(SITE).read(), re.S).group(0)
HEAD = '<g transform="translate(-17.1 -583.4) scale(6.3571)">'

def mark(fn, ns, split=False, size=None, cls='mk'):
    sz = f' width="{size}" height="{size}"' if size else ''
    return f'<svg class="{cls}" viewBox="0 0 100 100"{sz} aria-hidden="true"><g fill="currentColor">{fn(ns, split)}</g></svg>'

def lockup(fn, ns):
    """The logotype with the concept in the mark's box (the same box the current mark uses)."""
    i = LT.index(HEAD) + len(HEAD); j = LT.rfind('</g><path d=', 0, LT.index('transform="translate(488.1 0.0)'))
    s = LT[:i] + fn(ns + 'k', False) + LT[j:]
    for k in set(re.findall(r'id="([^"]+)"', LT)):
        s = s.replace(f'id="{k}"', f'id="{ns}{k}"').replace(f'url(#{k})', f'url(#{ns}{k})')
    return re.sub(r'<svg class="lt"[^>]*?(viewBox="[^"]+")[^>]*>', r'<svg class="lt" \1 aria-hidden="true">', s, count=1)

cards = ''
for key, num, name, fn, idea, why in C.CONCEPTS:
    states = ''
    for split, lab in ((False, 'Clasped'), (True, 'Split')):
        tiles = ''.join(f'<div class="tile sq" style="{st}" title="{p.title()}, {lab.lower()}">{mark(fn, f"{key}{p[0]}{int(split)}", split)}</div>' for p, st in PAL.items())
        states += f'<div class="state"><span class="lab">{lab}</span><div class="row">{tiles}</div></div>'
    small = ''.join(f'<div class="tile sm" style="{st}">' + ''.join(mark(fn, f'{key}{p[0]}s{px}', size=px, cls='px') for px in (16, 24, 32, 48)) + '</div>' for p, st in PAL.items())
    lock = ''.join(f'<div class="tile wide" style="{st}">{lockup(fn, f"{key}{p[0]}L")}</div>' for p, st in PAL.items())
    cards += (f'<article class="card" id="c{num}"><header><b>{num}</b><h2>{name}</h2></header><p>{idea}</p><p class="why">{why}</p>'
              f'<div class="states">{states}</div><span class="lab">16, 24, 32 and 48px</span><div class="row">{small}</div>'
              f'<span class="lab">With the logotype</span><div class="row">{lock}</div></article>')

CSS = '''
:root { --bg: #F3EEEB; --surface: #FBF8F6; --ink: #241D28; --muted: #6A5E6C; --line: rgba(36,29,40,.13); --accent: #8C5572;
  --serif: "Newsreader", Georgia, serif; --sans: "Archivo", "Helvetica Neue", Arial, sans-serif; --mono: "IBM Plex Mono", ui-monospace, Menlo, monospace; color-scheme: light; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --bg: #17131A; --surface: #211C25; --ink: #EFE6E1; --muted: #B3A6B4; --line: rgba(239,230,225,.13); --accent: #D9AFC2; color-scheme: dark; } }
:root[data-theme="dark"] { --bg: #17131A; --surface: #211C25; --ink: #EFE6E1; --muted: #B3A6B4; --line: rgba(239,230,225,.13); --accent: #D9AFC2; color-scheme: dark; }
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink); font: 400 16px/1.55 var(--sans); -webkit-font-smoothing: antialiased; }
.wrap { max-width: 1240px; margin: 0 auto; padding: clamp(40px, 7vw, 80px) clamp(16px, 4vw, 48px) 56px; }
.eyebrow, .lab { font: 500 11px/1 var(--mono); letter-spacing: .12em; text-transform: uppercase; color: var(--muted); }
h1, h2 { font-family: var(--serif); font-weight: 500; letter-spacing: -.012em; margin: 0; }
h1 { font-size: clamp(36px, 5vw, 58px); line-height: 1.04; margin-top: 12px; }
.lede { color: var(--muted); max-width: 70ch; margin: 14px 0 0; font-size: clamp(16px, 1.4vw, 18px); }
.lede b { color: var(--ink); font-weight: 600; }
.grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; margin-top: 36px; }
@media (max-width: 900px) { .grid { grid-template-columns: minmax(0, 1fr); } }
.card { background: var(--surface); border: 1px solid var(--line); border-radius: 22px; padding: clamp(16px, 2.2vw, 24px); display: grid; gap: 10px; min-width: 0; align-content: start; }
.card header { display: flex; align-items: baseline; gap: 12px; }
.card header b { font: 500 13px/1 var(--mono); color: var(--accent); letter-spacing: .06em; }
.card h2 { font-size: clamp(24px, 2.4vw, 30px); }
.card p { margin: 0; color: var(--muted); font-size: 15px; }
.card p.why { color: var(--ink); }
.states { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 4px; }
.state { display: grid; gap: 6px; min-width: 0; }
.row { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.tile { border-radius: 14px; display: grid; place-items: center; min-width: 0; }
.tile.sq { aspect-ratio: 1 / 1; padding: 8%; }
.tile.sm { display: flex; align-items: center; justify-content: center; gap: 14px; padding: 14px 8px; flex-wrap: wrap; }
.tile.wide { padding: clamp(14px, 2.4vw, 22px) 10px; }
.mk { width: 100%; height: 100%; display: block; }
.px { display: block; flex: none; }
.lt { width: 100%; height: auto; display: block; }
footer { margin-top: 40px; color: var(--muted); font-size: 13px; max-width: 80ch; }
code { font-family: var(--mono); font-size: .92em; }
'''
html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Oyster Mark Brainstorm</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=swap">
<style>{CSS}</style>
</head>
<body>
<main class="wrap">
  <span class="eyebrow">Oyster Therapeutics &middot; brandmark brainstorm</span>
  <h1>The oyster is already a SELFTAC</h1>
  <p class="lede"><b>An oyster is two separate halves, its valves, held together by one reversible joint, the hinge ligament.</b> A SELFTAC is two halves that clasp back together. So none of these adds a pearl or a molecule to a shell: the valves are the two halves, and the hinge, the lip or the seam between them carries the clasp, in the clasp colour. Every shell is drawn with a frilled edge and growth layers, which is what makes an oyster read as an oyster and not a clam, a cowrie or a coffee bean (smooth first sketches read as all three). Each is shown clasped and split: the split state is for motion, the halves coming together in the intro.</p>
  <div class="grid">{cards}</div>
  <footer>Rough concepts for choosing a direction, not finished artwork: the frills, layers and clasp proportions would all be redrawn for the chosen idea, and a small-size cut made for favicons. Built by <code>oyster/brand/brainstorm/build_brainstorm.py</code> from <code>concepts.py</code> and <code>shell.py</code>.</footer>
</main>
</body>
</html>
'''
open(D + '../brainstorm.html', 'w').write(html)
print('brainstorm.html', len(html) // 1024, 'KB')
