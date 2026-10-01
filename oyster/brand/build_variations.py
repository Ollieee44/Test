"""Build variations.html, the comparison sheet of Open Shell variations, from variations_defs.svg and sheet.css."""
import os
from wordmark_metrics import style
D=os.path.dirname(os.path.abspath(__file__))+'/'
defs=open(D+'variations_defs.svg').read()
import sys; sys.path.insert(0, D + 'logotype')
from build_logotype import logotype_svg
AH='aria-hidden="true"'
OPTS=[
 ('v-open','00','The Open Shell','The current mark, shown for reference: two shells, a hinge gap and a pearl.','The baseline. Simple and recognisable at every size.','The pearl floats in open space, so it is the least compact of the set.'),
 ('v-hollow','01','The Hollow','The lower shell has a round hollow cut into it, and the pearl sits in that cradle. The ring of empty space around the pearl makes the lower shell read as its home.','Calm and protective. The negative-space ring gives the pearl more presence without making it bigger.','The hollow fills in at 16px, where it looks close to the original.'),
 ('v-inside','02','Inside Out','Figure and ground swap: a solid disc with the open shell cut out of it, and the pearl inside the cut-out. The disc doubles as a natural O.','Strongest silhouette of the set, and a ready-made app icon, favicon and social avatar. It works as the O in a wordmark.','The shell detail is smaller inside the disc, so the idea needs the disc to be at least 24px.'),
 ('v-layers','03','Nacre','The lower shell is sliced by three fine lines, like the layers of nacre that build a pearl. Nacre is also the name of the Option D palette.','Adds texture and a precise, scientific feel. It links the mark to the palette name.','The fine lines disappear below 24px, so small sizes need a simplified version without them.'),
 ('v-halves','04','Two Halves','The pearl is made of two half-discs, one in each accent colour of the palette. Two small molecules form one whole.','Uses both palette accents and tells the two-part story at a glance.','It needs colour to work. In one-colour print it falls back to a plain pearl.'),
 ('v-strand','05','Pearl on a Strand','Beads grow along a strand from the hinge into the pearl, borrowing the bead linker from the SELFTAC molecule. It reads as a pearl being made, and as a linker leading to its payload.','Calm and close to the original, with a quiet link to the chemistry. The growing beads give it a natural animation: the beads build up into the pearl.','The smallest bead drops out first. At 16px it reads as the original mark with a few dots, which is a graceful fallback.'),
]
def use(id, sz, ink, p1, p2, extra=''):
    return f'<svg width="{sz}" height="{sz}" viewBox="0 0 100 100" style="color:{ink};fill:currentColor;--p1:{p1};--p2:{p2}" {extra}><use href="#{id}"/></svg>'
def app(id, tile, fg, p1, p2, sz):
    return f'<svg class="app" width="{sz}" height="{sz}" viewBox="0 0 100 100" {AH}><rect width="100" height="100" fill="{tile}"/><g transform="translate(9 9) scale(.82)" style="color:{fg};fill:currentColor;--p1:{p1};--p2:{p2}"><use href="#{id}" width="100" height="100"/></g></svg>'

# measured in the browser: ink bounds of each mark in its 0-100 viewBox, and font metrics in em
INK={'v-open':(8.5,10.56,90.69,91.5),'v-hollow':(8.5,10.56,90.69,91.5),'v-inside':(8,9.5,92,93.5),'v-layers':(8.5,10.56,90.69,91.5),'v-halves':(8.5,10.56,90.69,91.5),'v-strand':(8.5,10.56,90.69,91.5)}
FACE={'serif':'newsreader-500','sans':'archivo-700'}
def omark(id, face, ink, p1, p2):
    st=style(INK[id], FACE[face])+f';color:{ink};fill:currentColor;--p1:{p1};--p2:{p2}'
    return f'<svg class="omark" viewBox="0 0 100 100" style="{st}" {AH}><use href="#{id}"/></svg>'
N=('#2B2230','#C99BB0','#B8A7C9'); TD=('#EAF3EF','#F2B84B','#7FC4B0')
strip=''.join(f'<a class="cell" href="#{i}"><span class="mono">{n}</span>{use(i,72,*N,AH)}<span class="nm">{t}</span></a>' for i,n,t,*_ in OPTS)
strip2=''.join(f'<a class="cell" href="#{i}">{use(i,72,*TD,AH)}<span class="mono">{n}</span></a>' for i,n,t,*_ in OPTS)
cards=''
for i,n,t,idea,good,watch in OPTS:
    lockN=f'<div class="lock serif">{use(i,"1em",*N,AH)}<span>Oyster<small>Therapeutics</small></span></div>'
    lockT=f'<div class="lock sans">{use(i,"1em",*TD,AH)}<span>Oyster<small>Therapeutics</small></span></div>'
    # the mark standing in for the O: its ink runs from the round-letter overshoot below the
    # baseline up to the x-height of s, e and r, with side bearings matched to the letter o
    extra=(f'<div class="panel nacre oword"><span class="mono">Mark as the O &middot; Nacre</span>'
           f'<div class="olock">{logotype_svg("nacre", mark_id=i, sub=False, style=f"color:{N[0]};--p1:{N[1]};--p2:{N[2]}", mark_ink=INK[i])}</div></div>'
           f'<div class="panel tide oword"><span class="mono">Mark as the O &middot; Tidepool</span>'
           f'<div class="olock">{logotype_svg("tidepool", mark_id=i, sub=False, style=f"color:{TD[0]};--p1:{TD[1]};--p2:{TD[2]}", mark_ink=INK[i])}</div></div>')
    smallN=use(i,48,*N,AH)+use(i,32,*N,AH)+use(i,24,*N,AH)+app(i,N[0],'#EFE6E1',N[1],N[2],32)+app(i,N[0],'#EFE6E1',N[1],N[2],16)
    smallT=use(i,48,*TD,AH)+use(i,32,*TD,AH)+use(i,24,*TD,AH)+app(i,'#EAF3EF','#0F4C4A',TD[1],TD[2],32)+app(i,'#EAF3EF','#0F4C4A',TD[1],TD[2],16)
    heroN=use(i,220,*N,f'role="img" aria-label="{t} mark in Nacre colours" class="hero-m"')
    heroT=use(i,220,*TD,f'role="img" aria-label="{t} mark in Tidepool colours" class="hero-m"')
    cards+=f'''
  <section class="opt" id="{i}">
    <div class="wrap">
      <div class="opt-head"><span class="num">{n}</span><div><h2>{t}</h2><p>{idea}</p></div></div>
      <div class="panels">
        <div class="panel nacre"><span class="mono">Nacre</span>{heroN}{lockN}<div class="small">{smallN}</div></div>
        <div class="panel tide"><span class="mono">Tidepool</span>{heroT}{lockT}<div class="small">{smallT}</div></div>
        {extra}
      </div>
      <div class="notes"><div><h3>Strength</h3><p>{good}</p></div><div><h3>Watch out</h3><p>{watch}</p></div></div>
    </div>
  </section>'''
CSS=open(D+'sheet.css').read()
html=f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<!-- artifact:start -->
<title>Oyster Mark Variations</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=swap">
<style>
{CSS}
</style>
</head>
<body>
{defs}
<header class="top">
  <div class="wrap">
    <span class="mono">Oyster Therapeutics &middot; Brand mark</span>
    <h1>Variations on the Open Shell</h1>
    <p>Five directions built on the current mark, now all sharing The Hollow&rsquo;s cradle: the pearl sits in a round hollow cut into the lower shell. The original is shown first for comparison. Each option is also shown as the O of the Oyster logotype, with the letter spacing set in the Logotype studio.</p>
  </div>
</header>
<main>
  <div class="wrap">
    <div class="strip n">{strip}</div>
    <div class="strip t">{strip2}</div>
  </div>
{cards}
</main>
<footer><div class="wrap">Concepts for review. SVG files for each variation, in both palettes, are in the repository under <code>oyster/brand/</code>.</div></footer>
<!-- artifact:end -->
</body>
</html>
'''
open(D+'variations.html','w').write(html)
print(len(html))
