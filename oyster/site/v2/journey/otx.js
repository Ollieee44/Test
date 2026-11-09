// ---------- oyster-tx.com theme: proteins as particle clouds on emerald, in the site's pink, pale blue and yellow ----------
// The story and timing are the journey's own; this restyles it. Each protein (and the proteasome) is drawn as a cloud
// of glittering points sampled over its surface, like the hero of oyster-tx.com: the target in pink, the ligase in pale
// blue, Elongin B and C and the proteasome in mint and cyan, all with a few yellow-green flecks. The degrader keeps its
// solid form in the site's icon colours: pink binds the target, pale blue the ligase, and they join in yellow.
const OTX_RAND = (() => { let s = 7; return () => (s = (s * 16807) % 2147483647) / 2147483647; })();
const ptMat = new THREE.ShaderMaterial({
  uniforms: { uPx: { value: 600 } }, transparent: true, depthWrite: false,
  vertexShader: `attribute vec3 pcol; attribute float psize; uniform float uPx; varying vec3 vC;
    void main() { vC = pcol; vec4 mv = modelViewMatrix * vec4(position, 1.0); gl_PointSize = max(1.0, psize * uPx / -mv.z); gl_Position = projectionMatrix * mv; }`,
  fragmentShader: `varying vec3 vC;
    void main() { float d = length(gl_PointCoord - .5); if (d > .5) discard; gl_FragColor = vec4(vC, smoothstep(.5, .32, d));
      #include <colorspace_fragment>
    }`,
});
const FLECK = ['#96FF87', '#F7D16B', '#FFE7A0', '#C9FF8F'], WHITE = new THREE.Color('#FFFFFF'), GLINT = new THREE.Color('#D9FF8C');
function cloud(geo, n, cols, flecks = .07, fuzz = 1.1, size = .78, turn = null) {
  const sampler = new MeshSurfaceSampler(new THREE.Mesh(geo)).setRandomGenerator(OTX_RAND).build();
  const pos = new Float32Array(n * 3), col = new Float32Array(n * 3), sz = new Float32Array(n), p = new THREE.Vector3(), nm = new THREE.Vector3(), c = new THREE.Color();
  for (let i = 0; i < n; i++) {
    sampler.sample(p, nm); p.addScaledVector(nm, (OTX_RAND() - .35) * fuzz); pos.set([p.x, p.y, p.z], i * 3);
    const r = OTX_RAND(); c.set(r < flecks ? FLECK[Math.floor(OTX_RAND() * FLECK.length)] : cols[Math.floor(OTX_RAND() * cols.length)]).lerp(WHITE, OTX_RAND() * .1);
    if (turn) nm.applyQuaternion(turn);   // lit from above, as on the site: upper surfaces take a yellow-green glint
    const up = clamp((nm.y - .2) / .8, 0, 1); if (OTX_RAND() < up * .75) c.lerp(GLINT, .45 + OTX_RAND() * .4);
    col.set([c.r, c.g, c.b], i * 3); sz[i] = size * (.55 + OTX_RAND() * .9);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('pcol', new THREE.BufferAttribute(col, 3)); g.setAttribute('psize', new THREE.BufferAttribute(sz, 1));
  const pts = new THREE.Points(g, ptMat); pts.frustumCulled = false; return pts;
}
// replace a solid part with its cloud, in the same place
function toCloud(mesh, n, cols, opts = {}) {
  const pts = cloud(mesh.geometry, n, cols, opts.flecks, opts.fuzz, opts.size, mesh.quaternion);
  pts.position.copy(mesh.position); pts.quaternion.copy(mesh.quaternion); pts.scale.copy(mesh.scale);
  mesh.parent.add(pts); mesh.visible = false; return pts;
}
const PINK = ['#F59BC8', '#F0A6CA', '#FF8FC3', '#FBC6E0'], BLUE = ['#BFE3FF', '#CEE5F3', '#9FD3F5', '#DCEFFB'], MINT = ['#6CFEED', '#30FCBA', '#B8FFF1', '#4FE8D0'];
toCloud(P.brd4.children[0], 15000, PINK);
toCloud(P.vhl.children[0], 15000, BLUE);
toCloud(P.elob.children[0], 9000, MINT);
toCloud(P.eloc.children[0], 9000, MINT);
prot.children.filter(o => o.isMesh).forEach(m => toCloud(m, 2600, MINT, { fuzz: .8 }));
frags.forEach(f => { f.pts = cloud(f.m.geometry, 320, PINK, .07, .25, .55); scene.add(f.pts); });

// the speckled ground drifts a little as the camera pans, and the points keep their size in world units
const stars = document.getElementById('jstars');
const frameBase = frame;
frame = function (p) {
  frameBase(p);
  frags.forEach(f => { f.pts.position.copy(f.m.position); f.pts.rotation.copy(f.m.rotation); f.pts.scale.copy(f.m.scale); f.pts.visible = f.m.visible; f.m.visible = false; });   // the cloud stands in for the solid piece
  const fov = THREE.MathUtils.degToRad(camera.fov);
  ptMat.uniforms.uPx.value = renderer ? renderer.domElement.height / (2 * Math.tan(fov / 2)) : 600;
  const k = stage.clientHeight / (2 * camera.position.z * Math.tan(fov / 2));
  stars.style.backgroundPosition = `${(-camera.position.x * k * .22).toFixed(1)}px ${(camera.position.y * k * .22).toFixed(1)}px`;
};
