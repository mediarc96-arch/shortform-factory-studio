#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def make_contact_sheet(title: str, frames: list[tuple[str, Path]], output_path: Path) -> None:
    thumb_w, thumb_h = 320, 180
    cols = 3
    rows = max(1, math.ceil(len(frames) / cols))
    header_h = 44
    label_h = 28
    canvas = Image.new("RGB", (cols * thumb_w, header_h + rows * (thumb_h + label_h)), (18, 18, 18))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    draw.text((12, 12), title, fill=(255, 255, 255), font=font)

    for idx, (label, frame_path) in enumerate(frames):
        row = idx // cols
        col = idx % cols
        x = col * thumb_w
        y = header_h + row * (thumb_h + label_h)
        image = Image.open(frame_path).convert("RGB")
        image = image.resize((thumb_w, thumb_h))
        canvas.paste(image, (x, y))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill=(30, 30, 30))
        draw.text((x + 8, y + thumb_h + 8), label, fill=(240, 240, 240), font=font)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, quality=90)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a keyframe review bundle for daehan-pilot-codex-003.")
    parser.add_argument("--episode-dir", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    episode_dir = Path(args.episode_dir).resolve()
    plan = json.loads((episode_dir / "keyframe-plan.json").read_text(encoding="utf-8"))
    keyframes = plan.get("keyframes") or []
    review_dir = episode_dir / "review"
    contact_dir = review_dir / "contact-sheets"

    frames: list[tuple[str, Path]] = []
    for entry in keyframes:
        output_path = episode_dir / entry["outputPath"]
        if output_path.exists():
            frames.append((entry["id"], output_path))

    if not frames:
        raise FileNotFoundError(f"No generated keyframes found under {episode_dir / 'keyframes'}")

    make_contact_sheet("daehan-pilot-codex-003 keyframes", frames, contact_dir / "overview.jpg")

    review_lines = [
        "# Keyframe Review Report",
        "",
        "- episode: `daehan-pilot-codex-003`",
        "- status: `review-ready`",
        "- basis image: `docs/example/Daehan_2D.jpg`",
        "- clean base: `assets/refs/daehan-2d-clean-base-wide-refined.jpg`",
        "",
        "## Generated Keyframes",
        ""
    ]
    for entry in keyframes:
        review_lines.append(
            f"- `{entry['id']}`: `{entry['purpose']}` -> `{entry['outputPath']}`"
        )
    review_lines.extend(
        [
            "",
            "## Review Checklist",
            ""
        ]
    )
    for item in plan.get("reviewChecklist") or []:
        review_lines.append(f"- {item}")
    review_lines.extend(
        [
            "",
            "## Next Step",
            "",
            "- Approve or reject each keyframe before generating any 6-second scene videos.",
            "- After approval, scene-1 starts from `kf-01`; later scenes start from the previous scene's final frame."
        ]
    )

    review_dir.mkdir(parents=True, exist_ok=True)
    (review_dir / "review-report.md").write_text("\n".join(review_lines) + "\n", encoding="utf-8")
    print(str(review_dir / "review-report.md"))
    print(str(contact_dir / "overview.jpg"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
