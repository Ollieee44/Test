// ---------- click-through v2: the page's words come from one data block (#c2text), applied as the page loads ----------
// Each section: its title on the rail, its label, heading and body; then the end card's tagline (plain part, accent part).
// The editor (editor.js) rewrites this block and saves the page with it, so this is the one place the text lives.
(function () {
  const pad = n => String(n).padStart(2, '0');
  window.__applyText = function (T) {
    const beats = document.querySelectorAll('#copy .beat'), rail = document.querySelectorAll('.rail > div > span');
    T.sections.forEach((s, i) => {
      const b = beats[i];
      if (b) {
        const k = b.querySelector('.k'); k.textContent = ''; const n = document.createElement('b'); n.textContent = pad(i + 1); k.append(n, s.label);
        b.querySelector('h1, h2').textContent = s.heading; b.querySelector('p').textContent = s.body;
      }
      if (rail[i]) rail[i].textContent = s.title;
    });
    const tag = document.querySelector('#end .tag');
    if (tag) { tag.textContent = T.tagline[0] + ' '; const em = document.createElement('em'); em.textContent = T.tagline[1]; tag.append(em); }
  };
  window.__c2text = JSON.parse(document.getElementById('c2text').textContent);
  window.__applyText(window.__c2text);
})();
