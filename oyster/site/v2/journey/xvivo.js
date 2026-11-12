// ---------- v4: the proteins restyled after XVIVO's targeted-protein-degradation animation ----------
// Every protein becomes the bumpy envelope of its atoms (bumpy.json, from tools/bumpy_meshes.py) with a soft, glowing
// finish: wrapped light, a deeper, more saturated tone in shadow, crevices darkened by a baked occlusion term, a
// subsurface glow at the edges and through thin parts, and no ink outline. The proteasome stand-in, which has no atoms,
// gets the same finish on its smooth surface. Colours stay the palette's; the shader reads the same
// uniforms as the contour material it replaces (col, alpha, glow), so the page's colour and fade code still drives it.
{
  const BD = JSON.parse(document.getElementById('bumpy').textContent);
  const bgeom = p => { const g = geom(p), a = Uint8Array.from(atob(p.ao), c => c.charCodeAt(0)), f = new Float32Array(a.length);
    for (let i = 0; i < a.length; i++) f[i] = a[i] / 255; g.setAttribute('ao', new THREE.BufferAttribute(f, 1)); return g; };
  const XVS = `attribute float ao; varying vec3 vN; varying vec3 vV; varying vec3 vW; varying float vA;
    void main() { vec4 w = modelMatrix * vec4(position, 1.0); vW = w.xyz; vN = normalize(mat3(modelMatrix) * normal); vV = normalize(cameraPosition - w.xyz); vA = ao;
      gl_Position = projectionMatrix * viewMatrix * w; }`;
  const XFS = `uniform vec3 col; uniform float alpha; uniform float glow; uniform float hasAo; uniform float bump; varying vec3 vN; varying vec3 vV; varying vec3 vW; varying float vA;
    vec3 h3(vec3 p) { p = vec3(dot(p, vec3(127.1, 311.7, 74.7)), dot(p, vec3(269.5, 183.3, 246.1)), dot(p, vec3(113.5, 271.9, 124.6))); return fract(sin(p) * 43758.5453); }
    // atom-sized bumps for surfaces without atoms: the offset to the nearest cell feature (a cellular field) tilts the normal
    vec3 cells(vec3 p) { vec3 i = floor(p), f = fract(p), best = vec3(0.0); float d = 9.0;
      for (int x = -1; x <= 1; x++) for (int y = -1; y <= 1; y++) for (int z = -1; z <= 1; z++) { vec3 o = vec3(float(x), float(y), float(z)), r = o + h3(i + o) - f; float e = dot(r, r); if (e < d) { d = e; best = r; } }
      return -best * (1.0 - smoothstep(.0, .7, sqrt(d))); }
    void main() {
      vec3 n = normalize(vN), v = normalize(vV), l = normalize(vec3(-.35, .72, .6));
      if (bump > 0.0) n = normalize(n + cells(vW / bump) * 1.6);
      float ndl = dot(n, l), wrap = clamp((ndl + .6) / 1.6, 0.0, 1.0), ndv = max(dot(n, v), 0.0), fres = pow(1.0 - ndv, 2.4);
      float ao = mix(1.0, smoothstep(.0, .85, vA), hasAo);
      vec3 shadow = col * col * vec3(.78, .7, .82);                       // shadows deeper and more saturated, not grey
      vec3 c = mix(shadow, col * 1.06, wrap * wrap);
      c *= mix(.38, 1.0, ao);                                             // crevices
      c += col * fres * .5 + vec3(.06) * fres;                            // subsurface glow round the edges
      c += col * max(-ndl, 0.0) * (1.0 - ndv) * .22;                      // light through the thin parts
      c += vec3(pow(max(dot(n, normalize(l + v)), 0.0), 28.0) * .1);      // a soft sheen
      c = mix(c, vec3(1.0), glow);
      gl_FragColor = vec4(c, alpha);
      #include <colorspace_fragment>
    }`;
  const restyle = (mesh, geo, opts = {}) => {
    const old = mesh.material, u = old.uniforms;
    u.hasAo = { value: geo ? 1 : 0 }; u.bump = { value: opts.bump || 0 };
    const m = new THREE.ShaderMaterial({ vertexShader: XVS, fragmentShader: XFS, uniforms: u, transparent: old.transparent, depthWrite: old.depthWrite });
    m.userData = old.userData; const i = mats.indexOf(old); if (i >= 0) mats[i] = m; mesh.material = m;
    if (geo) mesh.geometry = geo;
    // no ink outline in this style
    mesh.children.forEach(o => { if (outlines.includes(o)) o.material.visible = false; });
  };
  const geos = {}; for (const k of ['brd4', 'vhl', 'elob', 'eloc', 'ub']) geos[k] = bgeom(BD.parts[k]);
  for (const k of ['brd4', 'brd4b', 'vhl', 'elob', 'eloc']) restyle(P[k].children[0], geos[k === 'brd4b' ? 'brd4' : k]);
  ubs.forEach(m => restyle(m, geos.ub)); restyle(e2, geos.ub);
  prot.children.forEach(m => m.isMesh && restyle(m, null));   // the same finish, smooth (no added bumps)

  // depth: out-of-focus molecules drifting far behind the cell, as in the film's cytoplasm (soft blots in the palette's
  // colours, low and slow, only from the membrane on, so they never sit over the gut or the bloodstream)
  const blot = (() => { const c = document.createElement('canvas'); c.width = c.height = 128; const g = c.getContext('2d');
    const gr = g.createRadialGradient(64, 64, 0, 64, 64, 62); gr.addColorStop(0, 'rgba(255,255,255,.7)'); gr.addColorStop(.45, 'rgba(255,255,255,.38)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr; g.fillRect(0, 0, 128, 128); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; })();
  const BOKEH = ['#F0A6CA', '#CEE5F3', '#67B791', '#8AB0AB', '#A2839E', '#90A9B7'], rnd = (a => () => (a = (a * 16807) % 2147483647) / 2147483647)(7);
  const bokeh = Array.from({ length: 24 }, (_, i) => { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: blot, color: BOKEH[i % BOKEH.length], transparent: true, depthWrite: false, opacity: .1 + .12 * rnd() }));
    const z = -260 - 420 * rnd(); s.position.set(330 + 520 * rnd(), -160 + 320 * rnd(), z); s.scale.setScalar(18 + 70 * rnd()); s.renderOrder = -20;
    s.userData = { y0: s.position.y, ph: rnd() * 6.28, a0: s.material.opacity }; scene.add(s); return s; });
  const frameX = frame;
  frame = function (p0) { frameX(p0); const pn = clamp(p0, 0, 1), on = clamp((pn - .6) / .06, 0, 1), t = performance.now() / 1000;
    bokeh.forEach(s => { s.position.y = s.userData.y0 + 6 * Math.sin(t * .15 + s.userData.ph); s.material.opacity = s.userData.a0 * on; s.visible = on > .01; }); };
}
