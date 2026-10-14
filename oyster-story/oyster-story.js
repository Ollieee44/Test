// Oyster Therapeutics: the SELFTAC 3D scroll story, extracted from the Science page of Website v2.
// Needs: three@0.160.0 through an import map (see index.html), oyster-story.css, the story markup
// (<section class="story" id="story">...) and meshes.json next to this file (or inline as
// <script type="application/json" id="meshes">). The story plays as the #story section scrolls past.
window.__storyStarted = true;
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

const root = document.documentElement, stage = document.getElementById('stage'), canvas = document.getElementById('gl');
// the protein and molecule shapes: inline if the page carries them, else meshes.json beside this script
let DATA;
try {
  const inline = document.getElementById('meshes');
  // <section class="story" data-meshes="other.json"> tries another set of shapes without touching meshes.json
  const src = document.getElementById('story').dataset.meshes;
  DATA = inline ? JSON.parse(inline.textContent) : await (await fetch(src ? new URL(src, location.href) : new URL('meshes.json', import.meta.url))).json();
} catch (e) {
  stage.classList.add('ready');
  const d = document.createElement('div'); d.className = 'nogl'; d.textContent = 'The 3D story could not load its shapes (meshes.json).'; stage.appendChild(d);
  throw e;
}
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

// ---------- palettes ----------
const PAL = {
  nacre: { ring: '#8C5572', ink: '#2B2230', brd4: '#E7C9D6', vhl: '#D6CBE6', elob: '#E8DEDB', eloc: '#DDD2D4', warhead: '#B4678B', e3lig: '#8A73B2',
    linker: '#8C5572', brk: '#2B2230', ub: '#C99BB0', pearl3d: '#F6EEF1', clasp: '#D9A443', e2: '#CDBFDF', prot: '#B9A9B6', wall: '#EADADF', cell: '#D8C6E2', flash: '#8C5572',
    sky: [['#F6EEEC', '#E3D3D8'], ['#F4E7E6', '#E6CBD0'], ['#EFE6EE', '#D9CCE2']] },
  tidepool: { ring: '#06302E', ink: '#06302E', brd4: '#F5D89A', vhl: '#9FD6C6', elob: '#3E7D78', eloc: '#346F6B', warhead: '#F2B84B', e3lig: '#5FC2A6',
    linker: '#EAF3EF', brk: '#F2B84B', ub: '#F7C873', pearl3d: '#EAF3EF', clasp: '#F27D62', e2: '#8CC9B8', prot: '#4F8C86', wall: '#2E6E69', cell: '#3F7F86', flash: '#F2B84B',
    sky: [['#1B6763', '#0F4C4A'], ['#1D615D', '#0E4543'], ['#155A57', '#0A3836']] },
};
Object.assign(PAL, {"pearlink": {"ring": "#120F16", "ink": "#120F16", "brd4": "#E6D3B3", "vhl": "#C4BCCB", "elob": "#3A3541", "eloc": "#322E39", "warhead": "#C9A877", "e3lig": "#968CA0", "linker": "#EDE8E0", "brk": "#D8B98A", "ub": "#E6D3B3", "pearl3d": "#F6F2EC", "clasp": "#D8B98A", "e2": "#A79FB0", "prot": "#4E4857", "wall": "#555057", "flash": "#D8B98A", "sky": [["#2B2731", "#1D1A22"], ["#2D2830", "#1A171F"], ["#26232F", "#16131B"]], "cell": "#605A66"}, "shellcoral": {"ring": "#2F6B5E", "ink": "#2A1410", "brd4": "#F2B9A9", "vhl": "#B9D3C8", "elob": "#EEE2D3", "eloc": "#E3D5C4", "warhead": "#B16959", "e3lig": "#2F6B5E", "linker": "#2F6B5E", "brk": "#2A1410", "ub": "#F0A08F", "pearl3d": "#FFF8EF", "clasp": "#E26D5A", "e2": "#C9DDD4", "prot": "#B7A595", "wall": "#E9D7C2", "flash": "#2F6B5E", "sky": [["#F8EDE0", "#EAD5BE"], ["#F7E8DA", "#EDCDB8"], ["#F1EADF", "#DCD9C8"]], "cell": "#BFCDC4"}, "abyssmint": {"ring": "#061A19", "ink": "#061A19", "brd4": "#D6EDE5", "vhl": "#8FC0B4", "elob": "#2C5A55", "eloc": "#254F4B", "warhead": "#B7D8CF", "e3lig": "#70A59B", "linker": "#E9F5F0", "brk": "#9FF0D0", "ub": "#B8F3DD", "pearl3d": "#F0FAF6", "clasp": "#9FF0D0", "e2": "#7DAFA4", "prot": "#3E7A70", "wall": "#325B58", "flash": "#9FF0D0", "sky": [["#1A403E", "#0E2B2A"], ["#1B3D3B", "#0C2726"], ["#163A3A", "#0A2221"]], "cell": "#3B6964"}, "charcoalviolet": {"ring": "#0F0E14", "ink": "#0F0E14", "brd4": "#D9D0FF", "vhl": "#9A93AC", "elob": "#3A3546", "eloc": "#322E3D", "warhead": "#A08BFF", "e3lig": "#928DA7", "linker": "#EEEAF6", "brk": "#7B5CFF", "ub": "#C4B6FF", "pearl3d": "#F6F4FB", "clasp": "#7B5CFF", "e2": "#9D97B2", "prot": "#4A4458", "wall": "#53505C", "flash": "#7B5CFF", "sky": [["#2A2733", "#1A1820"], ["#2B2632", "#17151D"], ["#25223A", "#14121B"]], "cell": "#5F5A6F"}});
// ---------- the scene: sizes of the barrier, the neuron and the proteasome (Angstrom, like the proteins) ----------
// Change these to restage the story. The halves' path down through the membranes is worked out from them (see HY
// below), so they still pause inside the barrier and at the neuron's membrane. Colours are in PAL above.
const SCENE = {
  // the blood-brain barrier: a row of endothelial cells, seen from just above as the halves sink through
  barrier: { cells: 3, width: 118, height: 16, depth: 96, gap: 2, corner: 7, y: -52, contour: 2.4, opacity: .42, outline: .35 },
  // the neuron: the top of a large cell body below the barrier, its membrane drawn as a bilayer of two shells
  // (`bilayer` apart); `cap` is how much of the sphere is drawn (radians from the top; Math.PI is all of it)
  neuron: { top: -82, radius: 140, bilayer: 6, cap: 1.25, contour: 2.6, opacity: .5, inner: .6, outline: .3, below: 30 },
  // the proteasome: a stand-in barrel of stacked rings with a lumpy cap at each end
  proteasome: { rings: 4, ringRadius: 10, ringTube: 5.2, ringGap: 10, cap: 11, contour: 1.2 },
};

// starts in the palette named on <html data-palette="...">, else Nacre
let pal = PAL[root.getAttribute('data-palette')] ? root.getAttribute('data-palette') : 'nacre';

// ---------- renderer ----------
let renderer;
try { renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true }); }
catch (e) { const d = document.createElement('div'); d.className = 'nogl'; d.textContent = 'This browser cannot show the 3D story (WebGL is unavailable). The copy still follows your scroll.'; stage.appendChild(d); }
const scene = new THREE.Scene(), camera = new THREE.PerspectiveCamera(26, 1, 1, 4000);

// ---------- geometry ----------
function geom(p) {
  const pb = Uint8Array.from(atob(p.pos), c => c.charCodeAt(0)), ib = Uint8Array.from(atob(p.idx), c => c.charCodeAt(0));
  const q = new Int16Array(pb.buffer), pos = new Float32Array(q.length);
  for (let i = 0; i < q.length; i++) pos[i] = q[i] / 100;
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  g.setIndex(new THREE.BufferAttribute(p.idx32 ? new Uint32Array(ib.buffer) : new Uint16Array(ib.buffer), 1));
  g.computeVertexNormals(); g.computeBoundingSphere(); return g;
}
const V = a => new THREE.Vector3(...a), C = DATA.centres;
// turn the crystal so the target sits on the left and the ligase on the right
const axis = V(C.brd4).sub(V(C.vhl)).normalize(), Q = new THREE.Quaternion().setFromUnitVectors(axis, new THREE.Vector3(-1, 0, 0));
const S = k => V(C[k]).applyQuaternion(Q);   // a centre in screen-aligned coordinates

// ---------- Nacre contour material: flat fill, ring lines in the mesh's own frame, soft rim ----------
const contour = {
  vertexShader: `varying vec3 vN; varying vec3 vL; varying vec3 vV;
    void main() { vec4 w = modelMatrix * vec4(position, 1.0); vL = position; vN = normalize(mat3(modelMatrix) * normal); vV = normalize(cameraPosition - w.xyz); gl_Position = projectionMatrix * viewMatrix * w; }`,
  fragmentShader: `uniform vec3 col; uniform vec3 ring; uniform vec3 centre; uniform float spacing; uniform float alpha; uniform float glow; varying vec3 vN; varying vec3 vL; varying vec3 vV;
    void main() {
      vec3 n = normalize(vN); float d = length(vL - centre) / spacing; float f = abs(fract(d) - .5); float w = fwidth(d);
      float line = smoothstep(.5 - 1.6 * w, .5 - .4 * w, f);
      float lit = .82 + .18 * max(dot(n, normalize(vec3(.4, .7, .6))), 0.0);
      float rim = pow(1.0 - max(dot(n, normalize(vV)), 0.0), 2.2);
      vec3 c = col * lit; c = mix(c, ring, line * .55); c = mix(c, ring, rim * .35); c = mix(c, vec3(1.0), glow);
      gl_FragColor = vec4(c, alpha);
      #include <colorspace_fragment>
    }`,
};
function cmat(key, spacing, centre) {
  return new THREE.ShaderMaterial({ ...contour, uniforms: { col: { value: new THREE.Color() }, ring: { value: new THREE.Color() }, centre: { value: centre || new THREE.Vector3() },
    spacing: { value: spacing }, alpha: { value: 1 }, glow: { value: 0 } }, userData: { key } });
}
const outlineVS = `uniform float thick; void main() { vec3 p = position + normalize(normal) * thick; gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.0); }`;
const outlineFS = `uniform vec3 color; uniform float alpha; void main() { gl_FragColor = vec4(color, alpha);
  #include <colorspace_fragment>
}`;
const mats = [], outlines = [];
function addOutline(mesh, thick) {
  const m = new THREE.ShaderMaterial({ uniforms: { color: { value: new THREE.Color() }, thick: { value: thick }, alpha: { value: 1 } }, vertexShader: outlineVS, fragmentShader: outlineFS, side: THREE.BackSide });
  const o = new THREE.Mesh(mesh.geometry, m); o.renderOrder = -1; mesh.add(o); outlines.push(o); return o;
}
// a part: a holder positioned in screen coordinates, holding the crystal-frame mesh turned by Q
function part(key, colorKey, spacing, thick) {
  const g = geom(DATA.parts[key]), mat = cmat(colorKey, spacing, g.boundingSphere.center.clone()); mats.push(mat);
  const mesh = new THREE.Mesh(g, mat); mesh.quaternion.copy(Q); const holder = new THREE.Group(); holder.add(mesh); scene.add(holder);
  addOutline(mesh, thick); return holder;
}
const P = {
  brd4: part('brd4', 'brd4', 1.7, .42), vhl: part('vhl', 'vhl', 1.7, .42), elob: part('elob', 'elob', 1.7, .42), eloc: part('eloc', 'eloc', 1.7, .42),
  brd4b: part('brd4', 'brd4', 1.7, .42),
};
// ubiquitin and E2: centred shapes, scaled down a little so they read as tags
const ubGeo = geom(DATA.parts.ub);
const ubs = [0, 1, 2, 3].map(() => { const mat = cmat('ub', 1.4, ubGeo.boundingSphere.center.clone()); mats.push(mat); const m = new THREE.Mesh(ubGeo, mat); m.scale.setScalar(.42); addOutline(m, .5); scene.add(m); return m; });
const e2 = (() => { const mat = cmat('e2', 1.6, ubGeo.boundingSphere.center.clone()); mats.push(mat); const m = new THREE.Mesh(ubGeo, mat); m.scale.set(.9, .75, .8); addOutline(m, .45); scene.add(m); return m; })();
// proteasome: a stand-in barrel of four stacked rings with a lumpy cap at each end
const prot = new THREE.Group(); scene.add(prot);
{ const S = SCENE.proteasome, half = (S.rings - 1) / 2 * S.ringGap;
  for (let i = 0; i < S.rings; i++) { const mat = cmat('prot', S.contour); mats.push(mat); const r = new THREE.Mesh(new THREE.TorusGeometry(S.ringRadius, S.ringTube, 24, 48), mat);
    r.rotation.y = Math.PI / 2; r.position.x = -half + i * S.ringGap; addOutline(r, .4); prot.add(r); }
  for (const s of [-1, 1]) { const mat = cmat('prot', S.contour); mats.push(mat); const c = new THREE.Mesh(new THREE.IcosahedronGeometry(S.cap, 3), mat);
    c.scale.set(.55, 1.05, 1.05); c.position.x = s * (half + S.cap * 1.09); addOutline(c, .4); prot.add(c); } }
// the see-through membranes must not hide each other through the depth buffer, even when faded almost to
// nothing (a near-invisible barrier outline was clipping the neuron), and they draw in a fixed order from the
// bottom up: inner neuron shell, outer neuron shell, then the barrier on top
function seeThrough(outline, mesh, order) {
  outline.material.transparent = true; outline.material.depthWrite = false; outline.renderOrder = order; mesh.renderOrder = order + 1;
}
// the blood-brain barrier: three endothelial cells side by side, seen from just above
const wall = new THREE.Group(); scene.add(wall);
{ const S = SCENE.barrier;
  for (let i = 0; i < S.cells; i++) { const mat = cmat('wall', S.contour); mat.transparent = true; mat.depthWrite = false; mats.push(mat);
    const b = new THREE.Mesh(new RoundedBoxGeometry(S.width, S.height, S.depth, 6, S.corner), mat);
    b.position.x = (i - (S.cells - 1) / 2) * (S.width + S.gap); seeThrough(addOutline(b, .5), b, 5); wall.add(b); }
  wall.position.y = S.y; }
// the neuron: a large cell body below the barrier; its membrane is drawn as a bilayer of two faint shells
const CELL_TOP = SCENE.neuron.top, CELL_R = SCENE.neuron.radius;
const cell = new THREE.Group(); scene.add(cell); cell.position.set(0, CELL_TOP - CELL_R, 0);
for (const [rad, a] of [[CELL_R, 1], [CELL_R - SCENE.neuron.bilayer, SCENE.neuron.inner]]) { const mat = cmat('cell', SCENE.neuron.contour, new THREE.Vector3(0, CELL_R, 0)); mat.transparent = true; mat.depthWrite = false; mat.userData.a = a; mats.push(mat);
  const m = new THREE.Mesh(new THREE.SphereGeometry(rad, 96, 64, 0, Math.PI * 2, 0, SCENE.neuron.cap), mat); seeThrough(addOutline(m, .5), m, rad < CELL_R ? 1 : 3); cell.add(m); }

// ---------- the degrader: two soft outlined halves joined by a string of pearls ----------
// Each half is a smooth outline traced along its bonds: it reads as a small molecule without showing
// atoms. The linker is generic and emphasised: evenly spaced pearls on a strand, with the reversible bond
// between the middle two. The strand starts and ends inside the two halves (at their attachment atoms),
// so it is always joined to them. Each half moves as a rigid body (offset plus turn about its own
// centre). Points on the linker blend between the two halves: when the molecule is joined they spread
// evenly along it, so it stretches across any gap; when it is split, each side rides with its own half.
function makeMolecule(THREE, D, Q, geom, bow) {
  const still = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const NB = 6, BRK = NB / 2;                    // six pearls; the break sits between pearls 3 and 4
  // the linker is laid out generically rather than folded as in the crystal: a smooth arc from one
  // attachment atom to the other, about as long as the real chain, bowed away from the two halves so the
  // pearls stay in view
  const L = D.linker.curve.map(a => new THREE.Vector3(...a).applyQuaternion(Q)), A0 = L[0], A1 = L[L.length - 1];
  const chainLen = L.slice(1).reduce((s, p, i) => s + p.distanceTo(L[i]), 0) * .9;
  const C0 = new THREE.Vector3(...D.centres.warhead).applyQuaternion(Q), C1 = new THREE.Vector3(...D.centres.e3lig).applyQuaternion(Q);
  const mid = A0.clone().add(A1).multiplyScalar(.5), chord = A1.clone().sub(A0), cl = chord.length(); chord.normalize();
  // bowed toward `bow` (a direction in the molecule's frame) if given, else away from the two halves
  const away = bow ? bow.clone() : mid.clone().sub(C0.clone().add(C1).multiplyScalar(.5)); away.addScaledVector(chord, -away.dot(chord)).normalize();
  const h = Math.sqrt(Math.max(0, chainLen * chainLen - cl * cl) * 3 / 16);
  const ctrl = mid.clone().addScaledVector(away, 2 * h);  // a quadratic arc peaks at half its control height
  const curve0 = new THREE.QuadraticBezierCurve3(A0, ctrl, A1);
  // glossy cartoon shading: two tones, a small highlight and a soft ink rim; no contour lines, so the
  // halves read as a different kind of thing from the proteins
  const VS = `varying vec3 vN; varying vec3 vV;
    void main() { mat4 m = modelMatrix;
      #ifdef USE_INSTANCING
      m = m * instanceMatrix;
      #endif
      vec4 w = m * vec4(position, 1.0); vN = normalize(mat3(m) * normal); vV = normalize(cameraPosition - w.xyz);
      gl_Position = projectionMatrix * viewMatrix * w; }`;
  const FS = `uniform vec3 col; uniform vec3 ink; uniform float gloss; varying vec3 vN; varying vec3 vV;
    void main() {
      vec3 n = normalize(vN), v = normalize(vV), l = normalize(vec3(-.35, .75, .55));
      float shade = mix(.76, 1.0, smoothstep(-.05, .12, dot(n, l)));
      float spec = smoothstep(.965, .985, dot(n, normalize(l + v)));
      float rim = pow(1.0 - max(dot(n, v), 0.0), 2.5);
      vec3 c = col * shade; c = mix(c, ink, rim * .28); c = mix(c, vec3(1.0), spec * gloss);
      gl_FragColor = vec4(c, 1.0);
      #include <colorspace_fragment>
    }`;
  const mats = {};
  const mat = (key, gloss) => (mats[key] = new THREE.ShaderMaterial({ vertexShader: VS, fragmentShader: FS,
    uniforms: { col: { value: new THREE.Color() }, ink: { value: new THREE.Color() }, gloss: { value: gloss } } }));
  const lineMat = new THREE.ShaderMaterial({
    uniforms: { color: { value: new THREE.Color() }, thick: { value: .12 } }, side: THREE.BackSide,
    vertexShader: `uniform float thick; void main() { mat4 m = mat4(1.0);
        #ifdef USE_INSTANCING
        m = instanceMatrix;
        #endif
        vec3 p = (m * vec4(position, 1.0)).xyz + normalize(mat3(m) * normal) * thick;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.0); }`,
    fragmentShader: `uniform vec3 color; void main() { gl_FragColor = vec4(color, 1.0);
      #include <colorspace_fragment>
    }`,
  });
  const group = new THREE.Group();
  const outline = (m, n) => { const o = n ? new THREE.InstancedMesh(m.geometry, lineMat, n) : new THREE.Mesh(m.geometry, lineMat);
    if (n) o.instanceMatrix = m.instanceMatrix; o.renderOrder = -1; o.frustumCulled = false; return o; };

  // the two halves: crystal-frame meshes turned by Q, then by each half's own turn about its centre
  const heads = ['warhead', 'e3lig'].map(k => {
    const g = geom(D.parts[k]), m = new THREE.Mesh(g, mat(k, .3));
    m.add(outline(m)); group.add(m); g.computeBoundingSphere();
    return { mesh: m, c: g.boundingSphere.center.clone().applyQuaternion(Q) };
  });
  const [cW, cE] = heads.map(h => h.c);

  // the linker: pearls (instanced), the strand on each side, and the reversible bond between the middle two
  const ball = new THREE.SphereGeometry(1, 28, 18);
  const pearls = new THREE.InstancedMesh(ball, mat('pearl', .9), NB - 2);
  pearls.frustumCulled = false; group.add(pearls, outline(pearls, NB - 2));
  // the meeting point is the idea worth showing, so it is drawn as a clasp: the two pearls either side of
  // the reversible bond are larger and in an accent colour, the bond is thick and the same colour, and a
  // soft glow breathes around the join while it is closed
  const clasp = new THREE.InstancedMesh(ball, mat('clasp', 1), 2);
  clasp.frustumCulled = false; group.add(clasp, outline(clasp, 2));
  const glowTex = (() => { const c = document.createElement('canvas'); c.width = c.height = 128; const g = c.getContext('2d');
    const r = g.createRadialGradient(64, 64, 0, 64, 64, 64); r.addColorStop(0, 'rgba(255,255,255,1)'); r.addColorStop(.35, 'rgba(255,255,255,.55)'); r.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = r; g.fillRect(0, 0, 128, 128); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; })();
  const glow = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex, transparent: true, depthWrite: false }));
  glow.renderOrder = 2; group.add(glow);
  const strandMat = mat('strand', 0), strands = [0, 1].map(() => { const t = new THREE.Mesh(new THREE.BufferGeometry(), strandMat); const o = outline(t); t.add(o); group.add(t); return t; });
  const bond = new THREE.Mesh(new THREE.CylinderGeometry(1, 1, 1, 18, 1, true), mat('brk', .8));
  bond.add(outline(bond)); group.add(bond);

  // the pearls sit only on the part of the linker that is out in the open: find where the curve leaves
  // each half (a ray-parity inside test against the half's outline) and space the pearls between there
  const inside = (mesh, p) => { const solid = new THREE.Mesh(mesh.geometry, new THREE.MeshBasicMaterial({ side: THREE.DoubleSide }));
    solid.quaternion.copy(Q); solid.updateMatrixWorld();
    return new THREE.Raycaster(p, new THREE.Vector3(.48, .71, .52).normalize()).intersectObject(solid).length % 2 === 1; };
  let u0 = 0, u1 = 1;
  while (u0 < .4 && inside(heads[0].mesh, curve0.getPointAt(u0))) u0 += .01;
  while (u1 > .6 && inside(heads[1].mesh, curve0.getPointAt(u1))) u1 -= .01;
  const uMid = (u0 + u1) / 2, uOf = k => u0 + (u1 - u0) * (k + (k >= BRK ? .25 : 0) + .6) / (NB + .45);   // a slightly wider gap at the break
  const pw = new THREE.Vector3(), pe = new THREE.Vector3(), up = new THREE.Vector3(0, 1, 0), m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), s3 = new THREE.Vector3();
  const R = { pearl: 1.1, clasp: 1.65, strand: .36, bond: .8 };
  // a point on the linker at fraction u, with each half's rigid move applied and blended across
  function along(u, T) {
    const p = curve0.getPointAt(u), side = u < uMid ? 0 : 1;
    T.w(pw.copy(p)); T.e(pe.copy(p));
    const t = u < uMid ? .5 * u / uMid : .5 + .5 * (u - uMid) / (1 - uMid);    // 0 at the warhead, .5 at the break, 1 at the ligand
    return new THREE.Vector3().lerpVectors(pw, pe, side + (t - side) * T.joined);
  }
  // oW, oE: offsets of the two halves; rW, rE: their turns (quaternions); joined: 1 joined, 0 split
  function update(oW, oE, rW, rE, joined) {
    heads[0].mesh.quaternion.multiplyQuaternions(rW, Q); heads[0].mesh.position.copy(cW).sub(cW.clone().applyQuaternion(rW)).add(oW);
    heads[1].mesh.quaternion.multiplyQuaternions(rE, Q); heads[1].mesh.position.copy(cE).sub(cE.clone().applyQuaternion(rE)).add(oE);
    const T = { joined, w: p => p.sub(cW).applyQuaternion(rW).add(cW).add(oW), e: p => p.sub(cE).applyQuaternion(rE).add(cE).add(oE) };
    const P = []; let j = 0;
    for (let k = 0; k < NB; k++) { P.push(along(uOf(k), T)); const c = k === BRK - 1 || k === BRK;
      (c ? clasp : pearls).setMatrixAt(c ? k - BRK + 1 : j++, m4.compose(P[k], q.identity(), s3.setScalar(c ? R.clasp : R.pearl))); }
    pearls.instanceMatrix.needsUpdate = clasp.instanceMatrix.needsUpdate = true;
    // strand: from inside each half to its middle pearl, sampled finely so it bends with the curve
    const half = (u0, u1) => { const pts = []; for (let i = 0; i <= 12; i++) pts.push(along(u0 + (u1 - u0) * i / 12, T)); return pts; };
    [half(0, uOf(BRK - 1)), half(uOf(BRK), 1)].forEach((pts, i) => { const t = strands[i]; t.geometry.dispose();
      t.geometry = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 48, R.strand, 10, false); t.children[0].geometry = t.geometry; });
    // the reversible bond: present when joined, gone when split
    const a = P[BRK - 1], b = P[BRK], d = b.clone().sub(a), len = d.length(), k = Math.max(0, Math.min(1, (joined - .5) / .5));
    bond.visible = k > .01; bond.position.copy(a).add(b).multiplyScalar(.5);
    bond.quaternion.setFromUnitVectors(up, d.divideScalar(len || 1)); bond.scale.set(R.bond * k, len, R.bond * k);
    const breath = still ? 1 : 1 + .08 * Math.sin(performance.now() / 600);
    glow.position.copy(bond.position); glow.scale.setScalar(13 * breath); glow.material.opacity = .72 * k; glow.visible = k > .01;
    return bond.position.clone();
  }
  function setColors(P) {
    mats.warhead.uniforms.col.value.set(P.warhead); mats.e3lig.uniforms.col.value.set(P.e3lig);
    mats.pearl.uniforms.col.value.set(P.pearl3d); mats.strand.uniforms.col.value.set(P.linker); mats.brk.uniforms.col.value.set(P.clasp); mats.clasp.uniforms.col.value.set(P.clasp); glow.material.color.set(P.clasp);
    for (const k in mats) mats[k].uniforms.ink.value.set(P.ink);
    lineMat.uniforms.color.value.set(P.ink);
  }
  group.traverse(o => { o.userData.mol = true; });
  glow.userData.mol = true;
  return { group, update, setColors, centre: cW.clone().add(cE).multiplyScalar(.5) };
}

const mol = makeMolecule(THREE, DATA, Q, geom, new THREE.Vector3(0, -1, .25)); scene.add(mol.group);
const flash = new THREE.Mesh(new THREE.RingGeometry(1.6, 2.1, 48), new THREE.MeshBasicMaterial({ transparent: true, side: THREE.DoubleSide })); scene.add(flash);

// ---------- colours ----------
function applyPalette() {
  const c = PAL[pal]; root.setAttribute('data-palette', pal);
  mats.forEach(m => { m.uniforms.col.value.set(c[m.userData.key]); m.uniforms.ring.value.set(c.ring); });
  outlines.forEach(o => o.material.uniforms.color.value.set(c.ink));
  flash.material.color.set(c.clasp); mol.setColors(c);
  document.querySelectorAll('.pal button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.pal === pal)));
}
document.querySelectorAll('.pal button').forEach(b => b.addEventListener('click', () => { pal = b.dataset.pal; applyPalette(); }));

// ---------- timeline helpers ----------
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const ease = t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
// keyframes: [[p, value], ...]; value a number or an array; eased between neighbours
function kf(p, keys) {
  if (p <= keys[0][0]) return keys[0][1];
  for (let i = 1; i < keys.length; i++) if (p <= keys[i][0]) {
    const [p0, a] = keys[i - 1], [p1, b] = keys[i], t = ease((p - p0) / (p1 - p0));
    return Array.isArray(a) ? a.map((v, j) => v + (b[j] - v) * t) : a + (b - a) * t;
  }
  return keys[keys.length - 1][1];
}
// a smooth curve through keys [[t, v], ...]: the speed carries through each key instead of stopping there
// (monotone cubic, Fritsch-Butland tangents, so it never overshoots a key); it eases in and out at its ends
function curve(keys) {
  const n = keys.length, x = keys.map(k => k[0]), y = keys.map(k => k[1]), h = [], d = [], m = new Array(n).fill(0);
  for (let i = 0; i < n - 1; i++) { h[i] = x[i + 1] - x[i]; d[i] = (y[i + 1] - y[i]) / h[i]; }
  for (let i = 1; i < n - 1; i++) if (d[i - 1] * d[i] > 0) { const w1 = 2 * h[i] + h[i - 1], w2 = h[i] + 2 * h[i - 1]; m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i]); }
  return t => {
    if (t <= x[0]) return y[0]; if (t >= x[n - 1]) return y[n - 1];
    let i = 0; while (t > x[i + 1]) i++;
    const u = (t - x[i]) / h[i], u2 = u * u, u3 = u2 * u;
    return (2 * u3 - 3 * u2 + 1) * y[i] + (u3 - 2 * u2 + u) * h[i] * m[i] + (-2 * u3 + 3 * u2) * y[i + 1] + (u3 - u2) * h[i] * m[i + 1];
  };
}
const bump = (p, a, b) => { const t = clamp((p - a) / (b - a), 0, 1); return Math.sin(Math.PI * t); };

// ---------- the story ----------
// Screen-aligned offsets in angstroms. In the crystal frame the degrader sits near the origin, BRD4 to
// its left and VHL to its right. Y is the depth of the scene: the halves sink through the barrier.
const Yn = CELL_TOP - SCENE.neuron.below;   // neuron level: where the complex forms, inside the neuron
const GAP = 12;                       // each side is pulled out this far so the degrader shows in the complex
const SPREAD = 7;                     // the degrader alone is shown slightly opened so its linker reads
const BEATS = [[0, .13], [.13, .26], [.26, .4], [.4, .6], [.6, .767], [.767, .883], [.883, 1]];
// the original six-beat timeline runs on q; the neuron beat holds it at .46 (halves just under the
// barrier) for 40%-58% of the scroll while the halves cross the neuron's membrane
const HOLD = [.4, .58], QH = .46;
// the hold is eased in and out (the old timeline slows to a stop and picks up again) so nothing lurches
const warp = (() => { const N = 2000, W = .03, sm = t => { t = clamp(t, 0, 1); return t * t * (3 - 2 * t); }, a = new Float32Array(N + 1), b = new Float32Array(N + 1);
  for (let i = 1; i <= N; i++) { const x = (i - .5) / N; a[i] = a[i - 1] + (1 - sm((x - HOLD[0] + W) / (2 * W))) / N; b[i] = b[i - 1] + sm((x - HOLD[1] + W) / (2 * W)) / N; }
  return p => { const f = clamp(p, 0, 1) * N, i = Math.min(N - 1, Math.floor(f)), t = f - i, A = a[i] + (a[i + 1] - a[i]) * t, B = b[i] + (b[i + 1] - b[i]) * t;
    return QH * A / a[N] + (1 - QH) * B / b[N]; }; })();
// target on BRD4 for the ubiquitin chain: its upper surface, on the side facing VHL
const ubSpot = (() => { const g = P.brd4.children[0].geometry, pos = g.attributes.position, v = new THREE.Vector3(); let best = null, bs = -1e9;
  for (let i = 0; i < pos.count; i++) { v.fromBufferAttribute(pos, i).applyQuaternion(Q); const s = v.y + .5 * v.x; if (s > bs) { bs = s; best = v.clone(); } } return best; })();
const vhlTop = (() => { const g = P.vhl.children[0].geometry, pos = g.attributes.position, v = new THREE.Vector3(); let best = null, bs = -1e9;
  for (let i = 0; i < pos.count; i++) { v.fromBufferAttribute(pos, i).applyQuaternion(Q); const s = v.y - .4 * v.x; if (s > bs) { bs = s; best = v.clone(); } } return best; })();
const PROT_AT = new THREE.Vector3(-118, Yn - 62, 0);
const degC = S('warhead').add(S('e3lig')).multiplyScalar(.5);
// the halves' depth against the scroll: in over the barrier's top, slowly through it, out under it, then slowly
// through the neuron's membrane and down to the neuron level (with the default scene: barrier -44 to -60, membrane -82)
const B_TOP = SCENE.barrier.y + SCENE.barrier.height / 2, B_BOT = SCENE.barrier.y - SCENE.barrier.height / 2;
const HY = curve([[.255, 0], [.31, B_TOP + 4], [.345, B_TOP - 2], [.385, B_BOT - 2], [.42, B_BOT - 7], [.46, CELL_TOP + 2], [.5, CELL_TOP - 2], [.55, CELL_TOP - 12], [.62, Yn]]);
// the camera: one smooth curve per setting, keyed on the scroll. Close on the degrader, back for the split,
// over the barrier looking down, riding down with the halves through both membranes, round to the side
// for the complex once the neuron has faded, across to the proteasome, and out for the end card.
const CAM = (() => {
  const fy = hy => degC.y + hy + (10 - degC.y) * clamp(hy / Yn, 0, 1);   // the camera's aim while it follows the halves
  const ty = [[0, degC.y], [.255, degC.y]];
  for (let t = .27; t < .615; t += .015) ty.push([t, fy(HY(t))]);
  ty.push([.62, Yn + 10], [.76, Yn], [.84, Yn - 18], [.87, Yn - 17], [.95, Yn], [1, Yn]);
  return {
    tx: curve([[0, degC.x], [.62, degC.x], [.76, 0], [.84, -40], [.87, -38], [.95, 0], [1, 0]]),
    ty: curve(ty),
    tz: curve([[0, degC.z], [.62, degC.z], [.76, 0], [1, 0]]),
    dist: curve([[0, 100], [.12, 112], [.24, 158], [.32, 188], [.4, 178], [.62, 176], [.74, 250], [.86, 320], [1, 430]]),
    az: curve([[0, -.35], [.11, .27], [.2, .2], [.3, .08], [.4, -.2], [.62, -.27], [.76, .14], [.86, -.05], [1, .22]]),
    el: curve([[0, .12], [.14, .18], [.25, .22], [.32, .6], [.4, .48], [.62, .46], [.75, .14], [1, .1]]),
  };
})();
// the free halves tumble on a clock that runs while the page is scrolling and settles when it stops
let spin = 0;

// ---------- v2 load-in: the fan mark holds, then its pearl becomes the clasp as the two halves close on it ----------
// The mark stays up for LOGO_MS (and until the first frame is drawn). Then, over INTRO_MS, the loader's ground fades
// and the shell shrinks away; the mark's pearl flies to where the clasp will be and turns gold; the two halves fly
// in from far behind along the line of sight to the clasp (so they grow in place, clear of the copy), close on it, and the bond clicks shut with a flash as the pearl melts into the clasp.
const LOGO_MS = 1700, INTRO_MS = 2100, pageT0 = performance.now();
const loaderEl = stage.querySelector('.loader'), claspNdc = new THREE.Vector3();
let introAnim = null, introHold = -1;
let intro = (reduce || !renderer || !loaderEl || location.hash.length > 1) ? 1 : 0, introStart = -1, drawnSig = '', firstDrawn = false;
function startIntro(now) {
  introStart = now;
  stage.classList.add('ready');
  if (intro >= 1) return;
  const src = loaderEl.querySelector('.pearl');
  if (!src) { intro = 1; return; }
  // aim the pearl at where the clasp will be once the halves have closed
  intro = 1; frame(prog); const aim = claspNdc.clone(); intro = 0; frame(prog);
  const sr = stage.getBoundingClientRect(), r = src.getBoundingClientRect(), cs = getComputedStyle(root);
  const d0 = Math.max(4, r.width), x0 = r.left - sr.left + r.width / 2, y0 = r.top - sr.top + r.height / 2;
  const x1 = (aim.x + 1) / 2 * stage.clientWidth, y1 = (1 - aim.y) / 2 * stage.clientHeight;
  const k = Math.max(26, Math.min(48, stage.clientWidth * .026)) / d0, mv = `translate(${(x1 - x0).toFixed(1)}px, ${(y1 - y0).toFixed(1)}px)`;
  const pearlCol = cs.getPropertyValue('--pearl').trim(), claspCol = cs.getPropertyValue('--clasp').trim();
  const el = document.createElement('i'); el.className = 'lpearl'; el.setAttribute('aria-hidden', 'true');
  Object.assign(el.style, { width: d0 + 'px', height: d0 + 'px', left: (x0 - d0 / 2) + 'px', top: (y0 - d0 / 2) + 'px', background: pearlCol });
  stage.appendChild(el); src.style.opacity = '0';
  // eased leg by leg: fly to the clasp (0-50%), wait there while the halves arrive (to 78%), then pop and melt into
  // the bond as it clicks shut (to 90%)
  const fly = 'cubic-bezier(.45, 0, .2, 1)', pop = 'cubic-bezier(.2, .7, .3, 1)';
  introAnim = el.animate([
    { transform: 'translate(0, 0) scale(1)', backgroundColor: pearlCol, opacity: 1, offset: 0, easing: fly },
    { transform: `${mv} scale(${k})`, backgroundColor: claspCol, opacity: 1, offset: .5, easing: 'linear' },
    { transform: `${mv} scale(${k})`, backgroundColor: claspCol, opacity: 1, offset: .78, easing: pop },
    { transform: `${mv} scale(${k * 1.7})`, backgroundColor: claspCol, opacity: 0, offset: .9 },
    { transform: `${mv} scale(${k * 1.7})`, backgroundColor: claspCol, opacity: 0, offset: 1 },
  ], { duration: INTRO_MS, easing: 'linear', fill: 'forwards' });
  introAnim.finished.then(() => el.remove(), () => el.remove());
}

// test hook: hold the load-in at ms milliseconds (screenshots)
window.__intro = ms => {
  if (!introAnim || ms === 0) {   // start over
    if (introAnim) introAnim.cancel();
    stage.querySelectorAll('.lpearl').forEach(e => e.remove());
    intro = 0; startIntro(performance.now());
  }
  introHold = ms / INTRO_MS; if (introAnim) { introAnim.pause(); introAnim.currentTime = ms; }
};

function frame(p0) {
  const p = warp(p0);
  // the two halves: joined, split, sinking through the wall (pausing at each membrane), rejoined in the neuron
  const hx = kf(p, [[.15, SPREAD], [.27, 22], [.5, 22], [.58, 22], [.66, GAP], [1, GAP]]);
  // one continuous sink on the scroll: slowing inside the barrier cells and again in the neuron's membrane
  const hy = HY(p0);
  const joined = kf(p, [[.16, 1], [.2, 0], [.6, 0], [.665, 1]]);
  // load-in: the halves fly in from far behind and close on the pearl (only at the top of the story)
  const ia = 1 - clamp(p0 / .05, 0, 1), ei = ease(clamp((intro - .2) / .6, 0, 1));
  const hxI = hx + ia * (1 - ei) * 8, joinedI = joined * (1 - ia * (1 - clamp((intro - .8) / .08, 0, 1)));
  // straight back along the line of sight: a fixed 160 units on wide screens; on portrait screens (the story's own
  // test, aspect < .9) the camera is pulled further back, so there it is 1.6 camera distances, to start as specks
  const away = mol.centre.clone().sub(camera.position);
  if (camera.aspect < .9) away.multiplyScalar(ia * (1 - ei) * 1.6); else away.normalize().multiplyScalar(ia * (1 - ei) * 160);
  const oW = new THREE.Vector3(-hxI, hy, 0).add(away), oE = new THREE.Vector3(hxI, hy, 0).add(away);
  // tumble the free halves a little while they travel, each about its own centre; settle before they rebind
  const free = kf(p, [[.17, 0], [.24, 1], [.56, 1], [.64, 0]]);
  const rW = new THREE.Quaternion().setFromEuler(new THREE.Euler(free * .35 * Math.sin(spin * 1.3), free * .5 * Math.sin(spin * .9) + ia * (1 - ei) * .9, 0));
  const rE = new THREE.Quaternion().setFromEuler(new THREE.Euler(free * -.3 * Math.sin(spin * 1.1), free * .45 * Math.cos(spin * 1.2) - ia * (1 - ei) * .9, 0));
  const brk = mol.update(oW, oE, rW, rE, joinedI);
  // the bond clicking shut
  const fs = bump(p, .655, .69), fi = ia * bump(intro, .8, 1), fx = Math.max(fs, fi); flash.position.copy(brk);
  flash.scale.setScalar(1 + 3 * (fi > fs ? clamp((intro - .8) / .2, 0, 1) : clamp((p - .655) / .035, 0, 1))); flash.material.opacity = fx * .9; flash.visible = fx > .01;
  flash.lookAt(camera.position);
  // target and ligase glide in once the halves reach the neuron; the target leaves for the proteasome
  // BRD4 rises into place from below (clear of the copy on the left), later leaving for the proteasome
  const bx = kf(p, [[.53, -70], [.64, -GAP], [.79, -GAP], [.84, PROT_AT.x + 12]]), by = kf(p, [[.53, Yn - 170], [.64, Yn], [.79, Yn], [.84, PROT_AT.y + 4]]);
  const bs = kf(p, [[.79, 1], [.845, .18]]);
  P.brd4.position.set(bx, by, 0); P.brd4.scale.setScalar(bs); P.brd4.visible = p > .52 && p < .86;
  const vx = kf(p, [[.53, 200], [.64, GAP], [1, GAP]]);
  for (const k of ['vhl', 'elob', 'eloc']) { P[k].position.set(vx, Yn, 0); P[k].visible = p > .52; }
  // E2 docks on top of VHL and hands four ubiquitins, one at a time, onto the face of BRD4 that faces it
  const e2in = kf(p, [[.7, 0], [.725, 1], [.8, 1], [.83, 0]]);
  const dock = vhlTop.clone().add(new THREE.Vector3(GAP - 4, Yn + 10, 0));
  e2.position.copy(dock).add(new THREE.Vector3(60 * (1 - e2in), 40 * (1 - e2in), 0)); e2.visible = e2in > .01; e2.rotation.y = p * 4;
  ubs.forEach((u, i) => {
    const t0 = .728 + i * .014, hop = clamp((p - t0) / .012, 0, 1);
    const slot = ubSpot.clone().add(new THREE.Vector3(-GAP - 1.5 * i, Yn + 4 + 9 * i, (i % 2 ? 3 : -3)));
    const from = e2.position.clone().add(new THREE.Vector3(-8, -2, 0));
    const pos = from.lerp(slot, ease(hop)); pos.y += 8 * Math.sin(Math.PI * hop);
    // once attached they ride with BRD4 into the proteasome
    const ride = clamp((p - .79) / .055, 0, 1); pos.lerp(PROT_AT.clone().add(new THREE.Vector3(12, 4, 0)), ease(ride));
    u.position.copy(pos); u.scale.setScalar(.42 * (1 - .8 * ride)); u.visible = p > t0 - .004 && e2in + hop > .01 && p < .85;
  });
  // proteasome appears, swallows the tagged target, then fades
  const pin = kf(p, [[.76, 0], [.79, 1], [.9, 1], [.95, 0]]);
  prot.position.copy(PROT_AT); prot.scale.setScalar(Math.max(.001, pin)); prot.visible = pin > .01; prot.rotation.x = p * 3;
  // a second target arrives for the same degrader
  const b2 = kf(p, [[.86, -70], [.95, -GAP]]), b2y = kf(p, [[.86, Yn - 170], [.95, Yn]]); P.brd4b.position.set(b2, b2y, 0); P.brd4b.visible = p > .86;
  // the barrier, seen from just above as the halves sink through it
  // the barrier fades out, the neuron fades in and the ground turns to the neuron's, all together (38-44%),
  // so everything has settled before the halves reach the membrane
  const wa = kf(p, [[.27, 0], [.32, 1]]) * (1 - ease(clamp((p0 - .38) / .06, 0, 1))); wall.visible = wa > .01;
  wall.children.forEach(b => { b.material.uniforms.alpha.value = SCENE.barrier.opacity * wa; b.children[0].material.uniforms.alpha.value = SCENE.barrier.outline * wa; });
  // the neuron rises into view under the barrier and fades once the halves are inside
  const ca = kf(p0, [[.37, 0], [.44, 1], [.57, 1], [.64, 0]]); cell.visible = ca > .01;
  cell.children.forEach(m => { m.material.uniforms.alpha.value = SCENE.neuron.opacity * m.material.userData.a * ca; m.children[0].material.uniforms.alpha.value = SCENE.neuron.outline * ca; });
  // camera: close on the degrader, back for the split, down with the halves, wide on the complex, across to the proteasome, out for the end
  // portrait screens have no room beside the copy: pull back until the subject fits the width
  const narrow = camera.aspect < .9, fitW = narrow ? Math.max(1, 1.1 / camera.aspect) : 1;
  const tgt = new THREE.Vector3(CAM.tx(p0), CAM.ty(p0), CAM.tz(p0)), dist = fitW * CAM.dist(p0), az = CAM.az(p0), el = CAM.el(p0);
  camera.position.set(tgt.x + dist * Math.sin(az) * Math.cos(el), tgt.y + dist * Math.sin(el), tgt.z + dist * Math.cos(az) * Math.cos(el));
  camera.lookAt(tgt);
  // compose to the right of the copy: slide the camera sideways so the subject sits right of centre,
  // easing back to the middle for the end card
  const settle = 1 - ease(clamp((p0 - .88) / .11, 0, 1)), right = new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 0);
  if (narrow) {   // portrait: centre the subject and lift it above the copy, which sits low on the screen
    const up = new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 1);
    camera.position.addScaledVector(up, -.07 * dist * settle);
  } else camera.position.addScaledVector(right, -.16 * dist * settle);
  camera.updateMatrixWorld();
  // ground colour: blood, barrier, neuron
  const sky = PAL[pal].sky, k1 = clamp((p - .28) / .08, 0, 1), k2 = ease(clamp((p0 - .37) / .07, 0, 1));
  const mix = (a, b, t) => '#' + new THREE.Color(a).lerp(new THREE.Color(b), t).getHexString();
  stage.style.setProperty('--sky-a', mix(mix(sky[0][0], sky[1][0], k1), sky[2][0], k2)); stage.style.setProperty('--sky-b', mix(mix(sky[0][1], sky[1][1], k1), sky[2][1], k2));
  // copy, rail, end card
  document.querySelectorAll('.beat').forEach((b, i) => { const [a, z] = BEATS[i];
    const o = i === BEATS.length - 1 ? clamp((p0 - a) / .03, 0, 1) * (1 - clamp((p - .93) / .03, 0, 1)) : i === 0 ? clamp((z - p0) / .03, 0, 1) : clamp(Math.min((p0 - a) / .03, (z - p0) / .03), 0, 1);   // the first line is there from the start
    b.style.opacity = o.toFixed(3); b.style.transform = 'translateY(calc(-50% + ' + ((1 - o) * 16).toFixed(1) + 'px))'; });
  document.querySelectorAll('.rail b').forEach((b, i) => { b.style.setProperty('--f', clamp((p0 - BEATS[i][0]) / (BEATS[i][1] - BEATS[i][0]), 0, 1).toFixed(3)); b.closest('.rail > div').classList.toggle('on', p0 >= BEATS[i][0]); });
  const endO = clamp((p - .955) / .035, 0, 1); const end = document.getElementById('end'); end.style.opacity = endO; end.style.pointerEvents = endO > .9 ? 'auto' : 'none';
  document.getElementById('copy').style.opacity = 1 - endO;
  canvas.style.opacity = (1 - .88 * endO).toFixed(3);
  document.getElementById('hint').style.opacity = 1 - clamp(p / .02, 0, 1);
  const skip = document.getElementById('skip'); if (skip) skip.classList.toggle('gone', p0 > .92);
  claspNdc.copy(brk).project(camera);   // where the load-in's pearl lands
}

// ---------- scroll: a smoothed progress through the pinned story ----------
const story = document.getElementById('story');
function target() { const r = story.getBoundingClientRect(); return clamp(-r.top / (r.height - innerHeight), 0, 1); }
let goalNow = target(), storyOn = true;
function measure() { goalNow = target(); storyOn = story.getBoundingClientRect().bottom > 0; }
addEventListener('scroll', measure, { passive: true }); addEventListener('resize', measure);
let prog = goalNow, last = performance.now(), hold = false, tumbleAct = 0;
function resize() { const w = stage.clientWidth, h = stage.clientHeight; if (renderer) { renderer.setPixelRatio(Math.min(devicePixelRatio, 2)); renderer.setSize(w, h, false); } camera.aspect = w / h; camera.updateProjectionMatrix(); }
addEventListener('resize', resize); resize(); applyPalette();
function loop(t) {
  const dt = Math.min(.1, (t - last) / 1000); last = t;
  const goal = hold ? prog : goalNow; prog += (goal - prog) * (reduce ? 1 : 1 - Math.exp(-dt / .3)); if (Math.abs(goal - prog) < 1e-5) prog = goal;
  // skip the work while the story is scrolled out of view
  // the tumble clock runs while the story is moving and winds down over about a second once it stops
  const moving = Math.abs(goal - prog) > 2e-4 ? 1 : 0; tumbleAct += (moving - tumbleAct) * (1 - Math.exp(-dt / .45)); if (!reduce) spin += dt * tumbleAct * 1.1;
  const now = performance.now();
  if (introStart < 0 && firstDrawn && now - pageT0 > (intro >= 1 ? 0 : LOGO_MS)) startIntro(now);
  if (introHold >= 0) intro = introHold; else if (introStart >= 0 && intro < 1) intro = Math.min(1, (now - introStart) / INTRO_MS);
  const sig = prog.toFixed(5) + '|' + spin.toFixed(4) + '|' + pal + '|' + intro.toFixed(4) + '|' + stage.clientWidth + 'x' + stage.clientHeight;
  if (storyOn && sig !== drawnSig) { frame(prog); if (renderer) renderer.render(scene, camera); drawnSig = sig; firstDrawn = true; }
  requestAnimationFrame(loop);
}
// every shader is built before the first frame, so nothing hitches when a new part of the story comes into view
if (renderer) { try { renderer.compile(scene, camera); } catch (e) {} }
requestAnimationFrame(loop);

window.__story = { frame: p => { hold = true; prog = p; frame(p); renderer.render(scene, camera); }, setPal: v => { pal = v; applyPalette(); } };
