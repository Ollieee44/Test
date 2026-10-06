"""Build hub.html, "Oyster Site Versions": one place to open every version of the website, old logo beside new.

Each logo shows its real logotype (taken from the header of its own site page) in both palettes, with links to its
intro in Nacre, its intro in Tidepool and the website without the intro. Brand tools are listed below. Update LINKS
when a page moves; rebuild after either site changes.
"""
import os, re
D = os.path.dirname(os.path.abspath(__file__)) + '/'
ART = 'https://claude.ai/artifact/'
LOGOS = [
 ('old', 'Old logo', 'Inside Out', 'The side-view shell cut out of a disc, with the pearl in its cradle. The mark on the live site.',
  D + 'site/index.html', [('Intro &middot; Nacre', ART + 'NTiBBienf6HvCseLhbCDHU'), ('Intro &middot; Tidepool', ART + 'QNC92GFvJXE6w1tULP5ELu'),
                          ('Website, no intro', ART + '9pFqdk4otTS46U21phpLCk')], 'Live', '4.1'),
 ('new', 'New logo', 'Fan, inside out', 'The face-on fan and pearl in line, cut out of a disc (80% pearl, rim 3.5). The intro&rsquo;s clam opens with its lid standing up as the fan.',
  D + 'intro/fan-site.html', [('Intro &middot; Nacre', ART + '7dgMtsG9wGQ18WXi8d6J73'), ('Intro &middot; Tidepool', ART + 'FdQsz8x3zDvkPnTZvowc1s'),
                              ('Website, no intro', ART + 'NSRLa7dnMy96W1ViKGfjHc')], 'Proposed', '11.7'),
]
TOOLS = [('Mark catalogue', 'Every mark drawn for Oyster, numbered.', ART + 'AJUpcjMJuGVzcQt5ZAfNrK'),
         ('Logotype studio', 'Letter spacing for the wordmark.', ART + '7tNEfaWQeav7iTWnMSocu1'),
         ('Palette explorer', 'The site in six palettes.', ART + 'AfzgUFchFXjBXQWcboMYMy')]
PAL = {'nacre': ('#EFE6E1', '#2B2230', '#C99BB0'), 'tidepool': ('#0F4C4A', '#EAF3EF', '#F2B84B')}

def wordmark(path, key, pal):
    """The header wordmark of a site page, with its ids made unique for this page."""
    s = re.search(r'<svg class="wm"[^>]*>.*?</svg>', open(path).read(), re.S).group(0)
    for i in set(re.findall(r'id="([^"]+)"', s)):
        s = s.replace(f'id="{i}"', f'id="{key}-{pal}-{i}"').replace(f'url(#{i})', f'url(#{key}-{pal}-{i})')
    s = re.sub(r'<svg class="wm"[^>]*?(viewBox="[^"]+")[^>]*>', lambda m: f'<svg class="wm" {m.group(1)} aria-hidden="true">', s, count=1)
    return s

cards = ''
for key, title, name, note, path, links, tag, num in LOGOS:
    tiles = ''.join(f'<div class="tile" style="background:{bg};color:{ink};--pearl:{pearl}" title="{p.title()}">{wordmark(path, key, p)}</div>'
                    for p, (bg, ink, pearl) in PAL.items())
    btns = ''.join(f'<a class="btn" href="{u}" target="_blank" rel="noopener">{lab}<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M3 9 9 3M4.5 3H9v4.5" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg></a>'
                   for lab, u in links)
    cards += (f'<section class="logo {key}" aria-labelledby="h-{key}"><header><span class="tag {tag.lower()}">{tag}</span>'
              f'<h2 id="h-{key}">{title}</h2><p class="name">{name} <span>&middot; catalogue {num}</span></p></header>'
              f'<div class="tiles">{tiles}</div><p class="note">{note}</p><div class="btns">{btns}</div></section>')
tools = ''.join(f'<a class="tool" href="{u}" target="_blank" rel="noopener"><b>{t}</b><span>{d}</span></a>' for t, d, u in TOOLS)

CSS = '''
:root { --bg: #F3EEEB; --surface: #FBF8F6; --ink: #241D28; --muted: #6A5E6C; --line: rgba(36,29,40,.13); --accent: #8C5572;
  --serif: "Newsreader", Georgia, serif; --sans: "Archivo", "Helvetica Neue", Arial, sans-serif; --mono: "IBM Plex Mono", ui-monospace, Menlo, monospace; color-scheme: light; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --bg: #17131A; --surface: #211C25; --ink: #EFE6E1; --muted: #B3A6B4; --line: rgba(239,230,225,.13); --accent: #D9AFC2; color-scheme: dark; } }
:root[data-theme="dark"] { --bg: #17131A; --surface: #211C25; --ink: #EFE6E1; --muted: #B3A6B4; --line: rgba(239,230,225,.13); --accent: #D9AFC2; color-scheme: dark; }
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink); font: 400 16px/1.55 var(--sans); -webkit-font-smoothing: antialiased; }
.wrap { max-width: 1180px; margin: 0 auto; padding: clamp(40px, 7vw, 84px) clamp(16px, 4vw, 48px) 56px; }
h1, h2 { font-family: var(--serif); font-weight: 500; letter-spacing: -.012em; margin: 0; }
.eyebrow { font: 500 11px/1 var(--mono); letter-spacing: .12em; text-transform: uppercase; color: var(--muted); }
h1 { font-size: clamp(38px, 5.4vw, 64px); line-height: 1.03; margin-top: 12px; }
.lede { color: var(--muted); max-width: 60ch; margin: 14px 0 0; font-size: clamp(16px, 1.4vw, 18px); }
.grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; margin-top: 40px; }
@media (max-width: 860px) { .grid { grid-template-columns: minmax(0, 1fr); } }
.logo { background: var(--surface); border: 1px solid var(--line); border-radius: 22px; padding: clamp(18px, 2.4vw, 26px); display: flex; flex-direction: column; gap: 16px; min-width: 0; }
.logo header { display: grid; gap: 4px; }
.tag { justify-self: start; font: 500 10.5px/1 var(--mono); letter-spacing: .12em; text-transform: uppercase; padding: 6px 9px; border-radius: 999px; border: 1px solid var(--line); color: var(--muted); }
.tag.live { background: #2F6B5E; border-color: #2F6B5E; color: #fff; }
.tag.proposed { background: var(--accent); border-color: var(--accent); color: var(--surface); }
.logo h2 { font-size: clamp(28px, 3vw, 36px); margin-top: 6px; }
.name { margin: 0; font-weight: 600; } .name span { font: 400 12px/1 var(--mono); color: var(--muted); letter-spacing: .04em; }
.tiles { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.tile { border-radius: 14px; padding: clamp(18px, 3vw, 30px) 12px; display: grid; place-items: center; min-width: 0; }
.tile .wm { width: 100%; max-width: 230px; height: auto; display: block; }
.note { margin: 0; color: var(--muted); font-size: 15px; }
.btns { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; margin-top: auto; }
@media (max-width: 480px) { .btns { grid-template-columns: minmax(0, 1fr); } }
.btn { display: flex; align-items: center; justify-content: space-between; gap: 8px; padding: 12px 14px; border-radius: 12px; border: 1px solid var(--line);
  color: var(--ink); text-decoration: none; font: 500 14px/1.2 var(--sans); background: var(--bg); transition: background-color .2s, border-color .2s; }
.btn svg { width: 12px; height: 12px; flex: none; opacity: .7; }
.btn:hover { border-color: var(--accent); background: color-mix(in srgb, var(--accent) 10%, var(--bg)); }
.btn:focus-visible, .tool:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
h3 { font: 500 11px/1 var(--mono); letter-spacing: .12em; text-transform: uppercase; color: var(--muted); margin: 48px 0 14px; }
.tools { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; }
@media (max-width: 760px) { .tools { grid-template-columns: minmax(0, 1fr); } }
.tool { display: grid; gap: 2px; padding: 14px 16px; border-radius: 14px; border: 1px solid var(--line); background: var(--surface); color: var(--ink); text-decoration: none; transition: border-color .2s; }
.tool:hover { border-color: var(--accent); }
.tool span { color: var(--muted); font-size: 14px; }
footer { margin-top: 40px; color: var(--muted); font-size: 13px; }
'''
html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<!-- artifact:start -->
<title>Oyster Site Versions</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=swap">
<style>{CSS}</style>
</head>
<body>
<main class="wrap">
  <span class="eyebrow">Oyster Therapeutics</span>
  <h1>Oyster Site Versions</h1>
  <p class="lede">The website with each logo, side by side. Each opens in its own tab: the intro in either palette, or the website without the intro. On any intro, Skip or a scroll jumps to the end.</p>
  <div class="grid">{cards}</div>
  <h3>Brand tools</h3>
  <div class="tools">{tools}</div>
  <footer>Built by <code>oyster/build_hub.py</code>.</footer>
</main>
<!-- artifact:end -->
</body>
</html>
'''
open(D + 'hub.html', 'w').write(html)
print('hub.html', len(html) // 1024, 'KB')
