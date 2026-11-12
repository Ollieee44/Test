// ---------- v4/v5: no SELFTAC clips the membrane once it is inside the cell ----------
// The cell's side of the membrane is the circle of radius 300 round (X.mem + 300, 0) (its head groups reach 2 in). Each
// frame, every SELFTAC in the cell is measured (its outline's box) and, if any of it reaches within 6 of that surface,
// moved toward the cell's centre until it clears. The push only ever grows, so once a molecule has settled clear it
// stays put (no jitter as it wobbles). The molecule we follow is checked too once it is through (from pn .69).
{
  const CC = V3(X.mem + 300, 0, 0), LIM = 300 - 2.1 - 6, bb = new THREE.Box3();
  // g: what moves; m: what is measured (the molecule only; the hero's group also holds the proteins). The reach is
  // measured on the molecule's own surface points (every few), not its box, which would overstate a molecule at an angle
  const tmp = V3(), far0 = m => { let far = 0; m.traverse(o => { if (!o.isMesh || o.isInstancedMesh || !o.visible || !o.material.visible) return;
      const pos = o.geometry.attributes.position; if (!pos) return;
      for (let i = 0; i < pos.count; i += 3) { tmp.fromBufferAttribute(pos, i).applyMatrix4(o.matrixWorld); far = Math.max(far, Math.hypot(tmp.x - CC.x, tmp.y - CC.y)); } });
    return far; };
  const clear = (g, push, m = g) => {
    g.position.x += push.x; g.position.y += push.y; g.updateMatrixWorld(true);
    const over = far0(m) - LIM; if (over <= 0) return;
    bb.setFromObject(m); const c = bb.getCenter(V3()), d = V3(CC.x - c.x, CC.y - c.y, 0).normalize().multiplyScalar(over);
    push.add(d); g.position.x += d.x; g.position.y += d.y; g.updateMatrixWorld(true);
  };
  const pushes = new Map(), heroPush = V3();
  const frameM = frame;
  frame = function (p0) {
    frameM(p0); const pn = clamp(p0, 0, 1);
    POP.forEach(c => { if (c.at !== 'cell' || !c.g.visible) return; if (!pushes.has(c)) pushes.set(c, V3()); clear(c.g, pushes.get(c)); });
    if (pn > .69 && cg.visible) clear(cg, heroPush, mol.group); else heroPush.set(0, 0, 0);
  };
}
