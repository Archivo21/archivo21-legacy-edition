#!/usr/bin/env python3
"""Build and validate Archivo 21's static Legacy Edition.

The published HTML already records its reviewed Tiny-Tile Galaxy assignment.
This builder copies that exact source state to ``_site`` and rejects any
release that breaks the asset bank, the Compiler background contract, local
links, or click-only reachability from the homepage.

No third-party Python packages are required.
"""

from __future__ import annotations

import argparse
from collections import deque
import hashlib
from pathlib import Path
import re
import shutil
import struct
import sys
from typing import Iterable
from urllib.parse import unquote, urlsplit

BANK_SIZE = 256
TILE_WIDTH = 8
TILE_HEIGHT = 8
MAX_GIF_BYTES = 160
EXCLUDED_TOP_LEVEL = {".git", ".github", "_site", "scripts"}

ATTR_RE = re.compile(
    r"""(?P<name>href|src|background)\s*=\s*(?P<quote>["'])(?P<value>.*?)(?P=quote)""",
    re.IGNORECASE | re.DOTALL,
)
BODY_RE = re.compile(r"<body\b[^>]*>", re.IGNORECASE | re.DOTALL)
CLASS_RE = re.compile(r"""\bclass\s*=\s*(["'])(.*?)\1""", re.IGNORECASE | re.DOTALL)
BG_COLOUR_RE = re.compile(r"""\bbgcolor\s*=\s*(["'])(.*?)\1""", re.IGNORECASE)
BACKGROUND_RE = re.compile(r"""\bbackground\s*=""", re.IGNORECASE)
GALAXY_RE = re.compile(r"^/tiles/galaxy/tile-(\d{3})\.gif$")
PLACEHOLDER_RE = re.compile(
    r"\b(lorem ipsum|placeholder text|example text|sample copy|dummy text|"
    r"your text here|replace me|coming soon)\b",
    re.IGNORECASE,
)

STANDARD_SCAFFOLD = {
    "path": "scaffold/releases/0.1.0-alpha.1/download.zip",
    "bytes": 50169,
    "sha256": "f34eb9aae666bbd5f961c602f6e7c882a628931d9935dee9ba355c8002f60bc8",
}
FLOPPY_SCAFFOLD = {
    "path": "scaffold/releases/0.1.0-alpha.1/download-floppy.zip",
    "bytes": 49524,
    "sha256": "36f3fee1a87b65abffd9dcec8421f20313f55ac9a1efd5d30598fffcdbd61c2e",
}

BASE_COLOURS: tuple[tuple[int, int, int], ...] = (
    (33, 28, 20), (29, 34, 33), (26, 35, 28), (31, 27, 38),
    (37, 28, 27), (30, 31, 42), (38, 34, 25), (24, 34, 40),
    (35, 30, 23), (31, 38, 30), (37, 31, 42), (40, 30, 30),
    (28, 38, 39), (42, 36, 28), (32, 33, 29), (27, 29, 34),
)


def clamp(value: int) -> int:
    return max(0, min(255, value))


def palette_for(index: int) -> list[tuple[int, int, int]]:
    family = index >> 4
    variant = index & 0x0F
    red, green, blue = BASE_COLOURS[family]
    drift = ((variant * 5) % 9) - 4
    base = (
        clamp(red + drift),
        clamp(green + drift),
        clamp(blue + drift),
    )
    return [
        base,
        (clamp(base[0] + 7), clamp(base[1] + 6), clamp(base[2] + 5)),
        (clamp(base[0] + 13), clamp(base[1] + 11), clamp(base[2] + 9)),
        (clamp(base[0] - 5), clamp(base[1] - 4), clamp(base[2] - 3)),
    ]


def pixel_pattern(index: int) -> list[int]:
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
                value = (
                    1
                    if x % 4 == family % 4 and y % 4 == (family // 2) % 4
                    else 0
                )
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
    palette = palette_for(index)
    codes: list[int] = []
    for pixel in pixel_pattern(index):
        codes.extend((4, pixel))
    codes.append(5)
    compressed = pack_lsb_codes(codes, 3)

    payload = bytearray(b"GIF89a")
    payload.extend(TILE_WIDTH.to_bytes(2, "little"))
    payload.extend(TILE_HEIGHT.to_bytes(2, "little"))
    payload.extend((0xF1, 0x00, 0x00))
    for colour in palette:
        payload.extend(colour)
    payload.extend((0x2C, 0, 0, 0, 0))
    payload.extend(TILE_WIDTH.to_bytes(2, "little"))
    payload.extend(TILE_HEIGHT.to_bytes(2, "little"))
    payload.extend((0x00, 0x02))
    for start in range(0, len(compressed), 255):
        block = compressed[start:start + 255]
        payload.append(len(block))
        payload.extend(block)
    payload.extend((0x00, 0x3B))
    return bytes(payload)


def write_gif_bank(root: Path) -> None:
    tile_dir = root / "tiles" / "galaxy"
    tile_dir.mkdir(parents=True, exist_ok=True)
    for index in range(BANK_SIZE):
        (tile_dir / f"tile-{index:03d}.gif").write_bytes(gif_bytes(index))


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


def page_route(page: Path, root: Path) -> str:
    relative = page.relative_to(root).as_posix()
    if relative == "index.html":
        return "/"
    if relative.endswith("/index.html"):
        return "/" + relative[: -len("index.html")]
    return "/" + relative


def resolved_target(root: Path, page: Path, raw_value: str) -> Path | None:
    value = raw_value.strip()
    if not value or value.startswith(("#", "//")):
        return None
    split = urlsplit(value)
    if split.scheme or split.netloc:
        return None
    path_text = unquote(split.path)
    if not path_text:
        return None
    if path_text.startswith("/"):
        candidate = root / path_text.lstrip("/")
    else:
        candidate = page.parent / path_text
    candidate = candidate.resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError(
            f"{page.relative_to(root)} links outside the site: {raw_value}"
        ) from exc
    if path_text.endswith("/") or candidate.is_dir():
        candidate = candidate / "index.html"
    elif not candidate.exists() and not candidate.suffix:
        candidate = candidate / "index.html"
    return candidate


def body_attributes(page: Path, root: Path) -> tuple[str, set[str], str | None, str | None]:
    text = page.read_text(encoding="utf-8")
    match = BODY_RE.search(text)
    if not match:
        raise ValueError(f"No <body> element in {page.relative_to(root)}")
    body = match.group(0)
    class_match = CLASS_RE.search(body)
    classes = set(class_match.group(2).split()) if class_match else set()
    colour_match = BG_COLOUR_RE.search(body)
    colour = colour_match.group(2).lower() if colour_match else None
    background = None
    for attr in ATTR_RE.finditer(body):
        if attr.group("name").lower() == "background":
            background = attr.group("value")
            break
    return text, classes, colour, background


def validate_gif_bank(root: Path) -> tuple[dict[int, str], int]:
    tile_dir = root / "tiles" / "galaxy"
    expected = {f"tile-{index:03d}.gif" for index in range(BANK_SIZE)}
    actual = {path.name for path in tile_dir.glob("tile-*.gif")}
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ValueError(f"Galaxy bank mismatch; missing={missing}, extra={extra}")

    hashes: dict[int, str] = {}
    maximum_size = 0
    for index in range(BANK_SIZE):
        path = tile_dir / f"tile-{index:03d}.gif"
        data = path.read_bytes()
        maximum_size = max(maximum_size, len(data))
        if not data.startswith((b"GIF87a", b"GIF89a")) or len(data) < 10:
            raise ValueError(f"Invalid GIF data: {path.relative_to(root)}")
        width, height = struct.unpack("<HH", data[6:10])
        if (width, height) != (TILE_WIDTH, TILE_HEIGHT):
            raise ValueError(
                f"Wrong tile dimensions in {path.relative_to(root)}: "
                f"{width}x{height}"
            )
        if len(data) > MAX_GIF_BYTES:
            raise ValueError(
                f"Oversized Galaxy tile {path.relative_to(root)}: {len(data)} bytes"
            )
        hashes[index] = hashlib.sha256(data).hexdigest()
    if len(set(hashes.values())) != BANK_SIZE:
        raise ValueError("Galaxy bank contains duplicate GIF files")
    return hashes, maximum_size


def validate_scaffold_download(root: Path, record: dict[str, object]) -> None:
    path = root / str(record["path"])
    if not path.is_file():
        raise ValueError(f"Missing Scaffold package: {path.relative_to(root)}")
    data = path.read_bytes()
    if len(data) != record["bytes"]:
        raise ValueError(f"Unexpected Scaffold package size: {path.relative_to(root)}")
    if hashlib.sha256(data).hexdigest() != record["sha256"]:
        raise ValueError(f"Unexpected Scaffold checksum: {path.relative_to(root)}")


def validate_compiler_backgrounds(root: Path) -> None:
    compiler_root = root / "compiler"
    for page in sorted(compiler_root.rglob("*.html")):
        _, classes, colour, background = body_attributes(page, root)
        relative = page.relative_to(root)
        if "blue-screen-page" in classes:
            if colour != "#0000aa" or background is not None:
                raise ValueError(
                    f"BSOD must be untextured #0000aa blue: {relative}"
                )
        elif {"logo-screen-page", "power-screen-page"} & classes:
            if colour != "#000000" or background is not None:
                raise ValueError(
                    f"Compiler Easter-egg state must be untextured black: {relative}"
                )
        else:
            galaxy_match = GALAXY_RE.match(background or "")
            approved_galaxy_scanline = (
                galaxy_match is not None and int(galaxy_match.group(1)) % 16 == 4
            )
            if background != "/tiles/compiler-a.gif" and not approved_galaxy_scanline:
                raise ValueError(
                    f"Compiler page must use a terminal/CRT scanline tile: {relative}"
                )


def validate_site(root: Path) -> tuple[int, int, int]:
    pages = sorted(root.rglob("*.html"), key=lambda path: path.relative_to(root).as_posix())
    if not pages:
        raise ValueError("No HTML pages found")
    page_set = set(pages)
    edges: dict[Path, set[Path]] = {page: set() for page in pages}
    galaxy_assignments: dict[int, Path] = {}

    for page in pages:
        text, _, _, background = body_attributes(page, root)
        placeholder = PLACEHOLDER_RE.search(text)
        if placeholder:
            raise ValueError(
                f"Placeholder-like copy '{placeholder.group(0)}' in "
                f"{page.relative_to(root)}"
            )
        galaxy_match = GALAXY_RE.match(background or "")
        if galaxy_match:
            index = int(galaxy_match.group(1))
            if index in galaxy_assignments:
                raise ValueError(
                    f"Galaxy tile {index:03d} is assigned twice: "
                    f"{galaxy_assignments[index].relative_to(root)} and "
                    f"{page.relative_to(root)}"
                )
            galaxy_assignments[index] = page

        for attr in ATTR_RE.finditer(text):
            target = resolved_target(root, page, attr.group("value"))
            if target is None:
                continue
            if not target.exists():
                raise ValueError(
                    f"Broken local {attr.group('name')} in {page.relative_to(root)}: "
                    f"{attr.group('value')}"
                )
            if attr.group("name").lower() == "href" and target in page_set:
                edges[page].add(target)

    home = root / "index.html"
    if home not in page_set:
        raise ValueError("Homepage is missing")
    home_text, _, _, home_background = body_attributes(home, root)
    if home_background != "/tiles/home.gif":
        raise ValueError("Homepage must retain /tiles/home.gif")
    for route in ("/scaffold", "/compiler", "/index", "/www"):
        if f'href="{route}"' not in home_text and f'href="{route}/"' not in home_text:
            raise ValueError(f"Homepage does not link directly to {route}")

    reached = {home}
    queue = deque([home])
    while queue:
        current = queue.popleft()
        for target in edges[current]:
            if target not in reached:
                reached.add(target)
                queue.append(target)
    unreachable = sorted(
        (page.relative_to(root).as_posix() for page in page_set - reached)
    )
    if unreachable:
        raise ValueError(
            "Pages not reachable by click from the homepage: " + ", ".join(unreachable)
        )

    www = (root / "www" / "index.html").read_text(encoding="utf-8")
    content_match = re.search(
        r"<div id=\"main\">(.*?)</div>\s*<div id=\"foot\">",
        www,
        re.IGNORECASE | re.DOTALL,
    )
    if not content_match:
        raise ValueError("Could not identify /www content")
    object_links = re.findall(
        r"^      <p><a\s+href=",
        content_match.group(1),
        re.IGNORECASE | re.MULTILINE,
    )
    if len(object_links) != 15:
        raise ValueError(f"/www must contain exactly 15 object links, found {len(object_links)}")
    for required in ('href="/scaffold"', 'href="https://web.archivo21.org/"'):
        if required not in content_match.group(1):
            raise ValueError(f"/www is missing required link {required}")

    scaffold = (root / "scaffold" / "index.html").read_text(encoding="utf-8")
    for required in (
        STANDARD_SCAFFOLD["path"],
        FLOPPY_SCAFFOLD["path"],
        "/scaffold/process",
        "/scaffold/releases/0.1.0-alpha.1",
    ):
        if str(required) not in scaffold:
            raise ValueError(f"Scaffold page is missing {required}")

    validate_compiler_backgrounds(root)
    return len(pages), len(galaxy_assignments), len(reached)


def write_build_records(
    output: Path,
    pages: int,
    galaxy_assignments: int,
    reached: int,
    hashes: dict[int, str],
    maximum_size: int,
) -> None:
    tile_dir = output / "tiles" / "galaxy"
    manifest_rows = ["page\ttile\ttheme\ttile_sha256"]
    for page in sorted(output.rglob("*.html")):
        _, classes, _, background = body_attributes(page, output)
        match = GALAXY_RE.match(background or "")
        if not match:
            continue
        index = int(match.group(1))
        theme = next(
            (token.removeprefix("theme-") for token in classes if token.startswith("theme-")),
            "compiler",
        )
        manifest_rows.append(
            f"{page.relative_to(output).as_posix()}\t{index:03d}\t"
            f"{theme}\t{hashes[index]}"
        )
    (tile_dir / "assignments.tsv").write_text(
        "\n".join(manifest_rows) + "\n", encoding="utf-8"
    )
    (tile_dir / "README.txt").write_text(
        "Archivo 21 Tiny-Tile Galaxy\n"
        "================================\n"
        f"Bank size: {BANK_SIZE} unique static GIF tiles\n"
        f"Tile dimensions: {TILE_WIDTH}x{TILE_HEIGHT} pixels\n"
        f"HTML pages in this build: {pages}\n"
        f"Pages using unique Galaxy assignments: {galaxy_assignments}\n"
        "The homepage retains its original tile. Compiler screen-state\n"
        "exceptions use reviewed scanline, plain-blue, or plain-black\n"
        "backgrounds. Each ordinary browser load requests only its assigned\n"
        "microscopic tile.\n",
        encoding="utf-8",
    )
    report = (
        "LEGACY EDITION BUILD: PASS\n"
        f"HTML pages: {pages}\n"
        f"Click-reachable from homepage: {reached}\n"
        f"GIF bank: {BANK_SIZE}\n"
        f"Unique Galaxy assignments in use: {galaxy_assignments}\n"
        f"Maximum Galaxy GIF bytes: {maximum_size}\n"
        "Compiler backgrounds: CRT/scanline normal; plain blue BSOD; "
        "plain black Easter egg\n"
        "Scaffold packages: standard and floppy-friendly verified\n"
    )
    (output / "TINY-TILE-GALAXY-BUILD.txt").write_text(report, encoding="utf-8")
    print(report, end="")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, default=Path("_site"))
    args = parser.parse_args()

    source = args.source.resolve()
    output = args.output.resolve()
    if source == output:
        parser.error("source and output must be different directories")

    copy_source(source, output)
    write_gif_bank(output)
    hashes, maximum_size = validate_gif_bank(output)
    validate_scaffold_download(output, STANDARD_SCAFFOLD)
    validate_scaffold_download(output, FLOPPY_SCAFFOLD)
    pages, galaxy_assignments, reached = validate_site(output)
    write_build_records(
        output,
        pages,
        galaxy_assignments,
        reached,
        hashes,
        maximum_size,
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"LEGACY EDITION BUILD: FAIL: {exc}", file=sys.stderr)
        raise
