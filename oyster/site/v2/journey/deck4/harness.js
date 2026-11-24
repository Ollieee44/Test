// Builds .harness.html: the v4 page (click6) with its scene exposed as window.__X for the deck exporter.
const fs = require('fs'), path = require('path');
const SRC = path.join(__dirname, '../click6/index.html');
let h = fs.readFileSync(SRC, 'utf8');
const hook = 'window.__journey = window.__story = {';
if (h.split(hook).length !== 2) throw new Error('journey hook not found once');
h = h.replace(hook, 'window.__X = { THREE, scene, camera, get renderer() { return renderer; }, cg, inner, mol, P, prot, ubs, e2, frags, flash, stage, wall, cell, frame: p => frame(p), resize: () => resize() };\n' + hook);
fs.writeFileSync(path.join(__dirname, '.harness.html'), h);
