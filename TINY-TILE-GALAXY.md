# Tiny-Tile Galaxy

## Status

Build-integrated Legacy Edition background system.

## Purpose

Every HTML page receives its own microscopic tiled GIF background without turning the Compatibility Edition into a bandwidth furnace or reducing text and link legibility.

## Design

- 256 static GIF images;
- 8×8 pixels each;
- four deliberately close colours per tile;
- approximately 88 bytes per GIF in the current generator;
- deterministic generation with no external packages;
- one tile request per page;
- no animation, tracking, cookies, remote assets or script dependency.

The visible patterns are intentionally subdued. The readable page surface remains opaque through `#page`, while the tile occupies the outer browser background.

## Assignment rule

At build time, `scripts/build_tiny_tile_galaxy.py`:

1. copies the static source into `_site`;
2. discovers every `.html` file;
3. generates and verifies the complete bank of 256 unique 8×8 GIFs;
4. preserves the reviewed source-level assignment on each page;
5. verifies that ordinary Galaxy assignments are unique;
6. writes `tiles/galaxy/assignments.tsv` and a build report;
7. validates all internal targets and every page's click path from `/`;
8. fails if a tile, route, Scaffold package or Compiler background contract
   has drifted.

New ordinary pages must receive an unused tile in their source HTML. That
assignment becomes part of the reviewed static record rather than an
unreviewed deployment-time rewrite.

## Reviewed exceptions

- `/` retains the original `/tiles/home.gif` background.
- Normal Compiler pages use only the horizontal CRT/terminal scanline family
  or `/tiles/compiler-a.gif`.
- Compiler blue-screen states are solid `#0000aa`, without a GIF.
- The Compiler logo and POWER Easter-egg states are solid black, without a
  GIF.

## Loading boundary

The browser does not download all 256 images. It downloads only the one tile referenced by the page being viewed. The complete bank adds roughly 22.5 KB to the deployed archive, while an ordinary page load adds about 88 bytes before protocol overhead and caching.

## Source and deployment boundary

The public GitHub repository is the canonical static Legacy Edition source.
GitHub Actions validates and copies that exact reviewed source into `_site`,
then GitHub Pages publishes it at `web.archivo21.org`. No ChatGPT Site origin
is part of the production path.
