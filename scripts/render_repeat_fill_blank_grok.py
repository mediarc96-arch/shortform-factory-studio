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

from PIL import Image, ImageDraw, ImageFilter, ImageFont


WIDTH = 1080
HEIGHT = 1920
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


def extract_clip_frames(video_path: Path, output_dir: Path, *, fps: int, start: float | None = None, duration: float | None = None) -> list[Path]:
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
            f"fps={fps},scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,crop={WIDTH}:{HEIGHT}",
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


def scene_for_time(t: float) -> dict:
    for scene in SCENES:
        if scene["start"] <= t < scene["end"]:
            return scene
    return SCENES[-1]


def local_progress(scene: dict, t: float) -> float:
    duration = max(scene["end"] - scene["start"], 0.001)
    return max(0.0, min((t - scene["start"]) / duration, 0.999999))


def draw_shadowed_card(base: Image.Image, rect: tuple[int, int, int, int], *, radius: int, alpha: int = 132, blur: int = 24):
    left, top, right, bottom = rect
    width = right - left
    height = bottom - top
    shadow = Image.new("RGBA", (width + 44, height + 44), (0, 0, 0, 0))
    ImageDraw.Draw(shadow, "RGBA").rounded_rectangle((22, 22, shadow.width - 22, shadow.height - 22), radius=radius, fill=(0, 0, 0, alpha))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=blur))
    base.alpha_composite(shadow, (left - 22, top - 10))


def draw_card(draw: ImageDraw.ImageDraw, rect: tuple[int, int, int, int], fill: tuple[int, int, int, int], radius: int):
    draw.rounded_rectangle(rect, radius=radius, fill=fill)


def draw_title(draw: ImageDraw.ImageDraw, packet: dict):
    header_rect = (44, 56, WIDTH - 44, 236)
    draw_card(draw, header_rect, fill=(7, 16, 28, 208), radius=40)
    chip_font = load_font(28, bold=True)
    title_font, title_lines = fit_text(draw, "Malmoelab Korean repeat practice", WIDTH - 170, max_size=58, min_size=40)
    draw.text((76, 100), "MALMOELAB HANGUL REPEAT", font=chip_font, fill=(255, 197, 96, 255), anchor="la")
    y = 144
    for line in title_lines:
        draw.text((76, y), line, font=title_font, fill=(255, 252, 245, 255), anchor="la")
        y += title_font.size + 6


def draw_alarm_clock(draw: ImageDraw.ImageDraw, center: tuple[int, int], progress: float):
    cx, cy = center
    pulse = 1.0 + math.sin(progress * math.pi * 6.0) * 0.08
    body_r = int(76 * pulse)
    bell_r = int(22 * pulse)
    draw.ellipse((cx - body_r, cy - body_r, cx + body_r, cy + body_r), fill=(255, 244, 209, 224), outline=(255, 199, 98, 255), width=8)
    draw.ellipse((cx - body_r + 18, cy - body_r + 18, cx + body_r - 18, cy + body_r - 18), fill=(249, 252, 255, 232))
    draw.ellipse((cx - body_r - 18, cy - body_r - 12, cx - body_r + 26, cy - body_r + 28), fill=(255, 204, 95, 236))
    draw.ellipse((cx + body_r - 26, cy - body_r - 12, cx + body_r + 18, cy - body_r + 28), fill=(255, 204, 95, 236))
    draw.line((cx, cy, cx, cy - 38), fill=(52, 77, 115, 255), width=9)
    draw.line((cx, cy, cx + 36, cy + 16), fill=(52, 77, 115, 255), width=9)
    draw.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), fill=(52, 77, 115, 255))


def draw_board_scene(draw: ImageDraw.ImageDraw, packet: dict, scene: dict, t: float):
    theme = packet["theme"]
    accent = rgb(theme["accent"])
    accent_warm = rgb(theme["accentWarm"])
    board_text = rgb(theme["boardText"])
    board_subtext = rgb(theme["boardSubtext"])

    board_rect = (76, 272, WIDTH - 76, 1494)
    footer_rect = (76, 1546, WIDTH - 76, 1826)
    draw_card(draw, board_rect, fill=(31, 88, 58, 164), radius=36)
    draw.rounded_rectangle(board_rect, radius=36, outline=(230, 240, 232, 120), width=3)
    draw_card(draw, footer_rect, fill=(10, 18, 30, 214), radius=36)

    left = board_rect[0] + 34
    top = board_rect[1] + 28
    max_width = board_rect[2] - board_rect[0] - 68
    scene_id = scene["id"]
    lesson = packet["lesson"]
    choices = packet["choices"]

    if scene_id == "scene-0-opening":
        title_font = load_font(76, bold=True)
        sub_font = load_font(38)
        draw.text((WIDTH // 2, 1012), "말모이랩 한글공부", font=title_font, fill=(*board_text, 255), anchor="mm")
        draw.text((WIDTH // 2, 1096), "Malmoelab Korean", font=sub_font, fill=(255, 223, 178, 242), anchor="mm")
        draw.text((WIDTH // 2, 1700), "30-second fill-blank and repeat lesson", font=load_font(32), fill=(235, 239, 242, 220), anchor="mm")
        return

    if scene_id in {"scene-1-question", "scene-2-thinking"}:
        eyebrow = "문장을 완성해 보세요" if scene_id == "scene-1-question" else "생각할 시간"
        draw.text((left, top), eyebrow, font=load_font(28, bold=True), fill=(*accent_warm, 250), anchor="la")
        y = top + 54
        ko_font, ko_lines = fit_text(draw, lesson["blankedSentenceKo"], max_width, max_size=64, min_size=48)
        for line in ko_lines:
            draw.text((left, y), line, font=ko_font, fill=(*board_text, 255), anchor="la")
            y += ko_font.size + 10
        draw.text((left, y + 6), lesson["blankedSentenceEn"], font=load_font(34), fill=(233, 236, 236, 240), anchor="la")
        y += 58
        draw.text((left, y + 4), lesson["blankedSentenceRomanization"], font=load_font(30), fill=(*accent_warm, 250), anchor="la")
        y += 90
        box_rect = (left, y, board_rect[2] - 30, y + 262)
        draw_card(draw, box_rect, fill=(8, 18, 30, 174), radius=28)
        draw.text((left + 22, y + 18), "보기", font=load_font(28, bold=True), fill=(255, 221, 164, 245), anchor="la")
        line_y = y + 72
        for item in choices:
            text = f"{item['order']}. {item['korean']}   {item['romanization']} ({item['gloss']})"
            draw.text((left + 24, line_y), text, font=load_font(34, bold=True), fill=(*board_text, 252), anchor="la")
            line_y += 58
        if scene_id == "scene-2-thinking":
            progress = local_progress(scene, t)
            draw_alarm_clock(draw, (board_rect[2] - 128, board_rect[3] - 144), progress)
            draw.text((left, board_rect[3] - 80), "또깍 또깍 또깍", font=load_font(34, bold=True), fill=(255, 235, 194, 252), anchor="la")
        draw.text((footer_rect[0] + 28, footer_rect[1] + 36), "천천히 듣고 정답을 생각해 보세요", font=load_font(40, bold=True), fill=(255, 252, 246, 255), anchor="la")
        draw.text((footer_rect[0] + 28, footer_rect[1] + 106), "Listen first, then choose the right word.", font=load_font(30), fill=(219, 228, 232, 232), anchor="la")
        return

    if scene_id == "scene-3-answer":
        draw.text((left, top), "정답 공개", font=load_font(28, bold=True), fill=(*accent_warm, 250), anchor="la")
        y = top + 54
        ko_font, ko_lines = fit_text(draw, lesson["sentenceKo"], max_width, max_size=64, min_size=48)
        for line in ko_lines:
            draw.text((left, y), line, font=ko_font, fill=(*board_text, 255), anchor="la")
            y += ko_font.size + 10
        draw.text((left, y + 10), lesson["sentenceEn"], font=load_font(34), fill=(233, 236, 236, 240), anchor="la")
        y += 60
        draw.text((left, y + 6), lesson["sentenceRomanization"], font=load_font(30), fill=(*accent_warm, 250), anchor="la")
        draw.rounded_rectangle((board_rect[2] - 170, top + 10, board_rect[2] - 22, top + 78), radius=28, fill=(*accent, 226))
        draw.text((board_rect[2] - 96, top + 44), "정답", font=load_font(34, bold=True), fill=(255, 255, 255, 255), anchor="mm")
        draw.text((WIDTH // 2, 1006), lesson["answerWord"], font=load_font(112, bold=True), fill=(*accent_warm, 255), anchor="mm")
        draw.rounded_rectangle((WIDTH // 2 - 82, 1068, WIDTH // 2 + 82, 1082), radius=7, fill=(*accent_warm, 240))
        draw.text((footer_rect[0] + 28, footer_rect[1] + 36), f"정답은 {lesson['answerWord']}", font=load_font(40, bold=True), fill=(255, 252, 246, 255), anchor="la")
        draw.text((footer_rect[0] + 28, footer_rect[1] + 106), "문장을 크게 보고 발음을 천천히 따라 읽을 준비를 하세요.", font=load_font(30), fill=(219, 228, 232, 232), anchor="la")
        return

    if scene_id == "scene-4-repeat":
        draw.text((left, top), "따라해 보세요", font=load_font(28, bold=True), fill=(*accent_warm, 250), anchor="la")
        draw.text((left, top + 52), "Repeat after me", font=load_font(32, bold=True), fill=(244, 246, 248, 246), anchor="la")
        draw.text((left, top + 110), lesson["sentenceKo"], font=load_font(40, bold=True), fill=(*board_text, 255), anchor="la")
        draw.text((left, top + 162), lesson["sentenceRomanization"], font=load_font(26), fill=(255, 220, 168, 240), anchor="la")

        repeat_sequence = [
            choices[0],
            choices[0],
            choices[1],
            choices[1],
            choices[2],
            choices[2],
        ]
        lp = local_progress(scene, t)
        seq_index = min(len(repeat_sequence) - 1, int(lp * len(repeat_sequence)))
        current = repeat_sequence[seq_index]
        repeat_mark = "2회" if seq_index % 2 == 1 else "1회"
        draw.text((WIDTH // 2, 980), current["korean"], font=load_font(132, bold=True), fill=(*board_text, 255), anchor="mm")
        draw.text((WIDTH // 2, 1098), current["romanization"], font=load_font(56, bold=True), fill=(*accent_warm, 252), anchor="mm")
        draw.text((WIDTH // 2, 1168), current["gloss"], font=load_font(46), fill=(235, 238, 240, 236), anchor="mm")
        draw.rounded_rectangle((WIDTH // 2 - 90, 1238, WIDTH // 2 + 90, 1302), radius=30, fill=(*accent, 220))
        draw.text((WIDTH // 2, 1270), repeat_mark, font=load_font(34, bold=True), fill=(255, 255, 255, 255), anchor="mm")
        draw.text((footer_rect[0] + 28, footer_rect[1] + 36), "각 단어를 두 번씩 천천히 반복합니다", font=load_font(38, bold=True), fill=(255, 252, 246, 255), anchor="la")
        draw.text((footer_rect[0] + 28, footer_rect[1] + 100), "집, 회사, 화장실 순서로 따라 읽어 보세요.", font=load_font(30), fill=(219, 228, 232, 232), anchor="la")
        return

    if scene_id == "scene-5-outro":
        draw.text((left, top), "오늘의 문장", font=load_font(28, bold=True), fill=(*accent_warm, 250), anchor="la")
        y = top + 54
        ko_font, ko_lines = fit_text(draw, lesson["sentenceKo"], max_width, max_size=64, min_size=48)
        for line in ko_lines:
            draw.text((left, y), line, font=ko_font, fill=(*board_text, 255), anchor="la")
            y += ko_font.size + 10
        draw.text((left, y + 8), lesson["sentenceEn"], font=load_font(34), fill=(233, 236, 236, 240), anchor="la")
        y += 60
        draw.text((left, y + 4), lesson["sentenceRomanization"], font=load_font(30), fill=(*accent_warm, 250), anchor="la")
        cta_rect = (footer_rect[0] + 22, footer_rect[1] + 30, footer_rect[2] - 22, footer_rect[1] + 112)
        draw.rounded_rectangle(cta_rect, radius=32, fill=(*accent, 230))
        draw.text((WIDTH // 2, footer_rect[1] + 72), packet["cta"]["caption"], font=load_font(34, bold=True), fill=(255, 255, 255, 255), anchor="mm")
        draw.text((WIDTH // 2, footer_rect[1] + 164), "malmoelab.com", font=load_font(30), fill=(235, 238, 240, 236), anchor="mm")


async def synthesize_edge_tts(text: str, output_path: Path, *, voice: str, rate: str, pitch: str, volume: str):
    import edge_tts

    output_path.parent.mkdir(parents=True, exist_ok=True)
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, pitch=pitch, volume=volume)
    await communicate.save(str(output_path))


def narration_segments(packet: dict) -> list[dict]:
    choices = packet["choices"]
    sequence = [choices[0], choices[0], choices[1], choices[1], choices[2], choices[2]]
    segments = [
        {"start": 3.05, "voice": "ko-KR-InJoonNeural", "rate": "-18%", "text": "저녁에는... 에서 쉽니다."},
        {"start": 4.65, "voice": "en-US-JennyNeural", "rate": "-10%", "text": "I relax at... in the evening."},
        {"start": 16.05, "voice": "ko-KR-InJoonNeural", "rate": "-12%", "text": "따라해 보세요."},
        {"start": 16.75, "voice": "en-US-JennyNeural", "rate": "-8%", "text": "Repeat after me."},
    ]
    base = 17.6
    step = 1.7
    for index, item in enumerate(sequence):
        start = base + index * step
        segments.append({"start": start, "voice": "ko-KR-InJoonNeural", "rate": "-4%", "text": f"{item['korean']}. {item['romanization']}."})
        segments.append({"start": start + 0.82, "voice": "en-US-JennyNeural", "rate": "-2%", "text": f"{item['romanization']}. {item['gloss']}."})
    return segments


def generate_tts_segments(packet: dict, output_dir: Path) -> list[dict]:
    generated: list[dict] = []
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
        generated.append({"path": audio_path, "start": segment["start"]})
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


def build_audio_mix(packet: dict, build_dir: Path, duration_seconds: int) -> Path:
    narration_dir = build_dir / "renders" / "narration"
    sfx_dir = build_dir / "renders" / "sfx"
    segments = generate_tts_segments(packet, narration_dir)
    tick_path = generate_sine_effect(sfx_dir / "tick.wav", frequency=1800, duration=0.05, volume=0.25)
    chime_path = generate_sine_effect(sfx_dir / "correct.wav", frequency=1046, duration=0.35, volume=0.25)

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
        filter_parts.append(f"[{input_index}:a]adelay={delay_ms}|{delay_ms},volume=1.0[{label}]")
        mix_inputs.append(f"[{label}]")
        input_index += 1

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

    filter_parts.append(f"{''.join(mix_inputs)}amix=inputs={len(mix_inputs)}:dropout_transition=0,volume=1.2[out]")
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
    opening_video = Path(args.opening_video).resolve()
    packet = load_json(source_packet_path)

    opening_frames = extract_clip_frames(opening_video, build_dir / "renders" / "opening-frames", fps=FPS, start=0.0, duration=3.0)
    scene_frames = {}
    for scene in SCENES[1:]:
        scene_frames[scene["id"]] = extract_clip_frames(
            build_dir / "renders" / "grok" / f"{scene['id']}.mp4",
            build_dir / "renders" / "scene-frames" / scene["id"],
            fps=FPS,
        )

    frames_dir = build_dir / "renders" / "frames"
    final_dir = build_dir / "final"
    frames_dir.mkdir(parents=True, exist_ok=True)
    final_dir.mkdir(parents=True, exist_ok=True)
    for old in frames_dir.glob("frame-*.png"):
        old.unlink()

    total_frames = int(packet["totalDurationSeconds"] * FPS)
    for frame_index in range(total_frames):
        t = frame_index / FPS
        scene = scene_for_time(t)
        progress = local_progress(scene, t)
        if scene["id"] == "scene-0-opening":
            base = pick_frame(opening_frames, progress)
        else:
            base = pick_frame(scene_frames[scene["id"]], progress)
        draw = ImageDraw.Draw(base, "RGBA")
        draw_title(draw, packet)
        draw_board_scene(draw, packet, scene, t)
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

    audio_mix = build_audio_mix(packet, build_dir, int(packet["totalDurationSeconds"]))
    final_video = final_dir / f"{packet['episodeSlug']}.mp4"
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

    thumbnail = final_dir / f"{packet['episodeSlug']}-thumb.png"
    Image.open(frames_dir / "frame-0390.png").save(thumbnail)
    publish_packet = build_publish_packet(packet, final_video, thumbnail)
    publish_path = build_dir / "publish-packet.json"
    publish_path.write_text(json.dumps(publish_packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"videoFile": str(final_video), "thumbnailFile": str(thumbnail), "publishPacket": str(publish_path)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
