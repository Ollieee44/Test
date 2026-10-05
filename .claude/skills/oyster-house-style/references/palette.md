# Oyster palette and type

Values as used in `oyster/landing/landing_template.html`, `oyster/site/site.css` and `oyster/deck/`.

## Page tokens

| Token | Nacre | Tidepool |
|---|---|---|
| `--ink` (text) | `#2B2230` | `#EAF3EF` |
| `--muted` | `#65586A` | `#B6D3CB` |
| `--accent` (eyebrows, links) | `#8C5572` | `#F2B84B` |
| `--paper` (page) | `#EFE6E1` | `#0F4C4A` |
| `--band` (tinted sections) | `#F6EFEC` | `#0C4341` |
| `--pearl` (logo pearl) | `#C99BB0` | `#F2B84B` |
| `--clasp` (the clasp, one meaning only) | `#D9A443` gold | `#F27D62` coral |
| `--line` | `rgba(43,34,48,.16)` | `rgba(234,243,239,.18)` |
| `color-scheme` | light | dark |

## 3D story colours (per palette)

| Part | Nacre | Tidepool |
|---|---|---|
| contour ring lines | `#8C5572` | `#06302E` |
| ink outline | `#2B2230` | `#06302E` |
| BRD4 (target) | `#E7C9D6` | `#F5D89A` |
| VHL (ligase) | `#D6CBE6` | `#9FD6C6` |
| Elongin B / C | `#E8DEDB` / `#DDD2D4` | `#3E7D78` / `#346F6B` |
| degrader half A (warhead end) | `#B4678B` | `#F2B84B` |
| degrader half B (ligase end) | `#8A73B2` | `#5FC2A6` |
| linker strand | `#8C5572` | `#EAF3EF` |
| linker pearls | `#F6EEF1` | `#EAF3EF` |
| ubiquitin | `#C99BB0` | `#F7C873` |
| E2 stand-in | `#CDBFDF` | `#8CC9B8` |
| proteasome stand-in | `#B9A9B6` | `#4F8C86` |
| barrier cells | `#EADADF` (alpha .42) | `#2E6E69` |

Story backgrounds (radial gradients, light corner top right), three grounds:
- Nacre: blood `#F6EEEC → #E3D3D8`, barrier `#F4E7E6 → #E6CBD0`, neuron `#EFE6EE → #D9CCE2`
- Tidepool: `#1B6763 → #0F4C4A`, `#1D615D → #0E4543`, `#155A57 → #0A3836`

Complex wallpaper outline fills: Nacre target `#C99BB0`, ligase `#B8A7C9`, ink `#2B2230`; Tidepool
`#F2B84B`, `#7FC4B0`, ink `#EAF3EF` (drawn at about 22% opacity).

## Type

- **Newsreader** (Google Fonts, `opsz,wght@6..72,400;6..72,500`): headings, statements, story beats.
  The logotype is outlined from Newsreader 500 at opsz 72; don't rebuild it from the live font.
- **Archivo** 400–600: body copy, buttons, nav (13.5px).
- **IBM Plex Mono** 400–500: eyebrows and labels, 11–12px, uppercase, letter-spacing about .12em.
- Big statements: Newsreader 400, `clamp(28px, 3.3vw, 50px)`, line-height 1.14, `text-wrap: balance`.
- In PowerPoint, the same three fonts are named in the deck; users must install them (free).
