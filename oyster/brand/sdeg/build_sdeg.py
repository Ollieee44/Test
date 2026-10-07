"""Build brand/sdegrader.html, "Oyster Degrader S": the wordmark's s drawn as a heterobifunctional
degrader (sdeg.py), each variant shown large, in the new logotype (mark 11.7) and at header size,
in Nacre and Tidepool. Usage: python3 build_sdeg.py"""
import os, re
import numpy as np
import sdeg
D = os.path.dirname(os.path.abspath(__file__)) + '/'
SITE = D + '../../intro/fan-site.html'

PAL = {'nacre': 'color:#2B2230;background:#EFE6E1;--pearl:#C99BB0;--clasp:#D9A443;--strand:#8C5572;--bead:#F6EEF1',
       'tidepool': 'color:#EAF3EF;background:#0F4C4A;--pearl:#F2B84B;--clasp:#F27D62;--strand:#B6D3CB;--bead:#EAF3EF'}
LT = re.search(r'<svg class="lt"[^>]*>.*?</svg>', open(SITE).read(), re.S).group(0)
S_EL = re.search(r'<path d="[^"]*" transform="translate\(949\.8 0\.0\) scale\(0\.5000 -0\.5000\)"/>', LT).group(0)

def logotype(fn, ns):
    s = LT.replace(S_EL, f'<g transform="translate(949.8 0.0) scale(0.5000 -0.5000)">{fn(ns + "s")}</g>')
    for i in set(re.findall(r'id="([^"]+)"', LT)):
        s = s.replace(f'id="{i}"', f'id="{ns}{i}"').replace(f'url(#{i})', f'url(#{ns}{i})')
    return re.sub(r'<svg class="lt"[^>]*?(viewBox="[^"]+")[^>]*>', r'<svg class="lt" \1 aria-hidden="true">', s, count=1)

def big(fn, ns):
    return f'<svg class="big" viewBox="-110 -1110 1010 1180" aria-hidden="true"><g transform="scale(1 -1)" fill="currentColor">{fn(ns)}</g></svg>'

def construction():
    """The traced centreline, the spine's middle and the two shoulders over the outline."""
    line = sdeg.pts(sdeg.C); dots = ''
    for s, lab in ((sdeg.S_TOP, 'shoulder'), (sdeg.S_MID, 'middle'), (sdeg.S_BOT, 'shoulder')):
        p, t, n, w = sdeg.at(s); a, b = p + n * w, p - n * w
        dots += (f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="var(--clasp)" stroke-width="8"/>'
                 f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="14" fill="var(--clasp)"/>')
    return (f'<svg class="big" viewBox="-110 -1110 1010 1180" aria-hidden="true"><g transform="scale(1 -1)">'
            f'<path d="{sdeg.D}" fill="currentColor" opacity=".18"/><polyline points="{line}" fill="none" stroke="currentColor" stroke-width="6"/>{dots}</g></svg>')

cards = ''
for num, name, idea, fn in sdeg.VARIANTS:
    k = f'v{num}'
    bigs = ''.join(f'<div class="tile sq" style="{st}" title="{p.title()}">{big(fn, f"{k}{p[0]}b")}</div>' for p, st in PAL.items())
    lts = ''.join(f'<div class="tile wide" style="{st}">{logotype(fn, f"{k}{p[0]}l")}</div>' for p, st in PAL.items())
    hdr = ''.join(f'<div class="tile hdr" style="{st}">{logotype(fn, f"{k}{p[0]}h")}</div>' for p, st in PAL.items())
    cards += (f'<article class="card{" ref" if num == "00" else ""}" id="s{num}"><header><b>{num}</b><h2>{name}</h2></header><p>{idea}</p>'
              f'<div class="row bigs">{bigs}</div><div class="row">{lts}</div><span class="lab">Header size, 42px</span><div class="row">{hdr}</div></article>')

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
.lede { color: var(--muted); max-width: 66ch; margin: 14px 0 0; font-size: clamp(16px, 1.4vw, 18px); }
.intro { display: grid; grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr); gap: 28px; align-items: center; margin-top: 8px; }
@media (max-width: 760px) { .intro { grid-template-columns: minmax(0, 1fr); } }
.intro .tile { max-width: 300px; justify-self: center; width: 100%; }
.grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; margin-top: 36px; }
@media (max-width: 900px) { .grid { grid-template-columns: minmax(0, 1fr); } }
.card { background: var(--surface); border: 1px solid var(--line); border-radius: 22px; padding: clamp(16px, 2.2vw, 24px); display: grid; gap: 12px; min-width: 0; }
.card.ref { border-style: dashed; }
.card header { display: flex; align-items: baseline; gap: 12px; }
.card header b { font: 500 13px/1 var(--mono); color: var(--accent); letter-spacing: .06em; }
.card h2 { font-size: clamp(24px, 2.4vw, 30px); }
.card p { margin: 0; color: var(--muted); font-size: 15px; min-height: 3.1em; }
.row { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.tile { border-radius: 14px; display: grid; place-items: center; min-width: 0; }
.tile.sq { aspect-ratio: 1 / 1; padding: 6%; }
.tile.wide { padding: clamp(14px, 2.4vw, 24px) 10px; }
.tile.hdr { padding: 14px 10px; }
.big { width: 100%; height: 100%; display: block; }
.lt { width: 100%; height: auto; display: block; }
.hdr .lt { width: auto; height: 42px; max-width: 100%; }
footer { margin-top: 40px; color: var(--muted); font-size: 13px; }
code { font-family: var(--mono); font-size: .92em; }
'''
html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Oyster Degrader S</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=swap">
<style>{CSS}</style>
</head>
<body>
<main class="wrap">
  <span class="eyebrow">Oyster Therapeutics &middot; wordmark study</span>
  <div class="intro">
    <div>
      <h1>The s as a degrader</h1>
      <p class="lede">A heterobifunctional degrader is two ligands joined by a linker, and a SELFTAC clasps its two halves together at the middle. The s already has that shape: two ends, one spine. Each option below keeps the letter and adds the story by degrees, from a clasp in the spine to a full ring&ndash;linker&ndash;ring molecule. Shown large, in the new logotype, and at the 42px header size, in Nacre and Tidepool.</p>
    </div>
    <div class="tile sq" style="{PAL['nacre']}" title="Construction">{construction()}</div>
  </div>
  <div class="grid">{cards}</div>
  <footer>Construction (top right): the s outline from the logotype export, its traced centreline, and the three cuts every option uses: the two shoulders where the serifs start and the middle of the spine. Rings are generic, as in the 3D story. Built by <code>oyster/brand/sdeg/build_sdeg.py</code>.</footer>
</main>
</body>
</html>
'''
open(D + '../sdegrader.html', 'w').write(html)
print('sdegrader.html', len(html) // 1024, 'KB')
