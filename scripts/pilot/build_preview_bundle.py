#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import math
import subprocess
from dataclasses import dataclass
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont


FPS = 30
WIDTH = 1280
HEIGHT = 720
TRANSITION_SEC = 0.2


@dataclass
class SceneSpec:
    scene_id: str
    input_path: Path
    duration_sec: float
    trim_start_sec: float = 0.0
    trim_end_sec: float | None = None


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def timecode(sec: float) -> str:
    total_ms = int(round(sec * 1000))
    ms = total_ms % 1000
    total_s = total_ms // 1000
    s = total_s % 60
    total_m = total_s // 60
    m = total_m % 60
    h = total_m // 60
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def extract_frame(ffmpeg: str, input_path: Path, time_sec: float, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            ffmpeg,
            "-y",
            "-ss",
            f"{time_sec:.3f}",
            "-i",
            str(input_path),
            "-frames:v",
            "1",
            "-update",
            "1",
            "-q:v",
            "2",
            str(output_path),
        ]
    )


def make_contact_sheet(title: str, frames: list[tuple[str, Path]], output_path: Path) -> None:
    thumb_w, thumb_h = 320, 180
    cols = 3
    rows = math.ceil(len(frames) / cols)
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


def build_preview(ffmpeg: str, episode_dir: Path, preview_path: Path) -> list[tuple[str, float, float]]:
    opening = episode_dir.parent.parent / "characters" / "daehan" / "01_Opening.mp4"
    ending = episode_dir.parent.parent / "characters" / "daehan" / "02_Ending.mp4"
    picture_dir = episode_dir / "renders" / "picture"

    scene_specs = [
        SceneSpec("scene-0-opening", opening, 3.0, trim_start_sec=0.0, trim_end_sec=3.0),
        SceneSpec("scene-1-situation", picture_dir / "scene-1-situation.mp4", 5.0),
        SceneSpec("scene-2-climax", picture_dir / "scene-2-climax.mp4", 4.0),
        SceneSpec("scene-3-question", picture_dir / "scene-3-question.mp4", 7.0),
        SceneSpec("scene-4-reveal-repeat", picture_dir / "scene-4-reveal-repeat.mp4", 7.0),
        SceneSpec("scene-5-ending", ending, 4.0, trim_start_sec=0.0, trim_end_sec=4.0),
    ]

    for spec in scene_specs:
        if not spec.input_path.exists():
            raise FileNotFoundError(f"Missing input clip: {spec.input_path}")

    filter_parts: list[str] = []
    input_args: list[str] = []
    ranges: list[tuple[str, float, float]] = []
    cursor = 0.0

    content_scene_count = 0
    for idx, spec in enumerate(scene_specs):
        input_args.extend(["-i", str(spec.input_path)])
        label = f"v{idx}"
        trim_end = spec.trim_end_sec if spec.trim_end_sec is not None else spec.duration_sec
        filter_parts.append(
            f"[{idx}:v]trim=start={spec.trim_start_sec}:end={trim_end},"
            f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
            f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2,setsar=1,setpts=PTS-STARTPTS[{label}]"
        )
        start = cursor
        end = cursor + spec.duration_sec
        cursor = end

        if spec.scene_id == "scene-0-opening":
            end += TRANSITION_SEC
            cursor = end
        if spec.scene_id == "scene-4-reveal-repeat":
            end += TRANSITION_SEC
            cursor = end

        ranges.append((spec.scene_id, start, end))
        content_scene_count += 1

    opening_black_label = "black_open"
    ending_black_label = "black_end"
    filter_parts.append(f"color=c=black:s={WIDTH}x{HEIGHT}:d={TRANSITION_SEC}[{opening_black_label}]")
    filter_parts.append(f"color=c=black:s={WIDTH}x{HEIGHT}:d={TRANSITION_SEC}[{ending_black_label}]")

    concat_labels = ["[v0]", f"[{opening_black_label}]", "[v1]", "[v2]", "[v3]", "[v4]", f"[{ending_black_label}]", "[v5]"]
    filter_parts.append("".join(concat_labels) + f"concat=n={len(concat_labels)}:v=1:a=0[outv]")

    preview_path.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            ffmpeg,
            "-y",
            *input_args,
            "-filter_complex",
            ";".join(filter_parts),
            "-map",
            "[outv]",
            "-r",
            str(FPS),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            "-an",
            str(preview_path),
        ]
    )
    return ranges


def write_review_metadata(review_dir: Path, ranges: list[tuple[str, float, float]]) -> None:
    review_dir.mkdir(parents=True, exist_ok=True)
    with (review_dir / "scene-ranges.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["scene_id", "start_sec", "end_sec", "start_frame", "end_frame"])
        for scene_id, start, end in ranges:
            start_frame = int(round(start * FPS))
            end_frame = int(round(end * FPS)) - 1
            writer.writerow([scene_id, f"{start:.3f}", f"{end:.3f}", start_frame, end_frame])

    total_duration = ranges[-1][2]
    with (review_dir / "frame-map.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["frame_index", "time_sec", "timecode", "scene_id"])
        total_frames = int(round(total_duration * FPS))
        for frame_index in range(total_frames):
            sec = frame_index / FPS
            scene_id = ranges[-1][0]
            for candidate_scene_id, start, end in ranges:
                if start <= sec < end:
                    scene_id = candidate_scene_id
                    break
            writer.writerow([frame_index, f"{sec:.3f}", timecode(sec), scene_id])


def sample_times(duration_sec: float, count: int = 6) -> list[float]:
    return [duration_sec * (idx + 0.5) / count for idx in range(count)]


def build_contact_sheets(ffmpeg: str, episode_dir: Path) -> None:
    review_dir = episode_dir / "review"
    contact_dir = review_dir / "contact-sheets"
    frame_dir = review_dir / "frames"
    contact_dir.mkdir(parents=True, exist_ok=True)
    frame_dir.mkdir(parents=True, exist_ok=True)

    scene_sources = [
        ("scene-0-opening", episode_dir.parent.parent / "characters" / "daehan" / "01_Opening.mp4", 3.0),
        ("scene-1-situation", episode_dir / "renders" / "picture" / "scene-1-situation.mp4", 5.0),
        ("scene-2-climax", episode_dir / "renders" / "picture" / "scene-2-climax.mp4", 4.0),
        ("scene-3-question", episode_dir / "renders" / "picture" / "scene-3-question.mp4", 7.0),
        ("scene-4-reveal-repeat", episode_dir / "renders" / "picture" / "scene-4-reveal-repeat.mp4", 7.0),
        ("scene-5-ending", episode_dir.parent.parent / "characters" / "daehan" / "02_Ending.mp4", 4.0),
    ]

    overview_frames: list[tuple[str, Path]] = []

    for scene_id, input_path, duration_sec in scene_sources:
        frames: list[tuple[str, Path]] = []
        for idx, sec in enumerate(sample_times(duration_sec)):
            frame_path = frame_dir / f"{scene_id}-{idx + 1}.jpg"
            extract_frame(ffmpeg, input_path, sec, frame_path)
            frames.append((f"{scene_id} / {sec:.2f}s", frame_path))
        make_contact_sheet(scene_id, frames, contact_dir / f"{scene_id}.jpg")

        center_idx = len(frames) // 2
        overview_frames.append((scene_id, frames[center_idx][1]))

    make_contact_sheet("overview", overview_frames, contact_dir / "overview.jpg")

    readme = review_dir / "README.md"
    readme.write_text(
        "# Review Bundle\n\n"
        "- `scene-ranges.csv`: preview cut 기준 씬 구간\n"
        "- `frame-map.csv`: 30fps 기준 프레임 매핑\n"
        "- `contact-sheets/*.jpg`: 씬별 contact sheet와 overview\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a preview cut and review bundle for a Daehan pilot episode.")
    parser.add_argument("--episode-dir", required=True, help="Episode directory")
    args = parser.parse_args()

    episode_dir = Path(args.episode_dir).resolve()
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    preview_path = episode_dir / "renders" / "final" / f"{episode_dir.name}-preview-cut.mp4"
    ranges = build_preview(ffmpeg, episode_dir, preview_path)
    write_review_metadata(episode_dir / "review", ranges)
    build_contact_sheets(ffmpeg, episode_dir)
    print(preview_path)
    print(episode_dir / "review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
