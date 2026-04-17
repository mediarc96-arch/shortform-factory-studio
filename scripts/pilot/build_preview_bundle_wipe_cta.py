#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import math
import subprocess
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from format_profiles import load_profile_for_episode_schema
from render_daehan_pilot_final import HEIGHT, ROOT, WIDTH, load_json, resolve_ffmpeg_binary


FPS = 30
WIPE_TRANSITION = "wipeleft"


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
        image = Image.open(frame_path).convert("RGB").resize((thumb_w, thumb_h))
        canvas.paste(image, (x, y))
        draw.rectangle((x, y + thumb_h, x + thumb_w, y + thumb_h + label_h), fill=(30, 30, 30))
        draw.text((x + 8, y + thumb_h + 8), label, fill=(240, 240, 240), font=font)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, quality=90)


def sample_times(duration_sec: float, count: int = 6) -> list[float]:
    return [duration_sec * (idx + 0.5) / count for idx in range(count)]


def resolve_scene_specs(episode_dir: Path) -> list[SceneSpec]:
    schema = load_json(episode_dir / "episode.schema.json")
    profile_id, _profile_path, profile = load_profile_for_episode_schema(schema)
    if profile_id != "wipe-cta-v2":
        raise ValueError(f"build_preview_bundle_wipe_cta.py only supports wipe-cta-v2, got {profile_id}")

    transition_sec = float(profile["transitionPolicy"]["openingToContent"]["durationSec"])
    if abs(transition_sec - float(profile["transitionPolicy"]["contentToEnding"]["durationSec"])) > 1e-6:
        raise ValueError("wipe-cta-v2 builder expects equal opening/content and content/ending transition durations")

    opening = ROOT / "characters" / "daehan" / "01_Opening.mp4"
    ending = ROOT / "characters" / "daehan" / "02_Ending.mp4"
    picture_dir = episode_dir / "renders" / "picture"

    return [
        SceneSpec("scene-0-opening", opening, 3.0, trim_start_sec=0.0, trim_end_sec=3.0),
        SceneSpec("scene-1-lesson-intro", picture_dir / "scene-1-lesson-intro.mp4", 5.0),
        SceneSpec("scene-2-guided-repeat", picture_dir / "scene-2-guided-repeat.mp4", 8.0),
        SceneSpec("scene-3-quiz-cta", picture_dir / "scene-3-quiz-cta.mp4", 8.0),
        SceneSpec("scene-4-ending", ending, 4.0, trim_start_sec=0.0, trim_end_sec=4.0),
    ]


def normalize_clip(ffmpeg: str, spec: SceneSpec, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    trim_end = spec.trim_end_sec if spec.trim_end_sec is not None else spec.duration_sec
    run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(spec.input_path),
            "-filter:v",
            (
                f"trim=start={spec.trim_start_sec}:end={trim_end},"
                f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
                f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2,"
                f"fps={FPS},format=yuv420p,settb=AVTB,setsar=1,setpts=PTS-STARTPTS"
            ),
            "-an",
            "-r",
            str(FPS),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(output_path),
        ]
    )


def xfade_pair(ffmpeg: str, left_path: Path, right_path: Path, output_path: Path, *, left_duration: float, transition_sec: float) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    offset = left_duration - transition_sec
    run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(left_path),
            "-i",
            str(right_path),
            "-filter_complex",
            (
                f"[0:v][1:v]xfade=transition={WIPE_TRANSITION}:duration={transition_sec}:offset={offset},"
                f"fps={FPS},format=yuv420p,settb=AVTB[outv]"
            ),
            "-map",
            "[outv]",
            "-an",
            "-r",
            str(FPS),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(output_path),
        ]
    )


def concat_clips(ffmpeg: str, clip_paths: list[Path], output_path: Path) -> None:
    list_file = output_path.with_suffix(".concat.txt")
    list_file.parent.mkdir(parents=True, exist_ok=True)
    list_file.write_text("".join(f"file '{path.as_posix()}'\n" for path in clip_paths), encoding="utf-8")
    run(
        [
            ffmpeg,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_file),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            "-an",
            str(output_path),
        ]
    )


def build_preview(ffmpeg: str, episode_dir: Path, preview_path: Path) -> list[tuple[str, float, float]]:
    schema = load_json(episode_dir / "episode.schema.json")
    _profile_id, _profile_path, profile = load_profile_for_episode_schema(schema)
    wipe_sec = float(profile["transitionPolicy"]["openingToContent"]["durationSec"])
    scene_specs = resolve_scene_specs(episode_dir)

    for spec in scene_specs:
        if not spec.input_path.exists():
            raise FileNotFoundError(f"Missing input clip: {spec.input_path}")

    intermediate_dir = episode_dir / "renders" / "intermediate"
    normalized_paths: list[Path] = []
    for spec in scene_specs:
        normalized_path = intermediate_dir / f"{spec.scene_id}-norm.mp4"
        normalize_clip(ffmpeg, spec, normalized_path)
        normalized_paths.append(normalized_path)

    opening_dur = scene_specs[0].duration_sec
    intro_dur = scene_specs[1].duration_sec
    guided_dur = scene_specs[2].duration_sec
    quiz_dur = scene_specs[3].duration_sec
    ending_dur = scene_specs[4].duration_sec

    opening_intro_path = intermediate_dir / "scene-0-1-wipe.mp4"
    xfade_pair(ffmpeg, normalized_paths[0], normalized_paths[1], opening_intro_path, left_duration=opening_dur, transition_sec=wipe_sec)

    prefix_duration = opening_dur + intro_dur - wipe_sec + guided_dur + quiz_dur
    prefix_path = intermediate_dir / "scene-0-3-prefix.mp4"
    concat_clips(ffmpeg, [opening_intro_path, normalized_paths[2], normalized_paths[3]], prefix_path)

    preview_path.parent.mkdir(parents=True, exist_ok=True)
    xfade_pair(ffmpeg, prefix_path, normalized_paths[4], preview_path, left_duration=prefix_duration, transition_sec=wipe_sec)

    scene_ranges = [
        ("scene-0-opening", 0.0, opening_dur),
        ("scene-1-lesson-intro", opening_dur - wipe_sec, opening_dur - wipe_sec + intro_dur),
        ("scene-2-guided-repeat", opening_dur + intro_dur - wipe_sec, opening_dur + intro_dur - wipe_sec + guided_dur),
        ("scene-3-quiz-cta", opening_dur + intro_dur + guided_dur - wipe_sec, prefix_duration),
        ("scene-4-ending", prefix_duration - wipe_sec, prefix_duration - wipe_sec + ending_dur),
    ]
    return scene_ranges


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
            chosen_scene_id = ranges[0][0]
            for scene_id, start, end in ranges:
                if start <= sec < end:
                    chosen_scene_id = scene_id
            writer.writerow([frame_index, f"{sec:.3f}", timecode(sec), chosen_scene_id])


def build_contact_sheets(ffmpeg: str, episode_dir: Path) -> None:
    review_dir = episode_dir / "review"
    contact_dir = review_dir / "contact-sheets"
    frame_dir = review_dir / "frames"
    contact_dir.mkdir(parents=True, exist_ok=True)
    frame_dir.mkdir(parents=True, exist_ok=True)

    scene_sources = resolve_scene_specs(episode_dir)
    overview_frames: list[tuple[str, Path]] = []

    for spec in scene_sources:
        frames: list[tuple[str, Path]] = []
        for idx, sec in enumerate(sample_times(spec.duration_sec)):
            frame_path = frame_dir / f"{spec.scene_id}-{idx + 1}.jpg"
            extract_frame(ffmpeg, spec.input_path, sec, frame_path)
            frames.append((f"{spec.scene_id} / {sec:.2f}s", frame_path))
        make_contact_sheet(spec.scene_id, frames, contact_dir / f"{spec.scene_id}.jpg")
        overview_frames.append((spec.scene_id, frames[len(frames) // 2][1]))

    make_contact_sheet("overview", overview_frames, contact_dir / "overview.jpg")

    (review_dir / "README.md").write_text(
        "# Review Bundle\n\n"
        "- `scene-ranges.csv`: wipe preview 기준 씬 구간\n"
        "- `frame-map.csv`: 30fps 기준 프레임 매핑\n"
        "- `contact-sheets/*.jpg`: 씬별 contact sheet와 overview\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a wipe-cta preview cut and review bundle.")
    parser.add_argument("--episode-dir", required=True)
    args = parser.parse_args()

    episode_dir = Path(args.episode_dir).resolve()
    ffmpeg = resolve_ffmpeg_binary()

    preview_path = episode_dir / "renders" / "final" / f"{episode_dir.name}-preview-cut.mp4"
    ranges = build_preview(ffmpeg, episode_dir, preview_path)
    write_review_metadata(episode_dir / "review", ranges)
    build_contact_sheets(ffmpeg, episode_dir)
    print(preview_path)
    print(episode_dir / "review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
