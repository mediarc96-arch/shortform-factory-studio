#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from ffmpeg_runtime import resolve_ffmpeg_binary


FPS = 30
WIDTH = 1280
HEIGHT = 720


@dataclass
class SceneSpec:
    scene_id: str
    input_path: Path
    duration_sec: float
    trim_start_sec: float = 0.0
    trim_end_sec: float | None = None


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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


def sample_times(duration_sec: float, count: int = 6) -> list[float]:
    if duration_sec <= 0:
        return [0.0]
    return [duration_sec * (idx + 0.5) / count for idx in range(count)]


def resolve_media_path(episode_dir: Path, raw_path: str) -> Path:
    candidate = (episode_dir / raw_path).resolve()
    if candidate.exists():
        return candidate

    repo_candidate = (episode_dir.parent.parent / raw_path).resolve()
    if repo_candidate.exists():
        return repo_candidate

    return candidate


def scene_time_range(scene: dict) -> tuple[float, float | None]:
    if "timeSec" in scene and isinstance(scene["timeSec"], list) and len(scene["timeSec"]) >= 2:
        start = float(scene["timeSec"][0] or 0.0)
        end = float(scene["timeSec"][1] or start)
        return start, end

    start = float(scene.get("startSec") or 0.0)
    duration = scene.get("durationSec")
    if duration is None:
        return start, None
    end = start + float(duration)
    return start, end


def build_scene_specs(episode_dir: Path) -> list[SceneSpec]:
    job = load_json(episode_dir / "video-generation-job.json")
    specs: list[SceneSpec] = []

    opening = (job.get("fixedClips") or {}).get("opening")
    if opening:
        opening_source_raw = str(opening.get("source") or opening.get("sourceFile") or "")
        if not opening_source_raw:
            raise ValueError("fixedClips.opening is missing source/sourceFile")
        trim_start_sec, trim_end_sec = scene_time_range(opening)
        duration_sec = (
            max(trim_end_sec - trim_start_sec, 0.0)
            if trim_end_sec is not None
            else float(opening.get("durationSec") or 0.0)
        )
        specs.append(
            SceneSpec(
                scene_id="scene-0-opening",
                input_path=resolve_media_path(episode_dir, opening_source_raw),
                duration_sec=duration_sec,
                trim_start_sec=trim_start_sec,
                trim_end_sec=trim_end_sec,
            )
        )

    scene_entries = list(job.get("scenes") or [])
    if not scene_entries:
        scene_entries = list(job.get("futureScenes") or [])

    for scene in scene_entries:
        output_raw = scene.get("outputPath") or scene.get("sourceFile")
        if not output_raw:
            raise ValueError(f"Scene {scene.get('sceneId') or '<unknown>'} is missing outputPath/sourceFile")
        trim_start_sec, trim_end_sec = scene_time_range(scene)
        duration_sec = (
            max(trim_end_sec - trim_start_sec, 0.0)
            if trim_end_sec is not None
            else float(scene.get("durationSec") or 0.0)
        )
        specs.append(
            SceneSpec(
                scene_id=str(scene["sceneId"]),
                input_path=resolve_media_path(episode_dir, str(output_raw)),
                duration_sec=duration_sec,
                trim_start_sec=trim_start_sec,
                trim_end_sec=trim_end_sec,
            )
        )

    return specs


def build_preview(ffmpeg: str, specs: list[SceneSpec], preview_path: Path) -> list[tuple[str, float, float]]:
    if not specs:
        raise ValueError("No preview clips found in video-generation-job.json; expected scenes or futureScenes entries.")
    for spec in specs:
        if not spec.input_path.exists():
            raise FileNotFoundError(f"Missing input clip: {spec.input_path}")

    filter_parts: list[str] = []
    input_args: list[str] = []
    ranges: list[tuple[str, float, float]] = []
    cursor = 0.0

    for idx, spec in enumerate(specs):
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
        ranges.append((spec.scene_id, start, end))
        cursor = end

    concat_labels = [f"[v{idx}]" for idx in range(len(specs))]
    filter_parts.append("".join(concat_labels) + f"concat=n={len(specs)}:v=1:a=0[outv]")

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


def build_contact_sheets(ffmpeg: str, review_dir: Path, specs: list[SceneSpec]) -> None:
    contact_dir = review_dir / "contact-sheets"
    frame_dir = review_dir / "frames"
    contact_dir.mkdir(parents=True, exist_ok=True)
    frame_dir.mkdir(parents=True, exist_ok=True)

    overview_frames: list[tuple[str, Path]] = []
    for spec in specs:
        frames: list[tuple[str, Path]] = []
        for idx, sec in enumerate(sample_times(spec.duration_sec)):
            frame_path = frame_dir / f"{spec.scene_id}-{idx + 1}.jpg"
            actual_time = min(sec, max(spec.duration_sec - 0.05, 0.0))
            extract_frame(ffmpeg, spec.input_path, spec.trim_start_sec + actual_time, frame_path)
            frames.append((f"{spec.scene_id} / {actual_time:.2f}s", frame_path))
        make_contact_sheet(spec.scene_id, frames, contact_dir / f"{spec.scene_id}.jpg")
        overview_frames.append((spec.scene_id, frames[len(frames) // 2][1]))

    make_contact_sheet("overview", overview_frames, contact_dir / "overview.jpg")
    (review_dir / "README.md").write_text(
        "# Picture Preview Review Bundle\n\n"
        "- `scene-ranges.csv`: picture preview 기준 씬 구간\n"
        "- `frame-map.csv`: 30fps 기준 프레임 매핑\n"
        "- `contact-sheets/*.jpg`: 씬별 contact sheet와 overview\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a horizontal picture-only preview for a Malmoelab quiz episode.")
    parser.add_argument("--episode-dir", required=True)
    args = parser.parse_args()

    episode_dir = Path(args.episode_dir).resolve()
    slug = episode_dir.name
    ffmpeg = resolve_ffmpeg_binary()
    specs = build_scene_specs(episode_dir)

    preview_path = episode_dir / "renders" / "final" / f"{slug}-picture-preview.mp4"
    picture_lock_path = episode_dir / "renders" / "picture-lock" / f"{slug}-picture-lock.mp4"
    review_dir = episode_dir / "review" / "picture-preview"

    ranges = build_preview(ffmpeg, specs, preview_path)
    picture_lock_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(preview_path, picture_lock_path)
    write_review_metadata(review_dir, ranges)
    build_contact_sheets(ffmpeg, review_dir, specs)

    print(preview_path)
    print(picture_lock_path)
    print(review_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
