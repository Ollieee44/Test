"""Build catalogue.html, the Oyster Mark Catalogue: every mark drawn for the project, once each,
numbered by family (group.item), in both palettes, with a link to the sheet it came from.

Marks are drawn from the same code as their sheets, each module under its own id prefix so masks
never collide. Run after any change to a mark module.
"""
import os, re
import marks, refine, frontal, threequarter, hinged, refs, riffs, linepearl

D = os.path.dirname(os.path.abspath(__file__)) + '/'
ART = 'https://claude.ai/artifact/'
SHEETS = {
    'first': (ART + 'PKcMKiixVGjLF587ERBM69', 'Oyster Brand Mark'),
    'variations': (ART + '7nbPJzaNZTv9pXDPZftmnP', 'Oyster Mark Variations'),
    'beads': (ART + '6ppVB3x6LGVpwS36p4kHZh', 'Oyster Bead Marks'),
    'refine': (ART + 'TYDiqpmFntUpWcALworY7g', 'Inside Out, Refined'),
    'frontal': (ART + 'H9Kr4y1ZRdNsRYhnCf1NKf', 'Beyond the Compact'),
    'open': (ART + '3XER9VkRqams9ryoFciMjb', 'Open Oyster'),
    'openpick': (ART + 'JCZmPkni1P6zVMZuQHMMFY', 'Open Oyster Picks'),
    'hinged': (ART + 'N8uzWVpwns4Skux3XkmCYy', 'Two Valves, One Hinge'),
    'refs': (ART + 'ACn2XP8bzFsQJVb5d5DKyb', 'From the References'),
    'riffs': (ART + 'S2YScwuN6szkQzeQ2rex7Y', 'Fan and Pearl Riffs'),
    'linepearl': (ART + '4zMWE6ipDqHpULNFiJG8os', 'Line Fan, Pearl Sizes'),
    'linepick': (ART + '4gdAYgpeD5UJzm2T1zwqw1', 'Line Fan, Inside Out'),
}

# ---------- the marks, as (masks, symbols) under a prefix each ----------
DEFS, SYM = [], {}
def take(prefix, masks, syms):
    DEFS.extend(masks.values() if isinstance(masks, dict) else masks)
    for k, v in syms.items(): SYM[f'{prefix}-{k}'] = v

m, s, _ = marks.marks('va-'); take('va', m, s)
for pre, mod in (('rf', refine), ('fr', frontal), ('tq', threequarter), ('hg', hinged), ('rs', refs), ('rr', riffs), ('lp', linepearl)):
    mm, ss = mod.build(pre + '-'); take(pre, mm, ss)
# the bead marks live only in beads.html: take its defs and prefix their ids
bd = re.search(r'<svg width="0" height="0"[^>]*>.*?</svg>', open(D + 'beads.html').read(), re.S).group(0)
bd = bd.replace('id="mHinge"', 'id="bd-mHinge"').replace('url(#mHinge)', 'url(#bd-mHinge)')
DEFS.extend(re.findall(r'<mask .*?</mask>', bd, re.S))
for k, v in re.findall(r'<symbol id="b-([^"]+)" viewBox="0 0 100 100"><g transform="translate\(-1\.5 1\.5\)">(.*?)</g></symbol>', bd, re.S):
    SYM[f'bd-{k}'] = v
# the two alternatives drawn alongside the very first mark (they had no code of their own)
SYM['first-rings'] = ('<g transform="translate(1.5 -1.5)"><g fill="none" stroke="currentColor"><circle cx="50" cy="50" r="41" stroke-width="7"/>'
                      '<circle cx="55" cy="46" r="27" stroke-width="3"/><circle cx="58" cy="44" r="16" stroke-width="1.6"/></g>'
                      '<circle cx="60" cy="43" r="7" style="fill:var(--p1)"/></g>')
SYM['first-halves'] = ('<g transform="translate(1.5 -1.5)"><path style="fill:var(--p1)" d="M43 8 A38 38 0 0 0 43 84 Z"/>'
                       '<path style="fill:var(--p2)" d="M57 16 A38 38 0 0 1 57 92 Z"/></g>')

# ---------- the catalogue: groups of (id, name, note, sheet, second accent, tag) ----------
CLASP, LILAC = 'clasp', 'lilac'
GROUPS = [
 ('First routes', 'The three directions drawn at the start. The Open Shell was chosen and became the base for everything after.', [
   ('va-open', 'The Open Shell', 'Two valves, a hinge gap and a pearl: the original mark.', 'first', CLASP, ''),
   ('first-rings', 'Nacre Rings', 'Growth lines forming an O.', 'first', CLASP, ''),
   ('first-halves', 'Pearl Halves', 'A sphere made from two halves.', 'first', LILAC, '')]),
 ('Open Shell variations', 'The side-view shell with a cradle cut for the pearl, and one idea added to each.', [
   ('va-hollow', 'The Hollow', 'The pearl sits in a round hollow in the lower shell.', 'variations', CLASP, ''),
   ('va-layers', 'Nacre', 'The lower shell sliced by nacre layers.', 'variations', CLASP, ''),
   ('va-halves', 'Two Halves', 'The pearl as two half-discs in the two accents.', 'variations', LILAC, ''),
   ('va-strand', 'Pearl on a Strand', 'Beads grow from the hinge into the pearl.', 'variations', CLASP, '')]),
 ('Bead linker', 'The SELFTAC molecule&rsquo;s bead linker brought into the side-view shell.', [
   ('bd-hinge', 'Bead Hinge', 'The hinge replaced by a chain of beads.', 'beads', CLASP, ''),
   ('bd-strand', 'Pearl on a Strand, Beaded', 'Graduated beads lead to the pearl.', 'beads', CLASP, ''),
   ('bd-linked', 'Two Halves, Linked', 'Two half-pearls joined by a bead linker.', 'beads', LILAC, ''),
   ('bd-ring', 'Bead Ring', 'A ring of beads as the O, the shell inside.', 'beads', LILAC, ''),
   ('bd-valve', 'Beaded Valve', 'The upper shell rebuilt as beads.', 'beads', CLASP, '')]),
 ('Inside Out (disc, side view)', 'A solid disc with the side-view shell cut out of it: the live mark and its refinements.', [
   ('va-inside', 'Inside Out', 'The live mark: the o of the logotype, the favicon and the header.', 'variations', CLASP, 'Live'),
   ('rf-seam', 'Clasped Pearl', 'The pearl as two halves held by a clasp band.', 'refine', CLASP, ''),
   ('rf-clasp', 'The Clasp', 'Two clasp pearls and their bond in a long cradle.', 'refine', CLASP, ''),
   ('rf-large', 'Larger Shell', 'The shell bigger, the rim thinner.', 'refine', CLASP, ''),
   ('rf-wide', 'Wider Mouth', 'The shell opened wider, a bigger pearl.', 'refine', CLASP, ''),
   ('rf-small', 'Small-size Cut', 'A favicon companion: no cradle ring, a big pearl.', 'refine', CLASP, ''),
   ('fr-rough', 'Shell Edge', 'The disc&rsquo;s perfect circle made lumpy, like a shell.', 'frontal', CLASP, ''),
   ('fr-ruffle', 'Ruffled Lips', 'The straight lips of both shells frilled.', 'frontal', CLASP, ''),
   ('fr-both', 'Edge and Ruffles', 'A shell-edged disc and frilled lips.', 'frontal', CLASP, '')]),
 ('Valve from above', 'A single oyster valve seen from above, with growth lines fanning from the hinge.', [
   ('fr-valve', 'Front-on Valve', 'The teardrop valve, its frilled lip and the pearl in the cup.', 'frontal', CLASP, ''),
   ('fr-valvedisc', 'Front-on, in the Disc', 'The valve drawn into the disc as cut lines.', 'frontal', CLASP, '')]),
 ('Open oyster, three-quarter', 'Both valves open, seen from a slight angle: we look into the bowl and the hollow of the upper valve.', [
   ('tq-open', 'Open Oyster', 'Smooth valves, the pearl in the cup.', 'open', CLASP, ''),
   ('tq-frilled', 'Open Oyster, Frilled', 'Frilled lips on both valves.', 'open', CLASP, ''),
   ('tq-frilled2', 'Frilled, Eye Fixed', 'The pearl moved onto the front lip.', 'openpick', CLASP, ''),
   ('tq-backed', 'Shell Behind', 'The upper valve solid, with growth lines.', 'open', CLASP, ''),
   ('tq-disc', 'Open Oyster, in the Disc', 'The open oyster cut into the disc.', 'open', CLASP, ''),
   ('tq-low', 'Lower Angle', 'Closer to front-on, more of the upper valve showing.', 'open', CLASP, ''),
   ('tq-low2', 'Lower Angle, Eye Fixed', 'The pearl moved onto the front lip.', 'openpick', CLASP, '')]),
 ('Two valves, one hinge', 'Teardrop oyster valves meeting at one hinge, blending the two references.', [
   ('hg-upright', 'Upright', 'The upper valve standing behind, a dish in front.', 'hinged', CLASP, ''),
   ('hg-book', 'Open Book', 'Mirror-image valves opening from one beak.', 'hinged', CLASP, ''),
   ('hg-cup', 'Deep Cup', 'A deep lower cup and a smaller upper valve.', 'hinged', CLASP, ''),
   ('hg-bigpearl', 'Big Pearl', 'A solid upper valve and the biggest pearl.', 'hinged', CLASP, '')]),
 ('Half shell (the painting)', 'One half shell seen three-quarter, drawn closely from the painting.', [
   ('rs-half', 'Half Shell', 'A deep cup, a thick front rim and a tinted inner wall.', 'refs', CLASP, ''),
   ('rs-rough', 'Half Shell, Rough Rim', 'The painting&rsquo;s chipped rim.', 'refs', CLASP, ''),
   ('rs-shadow', 'Half Shell, with Shadow', 'Resting on its cast shadow.', 'refs', CLASP, '')]),
 ('Fan and pearl, solid', 'Front-on, from the second reference: the upper valve as a fan, a dish in front, a big pearl.', [
   ('rs-ribbed', 'Fan and Pearl', 'B1: the fan with its ribs.', 'refs', CLASP, ''),
   ('rs-scalloped', 'Fan and Pearl, Scalloped', 'B2: the ribs carried by the edge.', 'refs', CLASP, ''),
   ('rs-smooth', 'Fan and Pearl, Smooth', 'B3: a smooth fan.', 'refs', CLASP, ''),
   ('rr-bold', 'Bold Ribs', 'Five deep grooves.', 'riffs', CLASP, ''),
   ('rr-strands', 'Pearl Strands', 'Each rib a string of pearls.', 'riffs', CLASP, ''),
   ('rr-growth', 'Growth Lines', 'An oyster&rsquo;s growth lines instead of ribs.', 'riffs', CLASP, ''),
   ('rr-frilled', 'Oyster Lip', 'B3 with an uneven, oyster edge.', 'riffs', CLASP, ''),
   ('rr-clasped', 'Clasped Pearl', 'The pearl as two halves held by the clasp.', 'riffs', CLASP, ''),
   ('rr-rays', 'Rays', 'Ribs as light coming off the pearl.', 'riffs', CLASP, '')]),
 ('Fan and pearl, line', 'The fan and pearl drawn as one even line, at five pearl sizes.', [
   ('rr-line', 'Line (R7)', 'The first line version, nine ribs.', 'riffs', CLASP, ''),
   ('lp-line-xs', 'Line, Pearl 60%', 'The smallest pearl; the shell leads.', 'linepearl', CLASP, ''),
   ('lp-line-s', 'Line, Pearl 80%', 'The chosen pearl size.', 'linepearl', CLASP, 'Favourite'),
   ('lp-line-m', 'Line, Pearl 100%', 'Even ribs between the fan&rsquo;s sides.', 'linepearl', CLASP, ''),
   ('lp-line-l', 'Line, Pearl 125%', 'The pearl rising over the fan.', 'linepearl', CLASP, ''),
   ('lp-line-xl', 'Line, Pearl 150%', 'The reference&rsquo;s proportions.', 'linepearl', CLASP, '')]),
 ('Fan and pearl, inside out', 'The fan and pearl cut out of the solid disc, so the logotype keeps a round o.', [
   ('rr-disc', 'Inside Out Fan', 'The smooth fan cut out of the disc.', 'riffs', CLASP, ''),
   ('lp-io-s', 'Inside Out Line, 80%', 'The line drawing in the disc, small.', 'linepearl', CLASP, ''),
   ('lp-io-m', 'Inside Out Line, 100%', 'With R7&rsquo;s pearl.', 'linepearl', CLASP, ''),
   ('lp-io-l', 'Inside Out Line, 125%', 'With the larger pearl.', 'linepearl', CLASP, ''),
   ('lp-io-s-rim7', '80%, Rim 7', 'Enlarged to fill the disc, a comfortable rim.', 'linepick', CLASP, 'Latest'),
   ('lp-io-s-rim5', '80%, Rim 5', 'Enlarged to fill the disc, a balanced rim.', 'linepick', CLASP, 'Latest'),
   ('lp-io-s-rim35', '80%, Rim 3.5', 'Enlarged to fill the disc, the tightest rim.', 'linepick', CLASP, 'Latest')]),
]
COL = {'nacre': ('#EFE6E1', '#2B2230', '#C99BB0', {CLASP: '#D9A443', LILAC: '#B8A7C9'}),
       'tide': ('#0F4C4A', '#EAF3EF', '#F2B84B', {CLASP: '#F27D62', LILAC: '#7FC4B0'})}

used = {i for _, _, items in GROUPS for i, *_ in items}
missing = used - set(SYM); assert not missing, missing

def mark(id, pal, acc, size=96, label=''):
    bg, ink, p1, p2 = COL[pal]; p2 = p2[acc]
    aria = f'role="img" aria-label="{label}"' if label else 'aria-hidden="true"'
    return (f'<svg class="mk" width="{size}" height="{size}" viewBox="0 0 100 100" style="color:{ink};fill:currentColor;--p1:{p1};--p2:{p2}" {aria}>'
            f'<use href="#{id}"/></svg>')

defs = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>' + ''.join(DEFS) + '</defs>'
        + ''.join(f'<symbol id="{k}" viewBox="0 0 100 100"><g transform="translate(-1.5 1.5)">{v}</g></symbol>' for k, v in SYM.items() if k in used)
        + '</svg>')

nav, body, total = '', '', 0
for g, (title, intro, items) in enumerate(GROUPS, 1):
    gid = f'g{g}'; total += len(items)
    nav += f'<a href="#{gid}"><b>{g}</b>{title}<span>{len(items)}</span></a>'
    cards = ''
    for n, (id, name, note, sheet, acc, tag) in enumerate(items, 1):
        url, sname = SHEETS[sheet]
        tagh = f'<span class="tag {tag.lower()}">{tag}</span>' if tag else ''
        cards += (f'<article class="card" id="m{g}-{n}"><div class="sw"><div class="t n">{mark(id, "nacre", acc, label=f"{g}.{n} {name}")}</div>'
                  f'<div class="t d">{mark(id, "tide", acc)}</div></div>'
                  f'<div class="meta"><div class="row"><span class="no">{g}.{n}</span>{tagh}</div><h3>{name}</h3><p>{note}</p>'
                  f'<a class="src" href="{url}" target="_blank" rel="noopener">{sname}</a></div></article>')
    body += f'<section class="grp" id="{gid}"><header><span class="gno">{g}</span><div><h2>{title}</h2><p>{intro}</p></div></header><div class="cards">{cards}</div></section>'

CSS = '''
:root { --bg: #F3EEEB; --surface: #FBF8F6; --ink: #241D28; --muted: #6A5E6C; --line: rgba(36,29,40,.13); --accent: #8C5572;
  --serif: "Newsreader", Georgia, serif; --sans: "Archivo", "Helvetica Neue", Arial, sans-serif; --mono: "IBM Plex Mono", ui-monospace, Menlo, monospace; color-scheme: light; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --bg: #17131A; --surface: #211C25; --ink: #EFE6E1; --muted: #B3A6B4; --line: rgba(239,230,225,.13); --accent: #D9AFC2; color-scheme: dark; } }
:root[data-theme="dark"] { --bg: #17131A; --surface: #211C25; --ink: #EFE6E1; --muted: #B3A6B4; --line: rgba(239,230,225,.13); --accent: #D9AFC2; color-scheme: dark; }
* { box-sizing: border-box; }
html { scroll-padding-top: 76px; }
body { margin: 0; background: var(--bg); color: var(--ink); font: 400 16px/1.55 var(--sans); -webkit-font-smoothing: antialiased; }
.wrap { max-width: 1280px; margin: 0 auto; padding-inline: clamp(16px, 4vw, 48px); }
h1, h2, h3 { font-family: var(--serif); font-weight: 500; letter-spacing: -.012em; margin: 0; text-wrap: balance; }
p { margin: 0; }
.eyebrow { font: 500 11px/1 var(--mono); letter-spacing: .12em; text-transform: uppercase; color: var(--muted); }
header.top { padding-block: clamp(44px, 7vw, 84px) 28px; }
header.top h1 { font-size: clamp(40px, 5.6vw, 72px); line-height: 1.02; margin-top: 12px; }
header.top p { color: var(--muted); max-width: 64ch; margin-top: 16px; font-size: clamp(16px, 1.4vw, 19px); }
nav.idx { position: sticky; top: 0; z-index: 5; background: color-mix(in srgb, var(--bg) 92%, transparent); backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px); border-block: 1px solid var(--line); }
nav.idx .wrap { display: flex; gap: 6px; overflow-x: auto; padding-block: 10px; scrollbar-width: thin; }
nav.idx a { flex: none; display: inline-flex; align-items: center; gap: 8px; padding: 7px 12px; border-radius: 999px; border: 1px solid var(--line); color: var(--ink); text-decoration: none; font-size: 13px; white-space: nowrap; transition: background-color .2s; }
nav.idx a:hover { background: var(--surface); }
nav.idx a:focus-visible, .src:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
nav.idx b { font: 500 11px/1 var(--mono); color: var(--accent); }
nav.idx span { font: 400 11px/1 var(--mono); color: var(--muted); }
.grp { padding-block: clamp(40px, 6vw, 72px) 8px; }
.grp > header { display: grid; grid-template-columns: 52px 1fr; gap: 16px; align-items: start; margin-bottom: 24px; }
.gno { width: 44px; height: 44px; border-radius: 50%; display: grid; place-items: center; font: 500 15px/1 var(--mono); background: var(--surface); border: 1px solid var(--line); }
.grp h2 { font-size: clamp(26px, 3vw, 38px); line-height: 1.1; }
.grp > header p { color: var(--muted); margin-top: 6px; max-width: 70ch; }
.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 232px), 1fr)); gap: 14px; }
.card { background: var(--surface); border: 1px solid var(--line); border-radius: 18px; overflow: hidden; display: flex; flex-direction: column; min-width: 0; }
.sw { display: grid; grid-template-columns: 1fr 1fr; }
.t { display: grid; place-items: center; padding: 20px 8px; }
.t.n { background: #EFE6E1; } .t.d { background: #0F4C4A; }
.mk { width: 100%; max-width: 96px; height: auto; }
.meta { padding: 14px 16px 16px; display: grid; gap: 4px; }
.row { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.no { font: 500 13px/1 var(--mono); color: var(--accent); letter-spacing: .04em; }
.tag { font: 500 10px/1 var(--mono); letter-spacing: .1em; text-transform: uppercase; padding: 5px 8px; border-radius: 999px; background: var(--accent); color: var(--surface); }
.tag.live { background: #2F6B5E; color: #fff; }
.card h3 { font-size: 19px; line-height: 1.2; }
.card p { color: var(--muted); font-size: 14px; }
.src { margin-top: 4px; font: 400 12px/1.3 var(--mono); color: var(--muted); text-decoration: underline; text-underline-offset: 3px; text-decoration-color: var(--line); width: fit-content; }
.src:hover { color: var(--ink); text-decoration-color: currentColor; }
@media (max-width: 560px) {   /* two cards a row on phones, so 59 marks are not one long column */
  .cards { grid-template-columns: 1fr 1fr; gap: 10px; }
  .t { padding: 12px 4px; } .meta { padding: 10px 10px 12px; } .card h3 { font-size: 16px; } .card p { font-size: 13px; }
  .row { flex-wrap: wrap; } .src { font-size: 11px; }
}
footer { margin-top: 56px; padding-block: 32px 48px; border-top: 1px solid var(--line); color: var(--muted); font-size: 14px; }
'''
html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<!-- artifact:start -->
<title>Oyster Mark Catalogue</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=swap">
<style>{CSS}</style>
</head>
<body>
{defs}
<header class="top"><div class="wrap">
  <span class="eyebrow">Oyster Therapeutics &middot; Brand mark</span>
  <h1>Oyster Mark Catalogue</h1>
  <p>Every mark drawn for Oyster, {total} in all, each shown once in Nacre and Tidepool. They are grouped by design type and numbered group.item, so any mark can be named by its number (for example 11.6). Each card links to the sheet where it was first shown in full, with lockups, sizes and notes.</p>
</div></header>
<nav class="idx" aria-label="Groups"><div class="wrap">{nav}</div></nav>
<main class="wrap">{body}</main>
<footer><div class="wrap">Built by <code>oyster/brand/build_catalogue.py</code> from the same code as each sheet. Live marks the mark in use on the website; Favourite and Latest mark the current direction.</div></footer>
<!-- artifact:end -->
</body>
</html>
'''
open(D + 'catalogue.html', 'w').write(html)
print('catalogue.html', len(html), total, 'marks in', len(GROUPS), 'groups')
