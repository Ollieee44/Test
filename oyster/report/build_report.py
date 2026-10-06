"""Build the Oyster project report: report.html, printed to Oyster-Project-Report.pdf by print_report.js.

A summary of the key discussions and decisions across the Oyster work, a map of how the four websites (two logos x
two palettes, each opened by its intro) came about, how to rebuild them, and the tools and skills used. Marks are
drawn from the project's own code (via the catalogue builder); screenshots come from img/.
"""
import base64, os, sys
D = os.path.dirname(os.path.abspath(__file__)) + '/'
sys.path.insert(0, D + '../brand')
import build_catalogue as C   # every mark, as SVG symbols (rebuilding the catalogue as a side effect is harmless)

ART = 'https://claude.ai/artifact/'
img = lambda n: 'data:image/jpeg;base64,' + base64.b64encode(open(D + 'img/' + n, 'rb').read()).decode()
def mark(id, size=64, pal='nacre', acc='clasp'):
    bg, ink, p1, p2 = C.COL[pal]; p2 = p2[acc]
    return f'<svg width="{size}" height="{size}" viewBox="0 0 100 100" style="color:{ink};fill:currentColor;--p1:{p1};--p2:{p2}" aria-hidden="true"><use href="#{id}"/></svg>'
used = ['va-open', 'va-hollow', 'va-inside', 'bd-hinge', 'rf-clasp', 'fr-ruffle', 'fr-valve', 'tq-frilled2', 'hg-cup', 'rs-half', 'rs-ribbed', 'rs-smooth',
        'rr-strands', 'rr-line', 'lp-line-s', 'lp-io-s', 'lp-io-s-rim35']
defs = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>' + ''.join(C.DEFS) + '</defs>'
        + ''.join(f'<symbol id="{k}" viewBox="0 0 100 100"><g transform="translate(-1.5 1.5)">{C.SYM[k]}</g></symbol>' for k in used) + '</svg>')
A = lambda id, text=None: f'<a href="{ART}{id}">{text or "claude.ai/artifact/" + id}</a>'

SITES = [  # logo, palette, intro artifact, picture at the opening, picture at the logotype
 ('Old logo', 'Nacre', 'NTiBBienf6HvCseLhbCDHU', 'old-nacre-900.jpg', 'old-nacre-2800.jpg', 'oyster/intro/index.html'),
 ('Old logo', 'Tidepool', 'QNC92GFvJXE6w1tULP5ELu', 'old-tide-900.jpg', 'old-tide-2800.jpg', 'oyster/intro/tidepool.html'),
 ('New logo', 'Nacre', '7dgMtsG9wGQ18WXi8d6J73', 'new-nacre-1300.jpg', 'new-nacre-3700.jpg', 'oyster/intro/fan-nacre.html'),
 ('New logo', 'Tidepool', 'FdQsz8x3zDvkPnTZvowc1s', 'new-tide-1300.jpg', 'new-tide-3700.jpg', 'oyster/intro/fan-tidepool.html'),
]
site_cards = ''.join(f'''<div class="site"><div class="shots"><img src="{img(a)}" alt=""><img src="{img(b)}" alt=""></div>
  <div class="meta"><b>{logo} &middot; {pal}</b><span>{A(art)}</span><code>{src}</code></div></div>''' for logo, pal, art, a, b, src in SITES)

# ---------- the map: two lanes (website, logo) meeting in the four sites ----------
def box(x, y, w, h, date, title, sub, cls=''):
    return (f'<g class="bx {cls}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7"/>'
            f'<text x="{x + 10}" y="{y + 15}" class="d">{date}</text><text x="{x + 10}" y="{y + 31}" class="t">{title}</text>'
            + ''.join(f'<text x="{x + 10}" y="{y + 46 + 12 * i}" class="s">{line}</text>' for i, line in enumerate(sub)) + '</g>')
def arrow(x1, y1, x2, y2):
    return f'<path class="ar" d="M{x1} {y1} C{x1} {(y1 + y2) / 2} {x2} {(y1 + y2) / 2} {x2} {y2 - 4}" marker-end="url(#ah)"/>'
W1, W2, X1, X2 = 300, 300, 20, 360
web = [('30 Sep', 'Concept site', ['Brand audit palettes D (Nacre) and', 'H (Tidepool); rebuilt on Kesmalea', 'content, Bicycle-style layout']),
       ('1 Oct', 'Editorial site, science art', ['nabla.bio-style variant; 5T35 complex', 'wallpaper; MZ1-derived molecule', 'studies; 2D SELFTAC animation']),
       ('5 Oct', '3D SELFTAC story', ['Three.js scroll story from PDB 5T35', 'and 1UBQ; generic degrader; the', 'clasp becomes the hero']),
       ('5 Oct', 'Website = story + sections', ['Fixed header, palette switch, WIG', 'audit fixed, palette explorer, deck,', 'house-style skill written']),
       ('5 Oct eve', 'Intro (old logo)', ['3D oyster opens; pearl becomes the', '‘o’; turns to side profile; dark', 'stage; Nacre and Tidepool pages'])]
logo = [('30 Sep', 'The Open Shell', ['Two valves, a hinge gap, a pearl;', 'Nacre Rings and Pearl Halves', 'drawn as alternatives']),
        ('30 Sep–1 Oct', 'Variations → Inside Out', ['Hollow, Nacre, Two Halves, Strand,', 'bead-linker marks; Inside Out', 'adopted as the ‘o’; spacing studio']),
        ('6 Oct', '“Looks like a compact”', ['Refinements, front-on valve, open', 'oyster (eye read fixed), two-valve', 'hybrids rejected']),
        ('6 Oct', 'From the references', ['Painted half shell vs front-on fan;', 'B1/B3 chosen; riffs; line fan R7;', '80% pearl; inside out, rim 3.5']),
        ('6 Oct', 'Intro (new logo)', ['Face-on fan clam; pearl pinned to', 'the logo; still pearl; smooth, no-', 'pinch hinge; 25% slower; Nacre'])]
svg = '<svg viewBox="0 0 680 640" class="map" role="img" aria-label="Project map"><defs><marker id="ah" viewBox="0 0 8 8" refX="6" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 8 4 0 8z" class="ah"/></marker></defs>'
svg += '<text x="20" y="18" class="lane">WEBSITE AND STORY</text><text x="360" y="18" class="lane">LOGO</text>'
for i, (d, t, s) in enumerate(web):
    y = 30 + i * 92; svg += box(X1, y, W1, 78, d, t, s, 'web')
    if i: svg += arrow(X1 + W1 / 2, y - 14, X1 + W1 / 2, y)
for i, (d, t, s) in enumerate(logo):
    y = 30 + i * 92; svg += box(X2, y, W2, 78, d, t, s, 'logo')
    if i: svg += arrow(X2 + W2 / 2, y - 14, X2 + W2 / 2, y)
svg += f'<path class="ar dash" d="M{X2} {30 + 92 + 39} C 340 {30 + 92 + 39} 340 {30 + 4 * 92 + 39} {X1 + W1} {30 + 4 * 92 + 39}" marker-end="url(#ah)"/>'
yb = 30 + 5 * 92 + 10
for j, (lab, x) in enumerate((('Old logo · Nacre', 20), ('Old logo · Tidepool', 185), ('New logo · Nacre', 350), ('New logo · Tidepool', 515))):
    svg += f'<g class="bx out"><rect x="{x}" y="{yb + 40}" width="145" height="44" rx="7"/><text x="{x + 10}" y="{yb + 58}" class="t">{lab}</text><text x="{x + 10}" y="{yb + 73}" class="s">website + intro</text></g>'
svg += arrow(X1 + W1 / 2, yb - 14, 92, yb + 40) + arrow(X1 + W1 / 2, yb - 14, 257, yb + 40)
svg += arrow(X2 + W2 / 2, yb - 14, 422, yb + 40) + arrow(X2 + W2 / 2, yb - 14, 587, yb + 40)
svg += '</svg>'

journey = [('va-open', '1.1', 'The Open Shell', 'first mark, 30 Sep'), ('va-hollow', '2.1', 'The Hollow', 'cradle for the pearl'), ('va-inside', '4.1', 'Inside Out', 'adopted; live mark'),
           ('bd-hinge', '3.1', 'Bead Hinge', 'linker as hinge'), ('rf-clasp', '4.3', 'The Clasp', 'clasp in the mark'), ('fr-ruffle', '4.8', 'Ruffled Lips', 'anti-compact fix'),
           ('fr-valve', '5.1', 'Front-on Valve', 'seen from above'), ('tq-frilled2', '6.3', 'Open Oyster', 'eye read fixed'), ('hg-cup', '7.3', 'Deep Cup', 'hybrid, rejected'),
           ('rs-half', '8.1', 'Half Shell', 'the painting'), ('rs-ribbed', '9.1', 'Fan and Pearl B1', 'second reference'), ('rs-smooth', '9.3', 'B3 Smooth', 'chosen with B1'),
           ('rr-strands', '9.5', 'Pearl Strands', 'riff'), ('rr-line', '10.1', 'Line R7', 'chosen riff'), ('lp-line-s', '10.3', 'Line, 80% pearl', 'favourite size'),
           ('lp-io-s', '11.2', 'Inside Out Line', 'drawing small'), ('lp-io-s-rim35', '11.7', 'Rim 3.5', 'new logo')]
jcards = ''.join(f'<div class="jc{" pick" if n in ("4.1", "11.7") else ""}">{mark(i, 54)}<b>{n}</b><span>{t}</span><i>{s}</i></div>' for i, n, t, s in journey)

CSS = open(D + 'report.css').read()
html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Oyster Project Report</title><style>{CSS}</style></head><body>{defs}

<section class="cover">
  <div class="eyebrow">Oyster Therapeutics &middot; project report &middot; 6 October 2026</div>
  <h1>How we got to the four Oyster websites</h1>
  <p class="lede">A summary of the key discussions and decisions behind the Oyster website and logo, a map of how they led to four versions of the website (two logos, each in the Nacre and Tidepool palettes, each opened by a 3D intro), and the steps, tools and skills needed to rebuild them.</p>
  <div class="sites">{site_cards}</div>
  <p class="small">Each site opens with its intro (left: the clam opening; right: the logotype it lands as), then the 3D SELFTAC scroll story and the company sections. All versions are linked from one page: {A("6TjGz7zGCkspdhHfUZicQa", "Oyster Site Versions")}. Links are private to the owner until shared from each page&rsquo;s Share menu.</p>
</section>

<section>
  <h2>1. The map</h2>
  <p>Two strands of work ran side by side and met at the end: the website and its science story on the left, the logo on the right. The old logo&rsquo;s intro was built around Inside Out; the new logo needed its own intro, so the intro was rebuilt once the new mark was chosen.</p>
  {svg}
  <p class="small">The dashed line: Inside Out, adopted on 1 October, is the logo the old intro lands in. Dates are the days the work was committed (Sept&ndash;Oct 2026), over four working days. Earlier days are reconstructed here from the repository&rsquo;s commit messages and the project&rsquo;s house-style notes; 6 October from the conversation itself.</p>
</section>

<section>
  <h2>2. Key discussions and decisions</h2>
  <h3>Brand foundations</h3>
  <ul>
    <li><b>Two palettes, always both.</b> From a brand audit, option D (<em>Nacre</em>: pearl pinks, mauve ink) and option H (<em>Tidepool</em>: deep teal with gold) were chosen. Every page has a palette switch and every element is checked in both. Four further palettes were explored later (palette explorer) but not adopted.</li>
    <li><b>Type:</b> Newsreader (headings and statements), Archivo (body and UI), IBM Plex Mono (small labels). The logotype is lowercase &ldquo;oyster&rdquo; drawn from Newsreader outlines with optically even spacing, set in a purpose-built Logotype studio, with &ldquo;therapeutics&rdquo; tucked under the tail of the y.</li>
    <li><b>The clasp is the hero.</b> The reversible bond where the two halves of a SELFTAC degrader meet is the idea the company most wants seen. It appears as two gold (Nacre) or coral (Tidepool) pearls joined by a bond: on section labels, the story&rsquo;s progress rail and the pipeline.</li>
  </ul>
  <h3>Website and science story</h3>
  <ul>
    <li><b>Content and layout.</b> The concept site was rebuilt on Kesmalea&rsquo;s public story and a Bicycle-style structure (a giant wordmark that shrinks into the header, labelled statement sections); an editorial variant (after nabla.bio) followed. The current site makes the 3D story its landing page, followed by vision, why Oyster, pipeline, team, investors, news and contact.</li>
    <li><b>Science illustration rules.</b> Proteins are smoothed real surfaces (BRD4 and VHL from PDB 5T35, ubiquitin from 1UBQ), credited on the page. The degrader must be <em>generic</em>: an early version traced from MZ1 was recognisable (JQ1, VH032), so the halves were replaced by invented ring systems, and the linker is drawn as a string of pearls.</li>
    <li><b>Story pacing.</b> Seven beats (size problem, split, barrier, into the neuron, rebuilt, cleared, again), one continuous camera path, a visible &ldquo;Skip to Oyster&rdquo;, a portrait cut for phones, and reduced-motion support. The site passed a Web Interface Guidelines audit.</li>
    <li><b>Working style.</b> &ldquo;Change nothing else&rdquo; means exactly that; renders are checked before success is claimed; existing pages are updated in place so links stay the same.</li>
  </ul>
  <h3>The first logo (old)</h3>
  <ul>
    <li><b>The Open Shell</b> (two valves, a hinge gap, a pearl) was chosen over Nacre Rings (read as a target) and Pearl Halves (read as a pill).</li>
    <li>Variations added a cradle for the pearl (The Hollow), bead-linker ideas from the molecule, and <b>Inside Out</b>: the shell cut out of a solid disc. Inside Out became the &lsquo;o&rsquo; of the logotype, the favicon and the header, and the target of the first intro.</li>
  </ul>
  <h3>Rethinking the logo (6 October)</h3>
  <ul>
    <li><b>&ldquo;It looks a bit like a makeup compact.&rdquo;</b> The cause: a perfect disc, ruler-straight lips and a lid hinged open like a mirror. Refinements (bringing the clasp in, legibility, a favicon cut) and anti-compact fixes (rough edge, ruffled lips) kept the side view.</li>
    <li><b>&ldquo;A front-on, open clamshell.&rdquo;</b> A straight front-on version read as an eye; a slight angle was allowed, giving open-oyster marks with depth. In one colour the pearl in an almond-shaped cup still read as an eye, fixed by moving the pearl onto the front lip.</li>
    <li><b>The two references.</b> A painted half shell and a front-on fan with a big pearl. Blends of the two were rejected (&ldquo;neither front-on nor half&rdquo;); marks drawn closely from each followed. Note: a single half shell loses the two shells coming together (the SELFTAC story). <b>B1 and B3</b> (front-on fan, dish, big pearl) were chosen, with a caution that ribbed fans resemble a scallop and the Shell logo.</li>
    <li><b>Riffs and the final mark.</b> Of eight riffs, <b>R7</b> (the fan as one even line) was taken forward; of five pearl sizes, <b>80%</b>; and an inside-out version with the drawing enlarged to fill the disc at three rim widths. The new logo is <b>11.7</b>: the line fan and 80% pearl inside out, rim 3.5.</li>
    <li>Every mark (59) is numbered by family in the {A("AJUpcjMJuGVzcQt5ZAfNrK", "Oyster Mark Catalogue")}.</li>
  </ul>
  <h3>The intros</h3>
  <ul>
    <li><b>Old intro:</b> a 3D oyster rushes in, opens on its pearl, turns a quarter to side profile and lands exactly in the Inside Out &lsquo;o&rsquo;; the word writes in and the logotype glides into the header. It plays on a dark stage and the lights come up as the logo lands.</li>
    <li><b>New intro, for the face-on mark:</b> both valves take the fan&rsquo;s outline, hinged at the back; the lid lifts to stand upright as the fan, and the camera swings round to face it and drops to the mark&rsquo;s slight angle (10&deg;) rather than turning side-on.</li>
    <li><b>Refinements asked for, in order:</b> the pearl stuttered at the handover (it is now pinned to the logo&rsquo;s pearl to within half a pixel, and still while the logo fades in); it popped into being (now always there); it rolled back (now it never moves); the whole intro 25% slower; the closed shell&rsquo;s hinge looked pointed (now a smooth dome); and the hinge pinched in as it opened (now the closed and open shapes share the hinge&rsquo;s width). A full-size, still pearl does not fit a thin fan&rsquo;s hinge, so the closed clam is domed over it, checked numerically so the lid never passes through the pearl.</li>
  </ul>
</section>

<section>
  <h2>3. The logo journey</h2>
  <p>Selected marks from the catalogue, in the order they were drawn. Numbers are catalogue numbers; the live mark (4.1) and the new logo (11.7) are outlined.</p>
  <div class="journey">{jcards}</div>
  <h3>The four websites, side by side</h3>
  <table class="t4"><tr><th></th><th>Nacre</th><th>Tidepool</th><th>Without intro</th></tr>
  <tr><th>Old logo (4.1, live)</th><td>{A("NTiBBienf6HvCseLhbCDHU", "Intro &middot; Nacre")}</td><td>{A("QNC92GFvJXE6w1tULP5ELu", "Intro &middot; Tidepool")}</td><td>{A("9pFqdk4otTS46U21phpLCk", "Website")}</td></tr>
  <tr><th>New logo (11.7, proposed)</th><td>{A("7dgMtsG9wGQ18WXi8d6J73", "Intro &middot; Nacre")}</td><td>{A("FdQsz8x3zDvkPnTZvowc1s", "Intro &middot; Tidepool")}</td><td>{A("NSRLa7dnMy96W1ViKGfjHc", "Website")}</td></tr></table>
</section>

<section>
  <h2>4. How to recreate it</h2>
  <h3>Where everything is</h3>
  <p>Repository <code>ollieee44/test</code>, branch <code>claude/sweet-keller-0aee5z</code> (which contains all earlier Oyster work), folder <code>oyster/</code>.</p>
  <table class="files">
    <tr><td><code>oyster/landing/</code></td><td>The 3D SELFTAC story: <code>build_meshes.py</code> (proteins and molecule from PDB 5T35 and 1UBQ) &rarr; <code>data/meshes.json</code>; <code>landing_template.html</code> + <code>js/molecule.js</code> &rarr; <code>build_landing.py</code></td></tr>
    <tr><td><code>oyster/site/</code></td><td>The website: <code>build_site.py</code> joins the story with <code>sections.html</code>, <code>site.css</code>, <code>site.js</code>, <code>wallpaper.js</code> &rarr; <code>index.html</code></td></tr>
    <tr><td><code>oyster/intro/</code></td><td>Old intro: <code>build_intro.py</code> + <code>intro.js</code> &rarr; <code>index.html</code> (Nacre), <code>tidepool.html</code>. New intro: <code>build_fan.py</code> + <code>intro_fan.js</code> &rarr; <code>fan-nacre.html</code>, <code>fan-tidepool.html</code>, <code>fan-site.html</code></td></tr>
    <tr><td><code>oyster/brand/</code></td><td>Marks and sheets: <code>marks.py</code> (first marks), <code>refine.py</code>, <code>frontal.py</code>, <code>threequarter.py</code>, <code>hinged.py</code>, <code>refs.py</code>, <code>riffs.py</code>, <code>linepearl.py</code> (the new logo); each <code>build_*.py</code> makes a sheet; <code>build_catalogue.py</code> makes the catalogue; <code>logotype/</code> holds the spacing studio and <code>settings.json</code></td></tr>
    <tr><td><code>oyster/deck/</code></td><td>The PowerPoint Morph deck of the story (embedded 3D models)</td></tr>
    <tr><td><code>oyster/build_hub.py</code></td><td>The Site Versions hub page; <code>report/</code> holds this report</td></tr>
  </table>
  <h3>Build order</h3>
<pre>cd oyster/landing &amp;&amp; python build_meshes.py   # only if geometry changes (rdkit, scikit-image, scipy)
python build_landing.py                         # the standalone story
cd ../site &amp;&amp; python build_site.py              # the website (rebuild after any story change)
cd ../intro &amp;&amp; python build_intro.py            # old-logo intros (index.html, tidepool.html)
python build_fan.py                             # new-logo intros and site
cd .. &amp;&amp; python build_hub.py                     # the hub page
cd brand &amp;&amp; python build_catalogue.py            # the mark catalogue (after any mark change)</pre>
  <h3>How the new intro lines up with the logo</h3>
  <ul>
    <li><code>build_fan.py</code> swaps the new mark into every wordmark and exports the mark&rsquo;s geometry (fan outline, rib angles, hinge, pearl) into the script, so the 3D clam is built to the logo&rsquo;s measurements.</li>
    <li>At the end the camera faces the clam at 10&deg; above, and its aim and distance are solved so the 3D pearl sits on the logo&rsquo;s pearl; the line-cut disc then fades in round it.</li>
    <li>Timings live in one table (<code>T</code>, scaled by <code>SLOW</code> = 1.25) in <code>intro_fan.js</code>; the closed shell&rsquo;s dome (<code>HW</code>, <code>CAP</code>, <code>PEAK</code>) was chosen with a clearance check so the lid never passes through the pearl.</li>
  </ul>
  <h3>Testing</h3>
  <p>Pages are checked in headless Chromium (Playwright), with the CDN copy of three.js 0.160.0 routed to a local npm copy (the sandbox cannot reach the CDN or Google Fonts). Every page that animates has a hook for frame-by-frame screenshots: <code>window.__story.frame(p)</code> for the story and <code>window.__intro.at(ms)</code> for the intros. Check desktop (1440&times;900) and phone (390&times;844), in both palettes, and look at the screenshots before reporting.</p>
  <h3>Publishing</h3>
  <p>Pages are published as Claude artifacts (claude.ai) and updated in place so links stay stable. The house-style skill&rsquo;s <code>references/pipelines.md</code> lists every page and its artifact link.</p>
</section>

<section>
  <h2>5. Skills, plugins and tools</h2>
  <h3>Not standard with Claude Code (installed in the project, <code>.claude/skills/</code>)</h3>
  <table class="files">
    <tr><td><b>oyster-house-style</b><br><span class="small">written for this project</span></td><td>The brand and build conventions: palettes, type, logotype, the clasp, science-illustration rules, how to work with the client, and where everything lives (<code>references/palette.md</code>, <code>references/pipelines.md</code>). Load it for any Oyster work; it is the most important file to share.</td></tr>
    <tr><td><b>Taste skills</b><br><span class="small"><a href="https://github.com/Leonxlnx/taste-skill">Leonxlnx/taste-skill</a></span></td><td>design-taste-frontend (and v1), gpt-taste, high-end-visual-design, minimalist-ui, industrial-brutalist-ui, stitch-design-taste, redesign-existing-projects, full-output-enforcement, image-to-code, imagegen-frontend-web, imagegen-frontend-mobile, brandkit. Installed at the start of the project to steer design quality; available to any session in this repository.</td></tr>
    <tr><td><b>web-design-guidelines</b><br><span class="small"><a href="https://github.com/vercel-labs/agent-skills">vercel-labs/agent-skills</a></span></td><td>Reviews UI code against the Web Interface Guidelines; used for the site&rsquo;s accessibility and interaction audit.</td></tr>
    <tr><td><b>playwright-cli</b><br><span class="small">@playwright/cli 0.1.22</span></td><td>Drives a real browser to test and screenshot pages. A SessionStart hook (<code>.claude/hooks/session-start.sh</code>, registered in <code>.claude/settings.json</code>) installs it in Claude Code on the web.</td></tr>
  </table>
  <h3>Available in Claude, used here</h3>
  <ul>
    <li><b>Artifacts</b> (claude.ai): published pages; the Logotype studio uses an artifact database to save spacing settings for Claude to read back.</li>
    <li><b>PDF and PowerPoint skills</b>: this report; the Morph deck (with pptxgenjs).</li>
  </ul>
  <h3>Libraries and tools</h3>
  <p>Python 3 with fontTools (logotype outlines and metrics), RDKit, scikit-image and SciPy (molecule and protein meshes), Pillow; three.js 0.160.0 (3D, loaded from jsDelivr); Playwright with Chromium (testing and rendering); Node.js; pptxgenjs (deck); LibreOffice (deck previews). Fonts: Newsreader, Archivo and IBM Plex Mono from Google Fonts (the logotype is outlined, so it does not need them). Structures: PDB 5T35 (Gadd et al., Nat. Chem. Biol. 2017) and 1UBQ, downloaded from RCSB.</p>
</section>

<section>
  <h2>Appendix: every page</h2>
  <table class="files links">
    <tr><td>Site Versions hub</td><td>{A("6TjGz7zGCkspdhHfUZicQa")}</td></tr>
    <tr><td>Old logo: intro Nacre / Tidepool / website</td><td>{A("NTiBBienf6HvCseLhbCDHU")}<br>{A("QNC92GFvJXE6w1tULP5ELu")}<br>{A("9pFqdk4otTS46U21phpLCk")}</td></tr>
    <tr><td>New logo: intro Nacre / Tidepool / website</td><td>{A("7dgMtsG9wGQ18WXi8d6J73")}<br>{A("FdQsz8x3zDvkPnTZvowc1s")}<br>{A("NSRLa7dnMy96W1ViKGfjHc")}</td></tr>
    <tr><td>Mark catalogue</td><td>{A("AJUpcjMJuGVzcQt5ZAfNrK")}</td></tr>
    <tr><td>Logo sheets, in order</td><td>Brand mark {A("PKcMKiixVGjLF587ERBM69")}<br>Mark variations {A("7nbPJzaNZTv9pXDPZftmnP")}<br>Bead marks {A("6ppVB3x6LGVpwS36p4kHZh")}<br>Inside Out, refined {A("TYDiqpmFntUpWcALworY7g")}<br>Beyond the compact {A("H9Kr4y1ZRdNsRYhnCf1NKf")}<br>Open oyster {A("3XER9VkRqams9ryoFciMjb")}<br>Open oyster picks {A("JCZmPkni1P6zVMZuQHMMFY")}<br>Two valves, one hinge {A("N8uzWVpwns4Skux3XkmCYy")}<br>From the references {A("ACn2XP8bzFsQJVb5d5DKyb")}<br>Fan and pearl riffs {A("S2YScwuN6szkQzeQ2rex7Y")}<br>Line fan, pearl sizes {A("4zMWE6ipDqHpULNFiJG8os")}<br>Line fan, inside out {A("4gdAYgpeD5UJzm2T1zwqw1")}</td></tr>
    <tr><td>Tools and other pages</td><td>Logotype studio {A("7tNEfaWQeav7iTWnMSocu1")}<br>Palette explorer {A("AfzgUFchFXjBXQWcboMYMy")}<br>3D story {A("9aJKZGFD5fzeHUrQu9EPTk")}<br>3D model viewer {A("7YaLDip9qnWoVVs9p7CVeh")}<br>First main site {A("WSV9dspDgvBBMTUiZZUEZN")}<br>Editorial site {A("12vnmPkAi83mVtPXTDLPZV")}</td></tr>
  </table>
</section>
</body></html>'''
open(D + 'report.html', 'w').write(html)
print('report.html', len(html) // 1024, 'KB')
