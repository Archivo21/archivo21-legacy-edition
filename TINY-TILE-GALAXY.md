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
3. generates the complete 256-tile bank;
4. hashes each page path to select a preferred tile;
5. resolves collisions so every current page is unique while there are no more than 256 pages;
6. replaces or adds the HTML `body background` attribute;
7. writes `tiles/galaxy/assignments.tsv` and a build report;
8. fails the build if files are duplicated, oversized, missing or incorrectly assigned.

A newly created page therefore receives one of the existing 256 backgrounds automatically during the next deployment. Once the site exceeds 256 HTML pages, deterministic reuse begins and is reported rather than silently pretending uniqueness remains possible.

## Loading boundary

The browser does not download all 256 images. It downloads only the one tile referenced by the page being viewed. The complete bank adds roughly 22.5 KB to the deployed archive, while an ordinary page load adds about 88 bytes before protocol overhead and caching.

## Source and deployment boundary

The canonical source remains readable and retains its older theme backgrounds. The generated `_site` deployment receives page-specific galaxy tiles. Historical source pages are therefore not rewritten merely to allocate backgrounds.

The GitHub repository currently functions as the canonical static export and deployment candidate. The custom hostname `web.archivo21.org` has also been recorded as pointing to a separate `chatgpt.site` origin. Repository deployment and custom-domain migration must therefore be verified as distinct operations.
