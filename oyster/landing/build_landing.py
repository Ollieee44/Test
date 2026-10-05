"""Build landing.html, the scroll-driven SELFTAC story, from landing_template.html, data/meshes.json and the
logotype exports in ../brand (recoloured to follow the page palette)."""
import os, re
D = os.path.dirname(os.path.abspath(__file__)) + '/'
def svg(name, cls, uid):
    s = open(D + '../brand/' + name).read()
    s = s.replace('x-mInside', uid).replace('fill="#2B2230"', 'fill="currentColor"').replace('fill="#C99BB0"', 'style="fill:var(--pearl)"')
    return s.replace('<svg ', f'<svg class="{cls}" role="img" aria-label="Oyster Therapeutics" ', 1)
html = open(D + 'landing_template.html').read()
html = html.replace('/*MOLECULE*/', open(D + 'js/molecule.js').read())
html = html.replace('/*MESHES*/', open(D + 'data/meshes.json').read())
html = html.replace('<!--WORDMARK-->', svg('oyster-wordmark-nacre.svg', 'wm', 'wmMask'))
html = html.replace('<!--LOGOTYPE-->', svg('oyster-logotype-nacre.svg', 'lt', 'ltMask'))
open(D + 'landing.html', 'w').write(html)
print('landing.html', len(html) // 1024, 'KB')
