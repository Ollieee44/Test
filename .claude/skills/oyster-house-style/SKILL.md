---
name: oyster-house-style
description: House style and build conventions for Oyster Therapeutics (SELFTAC® platform) — the Nacre and Tidepool palettes, the "oyster" logotype, the gold clasp motif, the 3D SELFTAC story look, the generic-degrader rule, and how the website, landing story, brand assets and PowerPoint Morph deck in oyster/ are built, tested and published. Use this skill for ANY Oyster or SELFTAC work, even small tweaks — website or landing page changes, new sections or pages, slides or decks, logos and marks, molecule or protein illustrations, animations, colours or copy — and whenever the user mentions Oyster, SELFTAC, Nacre, Tidepool, the clasp, the pearl, the ternary complex or anything under oyster/ in this repo.
---

# Oyster house style

Oyster Therapeutics makes oral, brain-penetrant protein degraders. Its SELFTAC® platform splits a
degrader into two small halves joined by a reversible linker; the halves cross the blood-brain barrier
and clasp back together inside the neuron. Everything visual for Oyster tells that story, and the
**clasp** (the reversible bond where the halves meet) is the idea the company most wants people to see.

This skill holds the decisions already made with the client, so new work starts on-brand. Exact values
and file paths live in the references:

- `references/palette.md` — every colour token for both palettes, fonts, type sizes
- `references/pipelines.md` — repo map, build commands, test harness, publishing, artifact links

Read `palette.md` before choosing any colour or font, and `pipelines.md` before building, testing or
publishing anything.

## Working with this client

- **"Change nothing else" means exactly that.** Make the one change, rebuild, check it, and leave every
  other value alone. Unrequested "improvements" have had to be undone before.
- **Check renders before claiming success.** Render the page or slide (headless Chromium, see
  pipelines.md), look at the image, and only then report. A past bug (a pearl behind text) shipped
  because a fix was claimed without checking every viewport; say plainly what was and wasn't verified.
- **Update existing artifacts in place** (publish to the same URL) rather than creating new links.
- Keep replies short and visual: say what changed, link it, note any caveat, offer one next step.

## Brand essentials

- **Two palettes, always both.** Nacre (light: pearl pinks, mauve ink `#2B2230`) and Tidepool (dark teal
  with gold). Every page has a palette switch, and every new element must look right in both — check both.
- **Type:** Newsreader (serif, headings and statements), Archivo (sans, body and UI), IBM Plex Mono
  (small uppercase eyebrows and labels, wide letter-spacing).
- **The logotype** is lowercase "oyster" with the "Inside Out" mark as the o (a pearl in a cradle, the
  Hollow-style cut-out), small lowercase "therapeutics" tucked under it by the tail of the y, and
  optically even letter spacing. Use the exported SVGs in `oyster/brand/`; never re-set it in a live
  font. It recolours through `currentColor` and `var(--pearl)`. Give it room: the client asked for it
  bigger in the header (42px tall on desktop), not smaller.
- **Section labels** carry the clasp glyph (two gold pearls joined by a bond) before mono uppercase text.

## The clasp motif

The clasp is the hero. Wherever the linker appears it is a string of pearls (white pearls on a mauve
strand), and the meeting point is emphasised: two larger gold clasp pearls (`#D9A443` Nacre, coral
`#F27D62` Tidepool) joined by a thick bond in the same colour, with a soft glow while it is closed. When
the halves split, each half keeps its clasp pearl. Reuse the motif with restraint: pearl-strand progress
rails (the "rebuilt" step is the gold one), pipeline stages as pearl strands, a gold full stop on big
figures. One accent colour, used for one meaning.

## Science illustration rules

- **Proteins** are smoothed, cartoon versions of real surfaces (BRD4 target, VHL ligase with Elongin B
  and C from PDB 5T35; ubiquitin from 1UBQ), shaded with Nacre contour lines and an ink outline.
  Diagrammatic but 3D: real shapes, cartoon finish.
- **The degrader must be generic.** A chemist should recognise a PROTAC (two ligands and a linker)
  without being able to tell which molecule or which ligase. So: never draw JQ1, VH032/hydroxyproline,
  thalidomide/glutarimide or any real ligand; use the invented ring systems already built (a piperidinyl
  benzothiazole and a biaryl amide), traced as smooth tubes along their bonds with the rings left open.
  Not ball-and-stick (too specific), not soft blobs (they read as proteins), not atom colours.
- **The linker** is generic and emphasised: pearls on a strand, bonded into both halves, never floating
  free of them.
- **Stand-ins** (E2 enzyme, proteasome) are simple shapes; say so in credits rather than presenting them
  as real structures.
- Credit the structures on any page that shows them (PDB 5T35, Gadd et al., Nat. Chem. Biol. 2017; PDB
  1UBQ), and note the degrader is drawn generically.

## Layout and motion

- Text first: illustrations, pearls and wallpaper must never sit behind copy. Test at several viewport
  sizes, not one.
- The ternary-complex wallpaper (traced 5T35 outlines, faint, fixed, wiggling only when the page is
  still) is the only background pattern on the site, and it appears only after the 3D story ends. Don't
  add competing patterns.
- Scroll-driven stories: keep them short, show the first line of copy from the start, give a visible
  "Skip to Oyster" control, and design a portrait cut for phones (camera pulled back, copy on a soft card).
- Honour `prefers-reduced-motion` for every loop, and animate transform and opacity where possible.

## Decks

The PowerPoint version of the story uses embedded 3D models (.glb) plus Morph transitions between
keyframe slides; see pipelines.md for the build. Objects that should move between slides share a name
starting with `!!`. Only the frame positions a model: never repeat its position inside the 3D model
markup, which can double the offset in PowerPoint. Flat brand art (the barrier, backgrounds, glow) goes
in as images rendered with the website's own shaders.
