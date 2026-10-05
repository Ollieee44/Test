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
