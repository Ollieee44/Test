// In-page exporter for the PowerPoint version of the journey (injected into the otx page by export_deck.js).
// window.__X is the journey's scene, exposed by the harness. Two jobs:
//   refRender(name): a still of one 3D element alone (transparent), framed straight on, with where its anchor and
//                    its frame's unit x land in the picture, so the deck can place and scale it on any slide
//   keyframe(p):     the journey held at p: every element's anchor, unit x and opacity on screen, the flat layer's
//                    world transform, and the labels, copy, rail and end card as laid out in the page
(() => {
  const X = window.__X, THREE = X.THREE, V = (...a) => new THREE.Vector3(...a);
  const ch = X.mol.group.children, heads = [ch[0], ch[1]];
  const centre = m => { m.geometry.computeBoundingSphere(); return m.localToWorld(m.geometry.boundingSphere.center.clone()); };
  // each element: the objects it draws, the point it is placed by, and the object whose unit x gives its scale and turn
  const EL = {
    halfW: { obj: X.mol.group, anchor: () => centre(heads[0]), frame: () => X.cg, show: () => X.cg.visible && X.j < .5, only: 0 },
    halfE: { obj: X.mol.group, anchor: () => centre(heads[1]), frame: () => X.cg, show: () => X.cg.visible && X.j < .5, only: 1 },
    dimerG: { obj: X.mol.group, anchor: () => X.cg.getWorldPosition(V()), frame: () => X.cg, show: () => X.cg.visible && X.j >= .5 && X.p < .5 },
    dimerC: { obj: X.mol.group, anchor: () => X.cg.getWorldPosition(V()), frame: () => X.cg, show: () => X.cg.visible && X.j >= .5 && X.p >= .5 },
    brd4: { obj: X.P.brd4, anchor: () => centre(X.P.brd4.children[0]), frame: () => X.P.brd4, show: () => X.P.brd4.visible },
    vhl: { obj: X.P.vhl, anchor: () => centre(X.P.vhl.children[0]), frame: () => X.P.vhl, show: () => X.P.vhl.visible },
    elob: { obj: X.P.elob, anchor: () => centre(X.P.elob.children[0]), frame: () => X.P.elob, show: () => X.P.elob.visible },
    eloc: { obj: X.P.eloc, anchor: () => centre(X.P.eloc.children[0]), frame: () => X.P.eloc, show: () => X.P.eloc.visible },
    prot: { obj: X.prot, anchor: () => X.prot.getWorldPosition(V()), frame: () => X.prot, show: () => X.prot.visible, flat: true },
  };
  X.ubs.forEach((u, i) => { EL['ub' + i] = { obj: u, anchor: () => u.getWorldPosition(V()), frame: () => u, show: () => u.visible, flat: true, img: 'ub0' }; });
  X.frags.forEach((f, i) => { EL['frag' + i] = { obj: f.m, anchor: () => f.m.getWorldPosition(V()), frame: () => f.m, show: () => f.m.visible, flat: true, img: 'frag' + (i % 3) }; });

  const W = () => X.stage.clientWidth, H = () => X.stage.clientHeight;
  function screen(v, cam, w, h) { const q = v.clone().project(cam); return [(q.x + 1) / 2 * w, (1 - q.y) / 2 * h]; }
  // the frame object's unit x in world space (for 'flat' objects, the scene's x scaled by the object, so a spin about
  // another axis does not read as a change of size)
  function unitX(e) {
    const f = e.frame(); f.updateMatrixWorld(true);
    if (e.flat) { const s = f.getWorldScale(V()); return V(s.x, 0, 0); }
    return f.localToWorld(V(1, 0, 0)).sub(f.localToWorld(V(0, 0, 0)));
  }
  function measure(e, cam, w, h) {
    const a = e.anchor(), A = screen(a, cam, w, h), B = screen(a.clone().add(unitX(e)), cam, w, h);
    return { A, v: [B[0] - A[0], B[1] - A[1]] };
  }
  // ---------- one element alone, straight on ----------
  function isolate(e) {
    const keep = new Set(), anc = new Set();
    e.obj.traverse(o => keep.add(o));
    for (let o = e.obj; o; o = o.parent) anc.add(o);
    const saved = [];
    X.scene.traverse(o => { if (!keep.has(o) && !anc.has(o)) { saved.push([o, o.visible]); o.visible = false; } else if (anc.has(o)) { saved.push([o, o.visible]); o.visible = true; } });
    e.obj.visible = true;
    if (e.only !== undefined) {   // one half: hide the other half's parts and its pearls
      const other = 1 - e.only;
      [heads[other], ch[7 + other], ch[9], ch[6]].forEach(o => { saved.push([o, o.visible]); o.visible = false; });
      const m4 = new THREE.Matrix4(), zero = new THREE.Matrix4().makeScale(0, 0, 0);
      const pearlIdx = other === 0 ? [0, 1] : [2, 3];
      pearlIdx.forEach(i => { ch[2].getMatrixAt(i, m4); saved.push(['pm', i, m4.clone()]); ch[2].setMatrixAt(i, zero); });
      ch[4].getMatrixAt(other, m4); saved.push(['cm', other, m4.clone()]); ch[4].setMatrixAt(other, zero);
      ch[2].instanceMatrix.needsUpdate = ch[4].instanceMatrix.needsUpdate = true;
    }
    return () => saved.reverse().forEach(s => { if (s[0] === 'pm') { ch[2].setMatrixAt(s[1], s[2]); ch[2].instanceMatrix.needsUpdate = true; }
      else if (s[0] === 'cm') { ch[4].setMatrixAt(s[1], s[2]); ch[4].instanceMatrix.needsUpdate = true; } else s[0].visible = s[1]; });
  }
  window.refRender = (name, p, N = 1600) => {
    const e = EL[name]; X.frame(p);
    const restore = isolate(e);
    const box = new THREE.Box3().setFromObject(e.obj), sph = box.getBoundingSphere(new THREE.Sphere());
    const D = 500, cam = new THREE.PerspectiveCamera(2 * Math.atan(sph.radius * 1.15 / D) * 180 / Math.PI, 1, 1, 4000);
    cam.position.set(sph.center.x, sph.center.y, sph.center.z + D); cam.lookAt(sph.center); cam.updateMatrixWorld(); cam.updateProjectionMatrix();
    const r = X.renderer, oldPR = r.getPixelRatio();
    r.setPixelRatio(1); r.setSize(N, N, false); r.setClearColor(0x000000, 0); r.render(X.scene, cam);
    const url = r.domElement.toDataURL('image/png'), m = measure(e, cam, N, N);
    restore(); r.setPixelRatio(oldPR); X.resize();
    return { url, size: N, ...m };
  };
  // ---------- the journey held at p ----------
  const opa = el => { let o = 1; for (let n = el; n && n !== document.documentElement; n = n.parentElement) { const v = parseFloat(getComputedStyle(n).opacity); if (!isNaN(v)) o *= v; } return o; };
  window.keyframe = p => {
    X.frame(p); X.renderer.render(X.scene, X.camera);
    const els = {};
    for (const [name, e] of Object.entries(EL)) {
      if (!e.show()) continue;
      const m = measure(e, X.camera, W(), H());
      els[name] = { ...m, img: e.img || name };
    }
    // the flash ring
    const f = X.flash, flash = f.visible ? { A: screen(f.position, X.camera, W(), H()), r: Math.hypot(...(() => { const a = screen(f.position, X.camera, W(), H()), b = screen(f.position.clone().add(V(2.1 * f.scale.x, 0, 0)), X.camera, W(), H()); return [b[0] - a[0], b[1] - a[1]]; })()), o: f.material.opacity } : null;
    // the flat layer: the world-to-screen matrix, each piece's opacity, and the pill's own transform
    const mt = document.getElementById('jworld').getAttribute('transform').match(/-?[\d.]+/g).map(Number);
    const flatO = {}; ['jperson', 'jroute', 'jgut', 'jtract', 'jgutring', 'jbeam', 'jmem', 'jpill'].forEach(id => flatO[id] = opa(document.getElementById(id)));
    const pt = (document.getElementById('jpill').getAttribute('transform') || '').match(/-?[\d.]+/g).map(Number);
    // labels, copy, rail, end card, as laid out
    const rect = el => { const r = el.getBoundingClientRect(), s = X.stage.getBoundingClientRect(); return [r.left - s.left, r.top - s.top, r.width, r.height]; };
    const labels = [...document.querySelectorAll('.jl')].map(el => ({ id: el.id, text: el.textContent.trim(), cls: el.className, o: opa(el), r: rect(el) })).filter(l => l.o > .3);
    const beat = [...document.querySelectorAll('.beat')].map((b, i) => ({ i, o: opa(b) })).sort((a, b) => b.o - a.o)[0];
    const bEl = document.querySelectorAll('.beat')[beat.i], kEl = bEl.querySelector('.k'), hEl = bEl.querySelector('h1,h2'), pEl = bEl.querySelector('p');
    const copy = beat.o > .3 ? { i: beat.i, num: kEl.querySelector('b') ? kEl.querySelector('b').textContent : '', kicker: kEl.textContent.replace(kEl.querySelector('b') ? kEl.querySelector('b').textContent : '', '').trim(),
      kR: rect(kEl), head: hEl.textContent, hR: rect(hEl), hSize: parseFloat(getComputedStyle(hEl).fontSize), body: pEl.textContent, pR: rect(pEl), pSize: parseFloat(getComputedStyle(pEl).fontSize) } : null;
    const rail = [...document.querySelectorAll('.rail > div')].map(d => ({ label: d.querySelector('span').textContent, on: d.classList.contains('on'), r: rect(d), sR: rect(d.querySelector('span')) }));
    const end = document.getElementById('end'), endO = opa(end);
    const endInfo = endO > .5 ? { logo: rect(end.querySelector('.otx-logo')), tag: rect(end.querySelector('.tag')), tagText: end.querySelector('.tag').textContent, tagSize: parseFloat(getComputedStyle(end.querySelector('.tag')).fontSize),
      ecr: rect(end.querySelector('.ecr')), ecrText: end.querySelector('.ecr').textContent, btn: rect(end.querySelector('a')) } : null;
    const sky = [getComputedStyle(X.stage).getPropertyValue('--sky-a').trim(), getComputedStyle(X.stage).getPropertyValue('--sky-b').trim()];
    const stars = getComputedStyle(document.getElementById('jstars')).backgroundPosition.match(/-?[\d.]+/g).map(Number);
    const sceneO = opa(X.renderer.domElement);
    return { p, W: W(), H: H(), els, flash, world: { k: mt[0], tx: mt[4], ty: mt[5] }, flatO, pill: pt, labels, copy, rail, end: endInfo, sky, stars, sceneO };
  };
  // ---------- the flat layer's pieces as stand-alone pictures (world units, y up) ----------
  // kd: the piece's typical on-slide scale (slide px per world unit), so its outlines come out at the page's weights
  window.flatPiece = (id, pxPerUnit, kd) => {
    const world = document.getElementById('jworld'), el = document.getElementById(id);
    const tf = el.getAttribute('transform'); if (id === 'jpill') el.removeAttribute('transform');
    const rel = world.getCTM().inverse().multiply(el.getCTM()), bb = el.getBBox();
    const cs = [[bb.x, bb.y], [bb.x + bb.width, bb.y], [bb.x, bb.y + bb.height], [bb.x + bb.width, bb.y + bb.height]].map(([x, y]) => [rel.a * x + rel.c * y + rel.e, rel.b * x + rel.d * y + rel.f]);
    const x0 = Math.min(...cs.map(c => c[0])) - 1, x1 = Math.max(...cs.map(c => c[0])) + 1, y0 = Math.min(...cs.map(c => c[1])) - 1, y1 = Math.max(...cs.map(c => c[1])) + 1;
    const clone = el.cloneNode(true); clone.style.opacity = '1';   // keep its own style (fills, strokes), only the fade goes clone.querySelectorAll('[style*="opacity:0"]').forEach(n => { n.style.opacity = 1; });
    if (id === 'jgut') { clone.querySelector('#jgutring').remove(); clone.querySelector('#jtract').remove(); }
    if (id === 'jperson') clone.querySelector('#jroute').remove();
    if (id === 'jroute' || id === 'jtract' || id === 'jgutring') clone.style.opacity = 1;
    clone.removeAttribute('id'); clone.querySelectorAll('[id]').forEach(n => n.removeAttribute('id'));
    if (tf) el.setAttribute('transform', tf);
    let html = clone.outerHTML.replace(/stroke-width:\s*([\d.]+)/g, (m, v) => `stroke-width:${(v / kd).toFixed(3)}`).replace(/stroke-width="([\d.]+)"/g, (m, v) => `stroke-width="${(v / kd).toFixed(3)}"`)
      .replace(/stroke-dasharray:\s*([\d.]+) ([\d.]+)/g, (m, a, b) => `stroke-dasharray:${(a / kd).toFixed(3)} ${(b / kd).toFixed(3)}`);
    const defs = document.querySelector('#jsvg defs').outerHTML;
    const w = (x1 - x0) * pxPerUnit, h = (y1 - y0) * pxPerUnit;
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="${x0} ${-y1} ${x1 - x0} ${y1 - y0}" style="display:block;overflow:hidden">${defs}`
      + `<g transform="scale(1 -1)"><g transform="matrix(${rel.a} ${rel.b} ${rel.c} ${rel.d} ${rel.e} ${rel.f})">${html}</g></g></svg>`;
    return { svg, rect: [x0, y0, x1, y1], w, h };
  };
})();
