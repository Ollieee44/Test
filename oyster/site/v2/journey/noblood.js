// ---------- v4/v5: no SELFTACs overlap in the bloodstream ----------
// While the bloodstream beat plays, each background dimer or monomer pair in the blood is measured against the pair we
// follow and against the others (on their own surface points, in the plane of the screen) and, if any part comes within
// MARG of another, moved apart along the line between their centres. It stays inside the vessel (its inner faces at
// y = +/-43); against a wall it moves along the vessel instead. Pushes only grow, so once settled nothing jitters.
{
  const IN = 43, MARG = 2.5, tmp = V3(), bbA = new THREE.Box3();
  const sample = (m, out) => { out.length = 0; m.updateMatrixWorld(true);
    m.traverse(o => { if (!o.isMesh || o.isInstancedMesh || !o.visible || !o.material.visible) return; const pos = o.geometry.attributes.position; if (!pos) return;
      const step = Math.max(1, Math.floor(pos.count / 160));
      for (let i = 0; i < pos.count; i += step) { tmp.fromBufferAttribute(pos, i).applyMatrix4(o.matrixWorld); out.push(tmp.x, tmp.y); } });
    return out; };
  const box = a => { let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9; for (let i = 0; i < a.length; i += 2) { x0 = Math.min(x0, a[i]); x1 = Math.max(x1, a[i]); y0 = Math.min(y0, a[i + 1]); y1 = Math.max(y1, a[i + 1]); } return [x0, x1, y0, y1]; };
  const gap = (a, ba, b, bb) => {   // the closest approach of two point sets (skipped when their boxes are clearly apart)
    if (ba[0] - bb[1] > MARG || bb[0] - ba[1] > MARG || ba[2] - bb[3] > MARG || bb[2] - ba[3] > MARG) return 1e9;
    let d = 1e18; for (let i = 0; i < a.length; i += 2) for (let j = 0; j < b.length; j += 2) { const dx = a[i] - b[j], dy = a[i + 1] - b[j + 1], e = dx * dx + dy * dy; if (e < d) d = e; }
    return Math.sqrt(d); };
  const BLOOD = POP.filter(c => c.at === 'blood'), push = new Map(BLOOD.map(c => [c, V3()])), pts = new Map(), heroPts = [];
  const frameB = frame;
  frame = function (p0) {
    frameB(p0); const pn = clamp(p0, 0, 1);
    const live = BLOOD.filter(c => c.g.visible); if (!live.length) return;
    const obst = [];
    if (cg.visible) { sample(mol.group, heroPts); obst.push({ a: heroPts, b: box(heroPts) }); }
    live.forEach(c => { const p = push.get(c); c.g.position.x += p.x; c.g.position.y += p.y; });
    live.forEach(c => { const a = pts.get(c) || []; pts.set(c, sample(c.g, a)); });
    live.forEach(c => {
      const a = pts.get(c), p = push.get(c);
      const others = obst.concat(live.filter(o => o !== c).map(o => ({ a: pts.get(o), b: box(pts.get(o)) })));
      for (let it = 0; it < 3; it++) {
        let moved = false, ba = box(a);
        for (const o of others) { const d = gap(a, ba, o.a, o.b); if (d >= MARG) continue;
          let dx = (ba[0] + ba[1]) / 2 - (o.b[0] + o.b[1]) / 2, dy = (ba[2] + ba[3]) / 2 - (o.b[2] + o.b[3]) / 2; const L = Math.hypot(dx, dy) || 1; dx /= L; dy /= L;
          const k = MARG - d + .6; let mx = dx * k, my = dy * k;
          if (ba[3] + my > IN || ba[2] + my < -IN) { my = 0; mx = (dx >= 0 ? 1 : -1) * k; }    // against a wall: along the vessel
          p.x += mx; p.y += my; c.g.position.x += mx; c.g.position.y += my;
          for (let i = 0; i < a.length; i += 2) { a[i] += mx; a[i + 1] += my; } ba = box(a); moved = true; }
        if (!moved) break;
      }
      // and inside the walls
      const ba = box(a), wy = Math.min(0, IN - ba[3]) + Math.max(0, -IN - ba[2]);
      if (wy) { p.y += wy; c.g.position.y += wy; for (let i = 1; i < a.length; i += 2) a[i] += wy; }
    });
  };
}
