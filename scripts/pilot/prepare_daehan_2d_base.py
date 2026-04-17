#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageFilter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare a rough 16:9 Daehan 2D base plate before xAI refinement.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve()
    img = Image.open(input_path).convert("RGB")

    target_w = args.width
    target_h = args.height
    resized_w = round(img.width * target_h / img.height)
    resized = img.resize((resized_w, target_h), Image.LANCZOS)

    if resized_w >= target_w:
        left = max(0, resized_w - target_w)
        cropped = resized.crop((left, 0, left + target_w, target_h))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cropped.save(output_path, quality=95)
        print(str(output_path))
        return 0

    pad_w = target_w - resized_w
    strip_w = min(160, max(80, resized_w // 8))
    strip = resized.crop((0, 0, strip_w, target_h)).resize((pad_w, target_h), Image.LANCZOS)
    strip = strip.filter(ImageFilter.GaussianBlur(radius=1.5))

    canvas = Image.new("RGB", (target_w, target_h))
    canvas.paste(strip, (0, 0))
    canvas.paste(resized, (pad_w, 0))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, quality=95)
    print(str(output_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
