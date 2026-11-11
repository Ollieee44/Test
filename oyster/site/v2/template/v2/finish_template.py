"""After build_template.js: give the body placeholders of the text layouts real bullets (pptxgenjs writes them without,
so text typed into a new slide in PowerPoint would come out unbulleted), then save the same package as a .potx too.
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
for path, potx in ((SRC, False), (D + 'oyster-template-v2.potx', True)):
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for n, b in items:
            if potx and n == '[Content_Types].xml': b = b.replace(b'presentationml.presentation.main+xml', b'presentationml.template.main+xml')
            z.writestr(n, b)
print('bullets on', ', '.join(BULLETED), '· wrote .pptx and .potx')
