// ---------- v5: the "Monomers pass through more easily" label sits between the two crossing monomers ----------
// Each frame, after the page has placed its labels: centred on the point midway between the two halves, then moved
// right only as far as it must to touch neither the membrane (its cell-side face) nor either half.
{
  const el = document.querySelector('.jl.loc[data-pl="pass"]'), CC = X.mem + 300, GAP = 8, bb = new THREE.Box3();
  const screenBox = o => { bb.setFromObject(o); let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9;
    for (const x of [bb.min.x, bb.max.x]) for (const y of [bb.min.y, bb.max.y]) { const [sx, sy] = toScreen(x, y); x0 = Math.min(x0, sx); x1 = Math.max(x1, sx); y0 = Math.min(y0, sy); y1 = Math.max(y1, sy); }
    return [x0, x1, y0, y1]; };
  const frameL = frame;
  frame = function (p0) {
    frameL(p0);
    if (!el || +el.style.opacity <= .01 || !cg.visible) return;
    mol.group.updateMatrixWorld(true);
    const H = mol.group.children.slice(0, 2).map(screenBox), w = el.offsetWidth, h = el.offsetHeight;
    const cx = (H[0][0] + H[0][1] + H[1][0] + H[1][1]) / 4, cy = (H[0][2] + H[0][3] + H[1][2] + H[1][3]) / 4;
    let x = cx - w / 2; const y = cy - h / 2;
    // the membrane's cell-side face at the label's height (in world units, then on screen)
    const mid = mol.group.children.slice(0, 2).map(c => { bb.setFromObject(c); return bb.getCenter(V3()); }), ym = (mid[0].y + mid[1].y) / 2;
    const [mx] = toScreen(CC - Math.sqrt(Math.max(0, 300 * 300 - ym * ym)) + 4, ym);
    x = Math.max(x, mx + GAP);
    for (let it = 0; it < 3; it++) H.forEach(b => { if (x < b[1] + GAP && x + w > b[0] - GAP && y < b[3] + GAP && y + h > b[2] - GAP) x = b[1] + GAP; });
    el.style.transform = `translate(${x.toFixed(1)}px, ${y.toFixed(1)}px)`;
  };
}
