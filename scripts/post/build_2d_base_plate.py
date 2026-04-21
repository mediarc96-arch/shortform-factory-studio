#!/usr/bin/env python3
"""Build a clean 1920x1080 2D base plate for pilot-codex-003-A from Daehan_2D.jpg.

Steps:
  1. Load the source illustration (1248x832).
  2. Inpaint the chalkboard Korean/English example text by replacing
     the text region with a nearby empty-chalkboard strip.
  3. Scale to fit height 1080 (yielding ~1620x1080).
  4. Paste onto a 1920x1080 canvas padded on the LEFT with matching
     chalkboard green so the character ends up in the right ~22%.

Idempotent — writes clean-board-base.png under the given episode dir.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def inpaint_board_text(src: Image.Image) -> Image.Image:
    """Overwrite the example-text region with a clean chalkboard strip.

    Strategy: take a thin 20-pixel horizontal strip of clean chalkboard
    immediately above the text block and stretch it vertically to cover
    the text region. This keeps the local lighting/shading of the board
    and avoids pulling in artifacts (chalk tray, frame).
    """
    out = src.copy()
    # Text region bounding box in 1248x832 source (measured visually)
    tx1, ty1, tx2, ty2 = 60, 225, 875, 450
    strip_h_src = 30
    strip_w = tx2 - tx1
    strip = out.crop((tx1, ty1 - strip_h_src - 4, tx2, ty1 - 4))
    tiled = strip.resize((strip_w, ty2 - ty1), Image.LANCZOS)
    out.paste(tiled, (tx1, ty1))
    return out


def build_plate(src: Image.Image) -> Image.Image:
    """Scale to 1080 height and left-pad to 1920 width with chalkboard green."""
    scale = 1080 / src.height
    new_w = int(round(src.width * scale))
    scaled = src.resize((new_w, 1080), Image.LANCZOS)

    # Sample chalkboard green from an empty region of the source (top-left corner).
    bg_color = src.getpixel((30, 30))

    canvas = Image.new("RGB", (1920, 1080), bg_color)
    pad_x = 1920 - new_w
    # Before pasting, build a left filler that matches the chalkboard texture
    # by mirroring a vertical strip from the leftmost columns of the scaled image.
    if pad_x > 0:
        strip_w = min(80, new_w)
        left_strip = scaled.crop((0, 0, strip_w, 1080))
        filler = Image.new("RGB", (pad_x, 1080), bg_color)
        # Tile the strip leftward
        x = pad_x
        while x > 0:
            paste_w = min(strip_w, x)
            piece = left_strip.crop((strip_w - paste_w, 0, strip_w, 1080))
            filler.paste(piece, (x - paste_w, 0))
            x -= paste_w
        canvas.paste(filler, (0, 0))
    canvas.paste(scaled, (pad_x, 0))
    return canvas


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="docs/example/Daehan_2D.jpg")
    ap.add_argument("--episode-dir", default="episodes/daehan-pilot-codex-003-A")
    ap.add_argument("--out-name", default="clean-board-base.png")
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    source_path = (repo_root / args.source).resolve()
    episode_dir = (repo_root / args.episode_dir).resolve()
    assets_dir = episode_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    src = Image.open(source_path).convert("RGB")
    inpainted = inpaint_board_text(src)
    plate = build_plate(inpainted)

    # Also save the intermediate inpainted source for debugging.
    inpainted.save(assets_dir / "source-inpainted.png")
    out_path = assets_dir / args.out_name
    plate.save(out_path)
    print(f"wrote {out_path.relative_to(repo_root)}  ({plate.size[0]}x{plate.size[1]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
