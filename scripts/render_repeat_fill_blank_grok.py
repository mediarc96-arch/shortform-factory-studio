#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import math
import os
import re
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


DEFAULT_WIDTH = 1080
DEFAULT_HEIGHT = 1920
FPS = 30
ROOT = Path(__file__).resolve().parents[1]

FONT_REGULAR_CANDIDATES = [
    Path(os.environ.get("SHORTFORM_FONT_REGULAR", "")).expanduser(),
    Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
    Path("/home/kindsr/projects/devscent-inmemorytrip-main/backend/app/infrastructure/pdf/fonts/Pretendard-Regular.otf"),
    Path("/home/kindsr/projects/devscent-atrader/.venv/lib/python3.12/site-packages/pykrx/NanumBarunGothic.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
]
FONT_BOLD_CANDIDATES = [
    Path(os.environ.get("SHORTFORM_FONT_BOLD", "")).expanduser(),
    Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"),
    Path("/home/kindsr/projects/devscent-inmemorytrip-main/backend/app/infrastructure/pdf/fonts/Pretendard-Bold.otf"),
    Path("/home/kindsr/projects/devscent-atrader/.venv/lib/python3.12/site-packages/pykrx/NanumBarunGothic.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
]
FFMPEG_CANDIDATES = [
    Path(os.environ.get("SHORTFORM_FFMPEG", "")).expanduser(),
    Path("/tmp/paperclip-ffmpeg/node_modules/ffmpeg-static/ffmpeg"),
    Path("/tmp/shortform-factory-bin/ffmpeg"),
]

SCENES = [
    {"id": "scene-0-opening", "source": "opening", "start": 0.0, "end": 3.0},
    {"id": "scene-1-question", "source": "grok", "start": 3.0, "end": 6.0},
    {"id": "scene-2-thinking", "source": "grok", "start": 6.0, "end": 11.0},
    {"id": "scene-3-answer", "source": "grok", "start": 11.0, "end": 16.0},
    {"id": "scene-4-repeat", "source": "grok", "start": 16.0, "end": 28.0},
    {"id": "scene-5-outro", "source": "grok", "start": 28.0, "end": 30.0},
]


def clone_default_scenes() -> list[dict]:
    return [dict(scene) for scene in SCENES]


def resolve_project_path(raw_path: str | None, *, base_dir: Path | None = None) -> Path | None:
    if not str(raw_path or "").strip():
        return None
    path = Path(str(raw_path))
    if path.is_absolute():
        return path
    candidates = []
    if base_dir is not None:
        candidates.append((base_dir / path).resolve())
    candidates.append((ROOT / path).resolve())
    for candidate in candidates:
        if candidate.exists():
            return candidate
    if base_dir is not None:
        return (base_dir / path).resolve()
    return (ROOT / path).resolve()


def load_episode_job(source_packet_path: Path) -> dict:
    job_path = source_packet_path.parent / "video-generation-job.json"
    if job_path.is_file():
        return load_json(job_path)
    return {}


def parse_scene_times(value: list | tuple) -> tuple[float, float]:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError(f"Invalid timeSec range: {value!r}")
    return float(value[0]), float(value[1])


def build_scene_timeline(job: dict) -> list[dict]:
    scenes = []
    for raw_scene in job.get("scenes", []):
        start, end = parse_scene_times(raw_scene.get("timeSec"))
        scene_duration = max(0.1, end - start)
        output_file = raw_scene.get("outputFile") or raw_scene.get("generateOnce", {}).get("outputFile") or f"./renders/grok/{raw_scene['sceneId']}.mp4"
        scene_type = str(raw_scene.get("type") or "")
        if scene_type == "fixed_clip" and raw_scene.get("sceneId") == "scene-0-opening":
            source = "opening"
        elif scene_type == "fixed_clip" or raw_scene.get("sourceFile"):
            source = "fixed_clip"
        else:
            source = "grok"
        source_duration = float(raw_scene.get("sourceDurationSec") or scene_duration)
        scenes.append(
            {
                "id": raw_scene["sceneId"],
                "source": source,
                "start": start,
                "end": end,
                "scene_duration": scene_duration,
                "clip_duration": max(0.1, source_duration),
                "output_name": Path(output_file).name,
                "source_file": raw_scene.get("sourceFile"),
                "source_start_sec": float(raw_scene.get("sourceStartSec") or 0.0),
                "loop_source": bool(raw_scene.get("loopSource") or False),
            }
        )
    return scenes or clone_default_scenes()


def is_repeat_v3(packet: dict, job: dict) -> bool:
    return packet.get("formatType") == "fill_blank_repeat" and str(packet.get("version") or "").lower() == "v3" and bool(job.get("scenes"))


def parse_total_duration_seconds(packet: dict, scenes: list[dict]) -> float:
    raw_value = packet.get("totalDurationSeconds")
    if isinstance(raw_value, (int, float)):
        return float(raw_value)
    return max((float(scene["end"]) for scene in scenes), default=30.0)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a Grok-assisted repeat/fill-blank Korean short.")
    parser.add_argument("--source-packet", required=True)
    parser.add_argument("--build-dir", required=True)
    parser.add_argument("--opening-video", required=True)
    return parser.parse_args()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_ffmpeg_binary() -> str:
    for candidate in FFMPEG_CANDIDATES:
        if str(candidate).strip() and candidate.is_file():
            return str(candidate)
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg
    raise RuntimeError("No usable ffmpeg binary found.")


def run_ffmpeg(cmd: list[str]) -> None:
    resolved = list(cmd)
    if resolved and resolved[0] == "ffmpeg":
        resolved[0] = resolve_ffmpeg_binary()
    elif resolved:
        resolved = [resolve_ffmpeg_binary(), *resolved]
    subprocess.run(resolved, check=True)


def load_font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = FONT_BOLD_CANDIDATES if bold else FONT_REGULAR_CANDIDATES
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size=size)
    raise RuntimeError("No usable font found.")


def rgb(value: str) -> tuple[int, int, int]:
    value = str(value).lstrip("#")
    return tuple(int(value[index : index + 2], 16) for index in (0, 2, 4))


def parse_resolution(packet: dict) -> tuple[int, int]:
    scene = packet.get("scene", {})
    resolution = str(scene.get("resolution") or "").strip()
    match = re.match(r"^(\d+)\s*x\s*(\d+)$", resolution, flags=re.IGNORECASE)
    if match:
        return int(match.group(1)), int(match.group(2))
    aspect = str(scene.get("aspectRatio") or "9:16")
    if aspect == "16:9":
        return 1920, 1080
    return DEFAULT_WIDTH, DEFAULT_HEIGHT


def render_mode(width: int, height: int) -> str:
    return "wide" if width > height else "vertical"


def scale_size(value: int, *, width: int, height: int, base_width: int, base_height: int, floor: int = 12) -> int:
    scale = min(width / base_width, height / base_height)
    return max(floor, int(round(value * scale)))


def scale_rect(rect: tuple[int, int, int, int], *, width: int, height: int, base_width: int, base_height: int) -> tuple[int, int, int, int]:
    left, top, right, bottom = rect
    return (
        int(round(left * width / base_width)),
        int(round(top * height / base_height)),
        int(round(right * width / base_width)),
        int(round(bottom * height / base_height)),
    )


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    if not str(text or "").strip():
        return []
    words = str(text).split(" ")
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if draw.textlength(candidate, font=font) <= max_width:
            current = candidate
            continue
        if current:
            lines.append(current)
            current = word
            continue
        fragment = ""
        for char in word:
            candidate_fragment = fragment + char
            if draw.textlength(candidate_fragment, font=font) <= max_width:
                fragment = candidate_fragment
            else:
                if fragment:
                    lines.append(fragment)
                fragment = char
        current = fragment
    if current:
        lines.append(current)
    return lines


def fit_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    *,
    max_size: int,
    min_size: int,
    bold: bool = True,
) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    for size in range(max_size, min_size - 1, -2):
        font = load_font(size, bold=bold)
        lines = wrap_text(draw, text, font, max_width)
        if len(lines) <= 3:
            return font, lines
    font = load_font(min_size, bold=bold)
    return font, wrap_text(draw, text, font, max_width)


def extract_clip_frames(
    video_path: Path,
    output_dir: Path,
    *,
    fps: int,
    width: int,
    height: int,
    start: float | None = None,
    duration: float | None = None,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    for old in output_dir.glob("frame-*.png"):
        old.unlink()
    cmd = ["ffmpeg", "-y"]
    if start is not None:
        cmd.extend(["-ss", f"{start:.3f}"])
    cmd.extend(["-i", str(video_path)])
    if duration is not None:
        cmd.extend(["-t", f"{duration:.3f}"])
    cmd.extend(
        [
            "-vf",
            f"fps={fps},scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}",
            "-start_number",
            "0",
            str(output_dir / "frame-%04d.png"),
        ]
    )
    run_ffmpeg(cmd)
    frames = sorted(output_dir.glob("frame-*.png"))
    if not frames:
        raise RuntimeError(f"Failed to extract frames from {video_path}")
    return frames


def pick_frame(frames: list[Path], progress: float) -> Image.Image:
    if not frames:
        raise RuntimeError("No frames available")
    index = min(len(frames) - 1, max(0, int(progress * len(frames))))
    return Image.open(frames[index]).convert("RGBA")


def scene_for_time(t: float, scenes: list[dict]) -> dict:
    for scene in scenes:
        if scene["start"] <= t < scene["end"]:
            return scene
    return scenes[-1]


def local_progress(scene: dict, t: float) -> float:
    duration = max(scene["end"] - scene["start"], 0.001)
    return max(0.0, min((t - scene["start"]) / duration, 0.999999))


def clip_progress(scene: dict, t: float) -> float:
    clip_duration = float(scene.get("clip_duration") or max(scene["end"] - scene["start"], 0.1))
    elapsed = max(0.0, t - scene["start"])
    if scene.get("loop_source"):
        return max(0.0, min((elapsed % clip_duration) / clip_duration, 0.999999))
    return max(0.0, min(elapsed / clip_duration, 0.999999))


def draw_card(draw: ImageDraw.ImageDraw, rect: tuple[int, int, int, int], fill: tuple[int, int, int, int], radius: int):
    draw.rounded_rectangle(rect, radius=radius, fill=fill)


def draw_alarm_clock(draw: ImageDraw.ImageDraw, center: tuple[int, int], progress: float, *, scale: float = 1.0):
    cx, cy = center
    pulse = 1.0 + math.sin(progress * math.pi * 6.0) * 0.08
    body_r = int(76 * scale * pulse)
    bell_r = int(22 * scale * pulse)
    stroke = max(3, int(8 * scale))
    draw.ellipse((cx - body_r, cy - body_r, cx + body_r, cy + body_r), fill=(255, 244, 209, 224), outline=(255, 199, 98, 255), width=stroke)
    inner = max(10, int(18 * scale))
    draw.ellipse((cx - body_r + inner, cy - body_r + inner, cx + body_r - inner, cy + body_r - inner), fill=(249, 252, 255, 232))
    bell_offset = max(16, int(18 * scale))
    draw.ellipse((cx - body_r - bell_offset, cy - body_r - bell_offset // 2, cx - body_r + bell_r * 2, cy - body_r + bell_r * 2), fill=(255, 204, 95, 236))
    draw.ellipse((cx + body_r - bell_r * 2, cy - body_r - bell_offset // 2, cx + body_r + bell_offset, cy - body_r + bell_r * 2), fill=(255, 204, 95, 236))
    hand_stroke = max(4, int(9 * scale))
    draw.line((cx, cy, cx, cy - int(38 * scale)), fill=(52, 77, 115, 255), width=hand_stroke)
    draw.line((cx, cy, cx + int(36 * scale), cy + int(16 * scale)), fill=(52, 77, 115, 255), width=hand_stroke)
    dot = max(5, int(8 * scale))
    draw.ellipse((cx - dot, cy - dot, cx + dot, cy + dot), fill=(52, 77, 115, 255))


def chalk_text(
    draw: ImageDraw.ImageDraw,
    position: tuple[int, int],
    text: str,
    *,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
    anchor: str = "la",
    shadow: tuple[int, int, int, int] = (10, 28, 18, 150),
):
    x, y = position
    shadow_offset = max(1, font.size // 24)
    stroke_width = max(1, font.size // 18)
    draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow, anchor=anchor)
    draw.text(
        (x, y),
        text,
        font=font,
        fill=fill,
        anchor=anchor,
        stroke_width=stroke_width,
        stroke_fill=(18, 48, 34, min(255, fill[3])),
    )


def draw_chalk_multiline(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    *,
    x: int,
    y: int,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
    line_gap: int,
) -> int:
    cursor = y
    for line in lines:
        chalk_text(draw, (x, cursor), line, font=font, fill=fill)
        cursor += font.size + line_gap
    return cursor


def draw_repeat_v3_scene_wide(draw: ImageDraw.ImageDraw, packet: dict, scene: dict, t: float, *, width: int, height: int):
    base_width, base_height = 1920, 1080
    theme = packet["theme"]
    lesson = packet["lesson"]
    choices = packet["choices"]
    scene_id = scene["id"]
    accent = rgb(theme["accent"])
    accent_warm = rgb(theme["accentWarm"])
    board_text = rgb(theme["boardText"])
    board_subtext = rgb(theme["boardSubtext"])

    board_rect = scale_rect((120, 118, 1170, 860), width=width, height=height, base_width=base_width, base_height=base_height)
    left = board_rect[0]
    top = board_rect[1]
    max_width = board_rect[2] - board_rect[0]

    heading_font = load_font(scale_size(42, width=width, height=height, base_width=base_width, base_height=base_height), bold=True)
    ko_font = load_font(scale_size(64, width=width, height=height, base_width=base_width, base_height=base_height), bold=True)
    en_font = load_font(scale_size(34, width=width, height=height, base_width=base_width, base_height=base_height))
    roman_font = load_font(scale_size(28, width=width, height=height, base_width=base_width, base_height=base_height))
    choice_font = load_font(scale_size(36, width=width, height=height, base_width=base_width, base_height=base_height), bold=True)
    answer_font = load_font(scale_size(96, width=width, height=height, base_width=base_width, base_height=base_height), bold=True)
    badge_font = load_font(scale_size(26, width=width, height=height, base_width=base_width, base_height=base_height), bold=True)
    repeat_font = load_font(scale_size(118, width=width, height=height, base_width=base_width, base_height=base_height), bold=True)
    gloss_font = load_font(scale_size(42, width=width, height=height, base_width=base_width, base_height=base_height))

    heading_fill = (*accent_warm, 252)
    board_fill = (*board_text, 248)
    sub_fill = (*board_subtext, 235)
    accent_fill = (*accent, 245)

    if scene_id == "scene-0-opening":
        return

    if scene_id in {"scene-5-ending", "scene-5-outro"}:
        cta_rect = scale_rect((670, 918, 1840, 1008), width=width, height=height, base_width=base_width, base_height=base_height)
        draw.rounded_rectangle(
            cta_rect,
            radius=scale_size(26, width=width, height=height, base_width=base_width, base_height=base_height),
            fill=(*accent, 220),
        )
        cta_text = packet.get("ending", {}).get("ctaText") or f"{packet['cta']['caption']} — malmoelab.com"
        draw.text(
            ((cta_rect[0] + cta_rect[2]) // 2, (cta_rect[1] + cta_rect[3]) // 2),
            cta_text,
            font=load_font(scale_size(28, width=width, height=height, base_width=base_width, base_height=base_height), bold=True),
            fill=(255, 255, 255, 255),
            anchor="mm",
        )
        return

    if scene_id in {"scene-1-question", "scene-2-thinking"}:
        chalk_text(draw, (left, top), "문장을 완성해 보세요", font=heading_font, fill=heading_fill)
        y = top + scale_size(76, width=width, height=height, base_width=base_width, base_height=base_height)
        ko_lines = wrap_text(draw, lesson["blankedSentenceKo"], ko_font, max_width)
        y = draw_chalk_multiline(
            draw,
            ko_lines,
            x=left,
            y=y,
            font=ko_font,
            fill=board_fill,
            line_gap=scale_size(10, width=width, height=height, base_width=base_width, base_height=base_height, floor=4),
        )
        y += scale_size(18, width=width, height=height, base_width=base_width, base_height=base_height)
        chalk_text(draw, (left, y), lesson["blankedSentenceRomanization"], font=roman_font, fill=sub_fill)
        y += scale_size(58, width=width, height=height, base_width=base_width, base_height=base_height)
        en_lines = wrap_text(draw, lesson["blankedSentenceEn"], en_font, max_width)
        y = draw_chalk_multiline(
            draw,
            en_lines,
            x=left,
            y=y,
            font=en_font,
            fill=sub_fill,
            line_gap=scale_size(8, width=width, height=height, base_width=base_width, base_height=base_height, floor=3),
        )
        y += scale_size(64, width=width, height=height, base_width=base_width, base_height=base_height)
        chalk_text(draw, (left, y), "보기", font=load_font(scale_size(30, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=heading_fill)
        y += scale_size(54, width=width, height=height, base_width=base_width, base_height=base_height)
        for item in choices:
            option_text = f"{item['order']}. {item['korean']}   {item['romanization']}   ({item['gloss']})"
            chalk_text(draw, (left, y), option_text, font=choice_font, fill=board_fill)
            y += scale_size(62, width=width, height=height, base_width=base_width, base_height=base_height)
        if scene_id == "scene-2-thinking":
            progress = local_progress(scene, t)
            clock_center = (
                board_rect[2] - scale_size(140, width=width, height=height, base_width=base_width, base_height=base_height),
                board_rect[3] - scale_size(126, width=width, height=height, base_width=base_width, base_height=base_height),
            )
            draw_alarm_clock(draw, clock_center, progress, scale=min(width / base_width, height / base_height) * 0.9)
        return

    if scene_id == "scene-3-answer":
        badge_rect = scale_rect((128, 110, 292, 168), width=width, height=height, base_width=base_width, base_height=base_height)
        draw.rounded_rectangle(
            badge_rect,
            radius=scale_size(24, width=width, height=height, base_width=base_width, base_height=base_height),
            fill=(*accent, 210),
        )
        draw.text(
            ((badge_rect[0] + badge_rect[2]) // 2, (badge_rect[1] + badge_rect[3]) // 2),
            "정답",
            font=badge_font,
            fill=(255, 255, 255, 255),
            anchor="mm",
        )
        y = top + scale_size(92, width=width, height=height, base_width=base_width, base_height=base_height)
        ko_lines = wrap_text(draw, lesson["sentenceKo"], ko_font, max_width)
        y = draw_chalk_multiline(
            draw,
            ko_lines,
            x=left,
            y=y,
            font=ko_font,
            fill=board_fill,
            line_gap=scale_size(10, width=width, height=height, base_width=base_width, base_height=base_height, floor=4),
        )
        y += scale_size(18, width=width, height=height, base_width=base_width, base_height=base_height)
        chalk_text(draw, (left, y), lesson["sentenceRomanization"], font=roman_font, fill=sub_fill)
        y += scale_size(56, width=width, height=height, base_width=base_width, base_height=base_height)
        en_lines = wrap_text(draw, lesson["sentenceEn"], en_font, max_width)
        y = draw_chalk_multiline(
            draw,
            en_lines,
            x=left,
            y=y,
            font=en_font,
            fill=sub_fill,
            line_gap=scale_size(8, width=width, height=height, base_width=base_width, base_height=base_height, floor=3),
        )
        progress = min(1.0, max(0.0, local_progress(scene, t) * 1.6))
        answer_alpha = int(120 + 135 * progress)
        answer_y = board_rect[3] - scale_size(150, width=width, height=height, base_width=base_width, base_height=base_height)
        chalk_text(draw, (left + scale_size(260, width=width, height=height, base_width=base_width, base_height=base_height), answer_y), lesson["answerWord"], font=answer_font, fill=(*accent, answer_alpha), anchor="mm")
        underline_width = scale_size(240, width=width, height=height, base_width=base_width, base_height=base_height)
        underline_height = scale_size(10, width=width, height=height, base_width=base_width, base_height=base_height, floor=4)
        center_x = left + scale_size(260, width=width, height=height, base_width=base_width, base_height=base_height)
        draw.rounded_rectangle(
            (center_x - underline_width // 2, answer_y + scale_size(44, width=width, height=height, base_width=base_width, base_height=base_height), center_x + underline_width // 2, answer_y + scale_size(44, width=width, height=height, base_width=base_width, base_height=base_height) + underline_height),
            radius=underline_height // 2,
            fill=(*accent, min(255, answer_alpha)),
        )
        return

    if scene_id == "scene-4-repeat":
        chalk_text(draw, (left, top), "따라해 보세요", font=heading_font, fill=heading_fill)
        chalk_text(
            draw,
            (left, top + scale_size(54, width=width, height=height, base_width=base_width, base_height=base_height)),
            "Repeat after me",
            font=load_font(scale_size(30, width=width, height=height, base_width=base_width, base_height=base_height), bold=True),
            fill=sub_fill,
        )
        repeat_sequence = repeat_sequence_from_packet(packet)
        repeat_items = ((packet.get("_renderTimings") or {}).get(scene_id) or {}).get("repeat_items") or []
        relative_t = max(0.0, t - float(scene["start"]))
        if repeat_items:
            current = repeat_items[0]
            for item in repeat_items:
                if relative_t >= float(item.get("start") or 0.0):
                    current = item
                else:
                    break
            current_ko = current.get("textKo") or repeat_sequence[0]["korean"]
            current_romanization = current.get("textRomanization") or repeat_sequence[0]["romanization"]
            current_gloss = current.get("textGloss") or repeat_sequence[0]["gloss"]
            repeat_mark = current.get("badge") or "1/2"
        else:
            progress = local_progress(scene, t)
            seq_index = min(len(repeat_sequence) - 1, int(progress * len(repeat_sequence)))
            current = repeat_sequence[seq_index]
            current_ko = current["korean"]
            current_romanization = current["romanization"]
            current_gloss = current["gloss"]
            repeat_mark = "2/2" if seq_index % 2 == 1 else "1/2"
        chalk_text(draw, (left + scale_size(260, width=width, height=height, base_width=base_width, base_height=base_height), top + scale_size(290, width=width, height=height, base_width=base_width, base_height=base_height)), current_ko, font=repeat_font, fill=board_fill, anchor="mm")
        chalk_text(draw, (left + scale_size(260, width=width, height=height, base_width=base_width, base_height=base_height), top + scale_size(430, width=width, height=height, base_width=base_width, base_height=base_height)), current_romanization, font=load_font(scale_size(52, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=accent_fill, anchor="mm")
        chalk_text(draw, (left + scale_size(260, width=width, height=height, base_width=base_width, base_height=base_height), top + scale_size(508, width=width, height=height, base_width=base_width, base_height=base_height)), current_gloss, font=gloss_font, fill=sub_fill, anchor="mm")
        badge_rect = (
            left + scale_size(50, width=width, height=height, base_width=base_width, base_height=base_height),
            top + scale_size(642, width=width, height=height, base_width=base_width, base_height=base_height),
            left + scale_size(220, width=width, height=height, base_width=base_width, base_height=base_height),
            top + scale_size(700, width=width, height=height, base_width=base_width, base_height=base_height),
        )
        draw.rounded_rectangle(
            badge_rect,
            radius=scale_size(24, width=width, height=height, base_width=base_width, base_height=base_height),
            fill=(*accent, 210),
        )
        draw.text(((badge_rect[0] + badge_rect[2]) // 2, (badge_rect[1] + badge_rect[3]) // 2), repeat_mark, font=badge_font, fill=(255, 255, 255, 255), anchor="mm")
        return


def draw_title(draw: ImageDraw.ImageDraw, packet: dict, *, width: int, height: int, mode: str):
    if str(packet.get("version") or "").lower() == "v3":
        return
    if mode == "wide":
        base_width, base_height = 1920, 1080
        header_rect = scale_rect((46, 34, 1210, 154), width=width, height=height, base_width=base_width, base_height=base_height)
        draw_card(draw, header_rect, fill=(7, 16, 28, 190), radius=scale_size(28, width=width, height=height, base_width=base_width, base_height=base_height))
        chip_font = load_font(scale_size(24, width=width, height=height, base_width=base_width, base_height=base_height), bold=True)
        title_font, title_lines = fit_text(
            draw,
            "Malmoelab Korean repeat practice",
            header_rect[2] - header_rect[0] - scale_size(120, width=width, height=height, base_width=base_width, base_height=base_height),
            max_size=scale_size(42, width=width, height=height, base_width=base_width, base_height=base_height),
            min_size=scale_size(28, width=width, height=height, base_width=base_width, base_height=base_height),
        )
        left = header_rect[0] + scale_size(28, width=width, height=height, base_width=base_width, base_height=base_height)
        draw.text((left, header_rect[1] + scale_size(24, width=width, height=height, base_width=base_width, base_height=base_height)), "MALMOELAB KOREAN REPEAT", font=chip_font, fill=(255, 197, 96, 255), anchor="la")
        y = header_rect[1] + scale_size(58, width=width, height=height, base_width=base_width, base_height=base_height)
        for line in title_lines:
            draw.text((left, y), line, font=title_font, fill=(255, 252, 245, 255), anchor="la")
            y += title_font.size + scale_size(4, width=width, height=height, base_width=base_width, base_height=base_height, floor=2)
        return

    base_width, base_height = 1080, 1920
    header_rect = scale_rect((44, 56, 1036, 236), width=width, height=height, base_width=base_width, base_height=base_height)
    draw_card(draw, header_rect, fill=(7, 16, 28, 208), radius=scale_size(40, width=width, height=height, base_width=base_width, base_height=base_height))
    chip_font = load_font(scale_size(28, width=width, height=height, base_width=base_width, base_height=base_height), bold=True)
    title_font, title_lines = fit_text(
        draw,
        "Malmoelab Korean repeat practice",
        header_rect[2] - header_rect[0] - scale_size(170, width=width, height=height, base_width=base_width, base_height=base_height),
        max_size=scale_size(58, width=width, height=height, base_width=base_width, base_height=base_height),
        min_size=scale_size(40, width=width, height=height, base_width=base_width, base_height=base_height),
    )
    draw.text(
        (header_rect[0] + scale_size(32, width=width, height=height, base_width=base_width, base_height=base_height), header_rect[1] + scale_size(44, width=width, height=height, base_width=base_width, base_height=base_height)),
        "MALMOELAB HANGUL REPEAT",
        font=chip_font,
        fill=(255, 197, 96, 255),
        anchor="la",
    )
    y = header_rect[1] + scale_size(88, width=width, height=height, base_width=base_width, base_height=base_height)
    for line in title_lines:
        draw.text((header_rect[0] + scale_size(32, width=width, height=height, base_width=base_width, base_height=base_height), y), line, font=title_font, fill=(255, 252, 245, 255), anchor="la")
        y += title_font.size + scale_size(6, width=width, height=height, base_width=base_width, base_height=base_height, floor=2)


def draw_board_scene_vertical(draw: ImageDraw.ImageDraw, packet: dict, scene: dict, t: float, *, width: int, height: int):
    base_width, base_height = 1080, 1920
    theme = packet["theme"]
    accent = rgb(theme["accent"])
    accent_warm = rgb(theme["accentWarm"])
    board_text = rgb(theme["boardText"])
    scene_id = scene["id"]

    if str(packet.get("version") or "").lower() == "v3":
        if scene_id == "scene-0-opening":
            return
        if scene_id in {"scene-5-outro", "scene-5-ending"}:
            cta_rect = scale_rect((96, 1696, 984, 1796), width=width, height=height, base_width=base_width, base_height=base_height)
            draw.rounded_rectangle(cta_rect, radius=scale_size(34, width=width, height=height, base_width=base_width, base_height=base_height), fill=(*accent, 232))
            cta_text = packet.get("ending", {}).get("ctaText") or f"{packet['cta']['caption']} — malmoelab.com"
            draw.text(((cta_rect[0] + cta_rect[2]) // 2, (cta_rect[1] + cta_rect[3]) // 2), cta_text, font=load_font(scale_size(34, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=(255, 255, 255, 255), anchor="mm")
            return

    board_rect = scale_rect((76, 272, 1004, 1494), width=width, height=height, base_width=base_width, base_height=base_height)
    footer_rect = scale_rect((76, 1546, 1004, 1826), width=width, height=height, base_width=base_width, base_height=base_height)
    draw_card(draw, board_rect, fill=(31, 88, 58, 164), radius=scale_size(36, width=width, height=height, base_width=base_width, base_height=base_height))
    draw.rounded_rectangle(board_rect, radius=scale_size(36, width=width, height=height, base_width=base_width, base_height=base_height), outline=(230, 240, 232, 120), width=max(2, scale_size(3, width=width, height=height, base_width=base_width, base_height=base_height, floor=2)))
    draw_card(draw, footer_rect, fill=(10, 18, 30, 214), radius=scale_size(36, width=width, height=height, base_width=base_width, base_height=base_height))

    left = board_rect[0] + scale_size(34, width=width, height=height, base_width=base_width, base_height=base_height)
    top = board_rect[1] + scale_size(28, width=width, height=height, base_width=base_width, base_height=base_height)
    max_width = board_rect[2] - board_rect[0] - scale_size(68, width=width, height=height, base_width=base_width, base_height=base_height)
    lesson = packet["lesson"]
    choices = packet["choices"]

    if scene_id == "scene-0-opening":
        title_font = load_font(scale_size(76, width=width, height=height, base_width=base_width, base_height=base_height), bold=True)
        sub_font = load_font(scale_size(38, width=width, height=height, base_width=base_width, base_height=base_height))
        draw.text((width // 2, scale_size(1012, width=width, height=height, base_width=base_width, base_height=base_height)), "말모이랩 한글공부", font=title_font, fill=(*board_text, 255), anchor="mm")
        draw.text((width // 2, scale_size(1096, width=width, height=height, base_width=base_width, base_height=base_height)), "Malmoelab Korean", font=sub_font, fill=(255, 223, 178, 242), anchor="mm")
        draw.text((width // 2, scale_size(1700, width=width, height=height, base_width=base_width, base_height=base_height)), "30-second fill-blank and repeat lesson", font=load_font(scale_size(32, width=width, height=height, base_width=base_width, base_height=base_height)), fill=(235, 239, 242, 220), anchor="mm")
        return

    if scene_id in {"scene-1-question", "scene-2-thinking"}:
        eyebrow = "문장을 완성해 보세요" if scene_id == "scene-1-question" else "생각할 시간"
        draw.text((left, top), eyebrow, font=load_font(scale_size(28, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=(*accent_warm, 250), anchor="la")
        y = top + scale_size(54, width=width, height=height, base_width=base_width, base_height=base_height)
        ko_font, ko_lines = fit_text(
            draw,
            lesson["blankedSentenceKo"],
            max_width,
            max_size=scale_size(64, width=width, height=height, base_width=base_width, base_height=base_height),
            min_size=scale_size(48, width=width, height=height, base_width=base_width, base_height=base_height),
        )
        for line in ko_lines:
            draw.text((left, y), line, font=ko_font, fill=(*board_text, 255), anchor="la")
            y += ko_font.size + scale_size(10, width=width, height=height, base_width=base_width, base_height=base_height, floor=4)
        draw.text((left, y + scale_size(6, width=width, height=height, base_width=base_width, base_height=base_height)), lesson["blankedSentenceEn"], font=load_font(scale_size(34, width=width, height=height, base_width=base_width, base_height=base_height)), fill=(233, 236, 236, 240), anchor="la")
        y += scale_size(58, width=width, height=height, base_width=base_width, base_height=base_height)
        draw.text((left, y + scale_size(4, width=width, height=height, base_width=base_width, base_height=base_height)), lesson["blankedSentenceRomanization"], font=load_font(scale_size(30, width=width, height=height, base_width=base_width, base_height=base_height)), fill=(*accent_warm, 250), anchor="la")
        y += scale_size(90, width=width, height=height, base_width=base_width, base_height=base_height)
        box_rect = (left, y, board_rect[2] - scale_size(30, width=width, height=height, base_width=base_width, base_height=base_height), y + scale_size(262, width=width, height=height, base_width=base_width, base_height=base_height))
        draw_card(draw, box_rect, fill=(8, 18, 30, 174), radius=scale_size(28, width=width, height=height, base_width=base_width, base_height=base_height))
        draw.text((left + scale_size(22, width=width, height=height, base_width=base_width, base_height=base_height), y + scale_size(18, width=width, height=height, base_width=base_width, base_height=base_height)), "보기", font=load_font(scale_size(28, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=(255, 221, 164, 245), anchor="la")
        line_y = y + scale_size(72, width=width, height=height, base_width=base_width, base_height=base_height)
        for item in choices:
            text = f"{item['order']}. {item['korean']}   {item['romanization']} ({item['gloss']})"
            draw.text((left + scale_size(24, width=width, height=height, base_width=base_width, base_height=base_height), line_y), text, font=load_font(scale_size(34, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=(*board_text, 252), anchor="la")
            line_y += scale_size(58, width=width, height=height, base_width=base_width, base_height=base_height)
        if scene_id == "scene-2-thinking":
            progress = local_progress(scene, t)
            draw_alarm_clock(draw, (board_rect[2] - scale_size(128, width=width, height=height, base_width=base_width, base_height=base_height), board_rect[3] - scale_size(144, width=width, height=height, base_width=base_width, base_height=base_height)), progress)
        draw.text((footer_rect[0] + scale_size(28, width=width, height=height, base_width=base_width, base_height=base_height), footer_rect[1] + scale_size(36, width=width, height=height, base_width=base_width, base_height=base_height)), "천천히 듣고 정답을 생각해 보세요", font=load_font(scale_size(40, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=(255, 252, 246, 255), anchor="la")
        draw.text((footer_rect[0] + scale_size(28, width=width, height=height, base_width=base_width, base_height=base_height), footer_rect[1] + scale_size(106, width=width, height=height, base_width=base_width, base_height=base_height)), "Listen first, then choose the right word.", font=load_font(scale_size(30, width=width, height=height, base_width=base_width, base_height=base_height)), fill=(219, 228, 232, 232), anchor="la")
        return

    if scene_id == "scene-3-answer":
        draw.text((left, top), "정답 공개", font=load_font(scale_size(28, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=(*accent_warm, 250), anchor="la")
        y = top + scale_size(54, width=width, height=height, base_width=base_width, base_height=base_height)
        ko_font, ko_lines = fit_text(
            draw,
            lesson["sentenceKo"],
            max_width,
            max_size=scale_size(64, width=width, height=height, base_width=base_width, base_height=base_height),
            min_size=scale_size(48, width=width, height=height, base_width=base_width, base_height=base_height),
        )
        for line in ko_lines:
            draw.text((left, y), line, font=ko_font, fill=(*board_text, 255), anchor="la")
            y += ko_font.size + scale_size(10, width=width, height=height, base_width=base_width, base_height=base_height, floor=4)
        draw.text((left, y + scale_size(10, width=width, height=height, base_width=base_width, base_height=base_height)), lesson["sentenceEn"], font=load_font(scale_size(34, width=width, height=height, base_width=base_width, base_height=base_height)), fill=(233, 236, 236, 240), anchor="la")
        y += scale_size(60, width=width, height=height, base_width=base_width, base_height=base_height)
        draw.text((left, y + scale_size(6, width=width, height=height, base_width=base_width, base_height=base_height)), lesson["sentenceRomanization"], font=load_font(scale_size(30, width=width, height=height, base_width=base_width, base_height=base_height)), fill=(*accent_warm, 250), anchor="la")
        answer_chip = scale_rect((910, 300, 1058, 368), width=width, height=height, base_width=base_width, base_height=base_height)
        draw.rounded_rectangle(answer_chip, radius=scale_size(28, width=width, height=height, base_width=base_width, base_height=base_height), fill=(*accent, 226))
        draw.text(((answer_chip[0] + answer_chip[2]) // 2, (answer_chip[1] + answer_chip[3]) // 2), "정답", font=load_font(scale_size(34, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=(255, 255, 255, 255), anchor="mm")
        draw.text((width // 2, scale_size(1006, width=width, height=height, base_width=base_width, base_height=base_height)), lesson["answerWord"], font=load_font(scale_size(112, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=(*accent_warm, 255), anchor="mm")
        underline = scale_rect((458, 1068, 622, 1082), width=width, height=height, base_width=base_width, base_height=base_height)
        draw.rounded_rectangle(underline, radius=scale_size(7, width=width, height=height, base_width=base_width, base_height=base_height), fill=(*accent_warm, 240))
        draw.text((footer_rect[0] + scale_size(28, width=width, height=height, base_width=base_width, base_height=base_height), footer_rect[1] + scale_size(36, width=width, height=height, base_width=base_width, base_height=base_height)), f"정답은 {lesson['answerWord']}", font=load_font(scale_size(40, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=(255, 252, 246, 255), anchor="la")
        draw.text((footer_rect[0] + scale_size(28, width=width, height=height, base_width=base_width, base_height=base_height), footer_rect[1] + scale_size(106, width=width, height=height, base_width=base_width, base_height=base_height)), "문장을 크게 보고 발음을 천천히 따라 읽을 준비를 하세요.", font=load_font(scale_size(30, width=width, height=height, base_width=base_width, base_height=base_height)), fill=(219, 228, 232, 232), anchor="la")
        return

    if scene_id == "scene-4-repeat":
        draw.text((left, top), "따라해 보세요", font=load_font(scale_size(28, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=(*accent_warm, 250), anchor="la")
        draw.text((left, top + scale_size(52, width=width, height=height, base_width=base_width, base_height=base_height)), "Repeat after me", font=load_font(scale_size(32, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=(244, 246, 248, 246), anchor="la")
        draw.text((left, top + scale_size(110, width=width, height=height, base_width=base_width, base_height=base_height)), lesson["sentenceKo"], font=load_font(scale_size(40, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=(*board_text, 255), anchor="la")
        draw.text((left, top + scale_size(162, width=width, height=height, base_width=base_width, base_height=base_height)), lesson["sentenceRomanization"], font=load_font(scale_size(26, width=width, height=height, base_width=base_width, base_height=base_height)), fill=(255, 220, 168, 240), anchor="la")
        repeat_sequence = repeat_sequence_from_packet(packet)
        lp = local_progress(scene, t)
        seq_index = min(len(repeat_sequence) - 1, int(lp * len(repeat_sequence)))
        current = repeat_sequence[seq_index]
        repeat_mark = "2회" if seq_index % 2 == 1 else "1회"
        draw.text((width // 2, scale_size(980, width=width, height=height, base_width=base_width, base_height=base_height)), current["korean"], font=load_font(scale_size(132, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=(*board_text, 255), anchor="mm")
        draw.text((width // 2, scale_size(1098, width=width, height=height, base_width=base_width, base_height=base_height)), current["romanization"], font=load_font(scale_size(56, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=(*accent_warm, 252), anchor="mm")
        draw.text((width // 2, scale_size(1168, width=width, height=height, base_width=base_width, base_height=base_height)), current["gloss"], font=load_font(scale_size(46, width=width, height=height, base_width=base_width, base_height=base_height)), fill=(235, 238, 240, 236), anchor="mm")
        badge = scale_rect((450, 1238, 630, 1302), width=width, height=height, base_width=base_width, base_height=base_height)
        draw.rounded_rectangle(badge, radius=scale_size(30, width=width, height=height, base_width=base_width, base_height=base_height), fill=(*accent, 220))
        draw.text(((badge[0] + badge[2]) // 2, (badge[1] + badge[3]) // 2), repeat_mark, font=load_font(scale_size(34, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=(255, 255, 255, 255), anchor="mm")
        draw.text((footer_rect[0] + scale_size(28, width=width, height=height, base_width=base_width, base_height=base_height), footer_rect[1] + scale_size(36, width=width, height=height, base_width=base_width, base_height=base_height)), "각 단어를 두 번씩 천천히 반복합니다", font=load_font(scale_size(38, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=(255, 252, 246, 255), anchor="la")
        draw.text((footer_rect[0] + scale_size(28, width=width, height=height, base_width=base_width, base_height=base_height), footer_rect[1] + scale_size(100, width=width, height=height, base_width=base_width, base_height=base_height)), "집, 회사, 화장실 순서로 따라 읽어 보세요.", font=load_font(scale_size(30, width=width, height=height, base_width=base_width, base_height=base_height)), fill=(219, 228, 232, 232), anchor="la")
        return

    if scene_id == "scene-5-outro":
        draw.text((left, top), "오늘의 문장", font=load_font(scale_size(28, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=(*accent_warm, 250), anchor="la")
        y = top + scale_size(54, width=width, height=height, base_width=base_width, base_height=base_height)
        ko_font, ko_lines = fit_text(
            draw,
            lesson["sentenceKo"],
            max_width,
            max_size=scale_size(64, width=width, height=height, base_width=base_width, base_height=base_height),
            min_size=scale_size(48, width=width, height=height, base_width=base_width, base_height=base_height),
        )
        for line in ko_lines:
            draw.text((left, y), line, font=ko_font, fill=(*board_text, 255), anchor="la")
            y += ko_font.size + scale_size(10, width=width, height=height, base_width=base_width, base_height=base_height, floor=4)
        draw.text((left, y + scale_size(8, width=width, height=height, base_width=base_width, base_height=base_height)), lesson["sentenceEn"], font=load_font(scale_size(34, width=width, height=height, base_width=base_width, base_height=base_height)), fill=(233, 236, 236, 240), anchor="la")
        y += scale_size(60, width=width, height=height, base_width=base_width, base_height=base_height)
        draw.text((left, y + scale_size(4, width=width, height=height, base_width=base_width, base_height=base_height)), lesson["sentenceRomanization"], font=load_font(scale_size(30, width=width, height=height, base_width=base_width, base_height=base_height)), fill=(*accent_warm, 250), anchor="la")
        cta_rect = scale_rect((98, 1576, 982, 1658), width=width, height=height, base_width=base_width, base_height=base_height)
        draw.rounded_rectangle(cta_rect, radius=scale_size(32, width=width, height=height, base_width=base_width, base_height=base_height), fill=(*accent, 230))
        draw.text(((cta_rect[0] + cta_rect[2]) // 2, (cta_rect[1] + cta_rect[3]) // 2), packet["cta"]["caption"], font=load_font(scale_size(34, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=(255, 255, 255, 255), anchor="mm")
        draw.text((width // 2, scale_size(1710, width=width, height=height, base_width=base_width, base_height=base_height)), "malmoelab.com", font=load_font(scale_size(30, width=width, height=height, base_width=base_width, base_height=base_height)), fill=(235, 238, 240, 236), anchor="mm")


def draw_board_scene_wide(draw: ImageDraw.ImageDraw, packet: dict, scene: dict, t: float, *, width: int, height: int):
    base_width, base_height = 1920, 1080
    theme = packet["theme"]
    accent = rgb(theme["accent"])
    accent_warm = rgb(theme["accentWarm"])
    board_text = rgb(theme["boardText"])
    scene_id = scene["id"]

    if str(packet.get("version") or "").lower() == "v3":
        draw_repeat_v3_scene_wide(draw, packet, scene, t, width=width, height=height)
        return

    board_rect = scale_rect((46, 170, 1298, 860), width=width, height=height, base_width=base_width, base_height=base_height)
    footer_rect = scale_rect((46, 886, 1298, 1036), width=width, height=height, base_width=base_width, base_height=base_height)
    draw_card(draw, board_rect, fill=(8, 22, 28, 118), radius=scale_size(30, width=width, height=height, base_width=base_width, base_height=base_height))
    draw.rounded_rectangle(board_rect, radius=scale_size(30, width=width, height=height, base_width=base_width, base_height=base_height), outline=(234, 240, 232, 118), width=max(2, scale_size(3, width=width, height=height, base_width=base_width, base_height=base_height, floor=2)))
    draw_card(draw, footer_rect, fill=(10, 18, 30, 194), radius=scale_size(24, width=width, height=height, base_width=base_width, base_height=base_height))

    left = board_rect[0] + scale_size(34, width=width, height=height, base_width=base_width, base_height=base_height)
    top = board_rect[1] + scale_size(24, width=width, height=height, base_width=base_width, base_height=base_height)
    max_width = board_rect[2] - board_rect[0] - scale_size(68, width=width, height=height, base_width=base_width, base_height=base_height)
    lesson = packet["lesson"]
    choices = packet["choices"]

    if scene_id == "scene-0-opening":
        title_font = load_font(scale_size(52, width=width, height=height, base_width=base_width, base_height=base_height), bold=True)
        sub_font = load_font(scale_size(28, width=width, height=height, base_width=base_width, base_height=base_height))
        draw.text((board_rect[0] + (board_rect[2] - board_rect[0]) // 2, scale_size(470, width=width, height=height, base_width=base_width, base_height=base_height)), "말모이랩 한글공부", font=title_font, fill=(*board_text, 255), anchor="mm")
        draw.text((board_rect[0] + (board_rect[2] - board_rect[0]) // 2, scale_size(540, width=width, height=height, base_width=base_width, base_height=base_height)), "Malmoelab Korean", font=sub_font, fill=(255, 223, 178, 242), anchor="mm")
        draw.text((board_rect[0] + (board_rect[2] - board_rect[0]) // 2, scale_size(945, width=width, height=height, base_width=base_width, base_height=base_height)), "30-second fill-blank and repeat lesson", font=load_font(scale_size(24, width=width, height=height, base_width=base_width, base_height=base_height)), fill=(235, 239, 242, 220), anchor="mm")
        return

    if scene_id in {"scene-1-question", "scene-2-thinking"}:
        eyebrow = "문장을 완성해 보세요" if scene_id == "scene-1-question" else "생각할 시간"
        draw.text((left, top), eyebrow, font=load_font(scale_size(24, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=(*accent_warm, 250), anchor="la")
        y = top + scale_size(44, width=width, height=height, base_width=base_width, base_height=base_height)
        ko_font, ko_lines = fit_text(
            draw,
            lesson["blankedSentenceKo"],
            max_width - scale_size(40, width=width, height=height, base_width=base_width, base_height=base_height),
            max_size=scale_size(52, width=width, height=height, base_width=base_width, base_height=base_height),
            min_size=scale_size(34, width=width, height=height, base_width=base_width, base_height=base_height),
        )
        for line in ko_lines:
            draw.text((left, y), line, font=ko_font, fill=(*board_text, 255), anchor="la")
            y += ko_font.size + scale_size(8, width=width, height=height, base_width=base_width, base_height=base_height, floor=3)
        draw.text((left, y + scale_size(6, width=width, height=height, base_width=base_width, base_height=base_height)), lesson["blankedSentenceEn"], font=load_font(scale_size(28, width=width, height=height, base_width=base_width, base_height=base_height)), fill=(233, 236, 236, 240), anchor="la")
        y += scale_size(50, width=width, height=height, base_width=base_width, base_height=base_height)
        draw.text((left, y + scale_size(2, width=width, height=height, base_width=base_width, base_height=base_height)), lesson["blankedSentenceRomanization"], font=load_font(scale_size(22, width=width, height=height, base_width=base_width, base_height=base_height)), fill=(*accent_warm, 250), anchor="la")
        y += scale_size(70, width=width, height=height, base_width=base_width, base_height=base_height)
        box_rect = (left, y, board_rect[2] - scale_size(28, width=width, height=height, base_width=base_width, base_height=base_height), y + scale_size(250, width=width, height=height, base_width=base_width, base_height=base_height))
        draw_card(draw, box_rect, fill=(8, 18, 30, 164), radius=scale_size(24, width=width, height=height, base_width=base_width, base_height=base_height))
        draw.text((box_rect[0] + scale_size(22, width=width, height=height, base_width=base_width, base_height=base_height), box_rect[1] + scale_size(18, width=width, height=height, base_width=base_width, base_height=base_height)), "보기", font=load_font(scale_size(24, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=(255, 221, 164, 245), anchor="la")
        line_y = box_rect[1] + scale_size(70, width=width, height=height, base_width=base_width, base_height=base_height)
        for item in choices:
            text = f"{item['order']}. {item['korean']}   {item['romanization']} ({item['gloss']})"
            draw.text((box_rect[0] + scale_size(24, width=width, height=height, base_width=base_width, base_height=base_height), line_y), text, font=load_font(scale_size(28, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=(*board_text, 252), anchor="la")
            line_y += scale_size(52, width=width, height=height, base_width=base_width, base_height=base_height)
        if scene_id == "scene-2-thinking":
            progress = local_progress(scene, t)
            draw_alarm_clock(
                draw,
                (
                    board_rect[2] - scale_size(118, width=width, height=height, base_width=base_width, base_height=base_height),
                    board_rect[3] - scale_size(118, width=width, height=height, base_width=base_width, base_height=base_height),
                ),
                progress,
                scale=min(width / base_width, height / base_height) * 0.9,
            )
        draw.text((footer_rect[0] + scale_size(26, width=width, height=height, base_width=base_width, base_height=base_height), footer_rect[1] + scale_size(28, width=width, height=height, base_width=base_width, base_height=base_height)), "천천히 듣고 정답을 생각해 보세요", font=load_font(scale_size(30, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=(255, 252, 246, 255), anchor="la")
        draw.text((footer_rect[0] + scale_size(26, width=width, height=height, base_width=base_width, base_height=base_height), footer_rect[1] + scale_size(82, width=width, height=height, base_width=base_width, base_height=base_height)), "Listen first, then choose the right word.", font=load_font(scale_size(22, width=width, height=height, base_width=base_width, base_height=base_height)), fill=(219, 228, 232, 232), anchor="la")
        return

    if scene_id == "scene-3-answer":
        draw.text((left, top), "정답 공개", font=load_font(scale_size(24, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=(*accent_warm, 250), anchor="la")
        y = top + scale_size(44, width=width, height=height, base_width=base_width, base_height=base_height)
        ko_font, ko_lines = fit_text(
            draw,
            lesson["sentenceKo"],
            max_width - scale_size(40, width=width, height=height, base_width=base_width, base_height=base_height),
            max_size=scale_size(52, width=width, height=height, base_width=base_width, base_height=base_height),
            min_size=scale_size(34, width=width, height=height, base_width=base_width, base_height=base_height),
        )
        for line in ko_lines:
            draw.text((left, y), line, font=ko_font, fill=(*board_text, 255), anchor="la")
            y += ko_font.size + scale_size(8, width=width, height=height, base_width=base_width, base_height=base_height, floor=3)
        draw.text((left, y + scale_size(6, width=width, height=height, base_width=base_width, base_height=base_height)), lesson["sentenceEn"], font=load_font(scale_size(28, width=width, height=height, base_width=base_width, base_height=base_height)), fill=(233, 236, 236, 240), anchor="la")
        y += scale_size(48, width=width, height=height, base_width=base_width, base_height=base_height)
        draw.text((left, y + scale_size(2, width=width, height=height, base_width=base_width, base_height=base_height)), lesson["sentenceRomanization"], font=load_font(scale_size(22, width=width, height=height, base_width=base_width, base_height=base_height)), fill=(*accent_warm, 250), anchor="la")
        answer_chip = scale_rect((1102, 190, 1260, 254), width=width, height=height, base_width=base_width, base_height=base_height)
        draw.rounded_rectangle(answer_chip, radius=scale_size(24, width=width, height=height, base_width=base_width, base_height=base_height), fill=(*accent, 226))
        draw.text(((answer_chip[0] + answer_chip[2]) // 2, (answer_chip[1] + answer_chip[3]) // 2), "정답", font=load_font(scale_size(28, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=(255, 255, 255, 255), anchor="mm")
        center_x = board_rect[0] + (board_rect[2] - board_rect[0]) // 2
        draw.text((center_x, scale_size(598, width=width, height=height, base_width=base_width, base_height=base_height)), lesson["answerWord"], font=load_font(scale_size(96, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=(*accent_warm, 255), anchor="mm")
        underline = scale_rect((540, 656, 760, 672), width=width, height=height, base_width=base_width, base_height=base_height)
        draw.rounded_rectangle(underline, radius=scale_size(8, width=width, height=height, base_width=base_width, base_height=base_height), fill=(*accent_warm, 240))
        draw.text((footer_rect[0] + scale_size(26, width=width, height=height, base_width=base_width, base_height=base_height), footer_rect[1] + scale_size(28, width=width, height=height, base_width=base_width, base_height=base_height)), f"정답은 {lesson['answerWord']}", font=load_font(scale_size(30, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=(255, 252, 246, 255), anchor="la")
        draw.text((footer_rect[0] + scale_size(26, width=width, height=height, base_width=base_width, base_height=base_height), footer_rect[1] + scale_size(82, width=width, height=height, base_width=base_width, base_height=base_height)), "문장을 보고 발음을 천천히 따라 읽을 준비를 하세요.", font=load_font(scale_size(22, width=width, height=height, base_width=base_width, base_height=base_height)), fill=(219, 228, 232, 232), anchor="la")
        return

    if scene_id == "scene-4-repeat":
        draw.text((left, top), "따라해 보세요", font=load_font(scale_size(24, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=(*accent_warm, 250), anchor="la")
        draw.text((left, top + scale_size(40, width=width, height=height, base_width=base_width, base_height=base_height)), "Repeat after me", font=load_font(scale_size(28, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=(244, 246, 248, 246), anchor="la")
        draw.text((left, top + scale_size(88, width=width, height=height, base_width=base_width, base_height=base_height)), lesson["sentenceKo"], font=load_font(scale_size(34, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=(*board_text, 255), anchor="la")
        draw.text((left, top + scale_size(134, width=width, height=height, base_width=base_width, base_height=base_height)), lesson["sentenceRomanization"], font=load_font(scale_size(20, width=width, height=height, base_width=base_width, base_height=base_height)), fill=(255, 220, 168, 240), anchor="la")
        repeat_sequence = repeat_sequence_from_packet(packet)
        lp = local_progress(scene, t)
        seq_index = min(len(repeat_sequence) - 1, int(lp * len(repeat_sequence)))
        current = repeat_sequence[seq_index]
        repeat_mark = "2/2" if seq_index % 2 == 1 else "1/2"
        center_x = board_rect[0] + (board_rect[2] - board_rect[0]) // 2
        draw.text((center_x, scale_size(570, width=width, height=height, base_width=base_width, base_height=base_height)), current["korean"], font=load_font(scale_size(112, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=(*board_text, 255), anchor="mm")
        draw.text((center_x, scale_size(676, width=width, height=height, base_width=base_width, base_height=base_height)), current["romanization"], font=load_font(scale_size(48, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=(*accent_warm, 252), anchor="mm")
        draw.text((center_x, scale_size(744, width=width, height=height, base_width=base_width, base_height=base_height)), current["gloss"], font=load_font(scale_size(36, width=width, height=height, base_width=base_width, base_height=base_height)), fill=(235, 238, 240, 236), anchor="mm")
        badge = scale_rect((580, 792, 760, 854), width=width, height=height, base_width=base_width, base_height=base_height)
        draw.rounded_rectangle(badge, radius=scale_size(28, width=width, height=height, base_width=base_width, base_height=base_height), fill=(*accent, 220))
        draw.text(((badge[0] + badge[2]) // 2, (badge[1] + badge[3]) // 2), repeat_mark, font=load_font(scale_size(28, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=(255, 255, 255, 255), anchor="mm")
        draw.text((footer_rect[0] + scale_size(26, width=width, height=height, base_width=base_width, base_height=base_height), footer_rect[1] + scale_size(28, width=width, height=height, base_width=base_width, base_height=base_height)), "각 단어를 두 번씩 천천히 반복합니다", font=load_font(scale_size(30, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=(255, 252, 246, 255), anchor="la")
        draw.text((footer_rect[0] + scale_size(26, width=width, height=height, base_width=base_width, base_height=base_height), footer_rect[1] + scale_size(82, width=width, height=height, base_width=base_width, base_height=base_height)), "집, 회사, 화장실 순서로 천천히 따라 읽어 보세요.", font=load_font(scale_size(22, width=width, height=height, base_width=base_width, base_height=base_height)), fill=(219, 228, 232, 232), anchor="la")
        return

    if scene_id == "scene-5-outro":
        draw.text((left, top), "오늘의 문장", font=load_font(scale_size(24, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=(*accent_warm, 250), anchor="la")
        y = top + scale_size(44, width=width, height=height, base_width=base_width, base_height=base_height)
        ko_font, ko_lines = fit_text(
            draw,
            lesson["sentenceKo"],
            max_width - scale_size(40, width=width, height=height, base_width=base_width, base_height=base_height),
            max_size=scale_size(52, width=width, height=height, base_width=base_width, base_height=base_height),
            min_size=scale_size(34, width=width, height=height, base_width=base_width, base_height=base_height),
        )
        for line in ko_lines:
            draw.text((left, y), line, font=ko_font, fill=(*board_text, 255), anchor="la")
            y += ko_font.size + scale_size(8, width=width, height=height, base_width=base_width, base_height=base_height, floor=3)
        draw.text((left, y + scale_size(6, width=width, height=height, base_width=base_width, base_height=base_height)), lesson["sentenceEn"], font=load_font(scale_size(28, width=width, height=height, base_width=base_width, base_height=base_height)), fill=(233, 236, 236, 240), anchor="la")
        y += scale_size(48, width=width, height=height, base_width=base_width, base_height=base_height)
        draw.text((left, y + scale_size(2, width=width, height=height, base_width=base_width, base_height=base_height)), lesson["sentenceRomanization"], font=load_font(scale_size(22, width=width, height=height, base_width=base_width, base_height=base_height)), fill=(*accent_warm, 250), anchor="la")
        cta_rect = scale_rect((68, 910, 1274, 990), width=width, height=height, base_width=base_width, base_height=base_height)
        draw.rounded_rectangle(cta_rect, radius=scale_size(28, width=width, height=height, base_width=base_width, base_height=base_height), fill=(*accent, 230))
        cta_text = f"{packet['cta']['caption']} — malmoelab.com"
        draw.text(((cta_rect[0] + cta_rect[2]) // 2, (cta_rect[1] + cta_rect[3]) // 2), cta_text, font=load_font(scale_size(28, width=width, height=height, base_width=base_width, base_height=base_height), bold=True), fill=(255, 255, 255, 255), anchor="mm")


def draw_board_scene(draw: ImageDraw.ImageDraw, packet: dict, scene: dict, t: float, *, width: int, height: int, mode: str):
    if mode == "wide":
        draw_board_scene_wide(draw, packet, scene, t, width=width, height=height)
        return
    draw_board_scene_vertical(draw, packet, scene, t, width=width, height=height)


async def synthesize_edge_tts(text: str, output_path: Path, *, voice: str, rate: str, pitch: str, volume: str):
    import edge_tts

    output_path.parent.mkdir(parents=True, exist_ok=True)
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, pitch=pitch, volume=volume)
    await communicate.save(str(output_path))


def clean_tts_text(text: str, *, fallback: str) -> str:
    value = str(text or "").strip()
    if not value:
        value = fallback
    value = re.sub(r"\([^)]*\)", "", value)
    value = value.replace("___", "...")
    value = value.replace("__", "...")
    value = value.replace("…", "...")
    value = re.sub(r"\s+", " ", value).strip()
    return value


def repeat_sequence_from_packet(packet: dict) -> list[dict]:
    for line in packet.get("narration", {}).get("lines", []):
        repeat_words = line.get("repeatWords")
        if not repeat_words:
            continue
        sequence: list[dict] = []
        for item in repeat_words:
            repeat_count = int(item.get("repeatCount") or 1)
            normalized = {
                "korean": item["ko"],
                "romanization": item["romanization"],
                "gloss": item["en"],
            }
            for _ in range(repeat_count):
                sequence.append(normalized)
        if sequence:
            return sequence
    choices = packet["choices"]
    return [choices[0], choices[0], choices[1], choices[1], choices[2], choices[2]]


def media_duration(path: Path) -> float:
    result = subprocess.run(
        [resolve_ffmpeg_binary(), "-i", str(path), "-f", "null", "-"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    output = result.stderr or ""
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", output)
    if not match:
        raise RuntimeError(f"Unable to determine media duration for {path}")
    hours = int(match.group(1))
    minutes = int(match.group(2))
    seconds = float(match.group(3))
    return hours * 3600 + minutes * 60 + seconds


def measure_audio_levels(audio_path: Path) -> tuple[float, float]:
    result = subprocess.run(
        [resolve_ffmpeg_binary(), "-i", str(audio_path), "-af", "volumedetect", "-f", "null", "-"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    output = result.stderr or ""
    mean_match = re.search(r"mean_volume:\s*(-?\d+(?:\.\d+)?) dB", output)
    max_match = re.search(r"max_volume:\s*(-?\d+(?:\.\d+)?) dB", output)
    if not mean_match or not max_match:
        raise RuntimeError(f"Unable to measure audio levels for {audio_path}")
    return float(mean_match.group(1)), float(max_match.group(1))


def normalize_audio_mean_volume(
    audio_path: Path,
    *,
    target_mean_db: float,
    peak_ceiling_db: float,
) -> Path:
    mean_db, max_db = measure_audio_levels(audio_path)
    desired_gain = target_mean_db - mean_db
    available_headroom = peak_ceiling_db - max_db
    applied_gain = min(desired_gain, available_headroom)
    if abs(applied_gain) < 0.1:
        return audio_path

    normalized_path = audio_path.with_name(f"{audio_path.stem}.norm{audio_path.suffix}")
    run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(audio_path),
            "-af",
            f"volume={applied_gain:+.2f}dB",
            str(normalized_path),
        ]
    )
    if normalized_path.is_file() and normalized_path.stat().st_size > 0:
        normalized_path.replace(audio_path)
    return audio_path


def trim_audio_edges(audio_path: Path) -> Path:
    trimmed_path = audio_path.with_name(f"{audio_path.stem}.trim{audio_path.suffix}")
    run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(audio_path),
            "-af",
            "silenceremove=start_periods=1:start_duration=0.05:start_threshold=-45dB:stop_periods=-1:stop_duration=0.10:stop_threshold=-45dB",
            str(trimmed_path),
        ]
    )
    if trimmed_path.is_file() and trimmed_path.stat().st_size > 0:
        trimmed_path.replace(audio_path)
    return audio_path


def edge_rate_from_multiplier(value: float | int | str | None, *, fallback: str) -> str:
    try:
        multiplier = float(value)
    except (TypeError, ValueError):
        return fallback
    pct = int(round((multiplier - 1.0) * 100))
    return f"{pct:+d}%"


def voice_profile(packet: dict, lang: str) -> dict:
    tracks = packet.get("narration", {}).get("tracks", {})
    track = tracks.get(lang, {})
    if lang == "ko":
        return {
            "voice": track.get("edgeVoice") or "ko-KR-InJoonNeural",
            "rate": edge_rate_from_multiplier(track.get("speedMultiplier"), fallback="-12%"),
            "pitch": str(track.get("pitch") or "-2Hz"),
            "gain": float(track.get("gain") or 1.0),
            "normalize": bool(track.get("normalizePerSegment") or False),
            "target_mean_db": float(track.get("targetMeanDb") or -19.0),
            "peak_ceiling_db": float(track.get("peakCeilingDb") or -2.0),
        }
    return {
        "voice": track.get("edgeVoice") or "en-US-GuyNeural",
        "rate": edge_rate_from_multiplier(track.get("speedMultiplier"), fallback="-6%"),
        "pitch": str(track.get("pitch") or "-1Hz"),
        "gain": float(track.get("gain") or 1.0),
        "normalize": bool(track.get("normalizePerSegment") or False),
        "target_mean_db": float(track.get("targetMeanDb") or -19.0),
        "peak_ceiling_db": float(track.get("peakCeilingDb") or -2.0),
    }


def build_render_timing_map(packet: dict, job: dict | None, tts_segments: list[dict]) -> dict:
    if not is_repeat_v3(packet, job or {}):
        return {}
    by_scene: dict[str, list[dict]] = {}
    for segment in tts_segments:
        scene_id = str(segment.get("scene_id") or "")
        if not scene_id:
            continue
        by_scene.setdefault(scene_id, []).append(
            {
                "relative_start": float(segment.get("relative_start") or 0.0),
                "duration": float(segment.get("duration") or 0.0),
                "lang": str(segment.get("lang") or ""),
                "text": str(segment.get("text") or ""),
            }
        )
    render_timings: dict[str, dict] = {}
    for raw_scene in (job or {}).get("scenes", []):
        scene_id = str(raw_scene.get("sceneId") or "")
        scene_segments = sorted(by_scene.get(scene_id, []), key=lambda item: item["relative_start"])
        render_timings[scene_id] = {"segments": scene_segments}
        if scene_id != "scene-4-repeat":
            continue
        overlay_sequence = (raw_scene.get("postOverlays") or {}).get("sequence") or []
        repeat_items = [item for item in overlay_sequence if item.get("textKo") and item.get("badge")]
        ko_repeat_segments = [
            item
            for item in scene_segments
            if item.get("lang") == "ko" and item.get("text") not in {"따라해 보세요.", "Repeat after me."}
        ]
        if ko_repeat_segments and repeat_items:
            render_timings[scene_id]["repeat_items"] = [
                {
                    "start": segment["relative_start"],
                    "textKo": item.get("textKo"),
                    "textRomanization": item.get("textRomanization"),
                    "textGloss": item.get("textGloss"),
                    "badge": item.get("badge"),
                }
                for item, segment in zip(repeat_items, ko_repeat_segments)
            ]
    return render_timings


def extract_audio_segment(video_path: Path, output_path: Path, *, start: float, duration: float) -> Path | None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        run_ffmpeg(
            [
                "ffmpeg",
                "-y",
                "-ss",
                f"{start:.3f}",
                "-i",
                str(video_path),
                "-t",
                f"{duration:.3f}",
                "-vn",
                "-ac",
                "2",
                "-ar",
                "24000",
                "-c:a",
                "aac",
                str(output_path),
            ]
        )
    except subprocess.CalledProcessError:
        return None
    if output_path.is_file():
        return output_path
    return None


def narration_segments(packet: dict, job: dict | None = None) -> list[dict]:
    if is_repeat_v3(packet, job or {}):
        segments: list[dict] = []
        for raw_scene in job.get("scenes", []):
            audio = raw_scene.get("audio") or {}
            sequence = audio.get("narrationSequence") or []
            if not sequence:
                continue
            scene_id = raw_scene["sceneId"]
            scene_start, _ = parse_scene_times(raw_scene.get("timeSec"))
            for item in sequence:
                text = clean_tts_text(item.get("text"), fallback="")
                if not text:
                    continue
                segments.append(
                    {
                        "start": scene_start,
                        "lang": item.get("lang", "ko"),
                        "text": text,
                        "pause_after": float(item.get("pauseAfterMs") or 0) / 1000.0,
                        "start_after_sfx": float(item.get("startAfterSfxMs") or 0) / 1000.0,
                        "scene_id": scene_id,
                        "scene_start": scene_start,
                    }
                )
        return segments

    lesson = packet["lesson"]
    narration_lines = packet.get("narration", {}).get("lines", [])
    scene1 = next((line for line in narration_lines if int(line.get("scene", 0)) == 1), {})
    instruction = next((line for line in narration_lines if int(line.get("scene", 0)) == 4 and line.get("ko") and line.get("en")), {})
    repeat_sequence = repeat_sequence_from_packet(packet)

    segments = [
        {
            "start": 3.05,
            "voice": "ko-KR-InJoonNeural",
            "rate": "-18%",
            "text": clean_tts_text(scene1.get("ko"), fallback=lesson["blankedSentenceKo"]),
        },
        {
            "start": 4.65,
            "voice": "en-US-JennyNeural",
            "rate": "-10%",
            "text": clean_tts_text(scene1.get("en"), fallback=lesson["blankedSentenceEn"]),
        },
        {
            "start": 16.05,
            "voice": "ko-KR-InJoonNeural",
            "rate": "-12%",
            "text": clean_tts_text(instruction.get("ko"), fallback="따라해 보세요."),
        },
        {
            "start": 16.75,
            "voice": "en-US-JennyNeural",
            "rate": "-8%",
            "text": clean_tts_text(instruction.get("en"), fallback="Repeat after me."),
        },
    ]

    base = 17.6
    step = 1.7
    for index, item in enumerate(repeat_sequence):
        start = base + index * step
        segments.append({"start": start, "voice": "ko-KR-InJoonNeural", "rate": "-4%", "text": f"{item['korean']}. {item['romanization']}."})
        segments.append({"start": start + 0.82, "voice": "en-US-JennyNeural", "rate": "-2%", "text": f"{item['romanization']}. {item['gloss']}."})
    return segments


def generate_tts_segments(packet: dict, output_dir: Path, *, job: dict | None = None) -> list[dict]:
    generated: list[dict] = []
    if is_repeat_v3(packet, job or {}):
        raw_segments = narration_segments(packet, job=job)
        cursor_by_scene: dict[str, float] = {}
        for index, segment in enumerate(raw_segments):
            profile = voice_profile(packet, segment["lang"])
            audio_path = output_dir / f"segment-{index:02d}.mp3"
            asyncio.run(
                synthesize_edge_tts(
                    segment["text"],
                    audio_path,
                    voice=profile["voice"],
                    rate=profile["rate"],
                    pitch=profile["pitch"],
                    volume="+0%",
                )
            )
            trim_audio_edges(audio_path)
            if profile.get("normalize"):
                normalize_audio_mean_volume(
                    audio_path,
                    target_mean_db=float(profile.get("target_mean_db") or -19.0),
                    peak_ceiling_db=float(profile.get("peak_ceiling_db") or -2.0),
                )
            duration = media_duration(audio_path)
            scene_id = str(segment["scene_id"])
            scene_start = float(segment["scene_start"])
            cursor = cursor_by_scene.get(scene_id, 0.0)
            relative_start = max(cursor, float(segment["start_after_sfx"]))
            start = scene_start + relative_start
            generated.append(
                {
                    "path": audio_path,
                    "start": start,
                    "relative_start": relative_start,
                    "scene_id": scene_id,
                    "duration": duration,
                    "volume": float(profile.get("gain") or 1.0),
                    "lang": str(segment["lang"]),
                    "text": str(segment["text"]),
                }
            )
            cursor_by_scene[scene_id] = relative_start + duration + float(segment["pause_after"])
        return generated

    for index, segment in enumerate(narration_segments(packet)):
        audio_path = output_dir / f"segment-{index:02d}.mp3"
        asyncio.run(
            synthesize_edge_tts(
                segment["text"],
                audio_path,
                voice=segment["voice"],
                rate=segment["rate"],
                pitch="-2Hz" if segment["voice"].startswith("ko-") else "+0Hz",
                volume="+0%",
            )
        )
        trim_audio_edges(audio_path)
        normalize_audio_mean_volume(audio_path, target_mean_db=-19.0, peak_ceiling_db=-2.0)
        generated.append({"path": audio_path, "start": segment["start"], "volume": 1.0})
    return generated


def generate_sine_effect(output_path: Path, *, frequency: int, duration: float, volume: float) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"sine=frequency={frequency}:duration={duration}:sample_rate=24000",
            "-filter:a",
            f"volume={volume}",
            str(output_path),
        ]
    )
    return output_path


def stretch_v3_scene_timeline(scenes: list[dict], tts_segments: list[dict], opening_audio_path: Path | None) -> list[dict]:
    required: dict[str, float] = {
        str(scene["id"]): float(scene.get("scene_duration") or max(scene["end"] - scene["start"], 0.1))
        for scene in scenes
    }
    for segment in tts_segments:
        scene_id = str(segment.get("scene_id") or "")
        if not scene_id:
            continue
        end = float(segment.get("relative_start", 0.0)) + float(segment.get("duration", 0.0))
        required[scene_id] = max(required.get(scene_id, 0.0), end)
    if opening_audio_path is not None and opening_audio_path.exists():
        required["scene-0-opening"] = max(required.get("scene-0-opening", 0.0), media_duration(opening_audio_path))

    updated = []
    cursor = 0.0
    for scene in scenes:
        clip_duration = float(scene.get("clip_duration") or max(scene["end"] - scene["start"], 0.1))
        base_duration = float(scene.get("scene_duration") or max(scene["end"] - scene["start"], 0.1))
        duration = max(base_duration, required.get(str(scene["id"]), base_duration))
        updated.append({**scene, "start": cursor, "end": cursor + duration, "scene_duration": duration, "clip_duration": clip_duration})
        cursor += duration
    return updated


def build_audio_mix(
    packet: dict,
    build_dir: Path,
    duration_seconds: int,
    *,
    job: dict | None = None,
    opening_video: Path | None = None,
    scenes: list[dict] | None = None,
    segments_override: list[dict] | None = None,
    opening_audio_override: Path | None = None,
) -> Path:
    narration_dir = build_dir / "renders" / "narration"
    sfx_dir = build_dir / "renders" / "sfx"
    tick_path = generate_sine_effect(sfx_dir / "tick.wav", frequency=1800, duration=0.05, volume=0.25)
    chime_path = generate_sine_effect(sfx_dir / "correct.wav", frequency=1046, duration=0.35, volume=0.25)
    segments = [dict(segment) for segment in segments_override] if segments_override is not None else generate_tts_segments(packet, narration_dir, job=job)

    opening_audio = opening_audio_override
    opening_audio_mode = str(packet.get("opening", {}).get("audioMode") or "embedded").strip().lower()
    if opening_audio is None and opening_audio_mode != "tts" and is_repeat_v3(packet, job or {}) and opening_video is not None:
        opening_scene = next((scene for scene in scenes or [] if scene["id"] == "scene-0-opening"), None)
        if opening_scene is not None:
            opening_duration = float(opening_scene.get("clip_duration") or max(opening_scene["end"] - opening_scene["start"], 0.1))
            opening_audio = extract_audio_segment(opening_video, narration_dir / "opening-audio.m4a", start=0.0, duration=opening_duration)
    if opening_audio is not None:
        segments.append({"path": opening_audio, "start": 0.0, "volume": 1.0})

    mix_path = narration_dir / "narration-mix.m4a"
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"anullsrc=r=24000:cl=stereo:d={duration_seconds}",
    ]
    filter_parts = []
    mix_inputs = ["[0:a]"]
    input_index = 1

    for segment in segments:
        cmd.extend(["-i", str(segment["path"])])
        delay_ms = max(0, int(segment["start"] * 1000))
        label = f"a{input_index}"
        volume = float(segment.get("volume", 1.0))
        filter_parts.append(f"[{input_index}:a]adelay={delay_ms}|{delay_ms},volume={volume}[{label}]")
        mix_inputs.append(f"[{label}]")
        input_index += 1

    if is_repeat_v3(packet, job or {}):
        scene_start_map = {str(scene["id"]): float(scene["start"]) for scene in scenes or []}
        for raw_scene in job.get("scenes", []):
            audio = raw_scene.get("audio") or {}
            sfx = audio.get("sfx")
            if not sfx:
                continue
            scene_start = scene_start_map.get(raw_scene.get("sceneId"), parse_scene_times(raw_scene.get("timeSec"))[0])
            if raw_scene.get("sceneId") == "scene-2-thinking":
                repeat_count = int(sfx.get("repeat") or 3)
                start_offset = float(sfx.get("startSec") or 1.0)
                for offset_index in range(repeat_count):
                    cmd.extend(["-i", str(tick_path)])
                    delay_ms = int((scene_start + start_offset + offset_index * 0.85) * 1000)
                    label = f"a{input_index}"
                    filter_parts.append(f"[{input_index}:a]adelay={delay_ms}|{delay_ms},volume=1.0[{label}]")
                    mix_inputs.append(f"[{label}]")
                    input_index += 1
                continue
            if raw_scene.get("sceneId") == "scene-3-answer":
                cmd.extend(["-i", str(chime_path)])
                delay_ms = int((scene_start + float(sfx.get("startSec") or 0.0)) * 1000)
                label = f"a{input_index}"
                filter_parts.append(f"[{input_index}:a]adelay={delay_ms}|{delay_ms},volume=1.0[{label}]")
                mix_inputs.append(f"[{label}]")
                input_index += 1
    else:
        for start in (6.3, 7.1, 7.9):
            cmd.extend(["-i", str(tick_path)])
            delay_ms = int(start * 1000)
            label = f"a{input_index}"
            filter_parts.append(f"[{input_index}:a]adelay={delay_ms}|{delay_ms},volume=1.0[{label}]")
            mix_inputs.append(f"[{label}]")
            input_index += 1

        cmd.extend(["-i", str(chime_path)])
        delay_ms = 11000
        label = f"a{input_index}"
        filter_parts.append(f"[{input_index}:a]adelay={delay_ms}|{delay_ms},volume=1.0[{label}]")
        mix_inputs.append(f"[{label}]")

    filter_parts.append(f"{''.join(mix_inputs)}amix=inputs={len(mix_inputs)}:dropout_transition=0,volume=1.0[out]")
    cmd.extend(
        [
            "-filter_complex",
            ";".join(filter_parts),
            "-map",
            "[out]",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            str(mix_path),
        ]
    )
    run_ffmpeg(cmd)
    return mix_path


def build_publish_packet(packet: dict, final_video: Path, thumbnail_file: Path) -> dict:
    lesson = packet["lesson"]
    return {
        "title": f"{lesson['answerWord']} Korean repeat lesson | MalmoeLab",
        "description": "\n".join(
            [
                "Grok-assisted Korean fill-blank and repeat short.",
                "",
                lesson["sentenceKo"],
                lesson["sentenceEn"],
                lesson["sentenceRomanization"],
                "",
                f"Learn more: {packet['cta']['url']}",
            ]
        ),
        "videoFile": str(final_video),
        "thumbnailFile": str(thumbnail_file),
        "privacyStatus": "private",
        "categoryId": "22",
        "tags": ["malmoelab", "learnkorean", "hangul", lesson["answerWord"]],
    }


def main() -> int:
    args = parse_args()
    source_packet_path = Path(args.source_packet).resolve()
    build_dir = Path(args.build_dir).resolve()
    packet = load_json(source_packet_path)
    job = load_episode_job(source_packet_path)
    scenes = build_scene_timeline(job)
    opening_video = resolve_project_path(packet.get("opening", {}).get("sourceFile"), base_dir=source_packet_path.parent) or Path(args.opening_video).resolve()

    width, height = parse_resolution(packet)
    mode = render_mode(width, height)
    opening_scene = next((scene for scene in scenes if scene["id"] == "scene-0-opening"), None)
    trim_start = float(packet.get("opening", {}).get("trimStartSec", 0.0))
    default_opening_duration = max(0.1, float(opening_scene["end"]) - float(opening_scene["start"])) if opening_scene else 3.0
    trim_end = float(packet.get("opening", {}).get("trimEndSec", trim_start + default_opening_duration))
    trim_duration = max(0.1, trim_end - trim_start)

    prebuilt_segments: list[dict] | None = None
    opening_audio_path: Path | None = None
    if is_repeat_v3(packet, job):
        narration_dir = build_dir / "renders" / "narration"
        prebuilt_segments = generate_tts_segments(packet, narration_dir, job=job)
        packet["_renderTimings"] = build_render_timing_map(packet, job, prebuilt_segments)
        opening_audio_mode = str(packet.get("opening", {}).get("audioMode") or "embedded").strip().lower()
        if opening_scene is not None and opening_audio_mode != "tts":
            opening_audio_path = extract_audio_segment(
                opening_video,
                narration_dir / "opening-audio.m4a",
                start=trim_start,
                duration=trim_duration,
            )
        scenes = stretch_v3_scene_timeline(scenes, prebuilt_segments, opening_audio_path)
        opening_scene = next((scene for scene in scenes if scene["id"] == "scene-0-opening"), None)

    opening_frames = extract_clip_frames(
        opening_video,
        build_dir / "renders" / "opening-frames",
        fps=FPS,
        width=width,
        height=height,
        start=trim_start,
        duration=trim_duration,
    )
    scene_frames = {}
    for scene in scenes:
        if scene["source"] == "opening":
            continue
        if scene["source"] == "fixed_clip":
            scene_video = resolve_project_path(scene.get("source_file"), base_dir=source_packet_path.parent)
            if scene_video is None:
                raise RuntimeError(f"Unable to resolve fixed clip for {scene['id']}")
        else:
            scene_video = build_dir / "renders" / "grok" / scene.get("output_name", f"{scene['id']}.mp4")
        scene_frames[scene["id"]] = extract_clip_frames(
            scene_video,
            build_dir / "renders" / "scene-frames" / scene["id"],
            fps=FPS,
            width=width,
            height=height,
            start=float(scene.get("source_start_sec") or 0.0),
            duration=float(scene.get("clip_duration") or max(scene["end"] - scene["start"], 0.1)),
        )

    frames_dir = build_dir / "renders" / "frames"
    final_dir = build_dir / "final"
    frames_dir.mkdir(parents=True, exist_ok=True)
    final_dir.mkdir(parents=True, exist_ok=True)
    for old in frames_dir.glob("frame-*.png"):
        old.unlink()

    total_duration_seconds = parse_total_duration_seconds(packet, scenes)
    total_frames = int(math.ceil(total_duration_seconds * FPS))
    for frame_index in range(total_frames):
        t = frame_index / FPS
        scene = scene_for_time(t, scenes)
        progress = clip_progress(scene, t)
        if scene["id"] == "scene-0-opening":
            base = pick_frame(opening_frames, progress)
        else:
            base = pick_frame(scene_frames[scene["id"]], progress)
        draw = ImageDraw.Draw(base, "RGBA")
        draw_title(draw, packet, width=width, height=height, mode=mode)
        draw_board_scene(draw, packet, scene, t, width=width, height=height, mode=mode)
        base.save(frames_dir / f"frame-{frame_index:04d}.png")

    video_only = build_dir / "renders" / "tmp-video-only.mp4"
    run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-framerate",
            str(FPS),
            "-i",
            str(frames_dir / "frame-%04d.png"),
            "-vf",
            f"fps={FPS},format=yuv420p",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(video_only),
        ]
    )

    audio_mix = build_audio_mix(
        packet,
        build_dir,
        int(math.ceil(total_duration_seconds)),
        job=job,
        opening_video=opening_video,
        scenes=scenes,
        segments_override=prebuilt_segments,
        opening_audio_override=opening_audio_path,
    )
    final_video_name = Path(job.get("postProduction", {}).get("outputFile") or f"./final/{packet['episodeSlug']}.mp4").name
    final_video = final_dir / final_video_name
    run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video_only),
            "-i",
            str(audio_mix),
            "-filter_complex",
            "[1:a]volume=1.0[aout]",
            "-map",
            "0:v:0",
            "-map",
            "[aout]",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-shortest",
            str(final_video),
        ]
    )

    thumbnail_second = float(job.get("postProduction", {}).get("thumbnailFromSceneSec") or packet.get("postProduction", {}).get("thumbnailFromSceneSec", 13))
    thumbnail_index = min(total_frames - 1, max(0, int(thumbnail_second * FPS)))
    thumbnail_name = Path(job.get("postProduction", {}).get("thumbnailFile") or f"./final/{packet['episodeSlug']}-thumb.png").name
    thumbnail = final_dir / thumbnail_name
    Image.open(frames_dir / f"frame-{thumbnail_index:04d}.png").save(thumbnail)
    publish_packet = build_publish_packet(packet, final_video, thumbnail)
    publish_path = build_dir / "publish-packet.json"
    publish_path.write_text(json.dumps(publish_packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"videoFile": str(final_video), "thumbnailFile": str(thumbnail), "publishPacket": str(publish_path)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
