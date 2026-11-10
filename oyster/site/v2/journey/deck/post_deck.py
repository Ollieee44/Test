"""Give every slide of stage1.pptx the Morph transition (by object), lasting what out/timing.json says, and advance on
its own once the Morph has played (a click still advances, and the last slide waits). Apps without Morph fade instead.
Usage: python post_deck.py stage1.pptx out/timing.json selftac-journey.pptx [--click]  (--click: advance on click only)"""
import json, re, sys, zipfile
src, timing_f, dst = sys.argv[1:4]
CLICK_ONLY = '--click' in sys.argv           # every slide waits for a click (Morph still plays on each)
timing = json.load(open(timing_f))
HOLD = 350                                   # a breath after each Morph before the next slide starts
zin = zipfile.ZipFile(src); files = {n: zin.read(n) for n in zin.namelist()}
slides = sorted((n for n in files if re.match(r'ppt/slides/slide\d+\.xml$', n)), key=lambda n: int(re.search(r'(\d+)\.xml', n).group(1)))
for i, name in enumerate(slides):
    xml = files[name].decode('utf8')
    xml = re.sub(r'<p:transition.*?</p:transition>|<p:transition[^>]*/>', '', xml, flags=re.S)
    dur = timing[i] if i < len(timing) and timing[i] else 900
    nxt = timing[i + 1] if i + 1 < len(timing) and timing[i + 1] else None
    adv = f' advTm="{(1600 if i == 0 else HOLD)}"' if nxt else ''
    if CLICK_ONLY: adv = ''
    t = ('<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006">'
         '<mc:Choice xmlns:p159="http://schemas.microsoft.com/office/powerpoint/2015/09/main" Requires="p159">'
         f'<p:transition xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" spd="slow" p14:dur="{dur}"{adv}><p159:morph option="byObject"/></p:transition>'
         f'</mc:Choice><mc:Fallback><p:transition spd="slow"{adv}><p:fade/></p:transition></mc:Fallback></mc:AlternateContent>')
    if '<p:timing' in xml: xml = xml.replace('<p:timing', t + '<p:timing', 1)
    elif '<p:extLst' in xml.split('</p:clrMapOvr>')[-1]: xml = xml.replace('</p:clrMapOvr>', '</p:clrMapOvr>' + t, 1)
    else: xml = xml.replace('</p:sld>', t + '</p:sld>', 1)
    files[name] = xml.encode('utf8')
# one copy of each picture: pptxgenjs embeds a fresh copy on every slide; point every slide at the first copy
import hashlib
first = {}
for n in sorted(n for n in files if n.startswith('ppt/media/')):
    h = hashlib.sha1(files[n]).hexdigest()
    first.setdefault(h, n)
dupes = {n: first[hashlib.sha1(files[n]).hexdigest()] for n in files if n.startswith('ppt/media/') and first[hashlib.sha1(files[n]).hexdigest()] != n}
for n in [n for n in files if n.endswith('.rels')]:
    x = files[n].decode('utf8')
    for d, keep in dupes.items(): x = x.replace('../media/' + d.split('/')[-1] + '"', '../media/' + keep.split('/')[-1] + '"')
    files[n] = x.encode('utf8')
for d in dupes: del files[d]
with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as z:
    for n, b in files.items():
        if not n.endswith('/'): z.writestr(n, b)   # no folder entries
print(dst, len(slides), 'slides, Morph throughout,', len(dupes), 'duplicate pictures folded')
