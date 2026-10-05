"""Build the Oyster Therapeutics site (index.html): the scroll-driven SELFTAC story from
../landing/landing_template.html as the landing page, followed by the company sections from the main
site (sections.html), styled by site.css and wired by site.js and wallpaper.js, with the brand
logotype."""
import os, re
D = os.path.dirname(os.path.abspath(__file__)) + '/'
L = D + '../landing/'
def svg(name, cls, uid):
    s = open(D + '../brand/' + name).read()
    s = s.replace('x-mInside', uid).replace('fill="#2B2230"', 'fill="currentColor"').replace('fill="#C99BB0"', 'style="fill:var(--pearl)"')
    return s.replace('<svg ', f'<svg class="{cls}" role="img" aria-label="Oyster Therapeutics" ', 1)
CG = '<svg class="cg" viewBox="0 0 30 12" aria-hidden="true"><line x1="6" y1="6" x2="24" y2="6"/><circle cx="6" cy="6" r="4.6"/><circle cx="24" cy="6" r="4.6"/></svg>'
ARROW = '<span class="arr"><svg viewBox="0 0 14 14" aria-hidden="true"><path d="M2 7h10M8 3l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></span>'

h = open(L + 'landing_template.html').read()
h = h.replace('<title>Oyster SELFTAC Story</title>', '<title>Oyster Therapeutics</title>')
h = h.replace('</style>', open(D + 'site.css').read() + '</style>', 1)
head = ('<header class="head" id="head"><a class="home" href="#story" aria-label="Oyster Therapeutics, back to the top"><!--WORDMARK--></a>'
        '<nav aria-label="Main"><a href="#story">Approach</a><a href="#pipeline">Pipeline</a><a href="#team">Team</a>'
        '<a href="#investors">Investors</a><a href="#news">News</a><a href="#contact">Contact</a></nav>'
        '<div class="pal" role="group" aria-label="Palette"><button type="button" data-pal="nacre" aria-pressed="true">Nacre</button>'
        '<button type="button" data-pal="tidepool" aria-pressed="false">Tidepool</button></div></header>\n')
h = h.replace('<main>', '<canvas id="bgArt" aria-hidden="true"></canvas>\n<a class="sr-only" href="#vision">Skip the story</a>\n' + head + '<main>', 1)
# the stage keeps only the scene; the header now lives outside it
h = re.sub(r'\s*<div class="bar-top">.*?</div>\s*</div>', '', h, count=1, flags=re.S)
h = h.replace('<a href="#more">Discover SELFTAC&reg;</a>', '<a href="#vision">Discover Oyster</a>')
h = h.replace('<div class="hint" id="hint">Scroll</div>', '<div class="hint" id="hint"><span>Scroll to see how SELFTAC&reg; works</span><i aria-hidden="true"></i></div>'
              '<a class="skip" id="skip" href="#vision">Skip to Oyster<svg viewBox="0 0 14 14" aria-hidden="true"><path d="M7 2v10M3 8l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></a>', 1)
a = h.index('<section class="after"'); b = h.index('</section>', a) + len('</section>')
sec = open(D + 'sections.html').read().replace('<!--CG-->', CG).replace('<!--ARROW-->', ARROW)
h = h[:a] + sec + h[b:]
h = h.replace('</main>', '</main>', 1)
h = h.replace('/*MOLECULE*/', open(L + 'js/molecule.js').read())
h = h.replace('/*MESHES*/', open(L + 'data/meshes.json').read())
h = h.replace('<!--WORDMARK-->', svg('oyster-wordmark-nacre.svg', 'wm', 'wmMask'))
h = h.replace('<!--LOGOTYPE-->', svg('oyster-logotype-nacre.svg', 'lt', 'ltMask'))
h = h.replace('<!--LOGOTYPE2-->', svg('oyster-logotype-nacre.svg', 'lt2', 'lt2Mask'))
h = h.replace('window.__story = {', open(D + 'site.js').read() + open(D + 'wallpaper.js').read() + '\nwindow.__story = {', 1)
h = h.replace('.nogl {', '.sr-only { position: absolute; left: -9999px; } .sr-only:focus { left: 16px; top: 16px; z-index: 20; background: var(--paper); padding: 10px 14px; border-radius: 8px; }\n.nogl {', 1)
open(D + 'index.html', 'w').write(h)
print('index.html', len(h) // 1024, 'KB')
