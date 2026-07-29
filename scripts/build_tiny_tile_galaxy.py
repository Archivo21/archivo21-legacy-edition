#!/usr/bin/env python3
"""Build Archivo 21's deterministic tiny-tile galaxy.

The build copies the static Legacy Edition into an output directory, creates a
bank of 256 microscopic low-contrast GIF tiles, and assigns one tile to every
HTML page. Assignments are deterministic for a given page set. New pages are
automatically assigned an existing tile at build time. When there are no more
unused tiles, deterministic reuse begins and is reported.

No third-party Python packages are required.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re
import shutil
import sys
from typing import Iterable

BANK_SIZE = 256
TILE_WIDTH = 8
TILE_HEIGHT = 8
MAX_GIF_BYTES = 160
BACKGROUND_RE = re.compile(
    r'(<body\b[^>]*?\bbackground\s*=\s*)(["\'])(.*?)(\2)',
    re.IGNORECASE | re.DOTALL,
)
BODY_RE = re.compile(r'<body\b([^>]*)>', re.IGNORECASE | re.DOTALL)
THEME_RE = re.compile(r'\bclass\s*=\s*(["\'])(.*?)\1', re.IGNORECASE | re.DOTALL)

EXCLUDED_TOP_LEVEL = {'.git', '.github', '_site', 'scripts'}

BASE_COLOURS: tuple[tuple[int, int, int], ...] = (
    (33, 28, 20), (29, 34, 33), (26, 35, 28), (31, 27, 38),
    (37, 28, 27), (30, 31, 42), (38, 34, 25), (24, 34, 40),
    (35, 30, 23), (31, 38, 30), (37, 31, 42), (40, 30, 30),
    (28, 38, 39), (42, 36, 28), (32, 33, 29), (27, 29, 34),
)


def clamp(value: int) -> int:
    return max(0, min(255, value))


def palette_for(index: int) -> list[tuple[int, int, int]]:
    """Return four deliberately close colours for a quiet background tile."""
    family = index >> 4
    variant = index & 0x0F
    r, g, b = BASE_COLOURS[family]
    drift = ((variant * 5) % 9) - 4
    base = (clamp(r + drift), clamp(g + drift), clamp(b + drift))
    return [
        base,
        (clamp(base[0] + 7), clamp(base[1] + 6), clamp(base[2] + 5)),
        (clamp(base[0] + 13), clamp(base[1] + 11), clamp(base[2] + 9)),
        (clamp(base[0] - 5), clamp(base[1] - 4), clamp(base[2] - 3)),
    ]


def pixel_pattern(index: int) -> list[int]:
    """Generate an 8x8 four-colour pattern unique to the tile index."""
    variant = index & 0x0F
    family = index >> 4
    pixels: list[int] = []
    for y in range(TILE_HEIGHT):
        for x in range(TILE_WIDTH):
            if variant == 0:
                value = 1 if (x == family % 8 and y == (family * 3) % 8) else 0
            elif variant == 1:
                value = 1 if (x + y + family) % 7 == 0 else 0
            elif variant == 2:
                value = 1 if (x - y - family) % 7 == 0 else 0
            elif variant == 3:
                value = 1 if (x + family) % 4 == 0 else 0
            elif variant == 4:
                value = 1 if (y + family) % 4 == 0 else 0
            elif variant == 5:
                value = 1 if ((x // 2) + (y // 2) + family) % 2 == 0 else 0
            elif variant == 6:
                value = 2 if (x + y + family) % 8 == 0 else 0
            elif variant == 7:
                value = 2 if (x * 3 + y * 5 + family) % 13 == 0 else 0
            elif variant == 8:
                value = 1 if x in ((family + y) % 8, (family - y) % 8) else 0
            elif variant == 9:
                value = 1 if (x % 4 == family % 4 and y % 4 == (family // 2) % 4) else 0
            elif variant == 10:
                value = 2 if ((x ^ y ^ family) & 3) == 0 else 0
            elif variant == 11:
                value = 1 if (x * y + family) % 11 == 0 else 0
            elif variant == 12:
                value = 2 if (x + 2 * y + family) % 9 == 0 else 0
            elif variant == 13:
                value = 1 if (2 * x + y + family) % 9 == 0 else 0
            elif variant == 14:
                value = 3 if (x + y * 3 + family) % 15 == 0 else 0
            else:
                value = ((x + family) // 3 + (y + family) // 3) % 2
            pixels.append(value)
    return pixels


def pack_lsb_codes(codes: Iterable[int], width: int) -> bytes:
    accumulator = 0
    bit_count = 0
    output = bytearray()
    mask = (1 << width) - 1
    for code in codes:
        accumulator |= (code & mask) << bit_count
        bit_count += width
        while bit_count >= 8:
            output.append(accumulator & 0xFF)
            accumulator >>= 8
            bit_count -= 8
    if bit_count:
        output.append(accumulator & 0xFF)
    return bytes(output)


def gif_bytes(index: int) -> bytes:
    """Create a standards-compliant 8x8, four-colour static GIF."""
    palette = palette_for(index)
    pixels = pixel_pattern(index)

    # Minimum LZW code size 2 gives clear=4 and end=5. Clearing before every
    # pixel keeps the code width fixed at three bits and avoids a full encoder.
    codes: list[int] = []
    for pixel in pixels:
        codes.extend((4, pixel))
    codes.append(5)
    compressed = pack_lsb_codes(codes, 3)

    payload = bytearray(b'GIF89a')
    payload.extend(TILE_WIDTH.to_bytes(2, 'little'))
    payload.extend(TILE_HEIGHT.to_bytes(2, 'little'))
    payload.extend((0xF1, 0x00, 0x00))
    for colour in palette:
        payload.extend(colour)
    payload.extend((0x2C,))
    payload.extend((0, 0, 0, 0))
    payload.extend(TILE_WIDTH.to_bytes(2, 'little'))
    payload.extend(TILE_HEIGHT.to_bytes(2, 'little'))
    payload.extend((0x00, 0x02))
    for start in range(0, len(compressed), 255):
        block = compressed[start:start + 255]
        payload.append(len(block))
        payload.extend(block)
    payload.extend((0x00, 0x3B))
    return bytes(payload)


def copy_source(source: Path, output: Path) -> None:
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    for child in source.iterdir():
        if child.name in EXCLUDED_TOP_LEVEL or child == output:
            continue
        target = output / child.name
        if child.is_dir():
            shutil.copytree(child, target)
        else:
            shutil.copy2(child, target)


def page_theme(text: str) -> str:
    body = BODY_RE.search(text)
    if not body:
        return 'unclassified'
    class_match = THEME_RE.search(body.group(1))
    if not class_match:
        return 'unclassified'
    for token in class_match.group(2).split():
        if token.startswith('theme-'):
            return token[6:]
    return 'unclassified'


def assign_tiles(pages: list[Path], root: Path) -> tuple[dict[Path, int], int]:
    assignments: dict[Path, int] = {}
    used: set[int] = set()
    reused = 0
    for page in pages:
        relative = page.relative_to(root).as_posix()
        preferred = int.from_bytes(
            hashlib.sha256(relative.encode('utf-8')).digest()[:2], 'big'
        ) % BANK_SIZE
        if len(used) < BANK_SIZE:
            candidate = preferred
            while candidate in used:
                candidate = (candidate + 1) % BANK_SIZE
            used.add(candidate)
        else:
            candidate = preferred
            reused += 1
        assignments[page] = candidate
    return assignments, reused


def apply_background(page: Path, tile_index: int) -> str:
    text = page.read_text(encoding='utf-8')
    tile_path = f'/tiles/galaxy/tile-{tile_index:03d}.gif'
    if BACKGROUND_RE.search(text):
        text = BACKGROUND_RE.sub(
            lambda match: f'{match.group(1)}{match.group(2)}{tile_path}{match.group(4)}',
            text,
            count=1,
        )
    else:
        body = BODY_RE.search(text)
        if not body:
            raise ValueError(f'No <body> element found in {page}')
        replacement = f'<body{body.group(1)} background="{tile_path}">'
        text = text[:body.start()] + replacement + text[body.end():]
    page.write_text(text, encoding='utf-8')
    return page_theme(text)


def write_bank(output: Path) -> dict[int, str]:
    tile_dir = output / 'tiles' / 'galaxy'
    tile_dir.mkdir(parents=True, exist_ok=True)
    hashes: dict[int, str] = {}
    for index in range(BANK_SIZE):
        data = gif_bytes(index)
        if len(data) > MAX_GIF_BYTES:
            raise ValueError(f'Tile {index} is unexpectedly large: {len(data)} bytes')
        path = tile_dir / f'tile-{index:03d}.gif'
        path.write_bytes(data)
        hashes[index] = hashlib.sha256(data).hexdigest()
    if len(set(hashes.values())) != BANK_SIZE:
        raise ValueError('Generated GIF bank contains duplicate files')
    return hashes


def validate_output(output: Path, pages: list[Path], assignments: dict[Path, int]) -> None:
    pattern = re.compile(
        r'background\s*=\s*(["\'])/tiles/galaxy/tile-(\d{3})\.gif\1',
        re.IGNORECASE,
    )
    for page in pages:
        text = page.read_text(encoding='utf-8')
        match = pattern.search(text)
        if not match:
            raise ValueError(f'No galaxy tile background in {page.relative_to(output)}')
        actual = int(match.group(2))
        if actual != assignments[page]:
            raise ValueError(f'Assignment mismatch for {page.relative_to(output)}')
    if len(pages) <= BANK_SIZE and len(set(assignments.values())) != len(pages):
        raise ValueError('Current HTML pages do not have unique tile assignments')


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=Path('.'))
    parser.add_argument('--output', type=Path, default=Path('_site'))
    args = parser.parse_args()

    source = args.source.resolve()
    output = args.output.resolve()
    if source == output:
        parser.error('source and output must be different directories')

    copy_source(source, output)
    hashes = write_bank(output)
    pages = sorted(
        output.rglob('*.html'),
        key=lambda path: path.relative_to(output).as_posix(),
    )
    if not pages:
        raise ValueError('No HTML pages found')
    assignments, reused = assign_tiles(pages, output)

    manifest_rows = ['page\ttile\ttheme\ttile_sha256']
    for page in pages:
        index = assignments[page]
        theme = apply_background(page, index)
        manifest_rows.append(
            f'{page.relative_to(output).as_posix()}\t{index:03d}\t{theme}\t{hashes[index]}'
        )

    validate_output(output, pages, assignments)

    tile_dir = output / 'tiles' / 'galaxy'
    (tile_dir / 'assignments.tsv').write_text(
        '\n'.join(manifest_rows) + '\n', encoding='utf-8'
    )
    (tile_dir / 'README.txt').write_text(
        'Archivo 21 Tiny-Tile Galaxy\n'
        '================================\n'
        f'Bank size: {BANK_SIZE} static GIF tiles\n'
        f'Tile dimensions: {TILE_WIDTH}x{TILE_HEIGHT} pixels\n'
        f'HTML pages in this build: {len(pages)}\n'
        f'Assignments reused after bank exhaustion: {reused}\n\n'
        'The build assigns tiles deterministically from page paths. Every page\n'
        'receives a unique tile while the page count is at or below 256. New\n'
        'pages are assigned automatically. The images are deliberately static,\n'
        'low-contrast and microscopic so the background does not compete with\n'
        'text and does not materially affect page loading.\n',
        encoding='utf-8',
    )
    maximum_size = max(
        (tile_dir / f'tile-{index:03d}.gif').stat().st_size
        for index in range(BANK_SIZE)
    )
    report = (
        'TINY-TILE GALAXY BUILD: PASS\n'
        f'HTML pages: {len(pages)}\n'
        f'GIF bank: {BANK_SIZE}\n'
        f'Unique current assignments: {len(set(assignments.values()))}\n'
        f'Reused assignments: {reused}\n'
        f'Maximum GIF bytes: {maximum_size}\n'
    )
    (output / 'TINY-TILE-GALAXY-BUILD.txt').write_text(report, encoding='utf-8')
    print(report, end='')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f'TINY-TILE GALAXY BUILD: FAIL: {exc}', file=sys.stderr)
        raise
