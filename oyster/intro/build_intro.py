"""Build intro/index.html: the current website (../site/index.html, left untouched) opened by an intro in which a
3D oyster, sculpted from the logo's shells, opens; its pearl becomes the 'o' of the logotype, the logotype forms
large and centred, then settles into the header wordmark as the scroll story fades in. Run ../site/build_site.py first."""
import os, re
D = os.path.dirname(os.path.abspath(__file__)) + '/'
h = open(D + '../site/index.html').read()

def once(old, new):
    global h
    assert old in h, old[:60]
    h = h.replace(old, new, 1)

# the logotype, with its parts named for the animation: the 'o' disc, the carve (the mask's shell cut-out and the
# pearl's hollow), the small pearl, the five letters (revealed through a clip) and 'therapeutics'
s = open(D + '../brand/oyster-logotype-nacre.svg').read()
s = s.replace('x-mInside', 'ioMask').replace('fill="#2B2230"', 'fill="currentColor"').replace('fill="#C99BB0"', 'style="fill:var(--pearl)"')
s = s.replace('<g fill="#000" transform="translate(51.5 50) scale(0.76) translate(-50.5 -47.5)">', '<g id="ioCut" fill="#000" transform="translate(51.5 50) scale(0) translate(-50.5 -47.5)">', 1)
s = s.replace('<circle cx="60.24" cy="53.42" r="10.26" fill="#000"/>', '<circle id="ioHole" cx="60.24" cy="53.42" r="0" fill="#000"/>', 1)
s = s.replace('<g transform="translate(-17.1 -583.4) scale(6.3571)">', '<g id="ioMark" style="opacity:0" transform="translate(-17.1 -583.4) scale(6.3571)">', 1)
s = s.replace('<circle cx="51.5" cy="50" r="42" mask="url(#ioMask)"/>', '<circle id="ioDisc" cx="51.5" cy="50" r="42" mask="url(#ioMask)"/>', 1)
s = s.replace('<circle cx="60.24" cy="53.42" r="7.22" style="fill:var(--pearl)"/>', '<circle id="ioPearl" cx="60.24" cy="53.42" r="0" style="fill:var(--pearl)"/>', 1)
paths = re.findall(r'<path d="[^"]*" transform="translate\([^)]*\) scale\((?:0\.5000|0\.1200) -[^)]*\)"/>', s)
big = [p for p in paths if 'scale(0.5000' in p]; small = [p for p in paths if 'scale(0.1200' in p]
assert len(big) == 5 and len(small) == 12, (len(big), len(small))
for p in paths: s = s.replace(p, '', 1)
s = s.replace('</defs>', '<clipPath id="ioClip"><rect id="ioClipR" x="470" y="-700" width="0" height="1000"/></clipPath></defs>', 1)
s = s.replace('</g></svg>', '<g id="ioLetters" style="opacity:0" clip-path="url(#ioClip)">' + ''.join(big) + '</g><g id="ioTher" style="opacity:0">' + ''.join(small) + '</g></g></svg>', 1)
s = s.replace('<svg ', '<svg class="ilogo" id="ilogo" aria-hidden="true" ', 1)
assert all(f'id="{i}"' in s for i in ('ioCut', 'ioHole', 'ioMark', 'ioDisc', 'ioPearl', 'ioClipR', 'ioLetters', 'ioTher'))

once('</style>', open(D + 'intro.css').read() + '</style>')
overlay = ('<script>document.documentElement.classList.add("intro")</script>\n'
           '<div class="intro-ov" id="intro" aria-hidden="true"><div class="ibg"></div><canvas id="introGl"></canvas><div class="ipearl" id="ipearl"></div>' + s + '</div>\n'
           '<button type="button" class="iskip" id="introSkip">Skip intro</button>\n')
once('<canvas id="bgArt"', overlay + '<canvas id="bgArt"')
once('\nwindow.__story = {', '\n' + open(D + 'intro.js').read() + '\nwindow.__story = {')
open(D + 'index.html', 'w').write(h)
# the same page opening in Tidepool, for comparison: the stage starts teal from the first frame
t = h.replace('<script>document.documentElement.classList.add("intro")</script>',
  '<script>document.documentElement.classList.add("intro"); window.__startPal = "tidepool";</script><style>.intro-ov .ibg { --intro-a: #0B3A38; --intro-b: #04201F; }</style>', 1)
open(D + 'tidepool.html', 'w').write(t)
print('intro/index.html', len(h) // 1024, 'KB')
