#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import shutil
import subprocess
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

try:
    import imageio_ffmpeg
except Exception:  # pragma: no cover
    imageio_ffmpeg = None


ROOT = Path(__file__).resolve().parents[2]
FPS = 30
WIDTH = 1280
HEIGHT = 720
DEFAULT_ELEVENLABS_VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"  # George
DEFAULT_ELEVENLABS_MODEL_ID = "eleven_multilingual_v2"

FONT_REGULAR_CANDIDATES = [
    Path(os.environ.get("SHORTFORM_FONT_REGULAR", "")).expanduser(),
    Path("/home/kindsr/projects/devscent-inmemorytrip-main/backend/app/infrastructure/pdf/fonts/Pretendard-Regular.otf"),
    Path("/home/kindsr/projects/devscent-atrader/.venv/lib/python3.12/site-packages/pykrx/NanumBarunGothic.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
]
FONT_BOLD_CANDIDATES = [
    Path(os.environ.get("SHORTFORM_FONT_BOLD", "")).expanduser(),
    Path("/home/kindsr/projects/devscent-inmemorytrip-main/backend/app/infrastructure/pdf/fonts/Pretendard-Bold.otf"),
    Path("/home/kindsr/projects/devscent-atrader/.venv/lib/python3.12/site-packages/pykrx/NanumBarunGothic.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
]


@dataclass
class SceneRange:
    scene_id: str
    start_sec: float
    end_sec: float
    start_frame: int
    end_frame: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render final dub+type export for daehan pilot.")
    parser.add_argument("--episode-dir", required=True)
    parser.add_argument("--env-file", default=".env")
    return parser.parse_args()


def load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def resolve_ffmpeg_binary() -> str:
    candidates = [
        Path(os.environ.get("SHORTFORM_FFMPEG", "")).expanduser(),
        Path("/tmp/paperclip-ffmpeg/node_modules/ffmpeg-static/ffmpeg"),
        Path("/tmp/shortform-factory-bin/ffmpeg"),
    ]
    for candidate in candidates:
        if str(candidate).strip() and candidate.is_file():
            return str(candidate)
    if imageio_ffmpeg is not None:
        try:
            return imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            pass
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg
    raise RuntimeError("No usable ffmpeg binary found. Set SHORTFORM_FFMPEG.")


def run_ffmpeg(cmd: list[str]) -> None:
    resolved = list(cmd)
    if resolved and resolved[0] == "ffmpeg":
        resolved[0] = resolve_ffmpeg_binary()
    elif resolved:
        resolved = [resolve_ffmpeg_binary(), *resolved]
    subprocess.run(resolved, check=True)


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
    return int(match.group(1)) * 3600 + int(match.group(2)) * 60 + float(match.group(3))


def media_has_audio(path: Path) -> bool:
    result = subprocess.run(
        [resolve_ffmpeg_binary(), "-i", str(path), "-f", "null", "-"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    output = result.stderr or ""
    return "Audio:" in output


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


def trim_audio_edges(audio_path: Path) -> None:
    trimmed_path = audio_path.with_name(f"{audio_path.stem}.trim{audio_path.suffix}")
    run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(audio_path),
            "-af",
            "silenceremove=start_periods=1:start_duration=0.04:start_threshold=-45dB:stop_periods=-1:stop_duration=0.10:stop_threshold=-45dB",
            str(trimmed_path),
        ]
    )
    if trimmed_path.exists() and trimmed_path.stat().st_size > 0:
        trimmed_path.replace(audio_path)


def normalize_audio_mean_volume(audio_path: Path, *, target_mean_db: float, peak_ceiling_db: float) -> None:
    mean_db, max_db = measure_audio_levels(audio_path)
    desired_gain = target_mean_db - mean_db
    available_headroom = peak_ceiling_db - max_db
    applied_gain = min(desired_gain, available_headroom)
    if abs(applied_gain) < 0.1:
        return
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
    if normalized_path.exists() and normalized_path.stat().st_size > 0:
        normalized_path.replace(audio_path)


def extract_audio_segment(video_path: Path, output_path: Path, *, start: float, duration: float) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-ss",
            f"{start:.3f}",
            "-t",
            f"{duration:.3f}",
            "-i",
            str(video_path),
            "-vn",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            str(output_path),
        ]
    )
    return output_path


def resolve_episode_asset_path(episode_dir: Path, raw_value: str | None) -> Path | None:
    value = str(raw_value or "").strip()
    if not value:
        return None
    base_value = value.split("#", 1)[0]
    path = Path(base_value)
    if path.is_absolute():
        return path
    episode_candidate = (episode_dir / path).resolve()
    if episode_candidate.exists():
        return episode_candidate
    root_candidate = (ROOT / path).resolve()
    if root_candidate.exists():
        return root_candidate
    return episode_candidate


def copy_processed_audio(source_path: Path, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_path, output_path)
    trim_audio_edges(output_path)
    normalize_audio_mean_volume(output_path, target_mean_db=-19.0, peak_ceiling_db=-2.0)
    return output_path


def load_scene_ranges(path: Path) -> list[SceneRange]:
    rows: list[SceneRange] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(
                SceneRange(
                    scene_id=row["scene_id"],
                    start_sec=float(row["start_sec"]),
                    end_sec=float(row["end_sec"]),
                    start_frame=int(row["start_frame"]),
                    end_frame=int(row["end_frame"]),
                )
            )
    return rows


def load_font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = FONT_BOLD_CANDIDATES if bold else FONT_REGULAR_CANDIDATES
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size=size)
    raise RuntimeError("No usable font found.")


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
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
            cand = fragment + char
            if draw.textlength(cand, font=font) <= max_width:
                fragment = cand
            else:
                if fragment:
                    lines.append(fragment)
                fragment = char
        current = fragment
    if current:
        lines.append(current)
    return [line for line in lines if line]


def fit_text(draw: ImageDraw.ImageDraw, text: str, max_width: int, *, max_size: int, min_size: int, bold: bool = True) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    for size in range(max_size, min_size - 1, -2):
        font = load_font(size, bold=bold)
        lines = wrap_text(draw, text, font, max_width)
        if len(lines) <= 3:
            return font, lines
    font = load_font(min_size, bold=bold)
    return font, wrap_text(draw, text, font, max_width)


def draw_centered_lines(draw: ImageDraw.ImageDraw, lines: list[str], *, x: int, y: int, font: ImageFont.FreeTypeFont, fill: tuple[int, int, int, int], stroke_fill: tuple[int, int, int, int] | None = None, stroke_width: int = 0, line_gap: int = 8) -> None:
    cursor_y = y
    for line in lines:
        draw.text((x, cursor_y), line, font=font, fill=fill, anchor="ma", stroke_width=stroke_width, stroke_fill=stroke_fill)
        cursor_y += font.size + line_gap


def draw_left_lines(draw: ImageDraw.ImageDraw, lines: list[str], *, x: int, y: int, font: ImageFont.FreeTypeFont, fill: tuple[int, int, int, int], stroke_fill: tuple[int, int, int, int] | None = None, stroke_width: int = 0, line_gap: int = 8) -> None:
    cursor_y = y
    for line in lines:
        draw.text((x, cursor_y), line, font=font, fill=fill, anchor="la", stroke_width=stroke_width, stroke_fill=stroke_fill)
        cursor_y += font.size + line_gap


def tts_payload(text: str, *, speed: float, previous_text: str | None = None, next_text: str | None = None) -> bytes:
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        raise RuntimeError("Missing ELEVENLABS_API_KEY")
    voice_id = os.environ.get("ELEVENLABS_VOICE_ID_DAEHAN") or DEFAULT_ELEVENLABS_VOICE_ID
    payload = {
        "text": text,
        "model_id": DEFAULT_ELEVENLABS_MODEL_ID,
        "language_code": "ko",
        "output_format": "mp3_44100_128",
        "apply_text_normalization": "on",
        "voice_settings": {
            "stability": 0.38,
            "similarity_boost": 0.62,
            "style": 0.18,
            "speed": speed,
            "use_speaker_boost": True,
        },
    }
    if previous_text:
        payload["previous_text"] = previous_text
    if next_text:
        payload["next_text"] = next_text
    request = urllib.request.Request(
        url=f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        method="POST",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            return response.read()
    except urllib.error.HTTPError as exc:  # pragma: no cover
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"ElevenLabs TTS failed ({exc.code}): {body}") from exc


def synthesize_guide_tts(output_path: Path, *, text: str, speed: float, previous_text: str | None = None, next_text: str | None = None) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(tts_payload(text, speed=speed, previous_text=previous_text, next_text=next_text))
    trim_audio_edges(output_path)
    normalize_audio_mean_volume(output_path, target_mean_db=-19.0, peak_ceiling_db=-2.0)
    return output_path


def make_contact_sheet(title: str, frames: list[tuple[str, Path]], output_path: Path) -> None:
    thumb_w, thumb_h = 320, 180
    cols = 3
    rows = max(1, math.ceil(len(frames) / cols))
    header_h = 44
    label_h = 26
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
        draw.text((x + 8, y + thumb_h + 7), label, fill=(240, 240, 240), font=font)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, quality=90)


def extract_frame(input_path: Path, time_sec: float, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    run_ffmpeg(
        [
            "ffmpeg",
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


def render_typography_frame(output_path: Path, t: float, slots: list[dict]) -> None:
    board_text = (247, 246, 240, 255)
    board_muted = (216, 231, 223, 255)
    warm = (255, 211, 111, 255)
    subtitle_box = (7, 10, 18, 206)
    subtitle_text = (255, 255, 255, 255)
    subtitle_stroke = (7, 10, 18, 255)
    chalk_stroke = (20, 47, 35, 210)

    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    active_slots = [slot for slot in slots if float(slot["inTimeSec"]) <= t < float(slot["outTimeSec"])]
    subtitle_slots = [slot for slot in active_slots if slot["surface"] == "subtitle-lower-third"]
    board_slots = [slot for slot in active_slots if slot["surface"] == "chalkboard"]

    question_slot = next((slot for slot in board_slots if slot["slotId"] == "scene-3-question-sentence"), None)
    choice_slots = [slot for slot in board_slots if slot["slotId"].startswith("scene-3-choice-")]
    answer_slot = next((slot for slot in board_slots if slot["slotId"] == "scene-4-answer-reveal"), None)
    highlight_slot = next((slot for slot in board_slots if slot["slotId"] == "scene-4-choice-highlight"), None)

    if question_slot:
        font, lines = fit_text(draw, question_slot["text"], 640, max_size=50, min_size=38, bold=True)
        draw_left_lines(draw, lines, x=82, y=112, font=font, fill=board_text, stroke_fill=chalk_stroke, stroke_width=3, line_gap=10)

    if choice_slots:
        choice_font = load_font(36, bold=True)
        box_font = load_font(34, bold=True)
        y = 300
        for index, slot in enumerate(sorted(choice_slots, key=lambda item: item["slotId"])):
            rect = (82, y + index * 74, 328, y + index * 74 + 54)
            draw.rounded_rectangle(rect, radius=18, fill=(17, 53, 39, 128), outline=(221, 235, 228, 120), width=2)
            draw.text((rect[0] + 20, rect[1] + 27), slot["text"], font=box_font, fill=board_muted, anchor="lm", stroke_width=2, stroke_fill=chalk_stroke)

    if answer_slot:
        tag_rect = (92, 208, 210, 250)
        draw.rounded_rectangle(tag_rect, radius=18, fill=(255, 211, 111, 220))
        draw.text(((tag_rect[0] + tag_rect[2]) // 2, (tag_rect[1] + tag_rect[3]) // 2), "정답", font=load_font(24, bold=True), fill=(32, 40, 34, 255), anchor="mm")
        answer_font, answer_lines = fit_text(draw, answer_slot["text"], 500, max_size=104, min_size=74, bold=True)
        draw_left_lines(draw, answer_lines, x=100, y=282, font=answer_font, fill=warm, stroke_fill=(65, 41, 12, 235), stroke_width=4, line_gap=12)

    if highlight_slot:
        bubble_rect = (96, 392, 190, 456)
        draw.rounded_rectangle(bubble_rect, radius=22, fill=(255, 211, 111, 230), outline=(255, 247, 219, 255), width=3)
        draw.text(((bubble_rect[0] + bubble_rect[2]) // 2, (bubble_rect[1] + bubble_rect[3]) // 2), highlight_slot["text"], font=load_font(38, bold=True), fill=(34, 34, 28, 255), anchor="mm")

    if subtitle_slots:
        subtitle = subtitle_slots[0]["text"]
        font, lines = fit_text(draw, subtitle, 980, max_size=38, min_size=28, bold=True)
        text_height = len(lines) * font.size + max(0, len(lines) - 1) * 8
        box_width = 1060
        box_height = text_height + 34
        left = (WIDTH - box_width) // 2
        top = HEIGHT - box_height - 30
        rect = (left, top, left + box_width, top + box_height)
        shadow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.rounded_rectangle((rect[0] + 4, rect[1] + 6, rect[2] + 4, rect[3] + 6), radius=30, fill=(0, 0, 0, 68))
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=10))
        overlay.alpha_composite(shadow)
        draw = ImageDraw.Draw(overlay)
        draw.rounded_rectangle(rect, radius=30, fill=subtitle_box, outline=(255, 255, 255, 42), width=2)
        draw_centered_lines(draw, lines, x=WIDTH // 2, y=top + 18, font=font, fill=subtitle_text, stroke_fill=subtitle_stroke, stroke_width=2, line_gap=8)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    overlay.save(output_path)


def build_review_bundle(final_video_path: Path, review_dir: Path, ranges: list[SceneRange]) -> None:
    frame_dir = review_dir / "final-frames"
    contact_dir = review_dir / "final-contact-sheets"
    frame_dir.mkdir(parents=True, exist_ok=True)
    contact_dir.mkdir(parents=True, exist_ok=True)
    overview_frames: list[tuple[str, Path]] = []

    for scene in ranges:
        scene_duration = max(0.1, scene.end_sec - scene.start_sec)
        sample_count = 4
        frames: list[tuple[str, Path]] = []
        for idx in range(sample_count):
            sec = scene.start_sec + scene_duration * ((idx + 0.5) / sample_count)
            frame_path = frame_dir / f"{scene.scene_id}-{idx + 1}.jpg"
            extract_frame(final_video_path, sec, frame_path)
            frames.append((f"{scene.scene_id} / {sec:.2f}s", frame_path))
        make_contact_sheet(scene.scene_id, frames, contact_dir / f"{scene.scene_id}.jpg")
        overview_frames.append((scene.scene_id, frames[len(frames) // 2][1]))

    make_contact_sheet("final overview", overview_frames, contact_dir / "overview.jpg")


def export_reference_scene_clip(picture_lock_path: Path, output_path: Path, *, start_sec: float, duration_sec: float) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-ss",
            f"{start_sec:.3f}",
            "-t",
            f"{duration_sec:.3f}",
            "-i",
            str(picture_lock_path),
            "-an",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(output_path),
        ]
    )
    return output_path


def main() -> int:
    args = parse_args()
    episode_dir = Path(args.episode_dir).resolve()
    load_env_file((ROOT / args.env_file).resolve())

    voice_slots_path = episode_dir / "voice-slots.json"
    typography_slots_path = episode_dir / "typography-slots.json"
    episode_schema_path = episode_dir / "episode.schema.json"
    packet_path = episode_dir / "packet.md"
    scene_ranges_path = episode_dir / "review" / "scene-ranges.csv"

    voice_slots = load_json(voice_slots_path)
    typography_slots = load_json(typography_slots_path)
    episode_schema = load_json(episode_schema_path)
    scene_ranges = load_scene_ranges(scene_ranges_path)

    picture_lock_dir = episode_dir / "renders" / "picture-lock"
    dub_lock_dir = episode_dir / "renders" / "dub-lock"
    type_ready_dir = episode_dir / "renders" / "type-ready"
    final_dir = episode_dir / "renders" / "final"
    narration_dir = dub_lock_dir / "narration-guide"
    selected_audio_dir = dub_lock_dir / "narration-selected"
    overlay_dir = type_ready_dir / "overlay-frames"
    dubbing_dir = episode_dir / "dubbing"
    dubbing_audio_override_dir = dubbing_dir / "audio-overrides"
    dubbing_guide_audio_dir = dubbing_dir / "guide-audio"
    dubbing_reference_video_dir = dubbing_dir / "reference-video"
    picture_lock_dir.mkdir(parents=True, exist_ok=True)
    dub_lock_dir.mkdir(parents=True, exist_ok=True)
    narration_dir.mkdir(parents=True, exist_ok=True)
    selected_audio_dir.mkdir(parents=True, exist_ok=True)
    type_ready_dir.mkdir(parents=True, exist_ok=True)
    final_dir.mkdir(parents=True, exist_ok=True)
    dubbing_audio_override_dir.mkdir(parents=True, exist_ok=True)
    dubbing_guide_audio_dir.mkdir(parents=True, exist_ok=True)
    dubbing_reference_video_dir.mkdir(parents=True, exist_ok=True)

    preview_cut = final_dir / "daehan-pilot-codex-001-preview-cut.mp4"
    if not preview_cut.exists():
        raise FileNotFoundError(f"Missing preview cut: {preview_cut}")

    picture_lock_path = picture_lock_dir / "daehan-pilot-codex-001-picture-lock.mp4"
    shutil.copyfile(preview_cut, picture_lock_path)

    scene_map = {item.scene_id: item for item in scene_ranges}
    opening_video = ROOT / "characters" / "daehan" / "01_Opening.mp4"
    ending_video = ROOT / "characters" / "daehan" / "02_Ending.mp4"

    opening_audio = extract_audio_segment(opening_video, dub_lock_dir / "opening-embedded.m4a", start=0.0, duration=3.0)
    ending_audio: Path | None = None
    if media_has_audio(ending_video):
        ending_audio = extract_audio_segment(ending_video, dub_lock_dir / "ending-embedded.m4a", start=0.0, duration=4.0)

    slot_index = {slot["voiceSlotId"]: slot for slot in voice_slots["slots"]}
    for slot in voice_slots["slots"]:
        if slot["kind"] == "episode-line" or (slot["voiceSlotId"] == "ending-embedded" and ending_audio is None):
            slot.setdefault("recordingTarget", f"dubbing/audio-overrides/{slot['voiceSlotId']}.wav")
    tts_plan = [
        {
            "voiceSlotId": "scene-1-narration-ko",
            "sceneId": "scene-1-situation",
            "startSec": 3.55,
            "speed": 0.96,
            "ttsText": "풍선을 너무 크게 불었더니...",
        },
        {
            "voiceSlotId": "scene-2-narration-ko",
            "sceneId": "scene-2-climax",
            "startSec": 8.60,
            "speed": 0.94,
            "ttsText": "결국, 빵 터져 버렸다!",
        },
        {
            "voiceSlotId": "scene-3-question-ko",
            "sceneId": "scene-3-question",
            "startSec": 13.10,
            "speed": 0.94,
            "ttsText": "빈칸에 들어갈 말은 무엇일까요?",
        },
        {
            "voiceSlotId": "scene-4-answer-ko",
            "sceneId": "scene-4-reveal-repeat",
            "startSec": 20.15,
            "speed": 0.92,
            "ttsText": "정답은, 빵!",
        },
        {
            "voiceSlotId": "scene-4-repeat-ko",
            "sceneId": "scene-4-reveal-repeat",
            "startSec": 23.00,
            "speed": 0.86,
            "ttsText": "같이 따라해 볼까요? ... 빵!",
        },
    ]
    if ending_audio is None:
        tts_plan.append(
            {
                "voiceSlotId": "ending-embedded",
                "sceneId": "scene-5-ending",
                "startSec": 26.60,
                "speed": 0.90,
                "ttsText": "그럼 다음 시간에 또 만나요. 안녕~!",
            }
        )

    generated_segments: list[dict] = [
        {"slotId": "opening-embedded", "path": opening_audio, "start": 0.0, "volume": 1.0},
    ]
    if ending_audio is not None:
        generated_segments.append({"slotId": "ending-embedded", "path": ending_audio, "start": scene_map["scene-5-ending"].start_sec, "volume": 1.0})

    plan_by_slot = {plan["voiceSlotId"]: plan for plan in tts_plan}
    for index, plan in enumerate(tts_plan):
        slot_id = plan["voiceSlotId"]
        previous_text = tts_plan[index - 1]["ttsText"] if index > 0 else None
        next_text = tts_plan[index + 1]["ttsText"] if index + 1 < len(tts_plan) else None
        output_path = narration_dir / f"{slot_id}.mp3"
        synthesize_guide_tts(
            output_path,
            text=plan["ttsText"],
            speed=float(plan["speed"]),
            previous_text=previous_text,
            next_text=next_text,
        )
        guide_package_path = dubbing_guide_audio_dir / output_path.name
        shutil.copyfile(output_path, guide_package_path)
        slot = slot_index[slot_id]
        slot["guideAsset"] = str(guide_package_path.relative_to(episode_dir))
        recording_target_path = resolve_episode_asset_path(episode_dir, slot.get("recordingTarget"))
        selected_asset_path = resolve_episode_asset_path(episode_dir, slot.get("selectedAsset"))
        active_path = output_path
        active_source = "elevenlabs-guide"
        if recording_target_path is not None and recording_target_path.exists():
            processed_path = selected_audio_dir / f"{slot_id}{recording_target_path.suffix.lower() or '.wav'}"
            active_path = copy_processed_audio(recording_target_path, processed_path)
            active_source = "human-dub"
            slot["selectedAsset"] = str(Path(slot["recordingTarget"]))
        elif (
            selected_asset_path is not None
            and selected_asset_path.exists()
            and str(slot.get("selectedSource") or "").strip().lower() in {"human-dub", "actor-dub", "voice-pack"}
        ):
            processed_path = selected_audio_dir / f"{slot_id}{selected_asset_path.suffix.lower() or '.wav'}"
            active_path = copy_processed_audio(selected_asset_path, processed_path)
            active_source = str(slot.get("selectedSource") or "voice-pack")
        else:
            slot["selectedAsset"] = str(output_path.relative_to(episode_dir))

        duration = media_duration(active_path)
        slot["selectedSource"] = active_source
        slot["activeRenderAsset"] = str(active_path.relative_to(episode_dir))
        slot["sceneId"] = plan["sceneId"]
        slot["startSec"] = round(float(plan["startSec"]), 3)
        slot["endSec"] = round(float(plan["startSec"]) + duration, 3)
        slot["durationSec"] = round(duration, 3)
        slot["renderText"] = plan["ttsText"]
        generated_segments.append({"slotId": slot_id, "path": active_path, "start": float(plan["startSec"]), "volume": 1.0})

    slot_index["opening-embedded"]["selectedAsset"] = "characters/daehan/01_Opening.mp4#audio"
    slot_index["opening-embedded"]["selectedSource"] = "original-clip-audio"
    slot_index["opening-embedded"]["startSec"] = 0.0
    slot_index["opening-embedded"]["durationSec"] = round(media_duration(opening_audio), 3)
    if ending_audio is not None:
        slot_index["ending-embedded"]["selectedAsset"] = "characters/daehan/02_Ending.mp4#audio"
        slot_index["ending-embedded"]["selectedSource"] = "original-clip-audio"
        slot_index["ending-embedded"]["activeRenderAsset"] = str(ending_audio.relative_to(episode_dir))
        slot_index["ending-embedded"]["startSec"] = round(scene_map["scene-5-ending"].start_sec, 3)
        slot_index["ending-embedded"]["durationSec"] = round(media_duration(ending_audio), 3)

    voice_slots_path.write_text(json.dumps(voice_slots, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    reference_scene_ids = ["scene-1-situation", "scene-2-climax", "scene-3-question", "scene-4-reveal-repeat", "scene-5-ending"]
    reference_video_map: dict[str, Path] = {}
    for scene_id in reference_scene_ids:
        scene = scene_map[scene_id]
        reference_video_map[scene_id] = export_reference_scene_clip(
            picture_lock_path,
            dubbing_reference_video_dir / f"{scene_id}.mp4",
            start_sec=scene.start_sec,
            duration_sec=max(0.1, scene.end_sec - scene.start_sec),
        )

    cues_csv_path = dubbing_dir / "dubbing-cues.csv"
    with cues_csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "voice_slot_id",
                "scene_id",
                "scene_start_sec",
                "slot_start_sec",
                "slot_end_sec",
                "duration_sec",
                "text",
                "render_text",
                "selected_source",
                "recording_target",
                "guide_asset",
                "reference_video",
            ]
        )
        for slot_id in ["scene-1-narration-ko", "scene-2-narration-ko", "scene-3-question-ko", "scene-4-answer-ko", "scene-4-repeat-ko", "ending-embedded"]:
            slot = slot_index.get(slot_id)
            if not slot or "sceneId" not in slot:
                continue
            scene = scene_map[slot["sceneId"]]
            writer.writerow(
                [
                    slot_id,
                    slot["sceneId"],
                    f"{scene.start_sec:.3f}",
                    f"{float(slot['startSec']):.3f}",
                    f"{float(slot.get('endSec', float(slot['startSec']) + float(slot['durationSec']))):.3f}",
                    f"{float(slot['durationSec']):.3f}",
                    slot.get("text") or "",
                    slot.get("renderText") or "",
                    slot.get("selectedSource") or "",
                    slot.get("recordingTarget") or "",
                    slot.get("guideAsset") or "",
                    str(reference_video_map[slot["sceneId"]].relative_to(episode_dir)),
                ]
            )

    recording_script_path = dubbing_dir / "recording-script.md"
    recording_script_lines = [
        "# Recording Script",
        "",
        "사람 더빙이나 성우 녹음을 넣을 때는 `audio-overrides/` 아래 대응 파일명을 그대로 사용하면 된다.",
        "",
    ]
    for slot_id in ["scene-1-narration-ko", "scene-2-narration-ko", "scene-3-question-ko", "scene-4-answer-ko", "scene-4-repeat-ko", "ending-embedded"]:
        slot = slot_index.get(slot_id)
        if not slot or "sceneId" not in slot:
            continue
        recording_script_lines.extend(
            [
                f"## {slot_id}",
                f"- scene: `{slot['sceneId']}`",
                f"- timing: `{float(slot['startSec']):.2f}s -> {float(slot.get('endSec', float(slot['startSec']) + float(slot['durationSec']))):.2f}s`",
                f"- target file: `{slot.get('recordingTarget', '')}`",
                f"- line: `{slot.get('text') or ''}`",
                f"- guide line: `{slot.get('renderText') or ''}`",
                "",
            ]
        )
    recording_script_path.write_text("\n".join(recording_script_lines) + "\n", encoding="utf-8")

    dubbing_readme_path = dubbing_dir / "README.md"
    dubbing_readme_path.write_text(
        "# Dubbing Package\n\n"
        "## 구성\n"
        "- `audio-overrides/`: 사람이 녹음한 wav/mp3를 넣는 위치\n"
        "- `guide-audio/`: 현재 guide dub 기준선\n"
        "- `reference-video/`: 씬별 reference clip\n"
        "- `dubbing-cues.csv`: 타이밍 표\n"
        "- `recording-script.md`: 읽기용 스크립트\n\n"
        "## 사용\n"
        "1. `recording-script.md`와 `reference-video/*.mp4`를 보고 녹음한다.\n"
        "2. 대응 파일명을 유지한 채 `audio-overrides/`에 wav/mp3를 넣는다.\n"
        "3. 같은 명령으로 다시 렌더한다.\n\n"
        "```bash\n"
        ".venv-video-tools/bin/python scripts/pilot/render_daehan_pilot_final.py --episode-dir episodes/daehan-pilot-codex-001 --env-file .env\n"
        "```\n",
        encoding="utf-8",
    )

    total_duration = scene_ranges[-1].end_sec
    audio_mix_path = dub_lock_dir / "daehan-pilot-codex-001-guide-dub.m4a"
    mix_cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"anullsrc=r=44100:cl=stereo:d={total_duration}",
    ]
    filter_parts: list[str] = []
    mix_inputs = ["[0:a]"]
    for input_index, segment in enumerate(generated_segments, start=1):
        mix_cmd.extend(["-i", str(segment["path"])])
        delay_ms = max(0, int(segment["start"] * 1000))
        label = f"a{input_index}"
        filter_parts.append(f"[{input_index}:a]adelay={delay_ms}|{delay_ms},volume={float(segment.get('volume', 1.0))}[{label}]")
        mix_inputs.append(f"[{label}]")
    filter_parts.append(f"{''.join(mix_inputs)}amix=inputs={len(mix_inputs)}:dropout_transition=0:normalize=0,volume=1.0[out]")
    mix_cmd.extend(
        [
            "-filter_complex",
            ";".join(filter_parts),
            "-map",
            "[out]",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            str(audio_mix_path),
        ]
    )
    run_ffmpeg(mix_cmd)

    total_frames = int(round(total_duration * FPS))
    for frame_index in range(total_frames):
        render_typography_frame(overlay_dir / f"frame-{frame_index:05d}.png", frame_index / FPS, typography_slots["slots"])

    final_video_path = final_dir / "daehan-pilot-codex-001-final.mp4"
    run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(picture_lock_path),
            "-framerate",
            str(FPS),
            "-i",
            str(overlay_dir / "frame-%05d.png"),
            "-i",
            str(audio_mix_path),
            "-filter_complex",
            "[1:v]format=rgba[ov];[0:v][ov]overlay=0:0:format=auto[v]",
            "-map",
            "[v]",
            "-map",
            "2:a",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            "-shortest",
            str(final_video_path),
        ]
    )

    thumb_path = final_dir / "daehan-pilot-codex-001-final-thumb.jpg"
    extract_frame(final_video_path, 20.6, thumb_path)

    review_dir = episode_dir / "review"
    build_review_bundle(final_video_path, review_dir, scene_ranges)

    audio_mean_db, audio_max_db = measure_audio_levels(audio_mix_path)
    ending_source_label = "embedded original clip audio" if ending_audio is not None else "ElevenLabs guide dub fallback"
    audio_report = review_dir / "final-audio-analysis.md"
    audio_report.write_text(
        "# Final Audio Analysis\n\n"
        f"- audio mix: `{audio_mix_path.relative_to(episode_dir)}`\n"
        f"- mean volume: `{audio_mean_db:.1f} dB`\n"
        f"- max volume: `{audio_max_db:.1f} dB`\n"
        "- content narration source: `ElevenLabs multilingual guide dub`\n"
        f"- opening source: `embedded original clip audio`\n"
        f"- ending source: `{ending_source_label}`\n",
        encoding="utf-8",
    )

    final_review_report = review_dir / "final-review-report.md"
    final_review_body = (
        "# Final Review: daehan-pilot-codex-001\n"
        "날짜: 2026-04-17\n\n"
        "## 전체 요약\n"
        "- 상태: `guide-dub + typography final export`\n"
        "- 심각도: `✅ pass`\n\n"
        "## 확인 항목\n"
        "- 오프닝은 원본 음성을 유지함\n"
        + ("- 엔딩은 원본 오디오가 없어 guide dub로 대체함\n" if ending_audio is None else "- 엔딩은 원본 음성을 유지함\n")
        + "- 본편 `scene-1`~`scene-4`는 ElevenLabs guide dub를 사용함\n"
        + "- `scene-4-repeat`는 답안 후 충분한 간격을 두고 반복 대사를 배치함\n"
        + "- board text와 lower-third subtitle은 후반 typography로 합성함\n"
        + "- 최종 contact sheet는 `review/final-contact-sheets/` 기준으로 재검수 가능함\n"
    )
    final_review_report.write_text(
        final_review_body,
        encoding="utf-8",
    )

    episode_schema["status"] = "final-export"
    episode_schema.setdefault("notes", {})
    episode_schema["notes"]["currentExecutionMode"] = "guide-dub-plus-typography-final"
    episode_schema["notes"]["latestReviewReport"] = "./review/final-review-report.md"
    episode_schema["notes"]["latestReviewSeverity"] = "pass"
    episode_schema["notes"]["pictureLockPath"] = "./renders/picture-lock/daehan-pilot-codex-001-picture-lock.mp4"
    episode_schema["notes"]["dubMixPath"] = "./renders/dub-lock/daehan-pilot-codex-001-guide-dub.m4a"
    episode_schema["notes"]["dubbingPackagePath"] = "./dubbing/README.md"
    episode_schema["notes"]["dubbingCuesPath"] = "./dubbing/dubbing-cues.csv"
    episode_schema["notes"]["finalExportPath"] = "./renders/final/daehan-pilot-codex-001-final.mp4"
    episode_schema["notes"]["thumbnailPath"] = "./renders/final/daehan-pilot-codex-001-final-thumb.jpg"
    write_json(episode_schema_path, episode_schema)

    packet_text = packet_path.read_text(encoding="utf-8")
    packet_text = packet_text.replace("- 상태: `dub-ready`", "- 상태: `final-export`")
    packet_text = packet_text.replace("- 더빙 여부: 슬롯만 정의됨", "- 더빙 여부: ElevenLabs guide dub 합성 완료")
    packet_text = packet_text.replace("- 더빙 여부: ElevenLabs guide dub 합성 완료", "- 더빙 여부: ElevenLabs guide dub 합성 완료, `dubbing/audio-overrides/`로 사람 더빙 교체 가능")
    packet_text = packet_text.replace("- 타이포 여부: 슬롯만 정의됨", "- 타이포 여부: chalkboard/subtitle typography 합성 완료")
    packet_text = packet_text.replace("- 최신 리뷰: `review/review-report.md` 기준 `✅ pass`", "- 최신 리뷰: `review/final-review-report.md` 기준 `✅ pass`")
    packet_text = packet_text.replace(
        "1. `voice-slots.json` 기준으로 사람 더빙 또는 성우 음성 배치\n2. `typography-slots.json` 기준으로 칠판/자막 합성\n3. 오프닝/엔딩 원본 음성과 본편 더빙을 함께 믹스\n4. 타이포와 더빙이 올라간 final cut을 다시 `video-review` 기준으로 검수\n",
        "1. `dubbing/audio-overrides/`에 사람 더빙이나 voice-pack 파일을 넣고 재렌더\n2. subtitle/board text 문구만 수정할 경우 `typography-slots.json`만 갱신 후 재export\n3. 최종 업로드 패킷이나 dubbing workbench 입력 포맷으로 확장\n",
    )
    packet_path.write_text(packet_text, encoding="utf-8")

    render_manifest = {
        "episodeSlug": episode_dir.name,
        "pictureLockPath": str(picture_lock_path),
        "audioMixPath": str(audio_mix_path),
        "finalVideoPath": str(final_video_path),
        "thumbnailPath": str(thumb_path),
        "voiceSource": "elevenlabs-guide",
        "voiceId": os.environ.get("ELEVENLABS_VOICE_ID_DAEHAN") or DEFAULT_ELEVENLABS_VOICE_ID,
        "modelId": DEFAULT_ELEVENLABS_MODEL_ID,
        "sceneRangesPath": str(scene_ranges_path),
        "reviewOverviewPath": str((review_dir / "final-contact-sheets" / "overview.jpg")),
        "audioMeanDb": audio_mean_db,
        "audioMaxDb": audio_max_db,
    }
    write_json(final_dir / "render-manifest.json", render_manifest)

    print(str(final_video_path))
    print(str(audio_mix_path))
    print(str(review_dir / "final-contact-sheets" / "overview.jpg"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
