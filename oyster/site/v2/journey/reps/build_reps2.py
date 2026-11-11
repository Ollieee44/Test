"""SELFTAC representations, round 2 (reps2/index.html): atomic space-filling models and variations on the pearl, on the
journey's own geometry and the v3/v4 palette. Built from build_reps.py's page (same molecule, linker, clasp, controls,
renderer); only the options change. The atoms are the journey's own generic halves (reps_atoms.json, from atoms_data.py),
so the space-filling models are the invented ring systems, never a real ligand."""
import json, os, re
D = os.path.dirname(os.path.abspath(__file__)) + '/'
src = open(D + 'build_reps.py', encoding='utf8').read()
once = lambda s, a, b: (s.count(a) == 1 or (_ for _ in ()).throw(AssertionError(a[:80]))) and s.replace(a, b)

# the v3/v4 page and palette
src = once(src, "page = open(D + '../click3/index.html', encoding='utf8').read()", "page = open(D + '../click5/index.html', encoding='utf8').read()")
src = once(src, '''pal = re.search(r"PAL\\.otx = \\{ \\.\\.\\.PAL\\.tidepool, (.*?) \\};", page).group(1)''',
           '''pal = re.search(r"PAL\\.otx = \\{ \\.\\.\\.PAL\\.tidepool, (.*?) \\};", page).group(1) + ', ' + re.search(r"PAL\\.otx = \\{ \\.\\.\\.PAL\\.otx, (.*?) \\};", page).group(1)''')
src = once(src, "DATA = open(D + 'reps_data.json').read()", "DATA = json.dumps({**json.load(open(D + 'reps_data.json')), 'atoms': json.load(open(D + 'reps_atoms.json')), 'mesh': json.load(open(D + 'reps_mesh.json'))})")

src = once(src, src[src.index('OPTIONS = ['):src.index(']\ntiles')], '''OPTIONS = [
    ('spacefill', 'Space-filling', 'Every heavy atom as a sphere at its van der Waals size, all in the half’s colour: a real molecule’s bulk, without element colours.'),
    ('spacefill_h', 'Space-filling, with hydrogens', 'The same with its hydrogens, paler: rounder and softer, closer to how a chemist pictures the molecule.'),
    ('spacefill_het', 'Space-filling, quiet heteroatoms', 'Carbons in the half’s colour, nitrogen, oxygen and sulfur a shade deeper: a hint of the chemistry, kept in palette.'),
    ('pearls', 'Pearl cluster (v4)', 'Today’s v4: each half as a few glossy pearls spread along its mass.'),
    ('ringpearls', 'Ring pearls', 'One large pearl for each ring and small pearls for the atoms between: the ring systems read at a glance.'),
    ('necklace', 'Pearl necklace', 'A small pearl on every atom, strung along the bonds: each half becomes a strand like the linker.'),
    ('graduated', 'Graduated pearls', 'Pearls on the atoms, growing from the linker outward: the halves bloom from the clasp.'),
    ('nacre', 'Nacre pearls', 'The pearl cluster with a pearlescent sheen that shifts through the palette as it turns.'),
    ('shell', 'Pearls in a shell', 'Ring pearls inside a faint, glassy outline of the half: structure and shape together.'),
    ('glass', 'Glass shell', 'A translucent surface round each half, brighter at its edges like glass, with today’s ring drawing inside.'),
    ('wire', 'Wire mesh', 'The half’s surface as a low-poly mesh of fine lines over a faint fill: technical and light.'),
    ('glassatoms', 'Glass atoms', 'Space-filling, but every atom a translucent glass bead: the molecule’s bulk without its weight.'),
''')
src = once(src, "<h1>Six ways to draw the SELFTAC.</h1>", "<h1>More ways to draw the SELFTAC.</h1>")
src = once(src, "<span class=\"k\">SELFTAC&reg; degrader &middot; representation options</span>", "<span class=\"k\">SELFTAC&reg; degrader &middot; representations, round 2</span>")
src = once(src, "the length is the same throughout. Only how the halves are drawn changes.</p>",
           "the length is the same throughout. Only how the halves are drawn changes. The atoms are the journey&rsquo;s own invented ring systems, never a real ligand.</p>")
src = once(src, "<title>SELFTAC Representations</title>", "<title>SELFTAC Representations 2</title>")
# Abyss ground and darker cards, as the v3/v4 journey
src = once(src, ":root {{ --paper: #158B63; --ink: #F5FFFC; --muted: #A8D8C6; --accent: #30FCBA; --clasp: #F7D16B; --card: rgba(6, 46, 33, .32); --line: rgba(245, 255, 252, .14);",
           ":root {{ --paper: #1A372A; --ink: #EBEBE3; --muted: #BADECD; --accent: #67B791; --clasp: #DCA84E; --card: rgba(7, 13, 10, .38); --line: rgba(235, 235, 227, .14);")
src = once(src, ".bar button[aria-pressed=\"true\"] {{ background: rgba(255,255,255,.92); color: #0E5C42; }}", ".bar button[aria-pressed=\"true\"] {{ background: #DCA84E; color: #070D0A; border-color: #DCA84E; }}")
src = src.replace('#8AC3B1', '#67B791')

NEW = r'''
const VDW = {{ C: 1.7, N: 1.55, O: 1.52, S: 1.8, H: 1.1 }};
const A_ = k => DATA.atoms[k], heavy = k => A_(k).el.map((e, i) => [e, i]).filter(([e]) => e !== 'H').map(([, i]) => i);
const tint = (hex, f, to = '#FFFFFF') => '#' + new THREE.Color(hex).lerp(new THREE.Color(to), f).getHexString();
const ball = (col, gloss, at, r) => {{ const s = new THREE.Mesh(sphere, shade(col, gloss)); s.position.set(...at); s.scale.setScalar(r); return s; }};
// pearlescent shading for the nacre option: the half's colour with a sheen that shifts through the palette with the view
const NFS = `uniform vec3 col; uniform vec3 ink; varying vec3 vN; varying vec3 vV; varying vec3 vP;
  void main() {{ vec3 n = normalize(vN), v = normalize(vV), l = normalize(vec3(-.35, .75, .55)); float nv = max(dot(n, v), 0.0);
    float shade = mix(.8, 1.0, smoothstep(-.05, .3, dot(n, l))); float spec = pow(max(dot(n, normalize(l + v)), 0.0), 60.0);
    vec3 a = vec3(.73, .87, .80), b = vec3(.81, .90, .95), c = vec3(.94, .65, .79); float t = fract((1.0 - nv) * 1.6 + n.y * .35);
    vec3 irid = t < .5 ? mix(a, b, t * 2.0) : mix(b, c, (t - .5) * 2.0);
    vec3 o = mix(col * shade, irid, .38 * pow(1.0 - nv, 1.2)); o = mix(o, ink, pow(1.0 - nv, 3.0) * .2); o += spec * .7; gl_FragColor = vec4(o, 1.0);
    #include <colorspace_fragment>
  }}`;
const nacre = col => new THREE.ShaderMaterial({{ vertexShader: VS, fragmentShader: NFS, uniforms: {{ col: {{ value: new THREE.Color(col) }}, ink: {{ value: new THREE.Color(P.ink) }} }} }});
const ringPearls = k => {{ const a = A_(k), inRing = new Set(a.rings.flat()), out = [];
  a.rings.forEach(r => {{ const c = r.reduce((s, i) => s.add(V(a.xyz[i])), new THREE.Vector3()).multiplyScalar(1 / r.length);
    const rad = r.reduce((s, i) => s + V(a.xyz[i]).distanceTo(c), 0) / r.length; out.push(ball(P[k], .9, c.toArray(), rad * 1.08)); }});
  heavy(k).filter(i => !inRing.has(i)).forEach(i => out.push(ball(P[k], .9, a.xyz[i], .62)));
  return out; }};
const cyl = new THREE.CylinderGeometry(1, 1, 1, 14);
const stick = (col, p, q, r) => {{ const a = V(p), b = V(q), m = new THREE.Mesh(cyl, shade(col, .2)); m.position.copy(a).add(b).multiplyScalar(.5);
  m.scale.set(r, a.distanceTo(b), r); m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), b.clone().sub(a).normalize()); return m; }};
'''
GLASS = r'''
// glass: a translucent fresnel surface, faint face-on and bright at the silhouette, drawn after what it encloses
const GFS = `uniform vec3 col; uniform float base; varying vec3 vN; varying vec3 vV; varying vec3 vP;
  void main() {{ vec3 n = normalize(vN), v = normalize(vV); if (!gl_FrontFacing) n = -n; float f = pow(1.0 - abs(dot(n, v)), 2.2);
    float spec = pow(max(dot(n, normalize(normalize(vec3(-.35, .75, .55)) + v)), 0.0), 50.0);
    gl_FragColor = vec4(mix(col, vec3(1.0), f * .45 + spec * .8), base + .75 * f + spec * .6);
    #include <colorspace_fragment>
  }}`;
const glassMat = (col, base = .08) => new THREE.ShaderMaterial({{ vertexShader: VS, fragmentShader: GFS, transparent: true, depthWrite: false,
  uniforms: {{ col: {{ value: new THREE.Color(col) }}, base: {{ value: base }} }} }});
const addTo = (h, o, order = 3) => {{ o.renderOrder = order; h.mesh.add(o); return o; }};
'''
src = once(src, "const BUILD = {{\n", NEW + GLASS + "const BUILD = {{\n")
b0 = src.index("const BUILD = {{\n") + len("const BUILD = {{\n"); b1 = src.index("}};\n// one scene per tile")
src = src[:b0] + r'''  spacefill: mol => mol.heads.forEach((h, i) => swapHead(h.mesh, KEYS[i], k => heavy(k).map(j => ball(P[k], .35, A_(k).xyz[j], VDW[A_(k).el[j]] * .92)))),
  spacefill_h: mol => mol.heads.forEach((h, i) => swapHead(h.mesh, KEYS[i], k => A_(k).el.map((e, j) => ball(e === 'H' ? tint(P[k], .55) : P[k], .35, A_(k).xyz[j], VDW[e] * .92)))),
  spacefill_het: mol => mol.heads.forEach((h, i) => swapHead(h.mesh, KEYS[i], k => heavy(k).map(j => {{ const e = A_(k).el[j];
    return ball(e === 'C' ? P[k] : tint(P[k], e === 'S' ? .5 : .32, '#2E6149'), .35, A_(k).xyz[j], VDW[e] * .92); }}))),
  pearls: mol => mol.heads.forEach((h, i) => swapHead(h.mesh, KEYS[i], k => DATA.reps[k].pearls.map(c => ball(P[k], .9, c, 1.55)))),
  ringpearls: mol => mol.heads.forEach((h, i) => swapHead(h.mesh, KEYS[i], ringPearls)),
  necklace: mol => mol.heads.forEach((h, i) => swapHead(h.mesh, KEYS[i], k => {{ const a = A_(k), hv = new Set(heavy(k));
    return [...heavy(k).map(j => ball(P[k], .9, a.xyz[j], .55)), ...a.bonds.filter(([p, q]) => hv.has(p) && hv.has(q)).map(([p, q]) => stick(P.linker, a.xyz[p], a.xyz[q], .13))]; }})),
  graduated: mol => mol.heads.forEach((h, i) => swapHead(h.mesh, KEYS[i], k => {{ const a = A_(k), o = V(a.xyz[a.attach]), hs = heavy(k), dm = Math.max(...hs.map(j => V(a.xyz[j]).distanceTo(o)));
    return hs.map(j => ball(P[k], .9, a.xyz[j], .42 + 1.0 * V(a.xyz[j]).distanceTo(o) / dm)); }})),
  nacre: mol => mol.heads.forEach((h, i) => swapHead(h.mesh, KEYS[i], k => DATA.reps[k].pearls.map(c => {{ const s = new THREE.Mesh(sphere, nacre(P[k])); s.position.set(...c); s.scale.setScalar(1.55); return s; }}))),
  shell: mol => mol.heads.forEach((h, i) => {{ swapHead(h.mesh, KEYS[i], ringPearls); const k = KEYS[i], g = geom(DATA.reps[k].surface);
    const m = new THREE.Mesh(g, new THREE.MeshBasicMaterial({{ color: tint(P[k], .2), transparent: true, opacity: .16, depthWrite: false }})); m.renderOrder = 3; h.mesh.add(m); }}),
  glass: mol => mol.heads.forEach((h, i) => addTo(h, new THREE.Mesh(geom(DATA.mesh[KEYS[i]].smooth), glassMat(tint(P[KEYS[i]], .15))))),
  wire: mol => mol.heads.forEach((h, i) => {{ const k = KEYS[i], g = geom(DATA.mesh[k].coarse); h.mesh.material.visible = false; h.mesh.children[0].visible = false;
    addTo(h, new THREE.Mesh(g, new THREE.MeshBasicMaterial({{ color: P[k], transparent: true, opacity: .14, depthWrite: false }})), 2);
    addTo(h, new THREE.LineSegments(new THREE.WireframeGeometry(g), new THREE.LineBasicMaterial({{ color: tint(P[k], .25), transparent: true, opacity: .85 }}))); }}),
  glassatoms: mol => mol.heads.forEach((h, i) => {{ const k = KEYS[i], a = A_(k); h.mesh.material.visible = false; h.mesh.children[0].visible = false;
    heavy(k).forEach(j => {{ const s = new THREE.Mesh(sphere, glassMat(tint(P[k], .1), .14)); s.position.set(...a.xyz[j]); s.scale.setScalar(VDW[a.el[j]] * .92); addTo(h, s); }}); }}),
''' + src[b1:]
# a little closer than round 1, so the atoms read
src = once(src, 'cam.position.set(0, 0, 88);', 'cam.position.set(0, 0, 70);')
# no flat icon in this round
src = once(src, "  if (opt === 'icon') {{ mol.group.visible = false; v.svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg'); v.el.appendChild(v.svg); }}\n", "")
src = src.replace("open(D + 'index.html', 'w', encoding='utf8').write(html)\nprint('reps/index.html', os.path.getsize(D + 'index.html') // 1024, 'KB')",
                  "os.makedirs(D + '../reps2', exist_ok=True)\nopen(D + '../reps2/index.html', 'w', encoding='utf8').write(html)\nprint('reps2/index.html', os.path.getsize(D + '../reps2/index.html') // 1024, 'KB')")
exec(compile(src, 'build_reps.py (round 2)', 'exec'))
