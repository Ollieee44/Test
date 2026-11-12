// ---------- v3: the degrader lets go and moves on ----------
// Once the target is in the proteasome the SELFTAC lets go of the E3 ligase and drifts into the space the target left,
// labelled as free again: the catalytic point, that one degrader goes on to the next target. The move is made inside the
// journey's frame, just after it has placed the complex (the heroOverride hook), so it always uses the current framing.
{
  // shown only while the degrader itself is on screen (on a phone the camera has moved on to the proteasome by now)
  const onScreen = () => { const p = mol.group.localToWorld(mol.centre.clone()), [x, y] = toScreen(p.x, p.y); return x > 40 && x < stage.clientWidth - 40 && y > 40 && y < stage.clientHeight - 40; };
  const relTag = tag('SELFTAC® · free again', 'key', () => mol.group, pn => winOf(.904, .99, .012)(pn) * (onScreen() ? 1 : 0), 10);
  relTag.el.style.setProperty('--dot', '#DCA84E'); relTag.el.classList.add('dright'); relTag.side = 'left'; relTag.gap = 8; relTag.ov = 6; TAGS.push(relTag);   // on its open left side, the dot by the molecule
  const away = V3(44, 36, 0), zero = V3(0, 0, 0), heroR = heroOverride;
  heroOverride = function (pn, brk) {
    const b = heroR(pn, brk), rel = smR((pn - .884) / .034);
    if (rel > 0) { cg.updateMatrixWorld(true); const a = inner.worldToLocal(zero.clone()), t = inner.worldToLocal(away.clone().multiplyScalar(rel));
      mol.group.position.copy(t.sub(a)); mol.group.rotation.z = .35 * rel; }
    else { mol.group.position.set(0, 0, 0); mol.group.rotation.z = 0; }
    return b;
  };
}
// ---------- v3: the monomers click back together in the cell ----------
// Through the membrane the two monomers rejoin into the dimer before the proteins come in; a label calls it out while
// the clasp closes (pn .688 to .75, the page's own timeline), sitting on the dimer.
{
  const reTag = tag('Monomers associate to form dimer', 'key', () => mol.group, pn => winOf(.688, .75, .012)(pn), 10);
  reTag.el.style.setProperty('--dot', '#DCA84E'); reTag.el.classList.add('dright'); reTag.side = 'left'; reTag.gap = 8; reTag.ov = 6; TAGS.push(reTag);
}
