"""Build palettes.html: the current site (index.html, left untouched) with the palettes from
palettes.json added beside Nacre and Tidepool. The header switch stays top right as a row of small
swatch dots. Open with ?palette=<id> to start on one. Run build_site.py first."""
import json, os
D = os.path.dirname(os.path.abspath(__file__)) + '/'
h = open(D + 'index.html').read()
P = json.load(open(D + 'palettes.json'))['palettes']

def once(old, new):
    global h
    assert old in h, old[:60]
    h = h.replace(old, new, 1)

HOUSE = [
    {'id': 'nacre', 'name': 'Nacre', 'css': {'paper': '#EFE6E1', 'clasp': '#D9A443'}},
    {'id': 'tidepool', 'name': 'Tidepool', 'css': {'paper': '#0F4C4A', 'clasp': '#F27D62'}},
]

# page tokens and the team monograms
css = ''
for p in P:
    c = p['css']
    css += (f':root[data-palette="{p["id"]}"] {{ --ink: {c["ink"]}; --muted: {c["muted"]}; --accent: {c["accent"]}; --paper: {c["paper"]}; '
            f'--band: {c["band"]}; --pearl: {c["pearl"]}; --clasp: {c["clasp"]}; --line: {c["line"]}; --card: {c["card"]}; '
            f'color-scheme: {"dark" if p["dark"] else "light"}; }}\n'
            f':root[data-palette="{p["id"]}"] .mono {{ color: {p["mono"]}; border-color: {p["mono"]}; }}\n')
css += '''/* compact palette switch: one swatch dot per palette, the name of the current one beside them */
.head .pal.dots { align-items: center; gap: 2px; padding: 3px 4px 3px 10px; }
.head .pal.dots .paln { font: 500 10.5px/1 var(--mono); letter-spacing: .1em; text-transform: uppercase; color: var(--muted); margin-right: 6px; white-space: nowrap; }
.head .pal.dots button { padding: 4px; display: grid; place-items: center; }
.head .pal.dots button[aria-pressed="true"] { background: transparent; }
.head .pal.dots button[aria-pressed="true"] i { box-shadow: 0 0 0 1.5px var(--paper), 0 0 0 3px var(--ink); }
.head .pal.dots i { display: block; width: 14px; height: 14px; border-radius: 50%; box-shadow: 0 0 0 1px var(--line); transition: box-shadow .2s; }
.sr-name { position: absolute; width: 1px; height: 1px; overflow: hidden; clip-path: inset(50%); white-space: nowrap; }
@media (max-width: 1100px) { .head .pal.dots .paln { display: none; } .head .pal.dots { padding-left: 4px; } }
@media (max-width: 700px) { .head .pal.dots button { padding: 3px; } .head .pal.dots i { width: 13px; height: 13px; } }
'''
once('</style>', css + '</style>')

# 3D story colours
once("let pal = 'nacre';", "Object.assign(PAL, " + json.dumps({p['id']: p['story'] for p in P}) + ");\nlet pal = 'nacre';")

# the wallpaper reads its colours per palette
walls = {'nacre': {'a': '#C99BB0', 'b': '#B8A7C9', 'ink': '#2B2230'}, 'tidepool': {'a': '#F2B84B', 'b': '#7FC4B0', 'ink': '#EAF3EF'}}
walls.update({p['id']: p['wall'] for p in P})
once("function readCol() { var tide = root.getAttribute('data-palette') === 'tidepool'; return tide ? { a: hexToRgb('#F2B84B'), b: hexToRgb('#7FC4B0'), ink: hexToRgb('#EAF3EF') } : { a: hexToRgb('#C99BB0'), b: hexToRgb('#B8A7C9'), ink: hexToRgb('#2B2230') }; }",
     "var WALLS = " + json.dumps(walls) + ";\n  function readCol() { var w = WALLS[root.getAttribute('data-palette')] || WALLS.nacre; return { a: hexToRgb(w.a), b: hexToRgb(w.b), ink: hexToRgb(w.ink) }; }")

# the header switch, top right as before: each dot is the palette's ground with its clasp colour
allp = HOUSE + P
label = lambda p: p['name'] + (f' (option {p["option"]})' if 'option' in p else '')
btns = ''.join(f'<button type="button" data-pal="{p["id"]}" aria-pressed="{str(p["id"] == "nacre").lower()}" title="{label(p)}">'
               f'<i aria-hidden="true" style="background:linear-gradient(135deg,{p["css"]["paper"]} 50%,{p["css"]["clasp"]} 50%)"></i>'
               f'<span class="sr-name">{label(p)}</span></button>' for p in allp)
once('<div class="pal" role="group" aria-label="Palette"><button type="button" data-pal="nacre" aria-pressed="true">Nacre</button><button type="button" data-pal="tidepool" aria-pressed="false">Tidepool</button></div></header>',
     f'<div class="pal dots" role="group" aria-label="Palette"><span class="paln" id="paln" aria-hidden="true">Nacre</span>{btns}</div></header>')
names = {p['id']: p['name'] for p in allp}
once('\nwindow.__story = {', '''
// ---------- palette switch: name of the current palette, and ?palette=<id> to link to one ----------
(() => {
  const NAMES = ''' + json.dumps(names) + ''', paln = document.getElementById('paln');
  const show = () => { const k = root.getAttribute('data-palette') || 'nacre'; paln.textContent = NAMES[k] || '';
    try { history.replaceState(null, '', '?palette=' + k + location.hash); } catch (e) {} };
  new MutationObserver(show).observe(root, { attributes: true, attributeFilter: ['data-palette'] });
  const want = new URLSearchParams(location.search).get('palette'), b = want && document.querySelector('.pal button[data-pal="' + want + '"]');
  if (b) b.click(); else show();
})();
\nwindow.__story = {''')
once('<title>Oyster Therapeutics</title>', '<title>Oyster Palettes</title>')
open(D + 'palettes.html', 'w').write(h)
print('palettes.html', len(h) // 1024, 'KB,', len(allp), 'palettes')
