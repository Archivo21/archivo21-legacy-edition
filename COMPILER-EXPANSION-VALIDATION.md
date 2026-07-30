# Compiler six-page expansion validation

**Prepared:** 2026-07-30  
**Repository:** `Archivo21/archivo21-legacy-edition`  
**Pre-commit baseline:** current GitHub `main` ending at `319695f`  
**Preserved template:** pre-visual candidate `9c31d8c`  
**Status:** local candidate generated and validated; GitHub commit and public verification fields are completed after publication.

## Scope

- Rewritten regular operational sequence: Boot Sector plus sectors `00`–`12`.
- Exactly six new regular pages: `/compiler/07/` through `/compiler/12/`.
- Six corresponding derived Turbo views.
- All existing special states, documentation routes and aliases retained.
- Global visible control-cell width: **7 characters**.

## Route / label / destination matrix

| Route | Label | Destination |
|---|---|---|
| `/compiler/` | `LOAD` | `/compiler/00/` |
| `/compiler/` | `ANY` | `/compiler/01/` |
| `/compiler/` | `MEMORY` | `/compiler/02/` |
| `/compiler/` | `ARCHIVE` | `/compiler/03/` |
| `/compiler/` | `POWER` | `/compiler/power/` |
| `/compiler/` | `TURBO` | `/compiler/turbo/` |
| `/compiler/00/` | `BOOT` | `/compiler/` |
| `/compiler/00/` | `RESET` | `/compiler/` |
| `/compiler/00/` | `ANY` | `/compiler/01/` |
| `/compiler/00/` | `MEMORY` | `/compiler/02/` |
| `/compiler/00/` | `POWER` | `/compiler/power/` |
| `/compiler/00/` | `TURBO` | `/compiler/00/turbo/` |
| `/compiler/01/` | `BOOT` | `/compiler/` |
| `/compiler/01/` | `MEMORY` | `/compiler/02/` |
| `/compiler/01/` | `ARCHIVE` | `/compiler/03/` |
| `/compiler/01/` | `ANY` | `/compiler/bsod/` |
| `/compiler/01/` | `POWER` | `/compiler/power/` |
| `/compiler/01/` | `TURBO` | `/compiler/01/turbo/` |
| `/compiler/02/` | `INPUT` | `/compiler/00/` |
| `/compiler/02/` | `ANY` | `/compiler/01/` |
| `/compiler/02/` | `ARCHIVE` | `/compiler/03/` |
| `/compiler/02/` | `RECORD` | `/compiler/04/` |
| `/compiler/02/` | `POWER` | `/compiler/power/` |
| `/compiler/02/` | `TURBO` | `/compiler/02/turbo/` |
| `/compiler/03/` | `MEMORY` | `/compiler/02/` |
| `/compiler/03/` | `INPUT` | `/compiler/00/` |
| `/compiler/03/` | `RECORD` | `/compiler/04/` |
| `/compiler/03/` | `ANY` | `/compiler/bsod/` |
| `/compiler/03/` | `POWER` | `/compiler/power/` |
| `/compiler/03/` | `TURBO` | `/compiler/03/turbo/` |
| `/compiler/04/` | `ARCHIVE` | `/compiler/03/` |
| `/compiler/04/` | `MEMORY` | `/compiler/02/` |
| `/compiler/04/` | `REVIEW` | `/compiler/05/` |
| `/compiler/04/` | `ANY` | `/compiler/05/` |
| `/compiler/04/` | `POWER` | `/compiler/power/` |
| `/compiler/04/` | `TURBO` | `/compiler/04/turbo/` |
| `/compiler/05/` | `RECORD` | `/compiler/04/` |
| `/compiler/05/` | `ARCHIVE` | `/compiler/03/` |
| `/compiler/05/` | `OUTPUT` | `/compiler/06/` |
| `/compiler/05/` | `ANY` | `/compiler/bsod/` |
| `/compiler/05/` | `POWER` | `/compiler/power/` |
| `/compiler/05/` | `TURBO` | `/compiler/05/turbo/` |
| `/compiler/06/` | `REVIEW` | `/compiler/05/` |
| `/compiler/06/` | `RECORD` | `/compiler/04/` |
| `/compiler/06/` | `PROV` | `/compiler/07/` |
| `/compiler/06/` | `ANY` | `/compiler/07/` |
| `/compiler/06/` | `POWER` | `/compiler/power/` |
| `/compiler/06/` | `TURBO` | `/compiler/06/turbo/` |
| `/compiler/07/` | `OUTPUT` | `/compiler/06/` |
| `/compiler/07/` | `REVIEW` | `/compiler/05/` |
| `/compiler/07/` | `INDEX` | `/compiler/08/` |
| `/compiler/07/` | `ANY` | `/compiler/bsod/` |
| `/compiler/07/` | `POWER` | `/compiler/power/` |
| `/compiler/07/` | `TURBO` | `/compiler/07/turbo/` |
| `/compiler/08/` | `PROV` | `/compiler/07/` |
| `/compiler/08/` | `OUTPUT` | `/compiler/06/` |
| `/compiler/08/` | `yB` | `/compiler/09/` |
| `/compiler/08/` | `ANY` | `/compiler/09/` |
| `/compiler/08/` | `POWER` | `/compiler/power/` |
| `/compiler/08/` | `TURBO` | `/compiler/08/turbo/` |
| `/compiler/09/` | `INDEX` | `/compiler/08/` |
| `/compiler/09/` | `PRINT` | `/compiler/08/` |
| `/compiler/09/` | `HANDOFF` | `/compiler/10/` |
| `/compiler/09/` | `ANY` | `/compiler/bsod/` |
| `/compiler/09/` | `POWER` | `/compiler/power/` |
| `/compiler/09/` | `TURBO` | `/compiler/09/turbo/` |
| `/compiler/10/` | `yB` | `/compiler/09/` |
| `/compiler/10/` | `INDEX` | `/compiler/08/` |
| `/compiler/10/` | `ANHQV` | `/compiler/11/` |
| `/compiler/10/` | `ANY` | `/compiler/11/` |
| `/compiler/10/` | `POWER` | `/compiler/power/` |
| `/compiler/10/` | `TURBO` | `/compiler/10/turbo/` |
| `/compiler/11/` | `HANDOFF` | `/compiler/10/` |
| `/compiler/11/` | `yB` | `/compiler/09/` |
| `/compiler/11/` | `FAVICON` | `/compiler/12/` |
| `/compiler/11/` | `ANY` | `/compiler/bsod/` |
| `/compiler/11/` | `POWER` | `/compiler/power/` |
| `/compiler/11/` | `TURBO` | `/compiler/11/turbo/` |
| `/compiler/12/` | `ANHQV` | `/compiler/11/` |
| `/compiler/12/` | `HANDOFF` | `/compiler/10/` |
| `/compiler/12/` | `BLUE` | `/compiler/bsod/` |
| `/compiler/12/` | `FAVICON` | `/compiler/bsod/turbo/` |
| `/compiler/12/` | `POWER` | `/compiler/power/` |
| `/compiler/12/` | `TURBO` | `/compiler/12/turbo/` |

## Special-state relationships

- Normal-page POWER → `/compiler/power/`.
- Normal-page TURBO → corresponding derived Turbo route.
- Turbo-page ordinary controls → `/compiler/bsod/`.
- Normal BSOD POWER → `/scaffold/`; TURBO → `/compiler/bsod/turbo/`.
- Turbo BSOD POWER → `/compiler/bsod/logo/`; TURBO → `/compiler/bsod/`.
- Safe-return bracket link → `https://web.archivo21.org/`; POWER → `/scaffold/`.
- Favicon footnote `ARCHIVO 21` → `/`.

## Test results

### Static route and graph validation — PASS

- 252 public HTML routes found.
- 14 regular Compiler screens found: BOOT SECTOR plus sectors `00`–`12`.
- Exactly six new regular sectors found: `07`–`12`.
- 14 derived Turbo views found.
- `ANY` appears visibly on 13 normal screens.
- 251 of 251 non-404 HTML routes are click-reachable from `/`.
- The favicon Easter egg is click-reachable without manual URL entry.
- Every internal Compiler href resolves.
- Every normal and alias operational page has four ordinary controls plus POWER and TURBO.
- Every odd regular sector `01`, `03`, `05`, `07`, `09`, `11` has one ordinary BSOD choice.
- Direction rules pass: except BOOT and `01`, at least two ordinary controls return to earlier screens and no more than two advance the story.
- Every Turbo ordinary control converges on `/compiler/bsod/`.
- No generic `KEY1`–`KEY4` filler remains in the authored operational sequence.
- No private, person-directed, withdrawn-example or outreach material appears in the operational or special-state pages.

### Literal control and degradation validation — PASS

- All control cells contain exactly seven visible characters after non-breaking-space padding.
- All panel rows have stable equal lengths.
- Box drawing uses only `╔`, `═`, `╗`, `║`, `╚` and `╝`.
- Ordinary and special panels are adjacent sibling blocks in one control container.
- CSS-disabled representative pages retain readable text, ordinary anchors and return routes.
- JavaScript is not required for reading or navigation.
- The favicon rendition contains no image, canvas or script element.

### Render validation — PASS

Chromium rendered representative normal, new-sector, BSOD, Turbo-BSOD, safe-return and favicon pages at 1440, 390, 240 and 176 CSS pixels.

- 1440 and 390 px: ordinary and POWER/TURBO panels remain side by side.
- 240 and 176 px: panels deliberately stack because horizontal presentation is no longer practical.
- No representative route has horizontal document overflow at any tested width.
- The safe-return screen remains centred and bright W95 orange.
- The text-only favicon scales to the narrow viewports and preserves the centred `ARCHIVO 21` return footnote.

### Full-site public-copy audit — PASS

The existing presentation-filler rules pass for `lorem ipsum`, `placeholder text`, `example text`, `replace me`, `insert ... here`, `coming soon`, unclassified `placeholder` and unclassified `TODO`, while retaining the already approved documentary exceptions.

## Known limitation

The render harness in this recovery environment embedded the current stylesheet into each page because local loopback navigation is administratively blocked. Layout, typography, backgrounds declared in HTML, link structure and responsive geometry were validated; the public post-deployment check remains the authority for actual hostname asset loading and Tiny-Tile delivery.
