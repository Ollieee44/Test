# Oyster 3D story

The SELFTAC 3D scroll story from the Science page of Website v2, on its own so it can be reused on another site.

- `index.html`: a demo page with the story and the steps to reuse it. Serve the folder over HTTP to view it (for example `python3 -m http.server`), since the script loads `meshes.json` with `fetch`.
- `oyster-story.js`: the scene, camera path and scroll timeline (three.js 0.160.0 via an import map).
- `oyster-story.css`: the pinned stage, copy, rail, end card and the six palettes.
- `meshes.json`: the protein and molecule shapes, traced from PDB 5T35.
- `story-markup.html`: the story's HTML to paste where it should appear.

Live version: https://claude.ai/artifact/HebMgTJeimPXxKsf7MKD8p
