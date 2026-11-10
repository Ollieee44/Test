"""Copy oyster-template.pptx to oyster-template.potx: the same package with the template content type, so it can be
saved as a PowerPoint template (File > New offers it once it sits in the Custom Office Templates folder)."""
import os, zipfile
D = os.path.dirname(os.path.abspath(__file__)) + '/'
zin = zipfile.ZipFile(D + 'oyster-template.pptx')
with zipfile.ZipFile(D + 'oyster-template.potx', 'w', zipfile.ZIP_DEFLATED) as z:
    for n in zin.namelist():
        b = zin.read(n)
        if n == '[Content_Types].xml':
            b = b.replace(b'presentationml.presentation.main+xml', b'presentationml.template.main+xml')
        z.writestr(n, b)
print('oyster-template.potx')
