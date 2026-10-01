  var LABELS = [
    ['Conventional degrader', 'Too large to cross the endothelium'],
    ['SELFTAC® molecule', 'Split into two halves by a reversible linker'],
    ['Crossing the blood-brain barrier', 'Through each cell membrane in turn, not between cells'],
    ['Degrader assembled', 'The linker clicks shut between target protein and E3 ligase'],
    ['Ubiquitin tagging and degradation', 'An E2 enzyme hands ubiquitin across; the proteasome breaks the target down'],
    ['Ready for the next target', 'The degrader is released and catches another']
  ];
  var BOUNDS = [[0, .17], [.17, .3], [.3, .55], [.55, .69], [.69, .87], [.87, 1]];
  var CELL = {}; // neuron layout (soma, BRD4, VHL, proteasome), written by molecule/gen_site_icon.py
  // routes through the barrier (viewBox units) as [x, y, duration, pause]: lumen, luminal membrane,
  // endothelial cell, abluminal membrane, end-foot cleft, neuron membrane. Pauses repeat a point.
  var KEY_A = [[262, 64, 0], [251, 122, 1], [250, 134, .5], [250, 134, .8, 1], [250, 167, 1], [250, 167, .8, 1], [262, 182, .4],
    [313, 198, .9], [313, 240, .6], [323, 301, .8], [323, 301, .8, 1], CELL.endA.concat(1)];
  var KEY_B = [[366, 64, 0], [408, 122, 1], [410, 134, .5], [410, 134, .8, 1], [410, 167, 1], [410, 167, .8, 1], [430, 182, .4],
    [473, 198, .9], [470, 250, .6], [452, 291, .8], [452, 291, .8, 1], CELL.endB.concat(1)];
  function keyed(K, t) { // position along keyframes; m is progress through a membrane pause, or -1
    var tot = 0, i; for (i = 1; i < K.length; i++) tot += K[i][2];
    var g = t * tot;
    for (i = 1; i < K.length; i++) {
      if (g <= K[i][2] || i === K.length - 1) { var k = K[i][2] ? clamp(g / K[i][2], 0, 1) : 1, e = ease(k);
        return { x: lerp(K[i - 1][0], K[i][0], e), y: lerp(K[i - 1][1], K[i][1], e), m: K[i][3] ? k : -1 }; }
      g -= K[i][2];
    }
  }
