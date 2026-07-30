# Legacy Edition public-release record — 2026-07-30

## Classification

Full public-site release affecting content, routes, assets, build validation
and hosting source.

## Pre-change state

- Repository: `Archivo21/archivo21-legacy-edition`
- Branch: `main`
- Commit: `efc77a7`
- Recoverable Git bundle retained for at least 28 days
- Bundle SHA-256:
  `dc6c0336630899f581d678ae501ff0906fb41f8f606f9f764c0d429a54447cd6`

## Release scope

- Import reviewed Compatibility Edition candidate `9c31d8c`.
- Publish 240 ordinary static HTML routes through GitHub Pages.
- Preserve the homepage's original background.
- Install and validate the 256 unique 8×8 Tiny-Tile Galaxy GIFs.
- Enforce CRT/terminal scanlines on normal Compiler routes.
- Enforce untextured blue on BSOD routes and untextured black on Compiler
  logo/POWER routes.
- Present both Scaffold ZIPs, their differences, sizes and SHA-256 checksums.
- Link Scaffold from the homepage and `/www`.
- Keep `/www` at exactly fifteen text-safe objects.
- Provide an A-Z route index and a click path from `/` to every HTML page.
- Use broad public recruitment wording without naming a video-editor role.

## Verification

`python3 scripts/build_tiny_tile_galaxy.py --source . --output _site`
must pass before publication. It verifies the GIF bank, all local targets,
homepage reachability, Compiler backgrounds, Scaffold packages and
placeholder-like interface copy.

The resulting Git commit and GitHub Pages deployment URL are recorded after
publication.
