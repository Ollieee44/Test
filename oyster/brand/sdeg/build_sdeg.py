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
S_T = 'translate(949.8 0.0) scale(0.5000 -0.5000)'

def _arch_lt():
    """The Archivo logotype (brand/oyster-logotype-tidepool.svg) recoloured through currentColor, with the
    new fan mark (11.7) from the Newsreader logotype put in its mark box (both marks share the same box)."""
    a = open(D + '../oyster-logotype-tidepool.svg').read()
    head = '<g transform="translate(-17.1 -583.4) scale(6.3571)">'
    # each mark group closes just before the y's outline
    i = LT.index(head) + len(head); j = LT.rfind('</g><path d=', 0, LT.index('transform="translate(488.1 0.0)'))
    fan = LT[i:j]
    a_head = '<g transform="translate(-14.4 -600.2) scale(6.5476)">'
    k = a.index(a_head) + len(a_head); m = a.rfind('</g><path d=', 0, a.index('transform="translate(530.6 0.0)'))
    a = a[:k] + fan + a[m:]
    a = a.replace('fill="#0F4C4A"', 'fill="currentColor"')
    return re.sub(r'<svg[^>]*?(viewBox="[^"]+")[^>]*>', r'<svg class="lt" \1>', a, count=1)

FACES = {'news': (LT, S_T, '-110 -1110 1010 1180'),
         'arch': (_arch_lt(), 'translate(986.6 0.0) scale(1.0000 -1.0000)', '-60 -575 650 650')}

def _font_lt(key):
    """The logotype re-set in another face: that face's "yster" (from fonts.json, scaled so its s matches the
    Newsreader s's height) on default spacing, the y's ink starting where the Newsreader y's does, and
    "therapeutics" moved to keep its place under the y's tail. Kerning is not applied."""
    g = sdeg.FONTS[key]['glyphs']; lt = LT
    news = re.findall(r'<path d="([^"]*)" transform="translate\(([\d.]+) 0\.0\) scale\(0\.5000 -0\.5000\)"/>', LT)
    y_left = float(news[0][1]) + .5 * sdeg.sgeom.polygon(news[0][0])[:, 0].min()
    x = y_left - .5 * g['y']['x0']; letters = ''; s_t = None
    for ch in 'yster':
        t = f'translate({x:.1f} 0.0) scale(0.5000 -0.5000)'
        if ch == 's': s_t = t
        if ch == 'y': y_end = x + .5 * g['y']['adv']
        letters += f'<path d="{g[ch]["d"]}" transform="{t}"/>'; end = x + .5 * g[ch]['x1']; x += .5 * g[ch]['adv']
    i = lt.index(f'<path d="{news[0][0]}"'); j = lt.index('/>', lt.index(f'<path d="{news[-1][0]}"')) + 2
    lt = lt[:i] + letters + lt[j:]
    dx = y_end - float(news[1][1])           # the Newsreader y ends where its s begins
    lt = re.sub(r'translate\(([\d.]+) ([\d.]+)\) scale\(0\.1200', lambda m: f'translate({float(m.group(1)) + dx:.1f} {m.group(2)}) scale(0.1200', lt)
    lt = re.sub(r'viewBox="([-\d.]+) ([-\d.]+) [\d.]+ ([\d.]+)"', lambda m: f'viewBox="{m.group(1)} {m.group(2)} {end + 30 - float(m.group(1)):.1f} {m.group(3)}"', lt, count=1)
    cx = .5 * (g['s']['x0'] + g['s']['x1'])
    return lt, s_t, f'{cx - 505:.0f} -1110 1010 1180'

for _k in sdeg.FONTS:
    FACES[_k] = _font_lt(_k)

def logotype(fn, ns):
    lt, st, _ = FACES[getattr(fn, 'lt_face', getattr(fn, 'face', 'news'))]
    el = re.search(r'<path d="[^"]*" transform="' + re.escape(st) + '"/>', lt).group(0)
    s = lt.replace(el, f'<g transform="{st}">{fn(ns + "s")}</g>')
    for i in set(re.findall(r'id="([^"]+)"', lt)):
        s = s.replace(f'id="{i}"', f'id="{ns}{i}"').replace(f'url(#{i})', f'url(#{ns}{i})')
    return re.sub(r'<svg class="lt"[^>]*?(viewBox="[^"]+")[^>]*>', r'<svg class="lt" \1 aria-hidden="true">', s, count=1)

def big(fn, ns):
    return f'<svg class="big" viewBox="{FACES[getattr(fn, "face", "news")][2]}" aria-hidden="true"><g transform="scale(1 -1)" fill="currentColor">{fn(ns)}</g></svg>'

def construction():
    """The traced centreline, the spine's middle and the two shoulders over the outline."""
    line = sdeg.pts(sdeg.C); dots = ''
    for s, lab in ((sdeg.S_TOP, 'shoulder'), (sdeg.S_MID, 'middle'), (sdeg.S_BOT, 'shoulder')):
        p, t, n, w = sdeg.at(s); a, b = p + n * w, p - n * w
        dots += (f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="var(--clasp)" stroke-width="8"/>'
                 f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="14" fill="var(--clasp)"/>')
    return (f'<svg class="big" viewBox="-110 -1110 1010 1180" aria-hidden="true"><g transform="scale(1 -1)">'
            f'<path d="{sdeg.D}" fill="currentColor" opacity=".18"/><polyline points="{line}" fill="none" stroke="currentColor" stroke-width="6"/>{dots}</g></svg>')

NOTES = {
    'fraunces': 'Serif. Soft and warm, with rounded terminals; the halves keep a friendly weight.',
    'sourceserif': 'Serif. Sturdier and lower in contrast than Newsreader, so the two halves stay even.',
    'literata': 'Serif. Bookish and close to the current face, but calmer; the nearest like-for-like swap.',
    'lora': 'Serif. Calligraphic, with flared terminals; more personality, less clinical.',
    'youngserif': 'Serif. Heavy and soft; the clasp stays legible at header size.',
    'dmserif': 'Serif. High contrast like Newsreader, so the cut s edges back towards the apple core.',
    'instrument': 'Serif. Condensed and elegant; the clasp gets small at header size.',
    'inter': 'Sans. Neutral and clean; the split reads as two simple hooks.',
    'dmsans': 'Sans. Geometric and friendly, with an open s.',
    'manrope': 'Sans. Modern, slightly rounded geometric; even halves.',
    'plexsans': 'Sans. Technical and scientific in tone, with angled terminals.',
    'spacegrotesk': 'Sans. Quirky and techy; the most start-up of the set.',
    'sora': 'Sans. Wide and geometric; the s is broad, which suits the clasp.',
    'outfit': 'Sans. Round geometric; light-hearted, the least pharma of the set.',
    'arch': 'Sans. The Tidepool logotype&rsquo;s face.',
}
FONT_CARDS = [('', '08 in other faces', 'The same treatment, the seam eased apart with the clasp in the pearl colour, on the s of other faces. Each is drawn from the font&rsquo;s own outlines, scaled to the height of the current s, and set in the logotype on the font&rsquo;s default spacing (no kerning or optical spacing yet, which the current logotype has). Serifs first, then sans.', None),
              ('08', 'Newsreader 500 (current)', 'The logotype&rsquo;s face, for reference.', sdeg.v_seam_apart)]
for n, (key, v) in enumerate(sorted(sdeg.FONTS.items(), key=lambda kv: kv[1]['kind'] == 'sans'), 1):
    FONT_CARDS.append((f'F{n:02d}', v['name'], NOTES.get(key, v['kind'].title() + '.'), sdeg.on(key, sdeg.v_seam_apart)))
FONT_CARDS.append((f'F{n + 1:02d}', 'Archivo 700', NOTES.get('arch', 'Sans. The Tidepool logotype&rsquo;s face.'), sdeg.on('arch', sdeg.v_seam_apart)))

cards = ''
for num, name, idea, fn in sdeg.VARIANTS + FONT_CARDS:
    if fn is None:
        cards += f'<div class="grp"><h2>{name}</h2><p>{idea}</p></div>'; continue
    k = f'v{num}' if fn is not sdeg.v_seam_apart or num != '08' or not cards.count('id="s08"') else 'v08r'
    bigs = ''.join(f'<div class="tile sq" style="{st}" title="{p.title()}">{big(fn, f"{k}{p[0]}b")}</div>' for p, st in PAL.items())
    lts = ''.join(f'<div class="tile wide" style="{st}">{logotype(fn, f"{k}{p[0]}l")}</div>' for p, st in PAL.items())
    hdr = ''.join(f'<div class="tile hdr" style="{st}">{logotype(fn, f"{k}{p[0]}h")}</div>' for p, st in PAL.items())
    cards += (f'<article class="card{" ref" if num == "00" else ""}" id="s{k[1:]}"><header><b>{num}</b><h2>{name}</h2></header><p>{idea}</p>'
              f'<div class="row bigs">{bigs}</div><div class="row">{lts}</div><span class="lab">Header size, 42px</span><div class="row">{hdr}</div></article>')

def _arch_tight():
    """The Archivo logotype for the negative-space mock-ups, with s, t, e and r moved together so the
    closest distance from the y to the s as drawn there (halves eased apart, which on its own pushes the s into the y) matches the mean closest
    distance of s-t and t-e. The y, the mark and "therapeutics" stay put."""
    lt = FACES['arch'][0]
    P = re.findall(r'<path d="([^"]*)" transform="translate\(([\d.]+) 0\.0\) scale\(1\.0000 -1\.0000\)"/>', lt)
    pts = lambda d, x: [sdeg.sgeom.polygon(c, 16) + [float(x), 0] for c in re.findall(r'M[^M]*', d)]
    sdeg.use('arch'); up, lo = sdeg.split_outline(); t = sdeg.at(sdeg.S_MID)[1]; dd = .22 * sdeg.W_MID; sdeg.use('news')
    sx = float(P[1][1]); s_pts = [np.array(up) - t * dd + [sx, 0], np.array(lo) + t * dd + [sx, 0]]
    def dense(A, step=2.0):
        """Points every `step` units along each edge (straight edges have only their two ends otherwise)."""
        B = np.roll(A, -1, 0); n = np.maximum(1, (np.linalg.norm(B - A, axis=1) / step).astype(int))
        return np.concatenate([A[k] + (B[k] - A[k]) * np.arange(n[k])[:, None] / n[k] for k in range(len(A))])
    def gap(A, B):
        """Closest distance between two outlines; negative-free, so overlapping letters measure 0."""
        A, B = dense(A), dense(B)
        return min(np.sqrt(((A[i:i + 2000, None] - B[None]) ** 2).sum(-1)).min() for i in range(0, len(A), 2000))
    y, tt, e = pts(*P[0]), pts(*P[2]), pts(*P[3])
    G = lambda A, B: min(gap(a, b) for a in A for b in B)
    def inside_any(pts, polys):
        P_ = np.concatenate([dense(q) for q in polys]); Q = np.concatenate(polys)
        hit = np.zeros(len(pts), bool)
        for q in polys:   # even-odd over every contour
            a, b = q, np.roll(q, -1, 0); x, yy = pts[:, :1], pts[:, 1:]
            c = (a[None, :, 1] > yy) != (b[None, :, 1] > yy)
            xi = a[None, :, 0] + (yy - a[None, :, 1]) * (b[None, :, 0] - a[None, :, 0]) / (b[None, :, 1] - a[None, :, 1] + 1e-12)
            hit ^= ((c & (x < xi)).sum(1) % 2 == 1)
        return hit.any()
    def signed(dx):
        """Closest distance from the y to the s moved left by dx; negative when they overlap."""
        S_ = [q - [dx, 0] for q in s_pts]
        over = inside_any(np.concatenate([dense(q) for q in S_]), y) or inside_any(np.concatenate([dense(q) for q in y]), S_)
        return -1.0 if over else G(y, S_)
    target = (G(s_pts, tt) + G(tt, e)) / 2
    lo_, hi_ = -150.0, 150.0                 # dx where the gap is too big / overlapping
    for _ in range(30):
        mid = (lo_ + hi_) / 2
        if signed(mid) > target: lo_ = mid
        else: hi_ = mid
    delta = lo_; before = signed(0)
    for d, x in P[1:]:
        lt = lt.replace(f'transform="translate({x} 0.0) scale(1.0000 -1.0000)"', f'transform="translate({float(x) - delta:.1f} 0.0) scale(1.0000 -1.0000)"')
    lt = re.sub(r'viewBox="([-\d.]+) ([-\d.]+) ([\d.]+) ([\d.]+)"', lambda m: f'viewBox="{m.group(1)} {m.group(2)} {float(m.group(3)) - delta:.1f} {m.group(4)}"', lt, count=1)
    print(f'Archivo y-s: {before:.1f} (-1 = overlapping) -> {signed(delta):.1f}, target {target:.1f} (moved {delta:.1f}); s-t {G(s_pts, tt):.1f}, t-e {G(tt, e):.1f}')
    return lt, f'translate({sx - delta:.1f} 0.0) scale(1.0000 -1.0000)', FACES['arch'][2]

FACES['arch_tight'] = _arch_tight()

# Negative-space heads: 08's clasp heads cut out of the letter, the bond in the pearl colour, tried at three head
# sizes and three distances from the seam, on Newsreader (08) and Archivo (F15).
SIZES = [(.30, 'Small head'), (.38, 'Medium head'), (.46, 'Large head')]
DISTS = [(.55, 'Close'), (.80, 'Middle'), (1.05, 'Far')]
def neg_section():
    out = ''
    for face, title, pick in (('news', '08 &middot; Newsreader 500', (.38, .80)), ('arch', 'F15 &middot; Archivo 700', (.38, .80))):
        mats = ''
        for p, st in PAL.items():
            cells = '<span></span>' + ''.join(f'<span class="ax">{lab}</span>' for _, lab in DISTS)
            for r, rl in SIZES:
                cells += f'<span class="ax ay">{rl}</span>'
                for c, cl in DISTS:
                    fn = sdeg.neg(r, c, face); ns = f'n{face[0]}{p[0]}{int(r * 100)}{int(c * 100)}'
                    on = ' on' if (r, c) == pick else ''
                    cells += f'<div class="tile sq{on}" style="{st}" title="{rl}, {cl.lower()}">{big(fn, ns)}</div>'
            mats += f'<div class="mat"><span class="lab">{p.title()}</span><div class="cells">{cells}</div></div>'
        fn = sdeg.neg(*pick, face)
        note = ''
        if face == 'arch': fn.lt_face = 'arch_tight'; note = '. The y&ndash;s gap set to match the other letters&rsquo; closest distance'
        lts = ''.join(f'<div class="tile wide" style="{st}">{logotype(fn, f"n{face[0]}{p[0]}L")}</div>' for p, st in PAL.items())
        hdr = ''.join(f'<div class="tile hdr" style="{st}">{logotype(fn, f"n{face[0]}{p[0]}H")}</div>' for p, st in PAL.items())
        out += (f'<article class="card wide-card" id="neg-{face}"><header><h2>{title}</h2></header>'
                f'<div class="mats">{mats}</div><span class="lab">In the logotype: medium head, middle distance (outlined above){note}</span>'
                f'<div class="row">{lts}</div><span class="lab">Header size, 42px</span><div class="row">{hdr}</div></article>')
    return (f'<section class="neg"><div class="grp"><h2>Negative-space heads</h2><p>The two finalists, 08 and F15, with the clasp&rsquo;s '
            f'round heads cut out of the letter, one in each half, and the bond between them in the logo&rsquo;s pearl colour. Rows change the '
            f'size of the heads; columns move them further from the seam, so further apart. Sizes and distances are fractions of the spine&rsquo;s '
            f'thickness, so the two fonts are like for like.</p></div>{out}</section>')

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
.grp { grid-column: 1 / -1; margin-top: 28px; }
.grp h2 { font-size: clamp(28px, 3vw, 38px); }
.grp p { color: var(--muted); max-width: 72ch; margin: 8px 0 0; }
.neg { display: grid; gap: 18px; margin-top: 8px; }
.mats { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; }
@media (max-width: 760px) { .mats { grid-template-columns: minmax(0, 1fr); } }
.mat { display: grid; gap: 8px; min-width: 0; }
.cells { display: grid; grid-template-columns: auto repeat(3, minmax(0, 1fr)); gap: 6px; align-items: center; }
.ax { font: 500 10px/1.2 var(--mono); letter-spacing: .1em; text-transform: uppercase; color: var(--muted); text-align: center; }
.ay { writing-mode: vertical-rl; transform: rotate(180deg); }
.tile.on { outline: 2px solid var(--accent); outline-offset: 2px; }
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
  {neg_section()}
  <div class="grp"><h2>All options so far</h2></div>
  <div class="grid">{cards}</div>
  <footer>Construction (top right): the s outline from the logotype export, its traced centreline, and the three cuts every option uses: the two shoulders where the serifs start and the middle of the spine. Rings are generic, as in the 3D story. Built by <code>oyster/brand/sdeg/build_sdeg.py</code>.</footer>
</main>
</body>
</html>
'''
open(D + '../sdegrader.html', 'w').write(html)
print('sdegrader.html', len(html) // 1024, 'KB')
