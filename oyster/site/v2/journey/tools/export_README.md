# SELFTAC® journey (v4): handoff package

An interactive, 11-step WebGL story that shows how a SELFTAC® degrader goes from a pill to a cleared protein. It runs as one standalone web page. This package has everything needed to put it on a Webflow site (or any other site), plus still images and a video for places where the live version can't run.

**Quick answer for most teams:** upload `2-self-contained/` to any static host, then paste `3-webflow-snippets/A-full-screen.html` or `B-fixed-height.html` into a Webflow Embed, with the `src` changed to your hosted address. That takes about 15 minutes.

---

## 1. What's in the folder

| Folder | What it is | Use it when |
|---|---|---|
| `1-hosted-page/` | The page (`index.html` + `site.css`). It loads three.js and the fonts from public CDNs (jsDelivr, Google Fonts). | You want the smallest upload and outside CDNs are acceptable. |
| `2-self-contained/` | The same page with three.js and every font bundled locally. It makes **no requests to any other domain**. | **Recommended default.** Also required for a strict Content-Security-Policy, for GDPR concerns (Google Fonts sends visitor IPs to Google), or for offline/kiosk/trade-show use. |
| `3-webflow-snippets/` | Copy-paste embed code: A full-screen section, B fixed-height block, C button that opens an overlay, D step events and site-controlled buttons. | Putting the hosted page into Webflow. |
| `4-stills/` | JPG of every step plus a poster, at desktop (1920×1080) and phone (390×844 @2x, i.e. 780×1688) sizes. | Social, decks, email, the `<noscript>`/no-WebGL fallback, CMS thumbnails, Open Graph image. |
| `5-video/` | 34-second MP4 slideshows (crossfades between the stills) for desktop and phone. | Autoplaying background video, LinkedIn/social posts, a fallback where scripts aren't allowed. See section 9 for recording a true motion video. |
| `package.json` | Build metadata (source file, step count). | Reference only. |

The page in folders 1 and 2 is identical apart from where three.js and the fonts come from.

---

## 2. Why it has to be hosted (and can't be pasted straight into Webflow)

- Webflow's Embed element has a **50,000-character limit**. The page is about 4.25 MB, since the molecular geometry is baked in.
- The page is a full-screen WebGL scene with its own styles, fonts and keyboard handling. Dropped into a Webflow page directly, it would clash with Webflow's CSS and scripts.
- An `<iframe>` keeps it isolated: Webflow can't break it and it can't break Webflow.

So the pattern is: **host the page somewhere → show it on Webflow with an iframe.** Section 8 covers a deeper, iframe-free integration if one is ever needed.

---

## 3. Step 1: host the page

Upload the **contents** of `2-self-contained/` (or `1-hosted-page/`) as a folder, e.g. `/selftac-journey/`, so that `https://YOUR-HOST/selftac-journey/` opens `index.html`. Keep the folder structure as it is, because the paths are relative.

Any static host works. Pick one:

| Option | How | Notes |
|---|---|---|
| **Subdomain of the company domain** (e.g. `story.your-domain.com`) | Any of the hosts below + a CNAME record. | Looks most professional. Easiest analytics/CSP story. |
| **Netlify** | app.netlify.com → *Add new site → Deploy manually* → drag the folder in. | Free tier is plenty. Gzip/Brotli and HTTPS automatic. |
| **Vercel** | `vercel deploy` in the folder, or drag-and-drop in the dashboard. | Same as Netlify. |
| **Cloudflare Pages** | Pages → *Upload assets* → drop the folder. | Fast global CDN, free. |
| **GitHub Pages** | Push the folder to a repo, enable Pages. | Fine for a public page. |
| **Existing web server / S3 + CloudFront / Azure static site** | Copy the folder up. | Turn on gzip or Brotli for `.html`, `.js`, `.css` (see section 7). |
| **Webflow itself** | Not possible: Webflow can't host an arbitrary HTML file at a path, and assets uploaded to Webflow can't be served as pages. | Use one of the above. |

**Check it:** open `https://YOUR-HOST/selftac-journey/` directly in a browser. It should load, show "1 / 11" bottom right, and Next should advance. That URL is also a perfectly good **standalone link** to share or put behind a "Launch" button.

> Opening `index.html` by double-clicking (a `file://` address) will **not** work. Browsers block the module scripts. Use a host, or locally run `python3 -m http.server` in the folder and visit `http://localhost:8000/`.

---

## 4. Step 2: put it on the Webflow page

In the Webflow Designer: add an **Embed** element (Add panel → Components → Code Embed), paste one snippet, and replace every `https://YOUR-HOST/selftac-journey/` with your real address. Embeds render only on the published/preview site, not in the Designer canvas, so publish to staging to see it.

### A. Full-screen section (`A-full-screen.html`): recommended
- Put the Embed in its own Section. Set that Section to **width 100%, height 100vh, padding 0**.
- The journey fills the viewport like a hero; the user steps through with Next / arrow keys, then scrolls on past it.

### B. Fixed-height block (`B-fixed-height.html`)
- A 720 px tall block on desktop, 640 px on phones; full width of its container.
- Use when the story sits inside a longer page between other content. Don't go below about 560 px tall or the text and molecules get cramped. On phones keep it full width.

### C. Button that opens an overlay (`C-button-opens-overlay.html`)
- A button ("See how SELFTAC® works") that opens the journey full screen over the page. It closes with the × or Escape, and focus returns to the button.
- **Nothing loads until the button is pressed**, so it has zero cost to page speed. Best for the homepage or a busy page.
- Style the button with the site's classes, but keep `selftac-open`, `selftac-overlay` and `selftac-close`.
- The button can be any element: a Webflow Button with the class `selftac-open` works too, provided the script part of the snippet is in the page (Page settings → Before `</body>`, or a site-wide Embed).

### D. Step events and site-controlled buttons (`D-step-events-and-controls.html`): optional, combine with A, B or C
- Add `id="selftac-frame"` to the `<iframe>` in whichever snippet you used.
- Set `ORIGIN` to your host's origin (scheme + domain only, e.g. `https://story.your-domain.com`). Messages from anywhere else are ignored.
- **Analytics:** each step pushes `{event: 'selftac_step', step, total}` to `dataLayer`. Google Tag Manager can pick that up as a Custom Event trigger. For GA4 direct, swap the `dataLayer.push` for `gtag('event', 'selftac_step', {step})`. For Plausible/Fathom/Segment, call their event function in the same place.
- **Drive it from the site:** `selftacSend('next')`, `selftacSend('back')`, `selftacSend('play')`, `selftacSend('goto', 7)`. Wire them to Webflow buttons if the design wants its own controls.

#### The message protocol (for developers)
Journey → host (`window.parent.postMessage`):
```js
{ source: 'selftac-journey', type: 'ready', step: 1, total: 11 }   // once, on load
{ source: 'selftac-journey', type: 'step',  step: 7, total: 11 }   // every time the step changes
```
Host → journey (`iframe.contentWindow.postMessage(msg, ORIGIN)`):
```js
{ source: 'selftac-journey-host', command: 'next' | 'back' | 'play' }
{ source: 'selftac-journey-host', command: 'goto', step: 7 }       // 1–11
```

### Deep links
Add `?step=N` to the iframe `src` or to the standalone URL to open at a step, e.g. `https://YOUR-HOST/selftac-journey/?step=7` opens at the ternary complex. Useful for linking from a specific paragraph, or for showing just one moment in a block (combine with a fixed-height embed).

### The 11 steps
| # | Chapter | What's on screen |
|---|---|---|
| 1 | 01 Oral dosing | Pill, figure, gut |
| 2–3 | 02 In the gut | SELFTAC® disassembles into two monomers |
| 4 | 03 In the bloodstream | Monomers and dimer in equilibrium |
| 5–6 | 04 The barrier | "Dimer harder to penetrate" / "Monomers pass through more easily" |
| 7–8 | 05 Ternary complex | Monomers associate to form dimer → ternary complex with target protein and E3 ligase |
| 9–10 | 06 Degradation | Ubiquitin tagging → proteasome degradation |
| 11 | End card | Oyster logo, "Watch again" |

See `4-stills/` for each one.

---

## 5. Changing the text

All on-screen copy (chapter titles, headlines, body lines, labels) lives in one JSON block near the top of `index.html`:

```html
<script type="application/json" id="c2text"> { ... } </script>
```

- **Quick edit:** open `index.html` in a text editor, search for `id="c2text"`, change the strings, save, re-upload. Keep the JSON valid (quotes, commas). The same block exists in both `1-hosted-page/` and `2-self-contained/`, so edit whichever you host.
- **Source of truth:** the copy is maintained in the Oyster repo at `oyster/site/v2/journey/text/click6.json`. Changes made there and rebuilt with `build_journey.py` + `tools/export_package.py` will flow into a fresh package. Hand-edits to an exported `index.html` will be lost the next time the package is rebuilt, so send copy changes back to whoever owns the repo.
- Keep ® on the first SELFTAC® on each screen, per brand rules.
- The page `<title>` (browser tab) is "How a SELFTAC® degrader works · Oyster Therapeutics". Change it in the `<title>` tag.
- Colours, molecules, timing and layout are **not** meant to be edited by hand; request those through the repo.

---

## 6. Browser support, WebGL and fallbacks

- Works in current Chrome, Edge, Safari (macOS and iOS, recent versions), Firefox and Samsung Internet. It needs **WebGL** and **JavaScript modules**.
- **No WebGL** (very old devices, some locked-down corporate machines, GPU blocklists): the page shows a short notice and the text still works, but there are no 3D scenes. If that audience matters, put a still from `4-stills/` beside or behind the embed, or use the overlay (C) so the page itself never depends on it.
- **No JavaScript / email / print / PDF:** use the stills or the MP4.
- **Reduced motion:** for visitors with "Reduce motion" turned on in their OS, transitions between steps cut instead of animating.
- **Very old browsers** (roughly pre-2021) aren't supported. Show a still.

Suggested fallback markup inside snippet A or B, which only appears if iframes are blocked:
```html
<iframe ...>
  <img src="https://YOUR-HOST/selftac-journey-stills/desktop-poster.jpg" alt="How a SELFTAC® degrader works">
</iframe>
```

---

## 7. Performance

- Page weight: `index.html` about 4.25 MB (about 2.5 MB gzipped), three.js about 1.2 MB (about 0.3 MB gzipped), fonts about 0.2 MB.
- **Turn on gzip or Brotli** on the host. Netlify, Vercel and Cloudflare do this automatically; on your own server/S3, enable it for `text/html`, `application/javascript` and `text/css`.
- Caching: the files don't change between releases, so `Cache-Control: public, max-age=31536000` is fine on `vendor/` and `fonts/`; use a shorter max-age (e.g. 1 hour) on `index.html` so copy updates show quickly.
- Snippets A and B use `loading="lazy"`, so the iframe doesn't load until it nears the viewport. Snippet C loads nothing until clicked. Avoid placing A/B in the first screen of the homepage if Lighthouse scores matter; use C there instead.
- It runs smoothly on any phone from the last ~5 years. The page caps its pixel ratio at 2× to keep phones smooth.

---

## 8. Other ways to integrate (only if needed)

| Need | Approach |
|---|---|
| Strict CSP on the Webflow site | Add your host to `frame-src` (e.g. `frame-src https://story.your-domain.com`). The self-contained page itself needs only `'self'` plus `'unsafe-inline'` for its inline script/style. |
| The page must sit on the **same domain** as Webflow (e.g. `your-domain.com/science/journey`) | Webflow can't serve it directly; use a reverse proxy (Cloudflare Worker / Netlify proxy) that routes that path to the static host. |
| No iframe at all (scroll-linked into Webflow sections, shared nav) | Custom development: load the scene's module into a Webflow page via an external script and mount it into a div. Not covered by this package; budget developer time and ask the repo owner for the source build. |
| Webflow CMS-driven copy | Possible via the postMessage bridge (send copy in), but not built. Ask if needed. |
| Cookie banner / consent | The self-contained page sets **no cookies**, uses **no storage** and contacts **no third parties**. It needs no consent. `1-hosted-page/` contacts Google Fonts and jsDelivr; use folder 2 if that's a concern. |

---

## 9. Stills and video

- `4-stills/desktop-step-01.jpg` … `-11.jpg`, `desktop-poster.jpg` (1920×1080), and the same set prefixed `phone-` (780×1688). The navigation buttons are hidden; the chapter rail is kept.
- Use `desktop-poster.jpg` as the **Open Graph / social share image** for the page that hosts the journey.
- `5-video/selftac-journey-slideshow-desktop.mp4` (1920×1080, 34 s) and `-phone.mp4` (780×1688) are **crossfade slideshows** of the stills, not recordings of the live motion. They're good for a muted autoplay loop (Webflow Background Video element, ≤ 30 MB) or social.
- **For a true motion video:** open the hosted page full screen on a good machine, press **Play from here** on step 1, and screen-record (macOS: Cmd-Shift-5; Windows: Xbox Game Bar Win-Alt-R, or OBS at 60 fps). Hide the cursor, and record at 1920×1080 or larger. The Play button runs the whole story hands-free.

---

## 10. Accessibility

- Keyboard: **→ / ↓ / Space / Page Down** next, **← / ↑ / Page Up** back. Chapter dots on the rail are focusable and open with Enter. Inside an iframe, the iframe must have focus first (one click or Tab).
- The scene has an `aria-label` describing it. All on-screen text is real text, so it's readable by screen readers and translatable.
- Give the iframe a meaningful `title` (the snippets do).
- Respects "Reduce motion" (transitions cut instead of animating).
- The overlay (C) closes with Escape or the × button, and focus returns to the button that opened it.

---

## 11. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Blank area in Webflow Designer | Normal. Embeds only render on the published or preview site. |
| Blank iframe on the published site | Wrong `src` (open it directly in a tab to check), or the host sends `X-Frame-Options: DENY` / `frame-ancestors 'none'`. Allow the Webflow domain(s) in `frame-ancestors`. |
| Nothing loads when `index.html` is opened by double-click | `file://` blocks modules. Use a web server (section 3). |
| Fonts look wrong (Times-like) | `1-hosted-page`: Google Fonts blocked by a network/CSP; switch to `2-self-contained`. `2-self-contained`: the `fonts/` folder wasn't uploaded alongside `index.html`. |
| "WebGL is unavailable" notice | Device/browser has WebGL off. Show a still (section 6). |
| Arrow keys scroll the Webflow page instead | Click inside the journey first, so the iframe takes focus. |
| Analytics events not arriving | `ORIGIN` in snippet D must exactly match the host (`https://`, no trailing slash, no path), and the iframe needs `id="selftac-frame"`. |
| Cut off on phones | Use A (100svh) or give B at least 640 px. Don't put the embed inside a Webflow container with fixed max-width + padding on mobile. |
| Slow first load | Enable compression (section 7); use snippet C on heavy pages. |

---

## 12. Credits and licences

- **Molecular structures** are illustrative, derived from public Protein Data Bank entries: **5T35** (VHL–ElonginB–ElonginC with a degrader), **1UBQ** (ubiquitin) and **6MSB** (26S proteasome). Courtesy of the RCSB PDB (rcsb.org). The SELFTAC® molecule shown is a **generic degrader illustration**, not a disclosed structure.
- **three.js** r160: MIT licence (`2-self-contained/vendor/three/LICENSE`).
- **Fonts:** Geist and Geist Mono (Vercel), Monomaniac One, and Newsreader, all under the SIL Open Font License 1.1, bundled via Fontsource. See `2-self-contained/LICENSES.txt`.
- SELFTAC® is a registered trademark of Oyster Therapeutics. The journey, copy and imagery are © Oyster Therapeutics; please don't reuse them outside Oyster's own channels without permission.

Questions about content or rebuilding: contact the owner of the Oyster site repo (`oyster/site/v2/journey/`).
