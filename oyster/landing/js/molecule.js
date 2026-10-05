// ---------- the degrader as chemical matter: a cartoon ball-and-stick model of MZ1 from the crystal ----------
// Every heavy atom and bond is drawn, so the linker is bonded straight into both heads and can never drift
// off them. Each half moves as a rigid body (offset plus turn about its own centre). Linker atoms blend
// between the two halves: when the molecule is joined they spread evenly along the chain, so the linker
// stretches across any gap; when it is split, each atom rides with its own half.
// Styles: 'ball' (ball and stick), 'space' (space-filling), 'stick' (licorice).
function makeMolecule(THREE, M, Q) {
  const n = M.el.length, base = M.xyz.map(a => new THREE.Vector3(...a).applyQuaternion(Q));
  const centre = name => { const c = new THREE.Vector3(); let k = 0; M.part.forEach((p, i) => { if (p === name) { c.add(base[i]); k++; } }); return c.divideScalar(k); };
  const cW = centre('warhead'), cE = centre('e3lig');
  const nb = Array.from({ length: n }, () => []); M.bonds.forEach(([a, b]) => { nb[a].push(b); nb[b].push(a); });
  const isBrk = ([a, b]) => (a === M.brk[0] && b === M.brk[1]) || (a === M.brk[1] && b === M.brk[0]);
  const STYLES = {
    ball: { r: { C: .5, N: .52, O: .52, S: .64, Cl: .66 }, bond: .17, multi: true },
    space: { r: { C: 1.5, N: 1.42, O: 1.38, S: 1.7, Cl: 1.66 }, bond: 0, multi: false },
    stick: { r: { C: .3, N: .3, O: .3, S: .3, Cl: .3 }, bond: .3, multi: false },
  };
  let style = STYLES.ball;

  // cartoon shading: two tones, a small glossy highlight like a model-kit ball, and a soft ink rim
  const mat = new THREE.ShaderMaterial({
    uniforms: { ink: { value: new THREE.Color() } },
    vertexShader: `varying vec3 vN; varying vec3 vV; varying vec3 vC;
      void main() { vec4 w = modelMatrix * instanceMatrix * vec4(position, 1.0);
        vN = normalize(mat3(modelMatrix) * mat3(instanceMatrix) * normal); vV = normalize(cameraPosition - w.xyz); vC = instanceColor;
        gl_Position = projectionMatrix * viewMatrix * w; }`,
    fragmentShader: `uniform vec3 ink; varying vec3 vN; varying vec3 vV; varying vec3 vC;
      void main() {
        vec3 n = normalize(vN), v = normalize(vV), l = normalize(vec3(-.35, .75, .55));
        float shade = mix(.74, 1.0, smoothstep(-.05, .1, dot(n, l)));
        float spec = smoothstep(.955, .975, dot(n, normalize(l + v)));
        float rim = pow(1.0 - max(dot(n, v), 0.0), 2.5);
        vec3 c = vC * shade; c = mix(c, ink, rim * .3); c = mix(c, vec3(1.0), spec * .8);
        gl_FragColor = vec4(c, 1.0);
        #include <colorspace_fragment>
      }`,
  });
  const lineMat = new THREE.ShaderMaterial({
    uniforms: { color: { value: new THREE.Color() }, thick: { value: .1 } }, side: THREE.BackSide,
    vertexShader: `uniform float thick; void main() {
        vec3 p = (instanceMatrix * vec4(position, 1.0)).xyz + normalize(mat3(instanceMatrix) * normal) * thick;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.0); }`,
    fragmentShader: `uniform vec3 color; void main() { gl_FragColor = vec4(color, 1.0);
      #include <colorspace_fragment>
    }`,
  });
  const group = new THREE.Group();
  const atoms = new THREE.InstancedMesh(new THREE.SphereGeometry(1, 28, 18), mat, n);
  // every bond is up to four half-sticks: main stick (two halves, one per atom colour) and, for a double
  // bond, a second shorter stick
  const nB = M.bonds.length * 4;
  const sticks = new THREE.InstancedMesh(new THREE.CylinderGeometry(1, 1, 1, 14, 1, true), mat, nB);
  const lines = [atoms, sticks].map(m => { const o = new THREE.InstancedMesh(m.geometry, lineMat, m.count); o.instanceMatrix = m.instanceMatrix; o.renderOrder = -1; o.frustumCulled = false; group.add(o); return o; });
  atoms.frustumCulled = sticks.frustumCulled = false;
  for (const m of [atoms, sticks]) m.instanceColor = new THREE.InstancedBufferAttribute(new Float32Array(m.count * 3), 3);
  group.add(atoms, sticks);

  const pos = base.map(p => p.clone()), up = new THREE.Vector3(0, 1, 0), m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), s3 = new THREE.Vector3(), zero = new THREE.Matrix4().makeScale(0, 0, 0);
  const pw = new THREE.Vector3(), pe = new THREE.Vector3(), d = new THREE.Vector3(), mid = new THREE.Vector3(), off = new THREE.Vector3(), tmp = new THREE.Vector3();
  function stick(k, a, b, r) {               // a half-stick from point a to point b
    if (r <= 0) { sticks.setMatrixAt(k, zero); return; }
    d.subVectors(b, a); const len = d.length(); q.setFromUnitVectors(up, d.divideScalar(len || 1));
    m4.compose(mid.addVectors(a, b).multiplyScalar(.5), q, s3.set(r, len, r)); sticks.setMatrixAt(k, m4);
  }
  // oW, oE: offsets of the two halves; rW, rE: their turns (quaternions); joined: 1 joined, 0 split
  function update(oW, oE, rW, rE, joined) {
    for (let i = 0; i < n; i++) {
      pw.subVectors(base[i], cW).applyQuaternion(rW).add(cW).add(oW);
      pe.subVectors(base[i], cE).applyQuaternion(rE).add(cE).add(oE);
      pos[i].lerpVectors(pw, pe, M.side[i] + (M.t[i] - M.side[i]) * joined);
      const r = style.r[M.el[i]] || .5; atoms.setMatrixAt(i, m4.compose(pos[i], q.identity(), s3.set(r, r, r)));
    }
    M.bonds.forEach((bd, j) => {
      const [a, b, order, ring] = bd, A = pos[a], B = pos[b], k = j * 4;
      const r = style.bond * (isBrk(bd) ? 1.25 * clamp01((joined - .5) / .5) : 1);
      const C = tmp.addVectors(A, B).multiplyScalar(.5).clone();
      if (order === 2 && style.multi) {
        d.subVectors(B, A).normalize();
        if (ring >= 0) {                     // ring double bond: an inner, shorter stick toward the ring centre
          off.set(0, 0, 0); M.rings[ring].forEach(i => off.add(pos[i])); off.divideScalar(M.rings[ring].length).sub(C);
          off.addScaledVector(d, -off.dot(d)).normalize().multiplyScalar(.42);
          stick(k, A, C, r); stick(k + 1, C, B, r);
          const a2 = A.clone().lerp(B, .2).add(off), b2 = A.clone().lerp(B, .8).add(off), c2 = a2.clone().add(b2).multiplyScalar(.5);
          stick(k + 2, a2, c2, r * .72); stick(k + 3, c2, b2, r * .72);
        } else {                             // open-chain double bond (C=O): two parallel sticks
          const o = nb[a].find(x => x !== b) ?? nb[b].find(x => x !== a);
          off.subVectors(pos[o], A); off.addScaledVector(d, -off.dot(d)).normalize().multiplyScalar(.2);
          const a1 = A.clone().sub(off), b1 = B.clone().sub(off), c1 = a1.clone().add(b1).multiplyScalar(.5);
          const a2 = A.clone().add(off), b2 = B.clone().add(off), c2 = a2.clone().add(b2).multiplyScalar(.5);
          stick(k, a1, c1, r * .7); stick(k + 1, c1, b1, r * .7); stick(k + 2, a2, c2, r * .7); stick(k + 3, c2, b2, r * .7);
        }
      } else { stick(k, A, C, r); stick(k + 1, C, B, r); sticks.setMatrixAt(k + 2, zero); sticks.setMatrixAt(k + 3, zero); }
    });
    atoms.instanceMatrix.needsUpdate = sticks.instanceMatrix.needsUpdate = true;
    return pos[M.brk[0]].clone().add(pos[M.brk[1]]).multiplyScalar(.5);
  }
  const clamp01 = x => Math.max(0, Math.min(1, x));
  // colours: carbons take their half's colour (the linker's are pearls), heteroatoms a muted element colour
  function setColors(P) {
    const c = new THREE.Color(), key = i => M.el[i] !== 'C' ? 'el' + M.el[i] : M.part[i] === 'linker' ? 'linkC' : M.part[i];
    for (let i = 0; i < n; i++) atoms.setColorAt(i, c.set(P[key(i)]));
    M.bonds.forEach((bd, j) => { const [a, b] = bd, brk = isBrk(bd);
      [a, b, a, b].forEach((x, h) => sticks.setColorAt(j * 4 + h, c.set(brk ? P.brk : P[key(x)]))); });
    atoms.instanceColor.needsUpdate = sticks.instanceColor.needsUpdate = true;
    mat.uniforms.ink.value.set(P.ink); lineMat.uniforms.color.value.set(P.ink);
  }
  function setStyle(name) { style = STYLES[name]; lineMat.uniforms.thick.value = name === 'space' ? .16 : .09; }
  return { group, update, setColors, setStyle, centre: cW.clone().add(cE).multiplyScalar(.5) };
}
