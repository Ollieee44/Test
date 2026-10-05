# SELFTAC Morph deck

`oyster-selftac-morph.pptx`: the website's 3D story as nine keyframe slides. Each part of the story is an
embedded 3D model (the same geometry as the site), named the same on every slide, and every slide uses
the Morph transition, so clicking through moves, scales and turns the parts between beats.

- Needs PowerPoint for Microsoft 365, or PowerPoint 2019 or later (Windows or Mac). Older versions,
  Keynote, Google Slides and LibreOffice show the built-in still images instead of the 3D models.
- Brand fonts: Newsreader, Archivo and IBM Plex Mono (free from Google Fonts). Install them for the
  intended look; otherwise PowerPoint substitutes.
- `models/` holds the parts as .glb files, to insert into other decks (Insert > 3D Models > This Device).

## Rebuild

    python bg.py out
    PPTX_SKILL=<pptx skill dir> NODE_PATH=<node_modules with pptxgenjs and playwright> node build.js <three.js package dir> out
    python post.py out/stage1.pptx out/models.json out/turns.json oyster-selftac-morph.pptx

`build.js` drives `exporter.html` in headless Chromium to export the parts and their stills, then lays
out the slides with pptxgenjs; `post.py` swaps each part's still for a 3D model and adds Morph.
