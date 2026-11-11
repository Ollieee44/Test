"""SELFTAC representations (reps/index.html): six ways to draw the degrader, side by side, all on the journey's own
geometry. Each option is the journey's molecule (makeMolecule, taken from the built page) with only the two halves
redrawn, so the halves sit where they always do and the linker, its pearls and the gold clasp are identical."""
import json, os, re
D = os.path.dirname(os.path.abspath(__file__)) + '/'
page = open(D + '../click3/index.html', encoding='utf8').read()
geom = re.search(r'function geom\(p\) \{.*?\n\}\n', page, re.S).group(0)
mm = re.search(r'function makeMolecule\(THREE, D, Q, geom, bow\) \{.*?\n  return \{ group, update, setColors, centre: cW\.clone\(\)\.add\(cE\)\.multiplyScalar\(\.5\) \};\n\}\n', page, re.S).group(0)
mm = mm.replace('return { group, update, setColors, centre: cW.clone().add(cE).multiplyScalar(.5) };',
                'return { group, update, setColors, centre: cW.clone().add(cE).multiplyScalar(.5), heads, pearls, clasp, strands, bond, glow, R, lineMat, mats };')
pal = re.search(r"PAL\.otx = \{ \.\.\.PAL\.tidepool, (.*?) \};", page).group(1)
DATA = open(D + 'reps_data.json').read()

OPTIONS = [
    ('skeletal', 'Skeletal', 'Today’s drawing: each half an outline traced along its bonds, rings as open loops.'),
    ('surface', 'Surface', 'Each half as a smooth, contoured surface: the same visual language as the proteins.'),
    ('pearls', 'Pearl cluster', 'Each half as a cluster of pearls in its colour: abstract, and on-brand with the pearl and clasp.'),
    ('pebble', 'Pebbles', 'Each half as one glossy pebble, shaped to the half’s length and breadth.'),
    ('dumbbell', 'Dumbbell', 'The simplest form: a sphere for each half on a smooth rod, with the gold clasp.'),
    ('icon', 'Flat icon', 'A 2D glyph for slides and the site: two ring motifs, the linker line and the clasp.'),
]
tiles = ''.join(f'<figure class="tile" data-opt="{k}"><div class="view"></div><figcaption><b>{i + 1:02d}</b><h2>{t}</h2><p>{d}</p></figcaption></figure>'
                for i, (k, t, d) in enumerate(OPTIONS))

html = f'''<!doctype html>
<html lang="en">
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>SELFTAC Representations</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500&family=Monomaniac+One&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=swap">
<script type="importmap">{{ "imports": {{ "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js" }} }}</script>
<style>
:root {{ --paper: #158B63; --ink: #F5FFFC; --muted: #A8D8C6; --accent: #30FCBA; --clasp: #F7D16B; --card: rgba(6, 46, 33, .32); --line: rgba(245, 255, 252, .14);
  --sans: "Geist", "Helvetica Neue", Arial, sans-serif; --serif: "Newsreader", Georgia, serif; --pixel: "Monomaniac One", "Geist Mono", monospace; color-scheme: dark; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--paper); color: var(--ink); font: 400 16px/1.5 var(--sans); }}
#gl {{ position: fixed; inset: 0; width: 100%; height: 100%; display: block; pointer-events: none; z-index: 1; }}
main {{ position: relative; z-index: 2; max-width: 1240px; margin: 0 auto; padding: 48px 24px 64px; }}
.k {{ font: 400 14px/1 var(--pixel); letter-spacing: .04em; text-transform: uppercase; color: #8AC3B1; }}
h1 {{ font: 400 clamp(34px, 4.4vw, 56px)/1.04 var(--serif); margin: 12px 0 10px; letter-spacing: -.01em; }}
.lede {{ color: var(--muted); max-width: 62ch; margin: 0; }}
.bar {{ display: flex; gap: 10px; flex-wrap: wrap; margin: 24px 0 26px; }}
.bar button {{ height: 40px; padding: 0 16px; border-radius: 10px; border: 1px solid rgba(255,255,255,.18); background: rgba(255,255,255,.12); color: #fff; font: 500 14px/1 var(--sans); cursor: pointer; }}
.bar button[aria-pressed="true"] {{ background: rgba(255,255,255,.92); color: #0E5C42; }}
.bar button:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
.grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px; }}
.tile {{ margin: 0; background: var(--card); border: 1px solid var(--line); border-radius: 16px; overflow: hidden; }}
.view {{ aspect-ratio: 4 / 3; position: relative; }}
.view svg {{ position: absolute; inset: 0; width: 100%; height: 100%; }}
figcaption {{ padding: 14px 16px 16px; border-top: 1px solid var(--line); }}
figcaption b {{ font: 400 13px/1 var(--pixel); color: #8AC3B1; font-weight: 400; }}
figcaption h2 {{ font: 400 22px/1.15 var(--serif); margin: 6px 0 4px; }}
figcaption p {{ margin: 0; color: var(--muted); font-size: 14px; }}
@media (max-width: 960px) {{ .grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
@media (max-width: 620px) {{ .grid {{ grid-template-columns: 1fr; }} main {{ padding: 32px 16px 48px; }} }}
</style>
<canvas id="gl" aria-hidden="true"></canvas>
<main>
<span class="k">SELFTAC&reg; degrader &middot; representation options</span>
<h1>Six ways to draw the SELFTAC.</h1>
<p class="lede">Every option keeps the journey&rsquo;s geometry: the two halves sit in the same places, and the linker, its pearls and the gold reversible clasp are identical, so the length is the same throughout. Only how the halves are drawn changes.</p>
<div class="bar" role="group" aria-label="View"><button type="button" id="bJoin" aria-pressed="true">Joined (dimer)</button><button type="button" id="bSplit" aria-pressed="false">Split (monomers)</button><button type="button" id="bTurn" aria-pressed="true">Turning</button></div>
<div class="grid">{tiles}</div>
</main>
<script type="application/json" id="data">{DATA}</script>
<script type="module">
import * as THREE from 'three';
const DATA = JSON.parse(document.getElementById('data').textContent);
const P = {{ {pal} }};
{geom}
const V = a => new THREE.Vector3(...a), C = DATA.centres;
const axis = new THREE.Vector3(15.52 - 7.42, -35.26 - 2.64, -11.39 + 7.47).normalize(), Q = new THREE.Quaternion().setFromUnitVectors(axis, new THREE.Vector3(-1, 0, 0));
{mm}
const canvas = document.getElementById('gl'), renderer = new THREE.WebGLRenderer({{ canvas, antialias: true, alpha: true }});
renderer.setPixelRatio(Math.min(devicePixelRatio, 2)); renderer.setScissorTest(true);
const KEYS = ['warhead', 'e3lig'];
// the shading the molecule uses, for the redrawn halves (with contour lines for the surface option)
const VS = `varying vec3 vN; varying vec3 vV; varying vec3 vP; void main() {{ vec4 w = modelMatrix * vec4(position, 1.0); vN = normalize(mat3(modelMatrix) * normal); vV = normalize(cameraPosition - w.xyz); vP = position; gl_Position = projectionMatrix * viewMatrix * w; }}`;
const FS = `uniform vec3 col; uniform vec3 ink; uniform float gloss; uniform float lines; uniform vec3 centre; varying vec3 vN; varying vec3 vV; varying vec3 vP;
  void main() {{ vec3 n = normalize(vN), v = normalize(vV), l = normalize(vec3(-.35, .75, .55));
    float shade = mix(.76, 1.0, smoothstep(-.05, .12, dot(n, l))); float spec = smoothstep(.965, .985, dot(n, normalize(l + v)));
    float rim = pow(1.0 - max(dot(n, v), 0.0), 2.5); vec3 c = col * shade;
    if (lines > 0.0) {{ float d = length(vP - centre) / lines; float f = abs(fract(d) - .5); c = mix(c * .62, c, smoothstep(.04, .11, f)); }}
    c = mix(c, ink, rim * .28); c = mix(c, vec3(1.0), spec * gloss); gl_FragColor = vec4(c, 1.0);
    #include <colorspace_fragment>
  }}`;
const shade = (col, gloss, lines = 0, centre = new THREE.Vector3()) => new THREE.ShaderMaterial({{ vertexShader: VS, fragmentShader: FS,
  uniforms: {{ col: {{ value: new THREE.Color(col) }}, ink: {{ value: new THREE.Color(P.ink) }}, gloss: {{ value: gloss }}, lines: {{ value: lines }}, centre: {{ value: centre }} }} }});
const sphere = new THREE.SphereGeometry(1, 40, 28);
function swapHead(m, k, build) {{ m.material.visible = false; m.children[0].visible = false; build(k).forEach(o => {{ const ol = new THREE.Mesh(o.geometry, m.children[0].material); ol.renderOrder = -1; ol.position.copy(o.position); ol.quaternion.copy(o.quaternion); ol.scale.copy(o.scale); m.add(ol, o); }}); }}
const BUILD = {{
  skeletal: () => {{}},
  surface: mol => mol.heads.forEach((h, i) => swapHead(h.mesh, KEYS[i], k => {{ const g = geom(DATA.reps[k].surface); g.computeBoundingSphere();
    return [new THREE.Mesh(g, shade(P[k], .15, 1.15, g.boundingSphere.center.clone()))]; }})),
  pearls: mol => mol.heads.forEach((h, i) => swapHead(h.mesh, KEYS[i], k => DATA.reps[k].pearls.map(c => {{ const s = new THREE.Mesh(sphere, shade(P[k], .9)); s.position.set(...c); s.scale.setScalar(1.55); return s; }}))),
  pebble: mol => mol.heads.forEach((h, i) => swapHead(h.mesh, KEYS[i], k => {{ const e = DATA.reps[k].pebble, s = new THREE.Mesh(sphere, shade(P[k], .7));
    const ax = V(e.axes[0]).normalize(), ay = V(e.axes[1]).normalize(), az = new THREE.Vector3().crossVectors(ax, ay);   // right-handed
    const M = new THREE.Matrix4().makeBasis(ax, ay, az); s.quaternion.setFromRotationMatrix(M); s.position.set(...e.c);
    s.scale.set(Math.max(2.2, e.r[0]), Math.max(2.4, e.r[1] * .9), e.r[2] * .78); return [s]; }})),
  dumbbell: mol => {{ mol.heads.forEach((h, i) => swapHead(h.mesh, KEYS[i], k => {{ const e = DATA.reps[k].sphere, s = new THREE.Mesh(sphere, shade(P[k], .8)); s.position.set(...e.c); s.scale.setScalar(e.r); return [s]; }}));
    mol.pearls.visible = false; mol.lineMat && mol.group.children.forEach(o => {{ if (o.isInstancedMesh && o.material === mol.lineMat && o.count === 4) o.visible = false; }}); mol.R.strand = .75; }},
  icon: () => {{}},
}};
// one scene per tile; each holds the journey's molecule, centred, and turns gently
const views = [...document.querySelectorAll('.tile')].map(tile => {{
  const opt = tile.dataset.opt, scene = new THREE.Scene(), cam = new THREE.PerspectiveCamera(30, 4 / 3, 1, 2000);
  const mol = makeMolecule(THREE, DATA, Q, geom, new THREE.Vector3(0, -1, .25)); mol.setColors(P);
  const pivot = new THREE.Group(); mol.group.position.copy(mol.centre).negate(); pivot.add(mol.group); scene.add(pivot);
  BUILD[opt](mol);
  cam.position.set(0, 0, 88); cam.lookAt(0, 0, 0);
  const v = {{ tile, el: tile.querySelector('.view'), opt, scene, cam, mol, pivot }};
  if (opt === 'icon') {{ mol.group.visible = false; v.svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg'); v.el.appendChild(v.svg); }}
  return v;
}});
let target = 1, joined = 1, turning = !matchMedia('(prefers-reduced-motion: reduce)').matches;
const bJ = document.getElementById('bJoin'), bS = document.getElementById('bSplit'), bT = document.getElementById('bTurn');
const setJ = j => {{ target = j; bJ.setAttribute('aria-pressed', String(j === 1)); bS.setAttribute('aria-pressed', String(j === 0)); }};
bJ.onclick = () => setJ(1); bS.onclick = () => setJ(0); bT.onclick = () => {{ turning = !turning; bT.setAttribute('aria-pressed', String(turning)); }};
bT.setAttribute('aria-pressed', String(turning));
const I = new THREE.Quaternion(), tmp = new THREE.Vector3();
function project(v, p) {{ tmp.copy(p).project(v.cam); const r = v.el.getBoundingClientRect(); return [(tmp.x + 1) / 2 * r.width, (1 - tmp.y) / 2 * r.height]; }}
// the flat icon: the same molecule, projected, drawn as a glyph (two fused-ring motifs, the linker line, pearls and clasp)
function drawIcon(v) {{
  const m = v.mol, r = v.el.getBoundingClientRect(), W = r.width, H = r.height; v.svg.setAttribute('viewBox', `0 0 ${{W}} ${{H}}`);
  m.group.updateMatrixWorld(true);
  const head = i => {{ const h = m.heads[i].mesh, s = DATA.reps[KEYS[i]]; const c = h.localToWorld(V(s.sphere.c)), e = h.localToWorld(V(s.pebble.c).addScaledVector(V(s.pebble.axes[2]), s.pebble.r[2] * .55));
    return {{ c: project(v, c), e: project(v, e) }}; }};
  const hw = head(0), he = head(1), mat4 = new THREE.Matrix4(), pos = new THREE.Vector3();
  const pts = []; for (let k = 0; k < 4; k++) {{ m.pearls.getMatrixAt(k, mat4); pos.setFromMatrixPosition(mat4); pts.push(project(v, m.group.localToWorld(pos.clone()))); }}
  const cl = []; for (let k = 0; k < 2; k++) {{ m.clasp.getMatrixAt(k, mat4); pos.setFromMatrixPosition(mat4); cl.push(project(v, m.group.localToWorld(pos.clone()))); }}
  const hex = (cx, cy, R, ang) => {{ let d = ''; for (let k = 0; k < 6; k++) {{ const a = ang + Math.PI / 6 + k * Math.PI / 3; d += (k ? 'L' : 'M') + (cx + R * Math.cos(a)).toFixed(1) + ',' + (cy + R * Math.sin(a)).toFixed(1); }} return d + 'Z'; }};
  const motif = (h, col) => {{ const dx = h.e[0] - h.c[0], dy = h.e[1] - h.c[1], L = Math.hypot(dx, dy) || 1, ux = dx / L, uy = dy / L, R = Math.min(W, H) * .062, ang = Math.atan2(uy, ux);
    const a = [h.c[0] - ux * R * .87, h.c[1] - uy * R * .87], b = [h.c[0] + ux * R * .87, h.c[1] + uy * R * .87];
    return `<path d="${{hex(a[0], a[1], R, ang)}}${{hex(b[0], b[1], R, ang)}}" fill="${{col}}" fill-opacity=".18" stroke="${{col}}" stroke-width="3.2" stroke-linejoin="round"/>`; }};
  const chain = [hw.c, pts[0], pts[1], cl[0], cl[1], pts[2], pts[3], he.c];
  const lineA = chain.slice(0, 4).map(p => p.map(n => n.toFixed(1)).join(',')).join(' '), lineB = chain.slice(4).map(p => p.map(n => n.toFixed(1)).join(',')).join(' ');
  const j = joined, R0 = Math.min(W, H) * .016, Rc = R0 * 1.5;
  v.svg.innerHTML = `<polyline points="${{lineA}}" fill="none" stroke="${{P.linker}}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>
    <polyline points="${{lineB}}" fill="none" stroke="${{P.linker}}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>
    <line x1="${{cl[0][0]}}" y1="${{cl[0][1]}}" x2="${{cl[1][0]}}" y2="${{cl[1][1]}}" stroke="${{P.clasp}}" stroke-width="4.5" stroke-linecap="round" opacity="${{Math.max(0, (j - .5) * 2).toFixed(2)}}"/>
    ${{motif(hw, P.warhead)}}${{motif(he, P.e3lig)}}
    ${{pts.map(p => `<circle cx="${{p[0].toFixed(1)}}" cy="${{p[1].toFixed(1)}}" r="${{R0.toFixed(1)}}" fill="#FFFFFF"/>`).join('')}}
    ${{cl.map(p => `<circle cx="${{p[0].toFixed(1)}}" cy="${{p[1].toFixed(1)}}" r="${{Rc.toFixed(1)}}" fill="${{P.clasp}}"/>`).join('')}}`;
}}
let last = performance.now(), t = 0;
function frame(now) {{
  const dt = Math.min(.05, (now - last) / 1000); last = now; if (turning) t += dt;
  joined += (target - joined) * Math.min(1, dt * 3);
  const W = canvas.clientWidth, H = canvas.clientHeight;
  if (canvas.width !== Math.round(W * renderer.getPixelRatio()) || canvas.height !== Math.round(H * renderer.getPixelRatio())) renderer.setSize(W, H, false);
  renderer.setScissor(0, 0, W, H); renderer.setClearColor(0x000000, 0); renderer.clear();
  const hx = 7 + 9 * (1 - joined);
  views.forEach(v => {{
    v.mol.update(new THREE.Vector3(-hx, 0, 0), new THREE.Vector3(hx, 0, 0), I, I, joined);
    if (v.opt !== 'icon') v.pivot.rotation.y = .5 * Math.sin(t * .5); v.pivot.rotation.x = .12 * Math.sin(t * .37);
    if (v.opt === 'icon') {{ v.pivot.rotation.set(0, 0, 0); drawIcon(v); return; }}
    const r = v.el.getBoundingClientRect(); if (r.bottom < 0 || r.top > H) return;
    const y = H - r.bottom; renderer.setViewport(r.left, y, r.width, r.height); renderer.setScissor(r.left, y, r.width, r.height);
    v.cam.aspect = r.width / r.height; v.cam.updateProjectionMatrix(); renderer.render(v.scene, v.cam);
  }});
  requestAnimationFrame(frame);
}}
requestAnimationFrame(frame);
window.__reps = true;
</script>
'''
open(D + 'index.html', 'w', encoding='utf8').write(html)
print('reps/index.html', os.path.getsize(D + 'index.html') // 1024, 'KB')
