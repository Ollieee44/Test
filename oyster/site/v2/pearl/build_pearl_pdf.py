"""Build print.html: variations 1, 3, 4 and 5 (detailed, silhouette, ghost, blueprint) two by two on one A3 landscape
page, for the PDF (print_pearl_pdf.js prints it to selftac-pearl-heroes.pdf). Run build_pearl.py first."""
import os, re
D = os.path.dirname(os.path.abspath(__file__)) + '/'
h = open(D + 'index.html').read()
style = re.search(r'<style>(.*?)</style>', h, re.S).group(1)
fonts = re.search(r'(<link rel="preconnect".*?display=swap">)', h, re.S).group(1)
cards = [re.search(r'<figure class="card" id="' + k + r'">.*?</figure>', h, re.S).group(0) for k in ('v1-detailed', 'v3-silhouette', 'v4-ghost', 'v5-blueprint')]
# number them as on the grid page, and keep only the name and the line
page = f'''<!doctype html><html lang="en"><meta charset="utf-8"><title>The SELFTAC Pearl: Heroes</title>{fonts}
<style>{style}
@page {{ size: 420mm 297mm; margin: 0; }}
html, body {{ width: 420mm; height: 297mm; }}
body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
.sheet {{ box-sizing: border-box; width: 420mm; height: 297mm; padding: 14mm 16mm 10mm; display: grid; grid-template-rows: auto 1fr auto; gap: 7mm; overflow: hidden; }}
.sheet .top {{ margin: 0; grid-template-columns: auto minmax(0, 1fr); align-items: end; }}
.sheet .top h1 {{ font-size: 40px; }}
.sheet .top p.d {{ font-size: 13px; max-width: 95ch; justify-self: end; text-align: right; }}
.sheet .grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 6mm 8mm; align-content: center; width: 360mm; justify-self: center; }}
.sheet .card {{ gap: 9px; }}
.sheet .card figcaption h2 {{ font-size: 18px; }}
.sheet .card figcaption p {{ font-size: 12.5px; }}
.sheet .foot {{ margin: 0; font-size: 11px; max-width: none; }}
</style>
<div class="sheet">
  <header class="top"><div><p class="k">Oyster &middot; Website v2 &middot; Tidepool</p><h1>The SELFTAC&reg; pearl: four heroes</h1></div>
  <p class="d">Static hero variations with the reversible linker&rsquo;s join drawn as one realistic pearl. Numbers match the variations page.</p></header>
  <div class="grid">{''.join(cards)}</div>
  <p class="foot">Rendered from the website&rsquo;s own 3D models. The degrader is generic and stands in for a SELFTAC&reg; compound; it is drawn larger than true scale, with the proteins eased apart so its linker shows. Structures: BRD4, VHL and Elongin B and C from PDB 5T35 (Gadd et al., Nat. Chem. Biol. 2017).</p>
</div>
<script>
(() => {{ const fit = () => document.querySelectorAll('.frame').forEach(f => f.style.setProperty('--s', (f.clientWidth / 1440).toFixed(5))); fit(); addEventListener('resize', fit); }})();
</script>
'''
open(D + 'print.html', 'w').write(page)
print('print.html', len(cards), 'heroes')
