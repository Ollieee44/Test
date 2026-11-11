// ---------- click-through v2: edit the words in place ----------
// For people who can edit this artifact: an "Edit text" button opens a panel with every section (its rail title, label,
// heading and body) and the end card's tagline. Changes preview live; Save rewrites the page's text block (#c2text) in the
// page's own source and publishes it as the new version, so everyone sees the new words and the code carries them.
(async () => {
  const claudeRT = window.claude;
  const art = claudeRT && claudeRT.use ? await claudeRT.use('artifact') : null;
  if (!art) return;                                   // not on claude.ai, or this view cannot save: no editor
  const who = await claudeRT.use('user');
  if (who && who.canEdit && !(await who.canEdit())) return;   // viewers who cannot edit never see it

  const SKEL = '<!doctype html><html><head><meta charset=utf8><meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover"><style>'
    + document.head.querySelector('style')?.textContent + '</style></head><body>';
  const pad = n => String(n).padStart(2, '0');
  const saved = window.__c2text, draft = JSON.parse(JSON.stringify(saved));
  const stage = document.getElementById('stage');

  const btn = document.createElement('button'); btn.type = 'button'; btn.className = 'jedit-btn';
  btn.innerHTML = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M11.2 2.3l2.5 2.5-8 8H3.2v-2.5z M9.6 3.9l2.5 2.5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/></svg><span>Edit text</span>';
  stage.appendChild(btn);

  const panel = document.createElement('aside'); panel.className = 'jedit'; panel.setAttribute('aria-label', 'Edit the text'); panel.hidden = true;
  const field = (lab, val, path, multi) => `<label class="jf"><span>${lab}</span>${multi
    ? `<textarea rows="4" data-path="${path}"></textarea>` : `<input type="text" data-path="${path}">`}</label>`;
  panel.innerHTML = '<header><h2>Edit text</h2><button type="button" class="jx" aria-label="Close">&times;</button></header><div class="jbody">'
    + draft.sections.map((s, i) => `<fieldset data-sec="${i}"><legend><b>${pad(i + 1)}</b><span class="jlg"></span></legend>`
      + field('Section title (on the progress bar)', s.title, `sections.${i}.title`)
      + field('Label', s.label, `sections.${i}.label`)
      + field('Heading', s.heading, `sections.${i}.heading`)
      + field('Text', s.body, `sections.${i}.body`, true) + '</fieldset>').join('')
    + '<fieldset data-sec="end"><legend><b>End</b><span class="jlg">Closing card</span></legend>'
    + field('Tagline', draft.tagline[0], 'tagline.0') + field('Tagline, highlighted part', draft.tagline[1], 'tagline.1') + '</fieldset>'
    + '</div><footer><span class="jst" role="status" aria-live="polite"></span><button type="button" class="jbtn jdis">Discard</button><button type="button" class="jbtn jnext jsave">Save</button></footer>';
  stage.appendChild(panel);

  const get = p => p.split('.').reduce((o, k) => o[k], draft);
  const set = (p, v) => { const ks = p.split('.'), last = ks.pop(); ks.reduce((o, k) => o[k], draft)[last] = v; };
  const inputs = [...panel.querySelectorAll('[data-path]')];
  const status = panel.querySelector('.jst'), save = panel.querySelector('.jsave');
  const legends = () => panel.querySelectorAll('fieldset[data-sec]').forEach(f => { if (f.dataset.sec !== 'end') f.querySelector('.jlg').textContent = draft.sections[+f.dataset.sec].title; });
  const dirty = () => JSON.stringify(draft) !== JSON.stringify(saved);
  const fill = () => { inputs.forEach(el => { el.value = get(el.dataset.path); }); legends(); };
  const refresh = () => { window.__applyText(draft); legends(); save.disabled = !dirty(); if (!busy) status.textContent = dirty() ? 'Unsaved changes' : ''; };
  let busy = false, lastSec = -1;
  fill(); refresh();

  inputs.forEach(el => el.addEventListener('input', () => { set(el.dataset.path, el.value); refresh(); }));
  // focusing a section's fields takes the journey to that section, so the preview is the one being edited
  panel.addEventListener('focusin', e => {
    const f = e.target.closest('fieldset[data-sec]'); if (!f) return;
    const i = f.dataset.sec === 'end' ? 'end' : +f.dataset.sec; if (i === lastSec) return; lastSec = i;
    const pearls = document.querySelectorAll('.rail > div');
    if (i === 'end') jumpEnd(); else pearls[i]?.click();
  });
  // the end card: from the last section's stop, step on until Next has become "Start again"
  function jumpEnd() { const pearls = document.querySelectorAll('.rail > div'); pearls[pearls.length - 1]?.click();
    setTimeout(() => { const n = document.getElementById('jnext'); for (let k = 0; k < 3; k++) if (!n.querySelector('span').textContent.includes('Start')) n.click(); }, 50); }

  const open = () => { const play = document.getElementById('jplay'); if (play?.classList.contains('on')) play.click();
    panel.hidden = false; document.documentElement.classList.add('jediting'); btn.setAttribute('aria-expanded', 'true'); panel.querySelector('input')?.focus(); };
  const close = () => { panel.hidden = true; document.documentElement.classList.remove('jediting'); btn.setAttribute('aria-expanded', 'false'); btn.focus(); };
  btn.addEventListener('click', () => (panel.hidden ? open() : close()));
  panel.querySelector('.jx').addEventListener('click', close);
  panel.addEventListener('keydown', e => { if (e.key === 'Escape') close(); e.stopPropagation(); });   // typing never steps the journey
  panel.querySelector('.jdis').addEventListener('click', () => { Object.assign(draft, JSON.parse(JSON.stringify(saved))); fill(); refresh(); });

  save.addEventListener('click', async () => {
    if (busy || !dirty()) return; busy = true; save.disabled = true; status.textContent = 'Saving…';
    try {
      const src = await (await fetch(location.href, { cache: 'no-store' })).text();
      const b0 = src.indexOf('<body>'), b1 = src.lastIndexOf('</body>');
      const OPEN = '<script type="application/json" id="c2text">', i0 = src.indexOf(OPEN), i1 = i0 < 0 ? -1 : src.indexOf('<\/script>', i0);
      if (b0 < 0 || b1 < 0 || i0 < 0 || i1 < 0) throw { code: 'source' };
      const json = JSON.stringify(draft).replace(/</g, '\\u003c');
      const body = src.slice(b0 + 6, i0 + OPEN.length) + json + src.slice(i1, b1);
      await art.publish(SKEL + body + '</body></html>');
      status.textContent = 'Saved. Reloading…';
    } catch (e) {
      const c = e && e.code;
      status.textContent = c === 'conflict' ? 'Someone saved a newer version first; the page will reload to it.'
        : c === 'not_writer' || c === 'not_granted' ? 'You can preview changes, but you don’t have permission to save this page.'
        : c === 'source' ? 'Couldn’t read this page’s source to save it.' : 'Couldn’t save. Please try again.';
      busy = false; save.disabled = !dirty();
    }
  });
})();
