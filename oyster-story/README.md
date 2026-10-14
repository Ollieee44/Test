# Oyster 3D story

The SELFTAC 3D scroll story from the Science page of Website v2, on its own so it can be reused on another site.

Live version: https://claude.ai/artifact/HebMgTJeimPXxKsf7MKD8p

| File | What it is |
|---|---|
| `index.html` | A demo page: the story, a palette switch, and the steps to reuse it |
| `oyster-story.js` | The scene, the camera path and the scroll timeline (three.js 0.160.0 through an import map) |
| `oyster-story.css` | The pinned stage, copy, rail, end card and the six palettes |
| `meshes.json` | The protein and molecule shapes |
| `story-markup.html` | The story's HTML, to paste where it should appear |
| `tools/build_meshes.py` | Rebuilds `meshes.json` from protein structures |
| `tools/meshes.config.json` | What the shapes are built from, and how |

Serve the folder over HTTP to view it (for example `python3 -m http.server`, then open http://localhost:8000). The script loads `meshes.json` with `fetch`, which does not work from a file opened directly.

## Using it on another site

1. In `<head>`: the Google Fonts link, `oyster-story.css`, and the three.js import map (copy all three from `index.html`).
2. Where the story goes: the contents of `story-markup.html`.
3. Before `</body>`: `<script type="module" src="oyster-story.js"></script>`, with `meshes.json` in the same folder.

Palette: `<html data-palette="nacre">` (or `tidepool`, `pearlink`, `shellcoral`, `abyssmint`, `charcoalviolet`). Any `.pal button[data-pal]` on the page switches it live.

## Changing the 3D shapes

The shapes in `meshes.json` come from crystal structure [5T35](https://www.rcsb.org/structure/5T35): BRD4 held to VHL (with Elongin B and C) by the degrader MZ1. Ubiquitin comes from [1UBQ](https://www.rcsb.org/structure/1UBQ). `tools/build_meshes.py` rebuilds them:

```sh
pip install numpy scipy scikit-image rdkit
python3 tools/build_meshes.py --out meshes-new.json
```

It downloads the structures from the PDB the first time (into `tools/cache/`). Try the result before replacing anything: put `data-meshes="meshes-new.json"` on the `<section class="story">` and the story loads that file instead. When you are happy, rename it to `meshes.json`.

### How each shape is made

- **Proteins** (`brd4`, `vhl`, `elob`, `eloc`, `ub`): a soft surface round the protein's atoms. Each atom adds a Gaussian blob, the surface is drawn where the total crosses a level, then smoothed. It sits about 3 Å outside the atoms, which hides the atoms but keeps each protein's real shape. The contour lines are drawn by the story, not stored.
- **The degrader's two halves** (`warhead` = JQ1, `e3lig` = the VHL ligand): MZ1 is cut at its PEG linker. Each half becomes a flat, textbook drawing of its rings and chains (RDKit's 2D layout), drawn as a smooth tube along every bond so the rings show as holes. The drawing faces the viewer and sits where that half binds in the crystal, turned to match its atoms.
- **The linker** (`linker.curve`): the attachment atom on each half and the PEG atoms between. The story only reads its two ends and its length; it draws its own arc with pearls.
- **Centres** (`centres`): the centroid of each part's real atoms. The story places and turns parts by these.
- **Frame**: the structure's own coordinates, shifted so the centre of the first copy of the complex (chains A–D) sits at 0,0,0. The story turns everything so the target sits left and the ligase right, so the structure's orientation does not matter.

### What you can change in `tools/meshes.config.json`

- **Another structure.** Set `complex.structure` to a PDB id or a local `.pdb` file. Map its chains to the part names in `complex.chains`. Keep the names, because the story looks for `brd4` (the target), `vhl` (the ligase), and `elob` and `eloc` (the ligase's partners).
- **Another degrader.** Set `degrader.residue` and `degrader.chain` to its ligand code and chain. List its linker atoms in order in `linker_atoms`, and name each half's attachment atom in `halves`. Atom names are the ones in the PDB file.
- **The look of the proteins.** `surface.sigma` and `surface.level` set how smooth and how puffy they are; `surface.grid` sets the detail (smaller = more vertices).
- **The look of the halves.** `outline.tube_radius` (thickness), `outline.scale` (drawing size), `outline.facing` (which way the drawing faces), `outline.trim_ends` (leave out methyls, Cl, =O, –OH). Set `degrader.layout` to `"crystal"` to use the real 3D bond geometry instead of a flat drawing.
- **Rebuilding some parts only.** `--only warhead,e3lig` rebuilds those and copies the rest from the current `meshes.json`.

The `meshes.json` that ships here is the website's original. The tool rebuilds the proteins closely: the same distance from the atoms, and within about 0.6 Å of the original surfaces. The halves come out in the same style but not identical, because the website's original drawings were made separately and their exact layout isn't recorded. Keep the original file if you only need the website's look.

## Changing the barrier, the neuron and the proteasome

These are drawn by the story itself, not stored in `meshes.json`. Their sizes are in the `SCENE` block near the top of `oyster-story.js`:

- **`barrier`**: the blood–brain barrier. The number of endothelial `cells`, each cell's `width`, `height` (thickness) and `depth`, the `gap` between cells, how far down it sits (`y`), its `opacity`, and the spacing of its contour rings (`contour`).
- **`neuron`**: where its membrane starts (`top`) and the cell's `radius`. Also the distance between the two layers of the membrane (`bilayer`), how much of the sphere shows (`cap`), the opacities, and how far below the membrane the complex forms (`below`).
- **`proteasome`**: the number of `rings`, their size (`ringRadius`, `ringTube`), their spacing (`ringGap`), and the size of the end caps (`cap`).

The halves' path down through the barrier and the membrane is worked out from these numbers. They still slow down inside the barrier and at the membrane after you move or resize them. Colours for all of these are in the `PAL` table just above, one set per palette (`wall`, `cell`, `prot`).
