"""Morph on every slide of stage1.pptx, timed from out/timing.json: each slide's Morph lasts the time since the previous
frame and the in-between frames advance on their own, so the deck plays the animation's moves. --click: the deck waits
for a click at each of the ten steps. Otherwise it plays through, holding at each step as the web page's autoplay does.
Apps without Morph fade instead.  Usage: python post.py stage1.pptx out/timing.json out.pptx [--click]"""
import hashlib, json, re, sys, zipfile
src, timing_f, dst = sys.argv[1:4]
CLICK = '--click' in sys.argv
timing = json.load(open(timing_f))
HOLD = [1800, 1800, 1500, 3200, 2200, 2000, 2800, 3000, 2000, 3500]   # autoplay: time to read each step before moving on
zin = zipfile.ZipFile(src); files = {n: zin.read(n) for n in zin.namelist()}
slides = sorted((n for n in files if re.match(r'ppt/slides/slide\d+\.xml$', n)), key=lambda n: int(re.search(r'(\d+)\.xml', n).group(1)))
assert len(slides) == len(timing), (len(slides), len(timing))
for i, name in enumerate(slides):
    xml = files[name].decode('utf8')
    xml = re.sub(r'<p:transition.*?</p:transition>|<p:transition[^>]*/>', '', xml, flags=re.S)
    dur = max(120, timing[i]['dur'] or 500); stop = timing[i]['stop']; last = i == len(slides) - 1
    if last: adv = ''
    elif stop is None: adv = ' advClick="0" advTm="0"'            # an in-between frame: straight on to the next
    elif CLICK: adv = ''                                          # a step: wait for the presenter
    else: adv = f' advTm="{HOLD[stop]}"'
    t = ('<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006">'
         '<mc:Choice xmlns:p159="http://schemas.microsoft.com/office/powerpoint/2015/09/main" Requires="p159">'
         f'<p:transition xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" spd="fast" p14:dur="{dur}"{adv}><p159:morph option="byObject"/></p:transition>'
         f'</mc:Choice><mc:Fallback><p:transition spd="fast"{adv}><p:fade/></p:transition></mc:Fallback></mc:AlternateContent>')
    if '<p:timing' in xml: xml = xml.replace('<p:timing', t + '<p:timing', 1)
    elif '<p:extLst' in xml.split('</p:clrMapOvr>')[-1]: xml = xml.replace('</p:clrMapOvr>', '</p:clrMapOvr>' + t, 1)
    else: xml = xml.replace('</p:sld>', t + '</p:sld>', 1)
    files[name] = xml.encode('utf8')
# one copy of each picture
first = {}
for n in sorted(n for n in files if n.startswith('ppt/media/')): first.setdefault(hashlib.sha1(files[n]).hexdigest(), n)
dupes = {n: first[hashlib.sha1(files[n]).hexdigest()] for n in files if n.startswith('ppt/media/') and first[hashlib.sha1(files[n]).hexdigest()] != n}
for n in [n for n in files if n.endswith('.rels')]:
    x = files[n].decode('utf8')
    for d, keep in dupes.items(): x = x.replace('../media/' + d.split('/')[-1] + '"', '../media/' + keep.split('/')[-1] + '"')
    files[n] = x.encode('utf8')
for d in dupes: del files[d]
with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as z:
    for n, b in files.items():
        if not n.endswith('/'): z.writestr(n, b)
print(dst, len(slides), 'slides,', sum(1 for t in timing if t['stop'] is not None), 'steps,', len(dupes), 'duplicate pictures folded')
