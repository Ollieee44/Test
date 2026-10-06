# Oyster repo: what lives where, and how to build, test and publish it

All work is on branch `claude/blissful-heisenberg-oewalt` of the repo, under `oyster/`.

## Map

| Path | What it is |
|---|---|
| `oyster/index.html` | Main site (first version): Nacre/Tidepool, 2D SELFTAC animation, complex wallpaper source |
| `oyster/editorial/index.html` | Editorial-style alternative site |
| `oyster/brand/` | Marks and exports: `oyster-logotype-*.svg`, `oyster-wordmark-*.svg`, `marks.py`, `build_variations.py` |
| `oyster/brand/logotype/` | Logotype studio and builder; `settings.json` holds the client's saved "optically even" spacing |
| `oyster/molecule/` | 2D molecule studies and the SELFTAC icon used in the first sites |
| `oyster/landing/` | The 3D scroll story: `build_meshes.py` → `data/meshes.json`; `js/molecule.js` (generic degrader, pearls, clasp); `landing_template.html` → `build_landing.py` → `landing.html`; `frames_template.html` → `frames.html` (model viewer) |
| `oyster/site/` | The current website: `build_site.py` combines the landing template + `sections.html` + `site.css` + `site.js` + `wallpaper.js` → `index.html` |
| `oyster/intro/` | The website opened by an intro (3D oyster opens, pearl becomes the 'o', logotype settles into the header): `intro.js` + `intro.css`, `build_intro.py` wraps `../site/index.html` → `index.html`. Test hook `window.__intro.at(ms)` |
| `oyster/deck/` | PowerPoint Morph deck: `bg.py`, `exporter.html`, `build.js`, `post.py` → `oyster-selftac-morph.pptx`; `models/*.glb` |

`data/5t35.pdb` and `data/1ubq.pdb` are gitignored; download from RCSB if missing.

## Build

```bash
cd oyster/landing && python build_meshes.py   # only when geometry changes (needs rdkit, scikit-image, scipy)
python build_landing.py                        # landing.html (the standalone story)
cd ../site && python build_site.py             # site index.html (always rebuild after landing changes)
python build_palettes.py                       # palettes.html, the six-palette explorer
cd ../intro && python build_intro.py           # the intro site (rebuild after any site change)
```

The site and the landing page share `landing_template.html` and `js/molecule.js`. A change there
affects both pages, so rebuild and republish both or say which one you left alone.

Deck (needs pptxgenjs and playwright on NODE_PATH, the pptx skill dir, a local three.js package):

```bash
cd oyster/deck && python bg.py out
PPTX_SKILL=<pptx skill dir> NODE_PATH=<node_modules> node build.js <three package dir> out
python post.py out/stage1.pptx out/models.json out/turns.json oyster-selftac-morph.pptx
python <pptx skill>/scripts/office/validate.py oyster-selftac-morph.pptx
```

LibreOffice previews show the still fallback images, not the 3D models, so check positions there but
ask the user to confirm the 3D behaviour in real PowerPoint. LibreOffice needs `libreoffice-impress`.

## Test (headless Chromium)

The sandbox cannot reach cdnjs/jsdelivr or Google Fonts, so tests route them to local copies:
three.js from an npm install of `three@0.160.0`, and font files. Launch Chromium at
`/opt/pw-browsers/chromium-1194/chrome-linux/chrome` with `--use-angle=swiftshader
--enable-unsafe-swiftshader` for WebGL. Hooks for screenshots:

- Landing: `window.__story.frame(p)` holds the story at progress p (0–1).
- Site: scroll to `story:<p>` (the story section's offset) or to `#vision`, `#why`, `#pipeline`,
  `#team`, `#investors`, `#news`, `#contact`; wait about 2 s for smoothing and reveals.

Check desktop (1440×900) and phone (390×844), and both palettes (click `.pal button[data-pal=tidepool]`).
Look at the screenshots before reporting.

## Publish

Copy the built HTML into the session scratchpad and publish it with the Artifact tool to the existing
URL, so the client's link stays the same:

| Page | Artifact |
|---|---|
| Website with intro (`intro/index.html`) | https://claude.ai/artifact/NTiBBienf6HvCseLhbCDHU |
| Palette explorer (`site/palettes.html`) | https://claude.ai/artifact/AfzgUFchFXjBXQWcboMYMy |
| Current website (`site/index.html`) | https://claude.ai/artifact/9pFqdk4otTS46U21phpLCk |
| 3D story (`landing/landing.html`) | https://claude.ai/artifact/9aJKZGFD5fzeHUrQu9EPTk |
| 3D model viewer (`landing/frames.html`) | https://claude.ai/artifact/7YaLDip9qnWoVVs9p7CVeh |
| Main site (first) | https://claude.ai/artifact/WSV9dspDgvBBMTUiZZUEZN |
| Editorial site | https://claude.ai/artifact/12vnmPkAi83mVtPXTDLPZV |
| Mark variations | https://claude.ai/artifact/7nbPJzaNZTv9pXDPZftmnP |
| Logotype studio | https://claude.ai/artifact/7tNEfaWQeav7iTWnMSocu1 |
| Inside Out, refined (`brand/refine.html`) | https://claude.ai/artifact/TYDiqpmFntUpWcALworY7g |
| Beyond the compact (`brand/frontal.html`) | https://claude.ai/artifact/H9Kr4y1ZRdNsRYhnCf1NKf |
| Open oyster (`brand/threequarter.html`) | https://claude.ai/artifact/3XER9VkRqams9ryoFciMjb |
| Open oyster picks, 02 and 05 (`brand/openpick.html`) | https://claude.ai/artifact/JCZmPkni1P6zVMZuQHMMFY |
| Two valves, one hinge (`brand/hinged.html`) | https://claude.ai/artifact/N8uzWVpwns4Skux3XkmCYy |
| From the references (`brand/refs.html`) | https://claude.ai/artifact/ACn2XP8bzFsQJVb5d5DKyb |
| Fan and pearl riffs (`brand/riffs.html`) | https://claude.ai/artifact/S2YScwuN6szkQzeQ2rex7Y |
| Line fan, pearl sizes (`brand/linepearl.html`) | https://claude.ai/artifact/4zMWE6ipDqHpULNFiJG8os |
| Line fan, inside out tighter (`brand/linepick.html`) | https://claude.ai/artifact/4gdAYgpeD5UJzm2T1zwqw1 |

The deck is delivered as a file (send it to the user), not an artifact. Commit and push after each
change with a message that says what changed and why.
