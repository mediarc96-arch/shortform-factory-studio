#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import math
import os
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 1080
HEIGHT = 1920

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
FFMPEG_STATIC_CANDIDATES = [
    Path(os.environ.get("SHORTFORM_FFMPEG", "")).expanduser(),
    Path("/tmp/paperclip-ffmpeg/node_modules/ffmpeg-static/ffmpeg"),
    Path("/tmp/shortform-factory-bin/ffmpeg"),
]

DEFAULT_CONFIG = {
    "teacherImage": str(ROOT / "shared" / "backgrounds" / "images" / "korean" / "teacher.png"),
    "fps": 15,
    "durationSeconds": 30,
    "outputSlug": "",
    "buttonCaption": "Learn more at malmoelab.com",
    "ctaUrl": "https://malmoelab.com",
    "panelRect": [72, 268, 1008, 1516],
    "motionPanel": {
        "enabled": False,
        "videoFile": "",
        "loopMode": "pingpong",
        "outputDir": "renders/motion-panel",
    },
    "narration": {
        "enabled": False,
        "segments": [],
    },
    "lessonScript": {
        "enabled": False,
        "brandLabel": "MALMOELAB KOREAN LESSON",
        "scenes": [],
    },
    "theme": {
        "accent": "#4A7BFF",
        "accentWarm": "#FFC857",
        "text": "#FFFDF8",
        "mutedText": "#D7E0EA",
        "boardText": "#FFFDF8",
        "boardSubtext": "#DAE7DE",
        "boardFill": "#1F5A3D",
        "boardStroke": "#CFE6D6",
        "cardFill": "#09111C",
        "cardFillMuted": "#0F1826",
        "shadow": "#000000",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a scripted 30-second Korean lesson short.")
    parser.add_argument("--source-packet", required=True)
    parser.add_argument("--render-config", default="")
    parser.add_argument("--episode-dir", default="")
    return parser.parse_args()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def merge_config(base: dict, override: dict) -> dict:
    merged = json.loads(json.dumps(base))
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key].update(value)
        else:
            merged[key] = value
    return merged


def resolve_path(base_dir: Path, raw_value: str) -> Path:
    candidate = Path(str(raw_value or "")).expanduser()
    if not candidate.is_absolute():
        candidate = (base_dir / candidate).resolve()
    return candidate


def resolve_existing_path(base_dir: Path, raw_value: str) -> Path | None:
    normalized = str(raw_value or "").strip()
    if not normalized:
        return None
    candidate = resolve_path(base_dir, normalized)
    return candidate if candidate.exists() else None


def rgb(value: str) -> tuple[int, int, int]:
    value = str(value).lstrip("#")
    return tuple(int(value[index : index + 2], 16) for index in (0, 2, 4))


def load_font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = FONT_BOLD_CANDIDATES if bold else FONT_REGULAR_CANDIDATES
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size=size)
    raise RuntimeError(f"No usable {'bold' if bold else 'regular'} font found.")


def contain(image: Image.Image, *, width: int | None = None, height: int | None = None) -> Image.Image:
    if width is None and height is None:
        raise ValueError("Either width or height must be provided")
    source_w, source_h = image.size
    if width is not None and height is not None:
        scale = min(width / source_w, height / source_h)
    elif width is not None:
        scale = width / source_w
    else:
        scale = height / source_h
    return image.resize((max(1, int(source_w * scale)), max(1, int(source_h * scale))), Image.LANCZOS)


def cover(image: Image.Image, width: int, height: int) -> Image.Image:
    source_w, source_h = image.size
    scale = max(width / source_w, height / source_h)
    resized = image.resize((max(1, int(source_w * scale)), max(1, int(source_h * scale))), Image.LANCZOS)
    left = (resized.width - width) // 2
    top = (resized.height - height) // 2
    return resized.crop((left, top, left + width, top + height))


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


def fit_text(draw: ImageDraw.ImageDraw, text: str, max_width: int, *, max_size: int, min_size: int) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    for size in range(max_size, min_size - 1, -2):
        font = load_font(size, bold=True)
        lines = wrap_text(draw, text, font, max_width)
        if len(lines) <= 3:
            return font, lines
    font = load_font(min_size, bold=True)
    return font, wrap_text(draw, text, font, max_width)


def build_background(teacher_image: Image.Image) -> Image.Image:
    background = cover(teacher_image, WIDTH, HEIGHT).filter(ImageFilter.GaussianBlur(radius=18))
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (14, 22, 26, 150))
    background.alpha_composite(overlay)
    vignette = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    vignette_draw = ImageDraw.Draw(vignette, "RGBA")
    vignette_draw.ellipse((-240, -160, WIDTH + 240, HEIGHT + 260), fill=(255, 255, 255, 18))
    vignette = vignette.filter(ImageFilter.GaussianBlur(radius=80))
    background.alpha_composite(vignette)
    return background


def resolve_ffmpeg_binary() -> str:
    for candidate in FFMPEG_STATIC_CANDIDATES:
        if str(candidate).strip() and candidate.is_file():
            return str(candidate)
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg
    raise RuntimeError("No usable ffmpeg binary found. Set SHORTFORM_FFMPEG or install ffmpeg.")


def run_ffmpeg(cmd: list[str]) -> None:
    resolved_cmd = list(cmd)
    if resolved_cmd and resolved_cmd[0] == "ffmpeg":
        resolved_cmd[0] = resolve_ffmpeg_binary()
    elif resolved_cmd:
        resolved_cmd = [resolve_ffmpeg_binary(), *resolved_cmd]
    subprocess.run(resolved_cmd, check=True)


def extract_motion_panel_frames(video_path: Path, output_dir: Path, *, width: int, height: int, fps: int) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    for old_frame in output_dir.glob("frame-*.png"):
        old_frame.unlink()
    vf = (
        f"fps={fps},"
        f"scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height}"
    )
    run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video_path),
            "-vf",
            vf,
            "-start_number",
            "0",
            str(output_dir / "frame-%04d.png"),
        ]
    )
    frames = sorted(output_dir.glob("frame-*.png"))
    if not frames:
        raise RuntimeError(f"Failed to extract motion panel frames from {video_path}")
    return frames


def select_looped_frame(frames: list[Path], frame_index: int, loop_mode: str) -> Path:
    if not frames:
        raise RuntimeError("No motion frames available")
    if loop_mode == "pingpong" and len(frames) > 1:
        cycle = len(frames) * 2 - 2
        index_in_cycle = frame_index % cycle
        if index_in_cycle >= len(frames):
            index_in_cycle = cycle - index_in_cycle
        return frames[index_in_cycle]
    return frames[frame_index % len(frames)]


async def synthesize_edge_tts(text: str, output_path: Path, *, voice: str, rate: str, pitch: str, volume: str):
    import edge_tts

    output_path.parent.mkdir(parents=True, exist_ok=True)
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, pitch=pitch, volume=volume)
    await communicate.save(str(output_path))


def generate_narration_segments(config: dict, episode_dir: Path) -> list[dict]:
    narration_cfg = config.get("narration") or {}
    if not narration_cfg.get("enabled"):
        return []

    segments = narration_cfg.get("segments") or []
    output_dir = episode_dir / "renders" / "narration"
    output_dir.mkdir(parents=True, exist_ok=True)
    generated: list[dict] = []
    for index, segment in enumerate(segments):
        text = str(segment.get("text") or "").strip()
        if not text:
            continue
        start_at = float(segment.get("start") or 0.0)
        audio_path = output_dir / f"segment-{index:02d}.mp3"
        asyncio.run(
            synthesize_edge_tts(
                text,
                audio_path,
                voice=str(segment.get("voice") or "ko-KR-SunHiNeural"),
                rate=str(segment.get("rate") or "-10%"),
                pitch=str(segment.get("pitch") or "-2Hz"),
                volume=str(segment.get("volume") or "+0%"),
            )
        )
        generated.append({"path": audio_path, "start": start_at})
    return generated


def build_narration_mix(config: dict, episode_dir: Path, duration_seconds: int) -> Path | None:
    segments = generate_narration_segments(config, episode_dir)
    if not segments:
        return None

    narration_mix_path = episode_dir / "renders" / "narration" / "narration-mix.m4a"
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
    for index, segment in enumerate(segments, start=1):
        cmd.extend(["-i", str(segment["path"])])
        delay_ms = max(0, int(float(segment["start"]) * 1000))
        label = f"a{index}"
        filter_parts.append(f"[{index}:a]adelay={delay_ms}|{delay_ms},volume=1.08[{label}]")
        mix_inputs.append(f"[{label}]")

    filter_parts.append(f"{''.join(mix_inputs)}amix=inputs={len(mix_inputs)}:dropout_transition=0,volume=1.15[narr]")
    cmd.extend(
        [
            "-filter_complex",
            ";".join(filter_parts),
            "-map",
            "[narr]",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            narration_mix_path.as_posix(),
        ]
    )
    run_ffmpeg(cmd)
    return narration_mix_path


def mux_video_with_audio(video_only_path: Path, final_video: Path, *, narration_path: Path | None, duration_seconds: int):
    if not narration_path:
        video_only_path.replace(final_video)
        return

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(video_only_path),
        "-i",
        str(narration_path),
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
    run_ffmpeg(cmd)


def rounded_shadow(base: Image.Image, rect: tuple[int, int, int, int], *, radius: int, alpha: int = 120, blur: int = 22):
    left, top, right, bottom = rect
    width = right - left
    height = bottom - top
    shadow = Image.new("RGBA", (width + 40, height + 40), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow, "RGBA")
    shadow_draw.rounded_rectangle((20, 20, shadow.width - 20, shadow.height - 20), radius=radius, fill=(0, 0, 0, alpha))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur))
    base.alpha_composite(shadow, (left - 20, top - 12))


def draw_card(draw: ImageDraw.ImageDraw, rect: tuple[int, int, int, int], fill: tuple[int, int, int, int], radius: int):
    draw.rounded_rectangle(rect, radius=radius, fill=fill)


def draw_chalk_text(draw: ImageDraw.ImageDraw, position: tuple[int, int], text: str, font: ImageFont.FreeTypeFont, fill: tuple[int, int, int], anchor: str = "la"):
    x, y = position
    for dx, dy, alpha in ((0, 0, 255), (2, 2, 86), (-1, 0, 70), (0, -1, 58), (1, -1, 46)):
        draw.text((x + dx, y + dy), text, font=font, fill=(*fill, alpha), anchor=anchor)


def draw_alarm_clock(draw: ImageDraw.ImageDraw, center: tuple[int, int], progress: float):
    cx, cy = center
    pulse = 1.0 + math.sin(progress * math.pi * 6.0) * 0.06
    body_r = int(86 * pulse)
    bell_r = int(24 * pulse)
    draw.ellipse((cx - body_r, cy - body_r, cx + body_r, cy + body_r), fill=(255, 241, 201, 220), outline=(255, 205, 92, 255), width=8)
    draw.ellipse((cx - body_r + 18, cy - body_r + 18, cx + body_r - 18, cy + body_r - 18), fill=(245, 251, 255, 230))
    draw.ellipse((cx - body_r - 22, cy - body_r - 18, cx - body_r + 26, cy - body_r + 30), fill=(255, 204, 87, 235))
    draw.ellipse((cx + body_r - 26, cy - body_r - 18, cx + body_r + 22, cy - body_r + 30), fill=(255, 204, 87, 235))
    draw.line((cx, cy, cx, cy - 42), fill=(44, 71, 111, 255), width=10)
    draw.line((cx, cy, cx + 46, cy + 18), fill=(44, 71, 111, 255), width=10)
    draw.ellipse((cx - 10, cy - 10, cx + 10, cy + 10), fill=(44, 71, 111, 255))


def scene_at_time(scenes: list[dict], t: float) -> dict:
    if not scenes:
        return {}
    for scene in scenes:
        start = float(scene.get("start") or 0.0)
        end = float(scene.get("end") or 0.0)
        if start <= t < end:
            return scene
    return scenes[-1]


def scene_progress(scene: dict, t: float) -> float:
    start = float(scene.get("start") or 0.0)
    end = float(scene.get("end") or start + 1.0)
    duration = max(end - start, 0.001)
    return max(0.0, min((t - start) / duration, 1.0))


def draw_header(draw: ImageDraw.ImageDraw, config: dict, brand_label: str):
    theme = config["theme"]
    card_fill = rgb(theme.get("cardFill", "#09111C"))
    accent_warm = rgb(theme.get("accentWarm", "#FFC857"))
    text_color = rgb(theme.get("text", "#FFFDF8"))
    draw_card(draw, (42, 56, WIDTH - 42, 246), fill=(*card_fill, 194), radius=42)
    chip_font = load_font(30, bold=True)
    title_font, title_lines = fit_text(draw, "Korean listening and speaking practice", WIDTH - 180, max_size=62, min_size=42)
    draw.text((76, 98), brand_label, font=chip_font, fill=(*accent_warm, 255), anchor="la")
    title_y = 142
    for line in title_lines:
        draw.text((76, title_y), line, font=title_font, fill=(*text_color, 255), anchor="la")
        title_y += title_font.size + 6


def draw_footer(draw: ImageDraw.ImageDraw, scene: dict, config: dict):
    footer_title = str(scene.get("footerTitle") or "").strip()
    footer_lines = [str(line).strip() for line in (scene.get("footerLines") or []) if str(line).strip()]
    if not footer_title and not footer_lines:
        return

    theme = config["theme"]
    card_fill = rgb(theme.get("cardFillMuted", "#0F1826"))
    text_color = rgb(theme.get("text", "#FFFDF8"))
    muted_color = rgb(theme.get("mutedText", "#D7E0EA"))
    draw_card(draw, (42, 1540, WIDTH - 42, 1834), fill=(*card_fill, 210), radius=42)
    title_font = load_font(42, bold=True)
    body_font = load_font(30)
    draw.text((74, 1588), footer_title, font=title_font, fill=(*text_color, 255), anchor="la")
    line_y = 1658
    max_width = WIDTH - 148
    for line in footer_lines:
        for wrapped in wrap_text(draw, line, body_font, max_width):
            draw.text((76, line_y), wrapped, font=body_font, fill=(*muted_color, 235), anchor="la")
            line_y += body_font.size + 12


def draw_options_block(draw: ImageDraw.ImageDraw, options_title: str, options: list[str], rect: tuple[int, int, int, int]):
    left, top, right, _ = rect
    max_width = right - left
    label_font = load_font(28, bold=True)
    option_font = load_font(34, bold=True)
    body_font = load_font(30)
    label_y = top
    if options_title:
        draw.text((left, label_y), options_title, font=label_font, fill=(255, 223, 160, 244), anchor="la")
        label_y += 52
    current_y = label_y
    for option in options:
        parts = [part.strip() for part in option.split("|")]
        primary = parts[0] if parts else option
        secondary = parts[1] if len(parts) > 1 else ""
        draw.text((left, current_y), primary, font=option_font, fill=(247, 252, 246, 252), anchor="la")
        current_y += option_font.size + 2
        if secondary:
            for wrapped in wrap_text(draw, secondary, body_font, max_width):
                draw.text((left + 12, current_y), wrapped, font=body_font, fill=(222, 232, 226, 235), anchor="la")
                current_y += body_font.size + 10
        current_y += 18


def draw_repeat_list(draw: ImageDraw.ImageDraw, items: list[str], rect: tuple[int, int, int, int]):
    left, top, right, _ = rect
    max_width = right - left
    font = load_font(36, bold=True)
    sub_font = load_font(29)
    current_y = top
    for index, item in enumerate(items, start=1):
        parts = [part.strip() for part in item.split("|")]
        primary = parts[0] if parts else item
        secondary = parts[1] if len(parts) > 1 else ""
        badge_x = left
        badge_y = current_y + 6
        draw.rounded_rectangle((badge_x, badge_y, badge_x + 58, badge_y + 58), radius=18, fill=(79, 121, 255, 224))
        draw.text((badge_x + 29, badge_y + 29), str(index), font=load_font(28, bold=True), fill=(255, 255, 255, 255), anchor="mm")
        draw.text((left + 78, current_y), primary, font=font, fill=(248, 252, 248, 252), anchor="la")
        current_y += font.size + 2
        if secondary:
            for wrapped in wrap_text(draw, secondary, sub_font, max_width - 78):
                draw.text((left + 88, current_y), wrapped, font=sub_font, fill=(223, 233, 227, 234), anchor="la")
                current_y += sub_font.size + 8
        current_y += 18


def draw_scene_panel(draw: ImageDraw.ImageDraw, scene: dict, panel_rect: tuple[int, int, int, int], config: dict, progress: float):
    theme = config["theme"]
    board_fill = rgb(theme.get("boardFill", "#1F5A3D"))
    board_stroke = rgb(theme.get("boardStroke", "#CFE6D6"))
    board_text = rgb(theme.get("boardText", "#FFFDF8"))
    board_subtext = rgb(theme.get("boardSubtext", "#DAE7DE"))
    accent = rgb(theme.get("accent", "#4A7BFF"))
    accent_warm = rgb(theme.get("accentWarm", "#FFC857"))

    left, top, right, bottom = panel_rect
    inner = (left + 46, top + 52, right - 46, bottom - 52)
    draw.rounded_rectangle(inner, radius=36, fill=(*board_fill, 182), outline=(*board_stroke, 150), width=4)
    draw.rounded_rectangle((inner[0] + 12, inner[1] + 12, inner[2] - 12, inner[3] - 12), radius=28, outline=(255, 255, 255, 24), width=2)

    eyebrow = str(scene.get("eyebrow") or "").strip()
    headline = str(scene.get("headline") or "").strip()
    sublines = [str(line).strip() for line in (scene.get("sublines") or []) if str(line).strip()]
    options = [str(line).strip() for line in (scene.get("options") or []) if str(line).strip()]
    repeat_list = [str(line).strip() for line in (scene.get("repeatList") or []) if str(line).strip()]
    callout = str(scene.get("callout") or "").strip()
    badge = str(scene.get("badge") or "").strip()
    scene_kind = str(scene.get("kind") or "").strip().lower()

    eyebrow_font = load_font(28, bold=True)
    headline_font, headline_lines = fit_text(draw, headline, inner[2] - inner[0] - 80, max_size=72, min_size=44)
    sub_font = load_font(32)
    headline_y = inner[1] + 42

    if eyebrow:
        draw.text((inner[0] + 30, headline_y), eyebrow, font=eyebrow_font, fill=(*accent_warm, 252), anchor="la")
        headline_y += 54
    for line in headline_lines:
        draw_chalk_text(draw, (inner[0] + 30, headline_y), line, headline_font, board_text)
        headline_y += headline_font.size + 12

    if badge:
        badge_font = load_font(40, bold=True)
        badge_w = int(draw.textlength(badge, font=badge_font)) + 72
        badge_rect = (inner[2] - badge_w - 24, inner[1] + 28, inner[2] - 24, inner[1] + 28 + 70)
        draw.rounded_rectangle(badge_rect, radius=30, fill=(*accent, 222))
        draw.text(((badge_rect[0] + badge_rect[2]) // 2, (badge_rect[1] + badge_rect[3]) // 2), badge, font=badge_font, fill=(255, 255, 255, 255), anchor="mm")

    sub_y = headline_y + 18
    for line in sublines:
        for wrapped in wrap_text(draw, line, sub_font, inner[2] - inner[0] - 80):
            draw.text((inner[0] + 32, sub_y), wrapped, font=sub_font, fill=(*board_subtext, 240), anchor="la")
            sub_y += sub_font.size + 10
        sub_y += 4

    if callout:
        callout_font = load_font(34, bold=True)
        callout_y = min(sub_y + 18, inner[3] - 280)
        draw.rounded_rectangle((inner[0] + 30, callout_y, inner[2] - 30, callout_y + 72), radius=26, fill=(255, 200, 76, 36), outline=(255, 214, 124, 160), width=2)
        draw.text((inner[0] + 58, callout_y + 36), callout, font=callout_font, fill=(255, 236, 204, 255), anchor="lm")
        sub_y = callout_y + 98

    if options:
        draw_options_block(draw, str(scene.get("optionsTitle") or ""), options, (inner[0] + 32, sub_y + 10, inner[2] - 32, inner[3] - 34))
    if repeat_list:
        draw_repeat_list(draw, repeat_list, (inner[0] + 26, max(sub_y, inner[1] + 236), inner[2] - 28, inner[3] - 36))

    if scene_kind == "pause":
        draw_alarm_clock(draw, ((inner[0] + inner[2]) // 2, inner[1] + 640), progress)
    if scene_kind == "reveal":
        alpha = int(150 + progress * 105)
        answer_word = str(scene.get("answerWord") or "").strip()
        if answer_word:
            word_font = load_font(116, bold=True)
            draw.text(((inner[0] + inner[2]) // 2, inner[1] + 710), answer_word, font=word_font, fill=(255, 248, 233, alpha), anchor="mm")
            underline_w = int(draw.textlength(answer_word, font=word_font))
            underline_y = inner[1] + 788
            draw.rounded_rectangle(
                ((inner[0] + inner[2] - underline_w) // 2 - 14, underline_y, (inner[0] + inner[2] + underline_w) // 2 + 14, underline_y + 12),
                radius=6,
                fill=(255, 202, 90, int(160 + progress * 60)),
            )


def build_publish_packet(packet: dict, config: dict, final_video: Path, thumbnail_file: Path) -> dict:
    source = packet.get("source") or {}
    quiz = packet.get("quiz") or {}
    title = f"{source.get('wordText', 'Korean')} speaking lesson | MalmoeLab"
    description_lines = [
        "Scripted Korean short rendered with Grok motion plus deterministic overlays.",
        "",
        f"Korean: {quiz.get('fullSentence', '')}",
        f"English: {source.get('exampleTranslationText', '')}",
        f"Answer: {source.get('wordText', '')} ({source.get('wordRomanization', '')})",
        "",
        f"Study more: {config.get('ctaUrl', 'https://malmoelab.com')}",
    ]
    return {
        "title": title,
        "description": "\n".join(line for line in description_lines if line),
        "videoFile": str(final_video),
        "thumbnailFile": str(thumbnail_file),
        "privacyStatus": "private",
        "categoryId": "22",
        "tags": ["malmoelab", "learnkorean", "koreanlesson", source.get("wordText", "korean")],
    }


def main() -> int:
    args = parse_args()
    source_path = Path(args.source_packet).resolve()
    source_packet = load_json(source_path)
    episode_dir = Path(args.episode_dir).resolve() if args.episode_dir else source_path.parent
    config_path = Path(args.render_config).resolve() if args.render_config else episode_dir / "render-config.json"
    config = merge_config(DEFAULT_CONFIG, load_json(config_path) if config_path.exists() else {})

    teacher_path = Path(config["teacherImage"]).resolve()
    episode_dir.mkdir(parents=True, exist_ok=True)
    frames_dir = episode_dir / "renders" / "frames"
    final_dir = episode_dir / "final"
    frames_dir.mkdir(parents=True, exist_ok=True)
    final_dir.mkdir(parents=True, exist_ok=True)

    for old_frame in frames_dir.glob("frame-*.png"):
        old_frame.unlink()

    slug = str(config.get("outputSlug") or source_packet["episodeSlug"]).strip()
    fps = int(config["fps"])
    duration_seconds = int(config["durationSeconds"])
    total_frames = fps * duration_seconds
    panel_rect_values = config.get("panelRect") or [72, 268, 1008, 1516]
    panel_rect = tuple(int(value) for value in panel_rect_values)
    teacher_image = Image.open(teacher_path).convert("RGBA")
    background = build_background(teacher_image)

    motion_cfg = config.get("motionPanel") or {}
    motion_frames: list[Path] = []
    if motion_cfg.get("enabled"):
        video_path = resolve_existing_path(episode_dir, str(motion_cfg.get("videoFile") or ""))
        if video_path is None:
            raise RuntimeError("motionPanel.enabled is true but motionPanel.videoFile was not found.")
        motion_frames = extract_motion_panel_frames(
            video_path,
            resolve_path(episode_dir, str(motion_cfg.get("outputDir") or "renders/motion-panel")),
            width=panel_rect[2] - panel_rect[0],
            height=panel_rect[3] - panel_rect[1],
            fps=fps,
        )

    lesson_cfg = config.get("lessonScript") or {}
    brand_label = str(lesson_cfg.get("brandLabel") or "MALMOELAB KOREAN LESSON").strip()
    scenes = lesson_cfg.get("scenes") or []
    theme = config["theme"]
    card_fill = rgb(theme.get("cardFill", "#09111C"))

    for frame_index in range(total_frames):
        t = frame_index / fps
        frame = background.copy()
        draw = ImageDraw.Draw(frame, "RGBA")
        draw_header(draw, config, brand_label)

        rounded_shadow(frame, panel_rect, radius=42, alpha=128, blur=24)
        if motion_frames:
            panel_image = Image.open(select_looped_frame(motion_frames, frame_index, str(motion_cfg.get("loopMode") or "pingpong"))).convert("RGBA")
        else:
            panel_image = contain(teacher_image, width=panel_rect[2] - panel_rect[0], height=panel_rect[3] - panel_rect[1])
            panel_image = cover(panel_image, panel_rect[2] - panel_rect[0], panel_rect[3] - panel_rect[1])
        mask = Image.new("L", (panel_rect[2] - panel_rect[0], panel_rect[3] - panel_rect[1]), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, mask.width, mask.height), radius=42, fill=255)
        panel = Image.new("RGBA", panel_image.size, (0, 0, 0, 0))
        panel.paste(panel_image, mask=mask)
        frame.alpha_composite(panel, (panel_rect[0], panel_rect[1]))
        draw.rounded_rectangle(panel_rect, radius=42, outline=(255, 255, 255, 36), width=3)

        scene = scene_at_time(scenes, t)
        progress = scene_progress(scene, t)
        draw_scene_panel(draw, scene, panel_rect, config, progress)
        draw_footer(draw, scene, config)
        draw_card(draw, (74, 1848, WIDTH - 74, 1910), fill=(*card_fill, 190), radius=30)
        draw.text((WIDTH // 2, 1879), str(config.get("buttonCaption") or "Learn more at malmoelab.com"), font=load_font(28, bold=True), fill=(255, 255, 255, 245), anchor="mm")

        frame.save(frames_dir / f"frame-{frame_index:04d}.png")

    final_video = final_dir / f"{slug}.mp4"
    thumb_path = final_dir / f"{slug}-thumb.png"
    thumb_frame = frames_dir / f"frame-{min(total_frames - 1, int(fps * 12)):04d}.png"
    Image.open(thumb_frame).save(thumb_path)

    video_only_path = episode_dir / "renders" / f"tmp-{slug}-video-only.mp4"
    run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-framerate",
            str(fps),
            "-i",
            str(frames_dir / "frame-%04d.png"),
            "-vf",
            f"fps={fps},format=yuv420p",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(video_only_path),
        ]
    )

    narration_path = build_narration_mix(config, episode_dir, duration_seconds)
    mux_video_with_audio(video_only_path, final_video, narration_path=narration_path, duration_seconds=duration_seconds)

    publish_packet = build_publish_packet(source_packet, config, final_video, thumb_path)
    publish_packet_path = episode_dir / "publish-packet.json"
    publish_packet_path.write_text(json.dumps(publish_packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"videoFile": str(final_video), "thumbnailFile": str(thumb_path), "publishPacket": str(publish_packet_path)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
