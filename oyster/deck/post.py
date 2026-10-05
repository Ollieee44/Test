"""Turn the stage-1 deck into the Morph deck.

Every picture named in models.json (a part of the story, e.g. "!!BRD4") becomes an embedded 3D model:
an mc:AlternateContent whose Choice is a PowerPoint 3D model (am3d:model3d, pointing at the part's .glb)
and whose Fallback is the original picture, so apps without 3D support still show the still. The model
keeps the picture's name, position and size, so Morph pairs it across slides and animates its move, its
size and its turn. Each slide also gets the Morph transition.

The 3D markup follows the element order and attribute names of the Open XML SDK's
Office2019.Drawing.Model3D classes. Each model sits centred at its own origin; its camera is PowerPoint's
default (45 degree view from 2.03 m), and its scale is set so its bounding sphere fills the frame.

Usage: python post.py stage1.pptx models.json turns.json out.pptx
"""
import json, os, re, shutil, sys, zipfile

src, models_f, turns_f, dst = sys.argv[1:5]
MODELS = json.load(open(models_f)); TURNS = json.load(open(turns_f))
SPHERE_M = .7                      # bounding sphere radius in metres, seen from the camera below
MORPH_MS = 1800

zin = zipfile.ZipFile(src)
files = {n: zin.read(n) for n in zin.namelist()}

def slide_no(name): return int(re.search(r'slide(\d+)\.xml$', name).group(1))

glb_target = {}                    # model file -> media name
def add_glb(path):
    if path not in glb_target:
        name = f'model{len(glb_target) + 1}.glb'; files['ppt/media/' + name] = open(path, 'rb').read(); glb_target[path] = name
    return glb_target[path]

def angle(rad):                    # 60000ths of a degree, kept in [0, 360)
    return int(round((((rad * 180 / 3.141592653589793) % 360) + 360) % 360 * 60000))

LIGHTS = ('<am3d:ambientLight><am3d:clr><a:scrgbClr r="50000" g="50000" b="50000"/></am3d:clr><am3d:illuminance n="500000" d="1000000"/></am3d:ambientLight>'
          '<am3d:ptLight rad="0"><am3d:clr><a:scrgbClr r="100000" g="100000" b="100000"/></am3d:clr><am3d:intensity n="9765625" d="1000000"/><am3d:pos x="21959998" y="70920001" z="16344003"/></am3d:ptLight>'
          '<am3d:ptLight rad="0"><am3d:clr><a:scrgbClr r="100000" g="100000" b="100000"/></am3d:clr><am3d:intensity n="6250000" d="1000000"/><am3d:pos x="-37964106" y="51130435" z="57631972"/></am3d:ptLight>'
          '<am3d:ptLight rad="0"><am3d:clr><a:scrgbClr r="100000" g="100000" b="100000"/></am3d:clr><am3d:intensity n="3125000" d="1000000"/><am3d:pos x="-37739122" y="58056624" z="-34769649"/></am3d:ptLight>')

def model3d(pic, glb_rid, info, turn):
    cnv = re.search(r'<p:cNvPr ([^>]*?)/?>', pic).group(1)
    attrs = dict(re.findall(r'(\w+)="([^"]*)"', cnv))
    off = re.search(r'<a:off x="(-?\d+)" y="(-?\d+)"/>', pic).groups()
    ext = re.search(r'<a:ext cx="(\d+)" cy="(\d+)"/>', pic).groups()
    png_rid = re.search(r'<a:blip r:embed="([^"]+)"', pic).group(1)
    n = max(1, int(round(SPHERE_M / info['radius'] * 1e6)))
    descr = f' descr="{attrs["descr"]}"' if 'descr' in attrs else ''   # already escaped in the source XML
    xfrm = f'<a:off x="{off[0]}" y="{off[1]}"/><a:ext cx="{ext[0]}" cy="{ext[1]}"/>'
    return (
        '<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006">'
        '<mc:Choice xmlns:am3d="http://schemas.microsoft.com/office/drawing/2017/model3d" Requires="am3d">'
        f'<p:graphicFrame><p:nvGraphicFramePr><p:cNvPr id="{attrs["id"]}" name="{attrs["name"]}"{descr}/>'
        '<p:cNvGraphicFramePr><a:graphicFrameLocks noGrp="1" noChangeAspect="1"/></p:cNvGraphicFramePr><p:nvPr/></p:nvGraphicFramePr>'
        f'<p:xfrm>{xfrm}</p:xfrm>'
        '<a:graphic><a:graphicData uri="http://schemas.microsoft.com/office/drawing/2017/model3d">'
        f'<am3d:model3d r:embed="{glb_rid}">'
        f'<am3d:spPr><a:xfrm>{xfrm}</a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></am3d:spPr>'
        '<am3d:camera><am3d:pos x="0" y="0" z="73100523"/><am3d:up dx="0" dy="36000000" dz="0"/><am3d:lookAt x="0" y="0" z="0"/>'
        '<am3d:perspective fov="2700000"/></am3d:camera>'
        f'<am3d:trans><am3d:meterPerModelUnit n="{n}" d="1000000"/><am3d:preTrans dx="0" dy="0" dz="0"/>'
        '<am3d:scale><am3d:sx n="1000000" d="1000000"/><am3d:sy n="1000000" d="1000000"/><am3d:sz n="1000000" d="1000000"/></am3d:scale>'
        f'<am3d:rot ax="{angle(turn["pitch"])}" ay="{angle(turn["yaw"])}" az="0"/><am3d:postTrans dx="0" dy="0" dz="0"/></am3d:trans>'
        f'<am3d:raster rName="Office3DRenderer" rVer="16.0.8326"><am3d:blip r:embed="{png_rid}"/></am3d:raster>'
        f'<am3d:objViewport viewportSz="{ext[0]}"/>' + LIGHTS +
        '</am3d:model3d></a:graphicData></a:graphic></p:graphicFrame></mc:Choice>'
        f'<mc:Fallback>{pic}</mc:Fallback></mc:AlternateContent>')

MORPH = ('<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006">'
         '<mc:Choice xmlns:p159="http://schemas.microsoft.com/office/powerpoint/2015/09/main" Requires="p159">'
         f'<p:transition xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" spd="slow" p14:dur="{MORPH_MS}"><p159:morph option="byObject"/></p:transition>'
         '</mc:Choice><mc:Fallback><p:transition spd="slow"><p:fade/></p:transition></mc:Fallback></mc:AlternateContent>')

count = 0
for name in sorted([n for n in files if re.match(r'ppt/slides/slide\d+\.xml$', n)], key=slide_no):
    no = slide_no(name); turn = TURNS[no - 1]
    xml = files[name].decode('utf8'); rels_name = f'ppt/slides/_rels/slide{no}.xml.rels'; rels = files[rels_name].decode('utf8')
    ids = [int(i) for i in re.findall(r'Id="rId(\d+)"', rels)]; nxt = [max(ids) + 1 if ids else 1]
    def swap(m):
        global count
        pic = m.group(0); nm = re.search(r'<p:cNvPr [^>]*name="([^"]*)"', pic).group(1)
        nm = nm.replace('&amp;', '&')
        if nm not in MODELS: return pic
        media = add_glb(MODELS[nm]['glb']); rid = f'rId{nxt[0]}'; nxt[0] += 1
        nonlocal_rels.append(f'<Relationship Id="{rid}" Type="http://schemas.microsoft.com/office/2017/06/relationships/model3d" Target="../media/{media}"/>')
        count += 1
        return model3d(pic, rid, MODELS[nm], turn)
    nonlocal_rels = []
    xml = re.sub(r'<p:pic>.*?</p:pic>', swap, xml, flags=re.S)
    rels = rels.replace('</Relationships>', ''.join(nonlocal_rels) + '</Relationships>')
    # Morph into this slide (skipped on the first)
    if no > 1:
        xml = re.sub(r'<p:transition.*?</p:transition>|<p:transition[^>]*/>', '', xml, flags=re.S)
        if '</p:clrMapOvr>' in xml: xml = xml.replace('</p:clrMapOvr>', '</p:clrMapOvr>' + MORPH, 1)
        else: xml = xml.replace('</p:cSld>', '</p:cSld>' + MORPH, 1)
    files[name] = xml.encode('utf8'); files[rels_name] = rels.encode('utf8')

ct = files['[Content_Types].xml'].decode('utf8')
if 'Extension="glb"' not in ct:
    ct = ct.replace('<Default ', '<Default Extension="glb" ContentType="model/gltf-binary"/><Default ', 1)
files['[Content_Types].xml'] = ct.encode('utf8')

with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml', files.pop('[Content_Types].xml'))
    for n, b in files.items(): z.writestr(n, b)
print(f'{dst}: {count} 3D models across {len(TURNS)} slides, {len(glb_target)} model files, Morph on every transition')
