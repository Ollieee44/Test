"""After build_template.js: give the body placeholders of the text layouts real bullets (pptxgenjs writes them without,
so text typed into a new slide in PowerPoint would come out unbulleted), pair each logo picture with its SVG so PowerPoint
draws the vector (the PNG stays as the fallback for older versions), then save the same package as a .potx too.
  python3 finish_template.py"""
import os, re, zipfile
D = os.path.dirname(os.path.abspath(__file__)) + '/'
SRC = D + 'oyster-template-v2.pptx'
BULLETED = ('Oyster Title and Content', 'Oyster Two Column', 'Oyster Divided')
BULLET = '<a:buClr><a:srgbClr val="408967"/></a:buClr><a:buFont typeface="Arial"/><a:buChar char="&#8226;"/>'

def fix_layout(xml):
    name = re.search(r'<p:cSld name="([^"]*)"', xml).group(1)
    if name not in BULLETED: return xml
    def sp(m):
        t = m.group(0)
        if '>Body text<' not in t: return t
        t = re.sub(r'<a:lvl1pPr[^>]*>(.*?)<a:buNone/>', lambda m: '<a:lvl1pPr indent="-228600" marL="228600">' + m.group(1) + BULLET, t, count=1, flags=re.S)
        # the prompt paragraph inherits the bullet instead of switching it off
        return re.sub(r'<a:pPr indent="0" marL="0">(.*?)<a:buNone/></a:pPr>', r'<a:pPr>\1</a:pPr>', t, flags=re.S)
    return re.sub(r'<p:sp>.*?</p:sp>', sp, xml, flags=re.S)

zin = zipfile.ZipFile(SRC); items = [(n, zin.read(n)) for n in zin.namelist()]; zin.close()
items = [(n, fix_layout(b.decode()).encode() if n.startswith('ppt/slideLayouts/slideLayout') and n.endswith('.xml') else b) for n, b in items]

# the logos as vectors: a picture whose PNG is one of assets/logo-* or mark-* gets that file's SVG as an svgBlip
import hashlib, posixpath
A = D + 'assets/'
SVG_OF = {hashlib.md5(open(A + f, 'rb').read()).hexdigest(): f[:-4] + '.svg' for f in os.listdir(A) if f.startswith(('logo-', 'mark-')) and f.endswith('.png')}
pkg = dict(items); added = {}
SVGNS = 'http://schemas.microsoft.com/office/drawing/2016/SVG/main'
for rels in [n for n in pkg if n.endswith('.rels') and n.startswith(('ppt/slides/', 'ppt/slideLayouts/', 'ppt/slideMasters/'))]:
    part = posixpath.join(posixpath.dirname(posixpath.dirname(rels)), posixpath.basename(rels)[:-5])
    rx, px = pkg[rels].decode(), pkg[part].decode(); n = 0
    for rid, tgt in re.findall(r'Id="(rId\d+)"[^>]*Target="([^"]+\.png)"', rx):
        media = posixpath.normpath(posixpath.join(posixpath.dirname(part), tgt))
        svg = SVG_OF.get(hashlib.md5(pkg[media]).hexdigest())
        if not svg: continue
        if svg not in added:
            added[svg] = 'ppt/media/oyster-' + svg; pkg[added[svg]] = open(A + svg, 'rb').read()
        n += 1; sid = 'rIdSvg%d' % n
        rx = rx.replace('</Relationships>', '<Relationship Id="%s" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/oyster-%s"/></Relationships>' % (sid, svg))
        ext = '<a:extLst><a:ext uri="{96DAC541-7B7A-43D3-8B79-37D633B846F1}"><asvg:svgBlip xmlns:asvg="%s" r:embed="%s"/></a:ext></a:extLst>' % (SVGNS, sid)
        px = re.sub(r'<a:blip r:embed="%s"\s*(/>|></a:blip>)' % rid, '<a:blip r:embed="%s">%s</a:blip>' % (rid, ext), px)
    pkg[rels], pkg[part] = rx.encode(), px.encode()
ct = pkg['[Content_Types].xml'].decode()
if 'Extension="svg"' not in ct: ct = ct.replace('<Default ', '<Default Extension="svg" ContentType="image/svg+xml"/><Default ', 1)
pkg['[Content_Types].xml'] = ct.encode()
items = list(pkg.items())
print('svg logos:', ', '.join(sorted(added)))
for path, potx in ((SRC, False), (D + 'oyster-template-v2.potx', True)):
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for n, b in items:
            if potx and n == '[Content_Types].xml': b = b.replace(b'presentationml.presentation.main+xml', b'presentationml.template.main+xml')
            z.writestr(n, b)
print('bullets on', ', '.join(BULLETED), '· wrote .pptx and .potx')
