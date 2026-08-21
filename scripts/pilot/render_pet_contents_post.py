#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


REPO_ROOT = Path(__file__).resolve().parents[2]
TARGET_DURATION_SEC = 30.0
FPS = 30
CANVAS_W = 1080
CANVAS_H = 1920
EDGE_TTS_VOICE = "ko-KR-SunHiNeural"


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def capture(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True).strip()


def ffprobe_duration(path: Path) -> float:
    raw = capture([
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=nw=1:nk=1",
        str(path),
    ])
    return float(raw)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def ffmpeg_text_escape(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace("'", r"\'")
        .replace(":", r"\:")
        .replace("%", r"\%")
    )


def ensure_guide_dub(episode_dir: Path, voice_slots: dict, *, force: bool) -> list[dict]:
    guide_dir = episode_dir / "renders" / "dub-lock" / "narration-guide"
    selected_dir = episode_dir / "renders" / "dub-lock" / "narration-selected"
    guide_dir.mkdir(parents=True, exist_ok=True)
    selected_dir.mkdir(parents=True, exist_ok=True)

    rendered: list[dict] = []
    for slot in voice_slots.get("slots", []):
        slot_id = slot["voiceSlotId"]
        text = slot["text"]
        guide_path = guide_dir / f"{slot_id}.mp3"
        selected_path = selected_dir / f"{slot_id}.mp3"
        if force or not guide_path.exists():
            run([
                "python3",
                "-m",
                "edge_tts",
                "--voice",
                EDGE_TTS_VOICE,
                "--rate",
                "+8%",
                "--text",
                text,
                "--write-media",
                str(guide_path),
            ])
        shutil.copyfile(guide_path, selected_path)
        duration = ffprobe_duration(selected_path)
        planned_duration = float(slot.get("plannedDurationSec") or duration)
        tempo = max(0.5, min(2.0, duration / planned_duration)) if planned_duration > 0 else 1.0
        rendered.append({
            "slot": slot,
            "path": selected_path,
            "durationSec": duration,
            "tempo": tempo,
        })
    return rendered


def scene_ranges(episode_dir: Path) -> list[dict]:
    ranges: list[dict] = []
    start = 0.0
    for index in range(1, 11):
        scene_id = f"scene-{index:02d}"
        clip = episode_dir / "renders" / "picture" / f"{scene_id}.mp4"
        duration = ffprobe_duration(clip)
        end = start + duration
        if index == 10:
            end = TARGET_DURATION_SEC
        ranges.append({
            "sceneId": scene_id,
            "startSec": round(start, 3),
            "endSec": round(end, 3),
            "durationSec": round(end - start, 3),
            "sourcePath": str(clip.relative_to(REPO_ROOT)),
        })
        start += duration
    return ranges


def caption_drawtext_filters(typography_slots: dict, font_path: Path) -> list[str]:
    filters: list[str] = []
    for slot in typography_slots.get("slots", []):
        text = ffmpeg_text_escape(slot["text"])
        start = float(slot["plannedInTimeSec"])
        end = min(TARGET_DURATION_SEC, float(slot["plannedOutTimeSec"]))
        preset = slot.get("stylePreset") or "soft-webtoon-subtitle"
        if preset == "comic-pop":
            fontsize = 82
            fontcolor = "0xFFF3A7"
            bordercolor = "0x3A2D12"
            borderw = 8
            y_expr = "h*0.34"
            boxcolor = "black@0.18"
            boxborderw = 20
        else:
            fontsize = 72
            fontcolor = "0xF8F5EC"
            bordercolor = "0x2E2A27"
            borderw = 6
            y_expr = "h-360"
            boxcolor = "black@0.28"
            boxborderw = 24
        filters.append(
            "drawtext="
            f"fontfile='{font_path}':"
            f"text='{text}':"
            f"fontcolor={fontcolor}:"
            f"fontsize={fontsize}:"
            f"borderw={borderw}:"
            f"bordercolor={bordercolor}:"
            f"box=1:"
            f"boxcolor={boxcolor}:"
            f"boxborderw={boxborderw}:"
            "x=(w-text_w)/2:"
            f"y={y_expr}:"
            f"enable='between(t,{start:.3f},{end:.3f})'"
        )
    return filters


def compose_final(
    episode_dir: Path,
    *,
    rendered_audio: list[dict],
    typography_slots: dict,
) -> Path:
    slug = episode_dir.name
    picture_lock = episode_dir / "renders" / "picture-lock" / f"{slug}-picture-lock.mp4"
    output_path = episode_dir / "renders" / "final" / f"{slug}-final-review.mp4"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    picture_duration = ffprobe_duration(picture_lock)
    pad_duration = max(0.0, TARGET_DURATION_SEC - picture_duration)
    font_path = REPO_ROOT / "shared" / "fonts" / "NanumSquareRoundB.ttf"

    inputs = ["-i", str(picture_lock)]
    for audio in rendered_audio:
        inputs.extend(["-i", str(audio["path"])])

    video_chain = (
        f"[0:v]fps={FPS},"
        f"tpad=stop_mode=clone:stop_duration={pad_duration:.3f},"
        f"trim=duration={TARGET_DURATION_SEC:.3f},setpts=PTS-STARTPTS,"
        "split=2[basebg][basefg];"
        f"[basebg]scale={CANVAS_W}:{CANVAS_H}:force_original_aspect_ratio=increase,"
        f"crop={CANVAS_W}:{CANVAS_H},boxblur=24:2[bg];"
        "[basefg]crop=ih*9/16:ih:(iw-ih*9/16)/2:0,"
        f"scale={CANVAS_W}:{CANVAS_H}[fg];"
        "[bg][fg]overlay=0:0[vbase]"
    )

    caption_filters = caption_drawtext_filters(typography_slots, font_path)
    last_label = "vbase"
    caption_chain_parts: list[str] = []
    for index, drawtext in enumerate(caption_filters):
        next_label = f"v{index + 1}"
        caption_chain_parts.append(f"[{last_label}]{drawtext}[{next_label}]")
        last_label = next_label
    if caption_chain_parts:
        caption_chain = ";" + ";".join(caption_chain_parts) + f";[{last_label}]format=yuv420p[vout]"
    else:
        caption_chain = ";[vbase]format=yuv420p[vout]"

    audio_parts = [
        f"anoisesrc=color=pink:duration={TARGET_DURATION_SEC:.3f}:amplitude=0.018,"
        "lowpass=f=950,volume=0.20[amb]",
        f"sine=frequency=392:duration={TARGET_DURATION_SEC:.3f},volume=0.010[pad]",
    ]
    audio_labels = ["[amb]", "[pad]"]
    for index, audio in enumerate(rendered_audio, start=1):
        slot = audio["slot"]
        start_ms = int(round(float(slot.get("plannedStartSec") or 0) * 1000))
        tempo = float(audio["tempo"])
        label = f"n{index}"
        audio_parts.append(
            f"[{index}:a]aresample=44100,atempo={tempo:.5f},"
            f"adelay={start_ms}|{start_ms},volume=1.65[{label}]"
        )
        audio_labels.append(f"[{label}]")
    audio_parts.append(
        "".join(audio_labels)
        + f"amix=inputs={len(audio_labels)}:duration=first:dropout_transition=0:normalize=0,"
        + f"atrim=duration={TARGET_DURATION_SEC:.3f}[aout]"
    )

    filter_complex = video_chain + caption_chain + ";" + ";".join(audio_parts)

    run([
        "ffmpeg",
        "-y",
        *inputs,
        "-filter_complex",
        filter_complex,
        "-map",
        "[vout]",
        "-map",
        "[aout]",
        "-t",
        f"{TARGET_DURATION_SEC:.3f}",
        "-r",
        str(FPS),
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-movflags",
        "+faststart",
        str(output_path),
    ])
    return output_path


def extract_frame(video_path: Path, output_path: Path, time_sec: float) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    run([
        "ffmpeg",
        "-y",
        "-ss",
        f"{time_sec:.3f}",
        "-i",
        str(video_path),
        "-frames:v",
        "1",
        "-update",
        "1",
        "-q:v",
        "2",
        str(output_path),
    ])


def write_review_bundle(
    episode_dir: Path,
    *,
    final_video: Path,
    rendered_audio: list[dict],
    typography_slots: dict,
    ranges: list[dict],
) -> None:
    review_dir = episode_dir / "review" / "final-post"
    frames_dir = review_dir / "frames"
    review_dir.mkdir(parents=True, exist_ok=True)
    frames_dir.mkdir(parents=True, exist_ok=True)

    with (review_dir / "scene-ranges.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["sceneId", "startSec", "endSec", "durationSec", "sourcePath"])
        writer.writeheader()
        writer.writerows(ranges)

    with (review_dir / "frame-map.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["kind", "id", "timeSec", "text"])
        for item in rendered_audio:
            slot = item["slot"]
            writer.writerow(["voice", slot["voiceSlotId"], slot.get("plannedStartSec"), slot.get("text")])
        for slot in typography_slots.get("slots", []):
            writer.writerow(["typography", slot["slotId"], slot.get("plannedInTimeSec"), slot.get("text")])

    thumbs: list[Path] = []
    for item in ranges:
        midpoint = min(float(item["endSec"]) - 0.15, (float(item["startSec"]) + float(item["endSec"])) / 2)
        frame_path = frames_dir / f"{item['sceneId']}-mid.jpg"
        extract_frame(final_video, frame_path, midpoint)
        thumbs.append(frame_path)

    make_contact_sheet(thumbs, review_dir / "contact-sheet.jpg", title=episode_dir.name)

    manifest = {
        "episodeSlug": episode_dir.name,
        "status": "post_review_ready",
        "finalVideo": str(final_video.relative_to(REPO_ROOT)),
        "reviewDir": str(review_dir.relative_to(REPO_ROOT)),
        "durationSec": TARGET_DURATION_SEC,
        "aspectRatio": "9:16",
        "dub": {
            "provider": "edge_tts_guide",
            "voice": EDGE_TTS_VOICE,
            "selectedDir": str((episode_dir / "renders" / "dub-lock" / "narration-selected").relative_to(REPO_ROOT)),
        },
        "typographySlots": [slot["slotId"] for slot in typography_slots.get("slots", [])],
        "publishReady": False,
        "qaRequired": True,
    }
    (review_dir / "final-post-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    (review_dir / "README.md").write_text(
        "\n".join([
            "# Final POST Review Bundle",
            "",
            f"- Final review video: `{final_video.relative_to(REPO_ROOT)}`",
            "- `scene-ranges.csv`: final 30s scene timing map",
            "- `frame-map.csv`: narration and typography timing map",
            "- `contact-sheet.jpg`: scene midpoint overview from the final review export",
            "- `frames/`: scene midpoint stills",
            "- This is a QA handoff, not publish-ready.",
            "",
        ]),
        encoding="utf-8",
    )

    (review_dir / "post-checklist.md").write_text(
        "\n".join([
            "# POST Checklist",
            "",
            "- [x] Picture lock consumed from `renders/picture-lock/`",
            "- [x] Picture held to 30.0s for final reaction readability",
            "- [x] Korean guide narration generated after picture lock",
            "- [x] Typography composited from `typography-slots.json` only",
            "- [x] Generated picture remains text-free before POST overlay",
            "- [x] Light guide ambience/BGM bed mixed under narration",
            "- [x] Review bundle generated for QA",
            "- [ ] QA clearance",
            "- [ ] Publish packet",
            "",
        ]),
        encoding="utf-8",
    )


def make_contact_sheet(frame_paths: list[Path], output_path: Path, *, title: str) -> None:
    thumbs: list[Image.Image] = []
    for path in frame_paths:
        image = Image.open(path).convert("RGB")
        image.thumbnail((220, 391))
        thumbs.append(image.copy())

    cols = 2
    rows = math.ceil(len(thumbs) / cols)
    margin = 24
    label_h = 36
    title_h = 56
    cell_w = 240
    cell_h = 430
    sheet = Image.new("RGB", (cols * cell_w + margin * 2, rows * cell_h + margin * 2 + title_h), "#161616")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(str(REPO_ROOT / "shared" / "fonts" / "NanumGothic-Bold.ttf"), 24)
    small = ImageFont.truetype(str(REPO_ROOT / "shared" / "fonts" / "NanumGothic-Bold.ttf"), 18)
    draw.text((margin, margin), title, font=font, fill="#f4f1ea")
    for index, thumb in enumerate(thumbs):
        row = index // cols
        col = index % cols
        x = margin + col * cell_w + (cell_w - thumb.width) // 2
        y = margin + title_h + row * cell_h
        sheet.paste(thumb, (x, y))
        draw.text((margin + col * cell_w, y + thumb.height + 10), f"scene-{index + 1:02d}", font=small, fill="#f4f1ea")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path, quality=92)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render pet-contents POST guide dub, typography, final review video, and review bundle.")
    parser.add_argument("--episode-dir", required=True)
    parser.add_argument("--force-tts", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    episode_dir = Path(args.episode_dir).resolve()
    voice_slots = load_json(episode_dir / "voice-slots.json")
    typography_slots = load_json(episode_dir / "typography-slots.json")
    rendered_audio = ensure_guide_dub(episode_dir, voice_slots, force=args.force_tts)
    final_video = compose_final(episode_dir, rendered_audio=rendered_audio, typography_slots=typography_slots)
    ranges = scene_ranges(episode_dir)
    write_review_bundle(
        episode_dir,
        final_video=final_video,
        rendered_audio=rendered_audio,
        typography_slots=typography_slots,
        ranges=ranges,
    )
    print(final_video)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
