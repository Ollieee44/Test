"""Build palettes.html: the current site (index.html, left untouched) with the alternative palettes
from palettes.json added beside Nacre and Tidepool, and a palette explorer in place of the header
switch. Open with ?palette=<id> to start on one. Run build_site.py first."""
import json, os
D = os.path.dirname(os.path.abspath(__file__)) + '/'
h = open(D + 'index.html').read()
P = json.load(open(D + 'palettes.json'))['palettes']

def once(old, new):
    global h
    assert h.count(old) >= 1, old[:60]
    h = h.replace(old, new, 1)

# the two house palettes, as the explorer shows them
HOUSE = [
    {'id': 'nacre', 'name': 'Nacre', 'idea': 'House light palette: pearl pinks, mauve ink, gold clasp.',
     'css': {'paper': '#EFE6E1', 'ink': '#2B2230', 'accent': '#8C5572', 'clasp': '#D9A443'}},
    {'id': 'tidepool', 'name': 'Tidepool', 'idea': 'House dark palette: deep teal with gold, coral clasp.',
     'css': {'paper': '#0F4C4A', 'ink': '#EAF3EF', 'accent': '#F2B84B', 'clasp': '#F27D62'}},
]

# page tokens and the team monograms
css = ''
for p in P:
    c = p['css']
    css += (f':root[data-palette="{p["id"]}"] {{ --ink: {c["ink"]}; --muted: {c["muted"]}; --accent: {c["accent"]}; --paper: {c["paper"]}; '
            f'--band: {c["band"]}; --pearl: {c["pearl"]}; --clasp: {c["clasp"]}; --line: {c["line"]}; --card: {c["card"]}; '
            f'color-scheme: {"dark" if p["dark"] else "light"}; }}\n'
            f':root[data-palette="{p["id"]}"] .mono {{ color: {p["mono"]}; border-color: {p["mono"]}; }}\n')
css += '''/* palette explorer */
.head > .pal { display: none; }
.palx { position: fixed; z-index: 30; left: 50%; bottom: calc(16px + env(safe-area-inset-bottom, 0px)); transform: translateX(-50%); width: min(720px, calc(100vw - 32px));
  background: color-mix(in srgb, var(--paper) 88%, transparent); -webkit-backdrop-filter: blur(14px); backdrop-filter: blur(14px);
  border: 1px solid var(--line); border-radius: 18px; padding: 10px 12px 12px; box-shadow: 0 10px 40px rgba(0, 0, 0, .14); color: var(--ink); transition: background-color .6s; }
.palx .row { display: flex; border: 0; padding: 0; border-radius: 0; gap: 4px; overflow-x: auto; scrollbar-width: none; }
.palx button { flex: 1 0 auto; display: flex; align-items: center; gap: 8px; font: 500 12.5px/1 var(--sans); border: 0; background: transparent; color: var(--ink);
  padding: 8px 10px; border-radius: 999px; cursor: pointer; white-space: nowrap; }
.palx button:hover:not([aria-pressed="true"]) { background: color-mix(in srgb, var(--ink) 9%, transparent); }
.palx button[aria-pressed="true"] { background: var(--ink); color: var(--paper); }
.palx button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.palx .sw { display: inline-flex; }
.palx .sw i { width: 12px; height: 12px; border-radius: 50%; margin-left: -3px; box-shadow: 0 0 0 1.5px var(--paper), 0 0 0 2.5px var(--line); }
.palx .sw i:first-child { margin-left: 0; }
.palx p { margin: 8px 6px 0; font-size: 13px; line-height: 1.4; color: var(--muted); }
.palx p b { font: 500 11px/1 var(--mono); letter-spacing: .12em; text-transform: uppercase; color: var(--accent); margin-right: 8px; }
.palx .x { position: absolute; top: -12px; right: 10px; flex: none; padding: 5px 9px; font-size: 11px; background: var(--paper); border: 1px solid var(--line); }
.palx.min p, .palx.min .row span.nm { display: none; }
@media (max-width: 700px) { .palx p { font-size: 12px; } .palx button { padding: 7px 8px; } .palx .row span.nm { display: none; } .palx button { flex: 1 1 0; min-width: 0; padding: 7px 2px; justify-content: center; } .palx .sw i { width: 10px; height: 10px; } }
'''
once('</style>', css + '</style>')

# 3D story colours
story = {p['id']: p['story'] for p in P}
once("let pal = 'nacre';", "Object.assign(PAL, " + json.dumps(story) + ");\nlet pal = 'nacre';")

# the wallpaper reads its colours per palette
walls = {'nacre': {'a': '#C99BB0', 'b': '#B8A7C9', 'ink': '#2B2230'}, 'tidepool': {'a': '#F2B84B', 'b': '#7FC4B0', 'ink': '#EAF3EF'}}
walls.update({p['id']: p['wall'] for p in P})
old = "function readCol() { var tide = root.getAttribute('data-palette') === 'tidepool'; return tide ? { a: hexToRgb('#F2B84B'), b: hexToRgb('#7FC4B0'), ink: hexToRgb('#EAF3EF') } : { a: hexToRgb('#C99BB0'), b: hexToRgb('#B8A7C9'), ink: hexToRgb('#2B2230') }; }"
once(old, "var WALLS = " + json.dumps(walls) + ";\n  function readCol() { var w = WALLS[root.getAttribute('data-palette')] || WALLS.nacre; return { a: hexToRgb(w.a), b: hexToRgb(w.b), ink: hexToRgb(w.ink) }; }")

# the explorer: one button per palette, a line on the idea behind the selected one
allp = HOUSE + P
btns = ''.join(f'<button type="button" data-pal="{p["id"]}" aria-pressed="{str(p["id"] == "nacre").lower()}">'
               f'<span class="sw" aria-hidden="true">' + ''.join(f'<i style="background:{p["css"][k]}"></i>' for k in ('paper', 'ink', 'accent', 'clasp')) +
               f'</span><span class="nm">{p["name"]}</span></button>' for p in allp)
panel = (f'<div class="palx" id="palx"><button type="button" class="x" id="palxMin" aria-expanded="true">Hide notes</button>'
         f'<div class="row pal" role="group" aria-label="Palette">{btns}</div><p id="palxIdea" aria-live="polite"></p></div>\n')
once('<main>', panel + '<main>')
ideas = {p['id']: [p['name'], p['idea']] for p in allp}
js = ('''
// ---------- palette explorer ----------
(() => {
  const IDEAS = ''' + json.dumps(ideas) + ''', px = document.getElementById('palx'), idea = document.getElementById('palxIdea'), min = document.getElementById('palxMin');
  const show = () => { const k = root.getAttribute('data-palette') || 'nacre', v = IDEAS[k]; idea.innerHTML = '<b>' + v[0] + '</b>' + v[1];
    try { history.replaceState(null, '', '?palette=' + k + location.hash); } catch (e) {} };
  new MutationObserver(show).observe(root, { attributes: true, attributeFilter: ['data-palette'] });
  min.addEventListener('click', () => { const m = px.classList.toggle('min'); min.textContent = m ? 'Show notes' : 'Hide notes'; min.setAttribute('aria-expanded', String(!m)); });
  const want = new URLSearchParams(location.search).get('palette'), b = want && px.querySelector('button[data-pal="' + want + '"]');
  if (b) b.click(); else show();
})();
''')
once('\nwindow.__story = {', js + '\nwindow.__story = {')
h = h.replace('<title>Oyster Therapeutics</title>', '<title>Oyster Palettes</title>', 1)
open(D + 'palettes.html', 'w').write(h)
print('palettes.html', len(h) // 1024, 'KB,', len(allp), 'palettes')
