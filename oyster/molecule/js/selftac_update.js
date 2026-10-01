  function updateSelftac(vh) {
    var r = selftac.getBoundingClientRect();
    if (r.bottom < 0 || r.top > vh) return;
    var p = clamp(-r.top / (r.height - vh), 0, 1);
    var s0 = clamp((p - .02) / .12, 0, 1), s1 = seg(p, .19, .28), s2 = clamp((p - .31) / .23, 0, 1), s3 = seg(p, .56, .635);
    var fx = clamp((p - .635) / .045, 0, 1), u = clamp((p - .7) / .11, 0, 1), s4 = seg(p, .815, .855), s5 = seg(p, .845, .875), s6 = seg(p, .89, .96);
    var ax, ay, bx, by, sc, qa = 1, qb = 1, ka = { m: -1 }, kb = { m: -1 };
    if (s2 <= 0) {
      // joined degrader bumps against the endothelium, then splits in the blood
      var bump = Math.sin(Math.PI * s0) * 34 * (1 - s1);
      sc = lerp(1, .8, s1);
      ax = lerp(309 - HALF_DX * sc / 2, 262, s1); ay = lerp(64 - HALF_DY * sc / 2, 64, s1) + bump;
      bx = lerp(309 + HALF_DX * sc / 2, 366, s1); by = lerp(64 + HALF_DY * sc / 2, 64, s1) + bump;
    } else {
      // each half pauses at every membrane it crosses, squeezing slightly as it passes through
      ka = keyed(KEY_A, s2); kb = keyed(KEY_B, s2);
      if (ka.m >= 0) qa = 1 - .14 * Math.sin(Math.PI * ka.m);
      if (kb.m >= 0) qb = 1 - .14 * Math.sin(Math.PI * kb.m);
      // then reassembles between the target protein and the E3 ligase
      ax = lerp(ka.x, CELL.asm[0] - HALF_DX * .4, s3); ay = lerp(ka.y, CELL.asm[1] - HALF_DY * .4, s3);
      bx = lerp(kb.x, CELL.asm[0] + HALF_DX * .4, s3); by = lerp(kb.y, CELL.asm[1] + HALF_DY * .4, s3); sc = .8;
    }
    A.setAttribute('transform', 'translate(' + ax.toFixed(1) + ' ' + ay.toFixed(1) + ') scale(' + sc.toFixed(3) + ' ' + (sc * qa).toFixed(3) + ')');
    B.setAttribute('transform', 'translate(' + bx.toFixed(1) + ' ' + by.toFixed(1) + ') scale(' + sc.toFixed(3) + ' ' + (sc * qb).toFixed(3) + ')');
    [[ripA, ka], [ripB, kb]].forEach(function (rk) {
      var k = rk[1], on = k.m >= 0 && s3 <= 0;
      rk[0].setAttribute('opacity', on ? (Math.sin(Math.PI * k.m) * .8).toFixed(2) : '0');
      if (on) rk[0].setAttribute('transform', 'translate(' + k.x.toFixed(1) + ' ' + k.y.toFixed(1) + ') scale(' + (.6 + .9 * k.m).toFixed(2) + ')');
    });
    // the reversible bond: dashed while open, then it clicks shut with a flash
    var mx = (ax + HALF_BRK[0][0] * sc + bx + HALF_BRK[1][0] * sc) / 2, my = (ay + HALF_BRK[0][1] * sc + by + HALF_BRK[1][1] * sc) / 2;
    LK.setAttribute('transform', 'translate(' + mx.toFixed(1) + ' ' + my.toFixed(1) + ')');
    var lkOn = s1 > 0 && s2 < .15 ? s1 * (1 - s2 / .15) : s3 > .4 && fx < .2 ? (s3 - .4) / .6 * (1 - fx / .2) : 0;
    LK.setAttribute('opacity', lkOn.toFixed(2));
    bondFx.setAttribute('opacity', (fx > 0 && fx < 1 ? Math.sin(Math.PI * fx) : 0).toFixed(2));
    bondFx.setAttribute('transform', 'translate(' + mx.toFixed(1) + ' ' + my.toFixed(1) + ') scale(' + (.7 + 1.5 * fx).toFixed(2) + ')');
    // an E2 enzyme docks on the E3 ligase and hands over four ubiquitins, one at a time, onto
    // the face of the target turned towards the ligase; it leaves as the target is destroyed
    var arrive = seg(u, 0, .18), dx2 = lerp(620, CELL.e2[0], arrive) + 220 * s4, dy2 = lerp(300, CELL.e2[1], arrive) - 40 * s4;
    e2G.setAttribute('transform', 'translate(' + dx2.toFixed(1) + ' ' + dy2.toFixed(1) + ')');
    e2G.setAttribute('opacity', (u > 0 ? Math.min(arrive * 2, 1 - s4) : 0).toFixed(2));
    var done = 0, hop = -1;
    for (var i = 0; i < 4; i++) { var q = (u - .2 - i * .2) / .2; if (q >= .999) done++; else if (q >= 0 && hop < 0) hop = q; }
    ubq.forEach(function (c, i) { c.setAttribute('opacity', i < done ? '1' : '0'); });
    var sx = dx2 + CELL.e2ub[0], sy = dy2 + CELL.e2ub[1];
    if (u > 0 && done < 4) {
      var tq = hop < 0 ? 0 : ease(hop), slot = CELL.ub[done];
      e2ub.setAttribute('cx', lerp(sx, slot[0], tq).toFixed(1)); e2ub.setAttribute('cy', (lerp(sy, slot[1], tq) - 16 * Math.sin(Math.PI * tq)).toFixed(1));
      e2ub.setAttribute('opacity', Math.min(arrive * 2, 1).toFixed(2));
    } else e2ub.setAttribute('opacity', '0');
    // the tagged target is fed into the proteasome
    var k = 1 - .8 * s4;
    tgtG.setAttribute('transform', 'translate(' + ((CELL.into[0] - CELL.tgt[0]) * s4 + CELL.tgt[0] * (1 - k)).toFixed(1) + ' ' + ((CELL.into[1] - CELL.tgt[1]) * s4 + CELL.tgt[1] * (1 - k)).toFixed(1) + ') scale(' + k.toFixed(3) + ')');
    tgtG.setAttribute('opacity', (1 - seg(p, .84, .87)).toFixed(2));
    frags.setAttribute('opacity', (s5 * (1 - s6)).toFixed(2));
    frags.setAttribute('transform', 'translate(' + (s5 * 18).toFixed(1) + ' 0)');
    // the degrader is not used up: a second target drifts in and is caught by the warhead
    tgt2.setAttribute('opacity', s6.toFixed(2));
    tgt2.setAttribute('transform', 'translate(' + (-150 * (1 - s6)).toFixed(1) + ' ' + (24 * (1 - s6)).toFixed(1) + ')');
    tgtLbl.setAttribute('opacity', Math.max(1 - seg(p, .7, .74), s6).toFixed(2));
    var step = 0; BOUNDS.forEach(function (bd, i) { if (p >= bd[0]) step = i; });
    if (step !== lastStep) {
      steps.forEach(function (el, i) { el.classList.toggle('on', i === step); });
      capT.textContent = LABELS[step][0]; capS.textContent = LABELS[step][1];
      lastStep = step;
    }
    progI.forEach(function (el, i) { el.style.setProperty('--f', clamp((p - BOUNDS[i][0]) / (BOUNDS[i][1] - BOUNDS[i][0]), 0, 1).toFixed(3)); });
  }
