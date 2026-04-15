#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import argparse
import json
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = {
    "teacherImage": str(ROOT / "shared" / "backgrounds" / "images" / "korean" / "teacher.png"),
    "fps": 15,
    "durationSeconds": 15,
    "panelWidth": 1040,
    "panelTop": 340,
    "panelImages": {"title": "", "question": "", "answer": ""},
    "boardRect": {"left": 52, "top": 76, "right": 1016, "bottom": 678},
    "titleCardDuration": 2.0,
    "questionDuration": 7.0,
    "engagementDuration": 2.0,
    "answerDuration": 4.0,
    "musicFile": "",
    "musicCredit": {},
    "ctaUrl": "https://malmoelab.com",
    "buttonCaption": "Learn more at malmoelab.com",
    "outputSlug": "",
    "narration": {
        "enabled": False,
        "mode": "manual",
        "contentLanguageCode": "",
        "learnerLanguageCode": "",
        "voice": "",
        "rate": "-8%",
        "pitch": "-2Hz",
        "volume": "+0%",
        "segments": [],
    },
    "teacherForeground": {
        "enabled": False,
        "crop": [0.60, 0.04, 0.99, 0.98],
        "width": 380,
        "offsetX": 18,
        "offsetY": 320,
        "shadowAlpha": 110,
        "motionEnabled": False,
        "xAmplitude": 14,
        "yAmplitude": 10,
        "rotationDegrees": 1.6,
        "periodSeconds": 3.2,
    },
    "aiAssetGeneration": {
        "enabled": False,
        "model": "gemini-3.1-flash-image-preview",
        "outputDir": "renders/generated-assets",
        "referenceImage": "",
        "imageSize": "2K",
    },
    "theme": {
        "accent": "#5A67FF",
        "accentWarm": "#FFC247",
        "text": "#FFF9F0",
        "boardText": "#FFFDF8",
        "boardSubtext": "#DDE8D8",
        "boardFill": "#244E38",
        "boardStroke": "#C7E7D0",
        "cardFill": "#0A1220",
        "cardFillMuted": "#101827",
        "shadow": "#000000",
    },
}

WIDTH = 1080
HEIGHT = 1920
FONT_REGULAR = Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
FONT_BOLD = Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc")
DEFAULT_EDGE_VOICES = {
    "ko": "ko-KR-SunHiNeural",
    "en": "en-US-JennyNeural",
    "ja": "ja-JP-NanamiNeural",
    "zh": "zh-CN-XiaoxiaoNeural",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a 15-second MalmoeLab hangul quiz short.")
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
    candidate = Path(raw_value).expanduser()
    if not candidate.is_absolute():
        candidate = (base_dir / candidate).resolve()
    return candidate


def resolve_existing_path(base_dir: Path, raw_value: str) -> Path | None:
    normalized = str(raw_value or "").strip()
    if not normalized:
        return None
    candidate = resolve_path(base_dir, normalized)
    return candidate if candidate.exists() else None


def normalize_language_code(raw_value: str) -> str:
    normalized = str(raw_value or "").strip().lower().replace("_", "-")
    if not normalized:
        return ""
    return normalized.split("-", 1)[0]


def pick_content_language_code(packet: dict, config: dict) -> str:
    narration_cfg = config.get("narration") or {}
    candidates = [
        narration_cfg.get("contentLanguageCode"),
        packet.get("contentLanguageCode"),
        packet.get("narrationLanguageCode"),
        (packet.get("source") or {}).get("languageCode"),
    ]
    for candidate in candidates:
        language_code = normalize_language_code(str(candidate or ""))
        if language_code:
            return language_code
    series_slug = str(packet.get("seriesSlug") or "")
    if series_slug.startswith("malmoelab-hangul-quiz"):
        return "ko"
    return "en"


def default_edge_voice_for_language(language_code: str) -> str:
    normalized = normalize_language_code(language_code)
    return DEFAULT_EDGE_VOICES.get(normalized, "en-US-JennyNeural")


def spoken_blank_token(language_code: str) -> str:
    normalized = normalize_language_code(language_code)
    if normalized == "ko":
        return "빈칸"
    if normalized == "ja":
        return "くうらん"
    if normalized == "zh":
        return "空格"
    return "blank"


def replace_blank_for_speech(text: str, language_code: str) -> str:
    if "_" not in text:
        return text
    replacement = spoken_blank_token(language_code)
    rebuilt: list[str] = []
    index = 0
    length = len(text)
    while index < length:
        char = text[index]
        if char != "_":
            rebuilt.append(char)
            index += 1
            continue
        while index < length and text[index] == "_":
            index += 1
        rebuilt.append(replacement)
    return "".join(rebuilt)


def join_sentence_parts(sentence_text: str, trailing_text: str) -> str:
    sentence = str(sentence_text or "").strip()
    trailing = str(trailing_text or "").strip()
    if not sentence:
        return trailing
    if not trailing:
        return sentence
    if sentence.endswith((".", "!", "?", "。", "！", "？")):
        return f"{sentence} {trailing}"
    return f"{sentence}. {trailing}"


def build_auto_narration_segments(packet: dict, config: dict) -> list[dict]:
    narration_cfg = config.get("narration") or {}
    quiz = packet.get("quiz") or {}
    source = packet.get("source") or {}
    content_language = pick_content_language_code(packet, config)

    title_text = str(narration_cfg.get("titleText") or quiz.get("titleCardTitle") or "").strip()
    blanked_sentence = replace_blank_for_speech(str(quiz.get("blankedSentence") or "").strip(), content_language)
    full_sentence = str(quiz.get("fullSentence") or "").strip()
    answer_word = str(quiz.get("answerWord") or source.get("wordText") or "").strip()

    if content_language == "ko":
        question_text = str(
            narration_cfg.get("questionPromptText")
            or join_sentence_parts(blanked_sentence, "들어갈 단어는 무엇일까요?")
        ).strip()
        engagement_text = str(
            narration_cfg.get("engagementText")
            or "정답이 생각나면 좋아요를 눌러 주세요."
        ).strip()
        answer_text = str(
            narration_cfg.get("answerRevealText")
            or f"정답은 {answer_word}입니다. {full_sentence}"
        ).strip()
    elif content_language == "en":
        question_text = str(
            narration_cfg.get("questionPromptText")
            or join_sentence_parts(blanked_sentence, "Which word fits the blank?")
        ).strip()
        engagement_text = str(
            narration_cfg.get("engagementText")
            or "Double tap if you know it."
        ).strip()
        answer_text = str(
            narration_cfg.get("answerRevealText")
            or f"The answer is {answer_word}. {full_sentence}"
        ).strip()
    else:
        question_text = str(narration_cfg.get("questionPromptText") or blanked_sentence).strip()
        engagement_text = str(narration_cfg.get("engagementText") or "").strip()
        answer_text = str(
            narration_cfg.get("answerRevealText")
            or " ".join(part for part in [answer_word, full_sentence] if part)
        ).strip()

    title_start = 0.0
    title_duration = float(config.get("titleCardDuration") or 2.0)
    question_duration = float(config.get("questionDuration") or 7.0)
    engagement_duration = float(config.get("engagementDuration") or 2.0)
    question_start = max(title_duration + 0.05, 0.0)
    engagement_start = max(title_duration + question_duration - 0.2, question_start)
    answer_start = max(title_duration + question_duration + engagement_duration - 0.1, engagement_start)

    segments: list[dict] = []
    for start_at, text in (
        (title_start, title_text),
        (question_start, question_text),
        (engagement_start, engagement_text),
        (answer_start, answer_text),
    ):
        normalized = str(text or "").strip()
        if normalized:
            segments.append({"start": round(start_at, 2), "text": normalized})
    return segments


def load_phase_panel_images(config: dict, episode_dir: Path, *, width: int) -> dict[str, Image.Image]:
    panel_cfg = config.get("panelImages") or {}
    ai_cfg = config.get("aiAssetGeneration") or {}
    generated_dir = resolve_path(episode_dir, str(ai_cfg.get("outputDir") or "renders/generated-assets"))
    defaults = {
        "title": generated_dir / "title-panel.png",
        "question": generated_dir / "question-panel.png",
        "answer": generated_dir / "answer-panel.png",
    }
    loaded: dict[str, Image.Image] = {}
    for phase in ("title", "question", "answer"):
        candidate = resolve_existing_path(episode_dir, str(panel_cfg.get(phase) or ""))
        if candidate is None:
            default_candidate = defaults[phase]
            if default_candidate.exists():
                candidate = default_candidate
        if candidate is None:
            continue
        loaded[phase] = contain(Image.open(candidate).convert("RGBA"), width=width)
    return loaded


def rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[index : index + 2], 16) for index in (0, 2, 4))


def as_float_list(values: list[float] | tuple[float, ...], fallback: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
    try:
        if len(values) != 4:
            raise ValueError
        return tuple(float(value) for value in values)  # type: ignore[return-value]
    except Exception:
        return fallback


def crop_by_normalized_box(image: Image.Image, box_values: list[float] | tuple[float, ...]) -> Image.Image:
    left_n, top_n, right_n, bottom_n = as_float_list(box_values, (0.6, 0.04, 0.99, 0.98))
    left = max(0, min(image.width - 1, int(image.width * left_n)))
    top = max(0, min(image.height - 1, int(image.height * top_n)))
    right = max(left + 1, min(image.width, int(image.width * right_n)))
    bottom = max(top + 1, min(image.height, int(image.height * bottom_n)))
    return image.crop((left, top, right, bottom))


def build_foreground_teacher(image: Image.Image, config: dict) -> Image.Image:
    teacher_cfg = config.get("teacherForeground") or {}
    crop = crop_by_normalized_box(image, teacher_cfg.get("crop") or [0.6, 0.04, 0.99, 0.98])
    enhanced = ImageEnhance.Contrast(crop).enhance(1.12)
    enhanced = ImageEnhance.Brightness(enhanced).enhance(1.04)
    return contain(enhanced, width=int(teacher_cfg.get("width") or 380))


def draw_teacher_foreground(base: Image.Image, teacher_cutout: Image.Image, config: dict, t: float):
    teacher_cfg = config.get("teacherForeground") or {}
    if not teacher_cfg.get("enabled"):
        return

    motion_enabled = bool(teacher_cfg.get("motionEnabled"))
    period = float(teacher_cfg.get("periodSeconds") or 3.2)
    phase = 0.0 if period <= 0 else (t / period) * math.pi * 2.0
    offset_x = int(teacher_cfg.get("offsetX") or 18)
    offset_y = int(teacher_cfg.get("offsetY") or 320)
    x = WIDTH - teacher_cutout.width - offset_x
    y = HEIGHT - teacher_cutout.height - offset_y

    current = teacher_cutout
    if motion_enabled:
        x += int(math.sin(phase) * float(teacher_cfg.get("xAmplitude") or 14))
        y += int(math.sin(phase * 1.25) * float(teacher_cfg.get("yAmplitude") or 10))
        rotation = math.sin(phase * 0.9) * float(teacher_cfg.get("rotationDegrees") or 1.6)
        current = teacher_cutout.rotate(rotation, resample=Image.BICUBIC, expand=True)
        x -= (current.width - teacher_cutout.width) // 2
        y -= (current.height - teacher_cutout.height) // 2

    shadow = Image.new("RGBA", (current.width + 40, current.height + 40), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow, "RGBA")
    shadow_alpha = int(teacher_cfg.get("shadowAlpha") or 110)
    shadow_draw.rounded_rectangle((20, 20, shadow.width - 20, shadow.height - 20), radius=40, fill=(0, 0, 0, shadow_alpha))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=26))
    base.alpha_composite(shadow, (x - 20, y - 12))

    mask = Image.new("L", current.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, current.width, current.height), radius=38, fill=255)
    panel = Image.new("RGBA", current.size, (0, 0, 0, 0))
    panel.paste(current, mask=mask)
    base.alpha_composite(panel, (x, y))


def draw_board_surface(draw: ImageDraw.ImageDraw, board_rect: tuple[int, int, int, int], config: dict):
    left, top, right, bottom = board_rect
    fill = rgb(config["theme"].get("boardFill", "#244E38"))
    stroke = rgb(config["theme"].get("boardStroke", "#C7E7D0"))
    draw.rounded_rectangle((left, top, right, bottom), radius=34, fill=(*fill, 180), outline=(*stroke, 160), width=4)
    draw.rounded_rectangle((left + 16, top + 16, right - 16, bottom - 16), radius=26, outline=(255, 255, 255, 20), width=2)


async def synthesize_edge_tts(text: str, output_path: Path, *, voice: str, rate: str, pitch: str, volume: str):
    import edge_tts

    output_path.parent.mkdir(parents=True, exist_ok=True)
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, pitch=pitch, volume=volume)
    await communicate.save(str(output_path))


def generate_narration_segments(packet: dict, config: dict, episode_dir: Path) -> list[dict]:
    narration_cfg = config.get("narration") or {}
    if not narration_cfg.get("enabled"):
        return []

    configured_segments = narration_cfg.get("segments") or []
    mode = str(narration_cfg.get("mode") or "").strip().lower()
    if mode == "auto" or (not configured_segments):
        segments = build_auto_narration_segments(packet, config)
    else:
        segments = configured_segments
    if not segments:
        return []

    output_dir = episode_dir / "renders" / "narration"
    output_dir.mkdir(parents=True, exist_ok=True)
    generated: list[dict] = []
    content_language = pick_content_language_code(packet, config)
    base_voice = str(narration_cfg.get("voice") or "").strip() or default_edge_voice_for_language(content_language)
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
                voice=str(segment.get("voice") or base_voice),
                rate=str(segment.get("rate") or narration_cfg.get("rate") or "-8%"),
                pitch=str(segment.get("pitch") or narration_cfg.get("pitch") or "-2Hz"),
                volume=str(segment.get("volume") or narration_cfg.get("volume") or "+0%"),
            )
        )
        generated.append({"path": audio_path, "start": start_at})
    return generated


def load_font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    font_path = FONT_BOLD if bold and FONT_BOLD.exists() else FONT_REGULAR
    return ImageFont.truetype(str(font_path), size=size)


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
    if not text.strip():
        return []
    words = text.split(" ")
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
                continue
            if fragment:
                lines.append(fragment)
            fragment = char
        current = fragment
    if current:
        lines.append(current)
    return lines


def fit_board_text(draw: ImageDraw.ImageDraw, text: str, max_width: int, max_height: int) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    for size in range(72, 41, -2):
        font = load_font(size, bold=True)
        lines = wrap_text(draw, text, font, max_width)
        if not lines:
            continue
        line_height = font.size + 22
        total_height = len(lines) * line_height
        if len(lines) <= 3 and total_height <= max_height:
            return font, lines
    font = load_font(40, bold=True)
    return font, wrap_text(draw, text, font, max_width)


def text_bbox(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    return right - left, bottom - top


def draw_card(draw: ImageDraw.ImageDraw, rect: tuple[int, int, int, int], fill: tuple[int, int, int, int], radius: int = 36):
    draw.rounded_rectangle(rect, radius=radius, fill=fill)


def draw_chalk_text(draw: ImageDraw.ImageDraw, position: tuple[int, int], text: str, font: ImageFont.FreeTypeFont, fill: tuple[int, int, int], anchor: str = "la"):
    x, y = position
    for dx, dy, alpha in ((0, 0, 255), (2, 2, 85), (-1, 0, 70), (0, -1, 60), (1, -1, 48)):
        draw.text((x + dx, y + dy), text, font=font, fill=(*fill, alpha), anchor=anchor)


def build_background(teacher_image: Image.Image) -> Image.Image:
    background = cover(teacher_image, WIDTH, HEIGHT).filter(ImageFilter.GaussianBlur(radius=18))
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (16, 24, 24, 120))
    background.alpha_composite(overlay)
    vignette = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    vignette_draw = ImageDraw.Draw(vignette, "RGBA")
    vignette_draw.ellipse((-260, -120, WIDTH + 260, HEIGHT + 360), fill=(255, 255, 255, 24))
    vignette = vignette.filter(ImageFilter.GaussianBlur(radius=80))
    background.alpha_composite(vignette)
    return background


def draw_panel(base: Image.Image, panel_image: Image.Image, *, top: int, shadow_alpha: int = 120) -> tuple[int, int]:
    left = (WIDTH - panel_image.width) // 2
    shadow = Image.new("RGBA", (panel_image.width + 24, panel_image.height + 24), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow, "RGBA")
    shadow_draw.rounded_rectangle((12, 12, shadow.width - 12, shadow.height - 12), radius=44, fill=(0, 0, 0, shadow_alpha))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=18))
    base.alpha_composite(shadow, (left - 12, top - 8))
    mask = Image.new("L", panel_image.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, panel_image.width, panel_image.height), radius=36, fill=255)
    panel = Image.new("RGBA", panel_image.size, (0, 0, 0, 0))
    panel.paste(panel_image, mask=mask)
    base.alpha_composite(panel, (left, top))
    return left, top


def draw_board_quiz(draw: ImageDraw.ImageDraw, board_rect: tuple[int, int, int, int], packet: dict, config: dict, phase: str, pointer_phase_t: float):
    left, top, right, bottom = board_rect
    width = right - left
    height = bottom - top
    draw_board_surface(draw, board_rect, config)
    padding_x = 56
    sentence_top = top + 88
    board_main_width = width - padding_x * 2
    board_main_height = 236
    main_text = packet["quiz"]["blankedSentence"] if phase != "answer" else packet["quiz"]["fullSentence"]
    romanized_text = (
        packet["quiz"].get("blankedSentenceRomanization") if phase != "answer" else packet["quiz"].get("fullSentenceRomanization")
    ) or ""
    font, lines = fit_board_text(
        draw,
        main_text,
        board_main_width,
        board_main_height,
    )
    line_height = font.size + 22
    block_height = max(line_height * len(lines), 1)
    line_y = sentence_top + max((board_main_height - block_height) // 2, 0)
    board_color = rgb(config["theme"]["boardText"])

    blank_box = None
    for index, line in enumerate(lines):
        draw_chalk_text(draw, (left + padding_x, line_y + index * line_height), line, font, board_color)
        if "_" in line and blank_box is None:
            prefix = line.split("_", 1)[0]
            blank_count = len(line) - len(line.rstrip("_")) if line.endswith("_") else line.count("_")
            prefix_width = draw.textlength(prefix, font=font)
            underscore_width = draw.textlength("_" * blank_count, font=font)
            blank_box = (
                int(left + padding_x + prefix_width - 4),
                int(line_y + index * line_height - 8),
                int(left + padding_x + prefix_width + underscore_width + 4),
                int(line_y + index * line_height + font.size + 8),
            )

    sub_font = load_font(28)
    sub_color = rgb(config["theme"]["boardSubtext"])
    sub_lines = []
    if romanized_text:
        sub_lines.append(romanized_text)
    if phase == "answer":
        answer_romanization = packet["quiz"].get("answerRomanization") or ""
        answer_gloss = packet["quiz"].get("answerGloss") or ""
        details = " · ".join(part for part in [answer_romanization, answer_gloss] if part)
        if details:
            sub_lines.append(details)
        translation = packet["quiz"].get("answerTranslation") or ""
        if translation:
            sub_lines.append(translation)

    sub_y = line_y + block_height + 48
    for sub_line in sub_lines:
        wrapped = wrap_text(draw, sub_line, sub_font, board_main_width)
        for line in wrapped:
            draw.text((left + padding_x, sub_y), line, font=sub_font, fill=(*sub_color, 250), anchor="la")
            sub_y += sub_font.size + 14

    if phase != "answer" and blank_box:
        pulse = 0.5 + 0.5 * math.sin(pointer_phase_t * math.pi * 2.0)
        outline = (255, 225, 153, int(110 + pulse * 95))
        draw.rounded_rectangle(blank_box, radius=18, outline=outline, width=5)
        start = (right + 84, top + 236 + int(math.sin(pointer_phase_t * math.pi * 2.0) * 12))
        end = ((blank_box[0] + blank_box[2]) // 2, blank_box[1] - 14)
        draw.line((start, end), fill=(255, 229, 174, 220), width=8)
        draw.ellipse((start[0] - 14, start[1] - 14, start[0] + 14, start[1] + 14), fill=(255, 244, 219, 240))


def build_publish_packet(packet: dict, config: dict, final_video: Path, thumbnail_file: Path) -> dict:
    source = packet["source"]
    quiz = packet["quiz"]
    title = f"{quiz['questionCaption']} | {source['wordText']} Korean quiz"
    description_lines = [
        "MalmoeLab Korean fill-in-the-blank short for English learners.",
        "",
        f"Question: {quiz['blankedSentence']}",
        f"Answer: {source['wordText']} ({source.get('wordRomanization') or 'romanization unavailable'})",
        f"Meaning: {source.get('englishGloss') or 'gloss unavailable'}",
        f"Example: {quiz['fullSentence']}",
        f"English: {source.get('exampleTranslationText') or 'translation unavailable'}",
        "",
        f"Study more: {config.get('ctaUrl', 'https://malmoelab.com')}",
        f"Source: {source.get('baseUrl', 'https://malmoelab.com')}",
    ]
    music_credit = config.get("musicCredit") or {}
    if music_credit:
        description_lines.extend(
            [
                "",
                "Music credit:",
                f"- Title: {music_credit.get('title', '').strip()}",
                f"- Artist: {music_credit.get('artist', '').strip()}",
                f"- License: {music_credit.get('license', '').strip()}",
                f"- URL: {music_credit.get('sourceUrl', '').strip()}",
            ]
        )
    description = "\n".join(line for line in description_lines if line is not None)
    return {
        "title": title,
        "description": description,
        "videoFile": str(final_video),
        "thumbnailFile": str(thumbnail_file),
        "privacyStatus": "private",
        "categoryId": "22",
        "tags": [
            "malmoelab",
            "learnkorean",
            "koreanquiz",
            "hangul",
            source["wordText"],
        ],
    }


def run_ffmpeg(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def build_narration_mix(packet: dict, episode_dir: Path, config: dict, duration_seconds: int) -> Path | None:
    segments = generate_narration_segments(packet, config, episode_dir)
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
        filter_parts.append(f"[{index}:a]adelay={delay_ms}|{delay_ms},volume=1.1[{label}]")
        mix_inputs.append(f"[{label}]")

    filter_parts.append(f"{''.join(mix_inputs)}amix=inputs={len(mix_inputs)}:dropout_transition=0,volume=1.2[narr]")
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


def mux_video_with_audio(video_only_path: Path, final_video: Path, *, narration_path: Path | None, music_file: str, duration_seconds: int):
    if not narration_path and not music_file:
        video_only_path.replace(final_video)
        return

    cmd = ["ffmpeg", "-y", "-i", str(video_only_path)]
    filter_parts = []
    mix_inputs = []
    next_index = 1

    if narration_path:
        cmd.extend(["-i", str(narration_path)])
        filter_parts.append(f"[{next_index}:a]volume=1.0[narr]")
        mix_inputs.append("[narr]")
        next_index += 1

    if music_file:
        cmd.extend(["-stream_loop", "-1", "-i", music_file])
        filter_parts.append(
            f"[{next_index}:a]atrim=0:{duration_seconds},afade=t=out:st={max(duration_seconds - 1, 0)}:d=1,volume=0.12[music]"
        )
        mix_inputs.append("[music]")

    if mix_inputs:
        filter_parts.append(f"{''.join(mix_inputs)}amix=inputs={len(mix_inputs)}:dropout_transition=0[aout]")
        cmd.extend(
            [
                "-filter_complex",
                ";".join(filter_parts),
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
        run_ffmpeg(cmd)
        return

    video_only_path.replace(final_video)


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
    title_cut = int(config["titleCardDuration"] * fps)
    question_cut = int((config["titleCardDuration"] + config["questionDuration"]) * fps)
    engagement_cut = int((config["titleCardDuration"] + config["questionDuration"] + config["engagementDuration"]) * fps)

    teacher_image = Image.open(teacher_path).convert("RGBA")
    background = build_background(teacher_image)
    fallback_panel_image = contain(teacher_image, width=int(config["panelWidth"]))
    phase_panel_images = load_phase_panel_images(config, episode_dir, width=int(config["panelWidth"]))
    teacher_foreground = build_foreground_teacher(teacher_image, config)
    panel_top = int(config["panelTop"])
    board_cfg = config["boardRect"]

    accent = rgb(config["theme"]["accent"])
    accent_warm = rgb(config["theme"]["accentWarm"])
    base_text = rgb(config["theme"]["text"])
    card_fill = rgb(config["theme"].get("cardFill", "#0A1220"))
    card_fill_muted = rgb(config["theme"].get("cardFillMuted", "#101827"))

    for frame_index in range(total_frames):
        t = frame_index / fps
        frame = background.copy()
        draw = ImageDraw.Draw(frame, "RGBA")
        phase_key = "title" if frame_index < title_cut else ("question" if frame_index < engagement_cut else "answer")
        panel_image = phase_panel_images.get(phase_key, fallback_panel_image)
        panel_left = (WIDTH - panel_image.width) // 2
        scale = panel_image.width / teacher_image.width
        wobble_top = panel_top + int(math.sin(t * 1.8) * 6)
        draw_panel(frame, panel_image, top=wobble_top)
        board_rect = (
            int(panel_left + board_cfg["left"] * scale),
            int(wobble_top + board_cfg["top"] * scale),
            int(panel_left + board_cfg["right"] * scale),
            int(wobble_top + board_cfg["bottom"] * scale),
        )
        draw_teacher_foreground(frame, teacher_foreground, config, t)

        draw_card(draw, (42, 72, WIDTH - 42, 216), fill=(*card_fill, 190), radius=42)
        chip_font = load_font(30, bold=True)
        title_font = load_font(84, bold=True)
        small_title_font = load_font(38)
        prompt_font = load_font(46, bold=True)
        detail_font = load_font(32)

        draw.text((74, 108), "MALMOELAB HANGUL QUIZ", font=chip_font, fill=(*accent_warm, 255), anchor="la")

        if frame_index < title_cut:
            draw.text((74, 248), source_packet["quiz"]["titleCardTitle"], font=title_font, fill=(*base_text, 255), anchor="la")
            draw.text((78, 360), source_packet["quiz"]["titleCardSubtitle"], font=small_title_font, fill=(235, 228, 215, 235), anchor="la")
            draw_card(draw, (42, 1490, WIDTH - 42, 1738), fill=(*card_fill_muted, 208), radius=42)
            draw.text((76, 1548), source_packet["quiz"]["questionCaption"], font=prompt_font, fill=(*base_text, 255), anchor="la")
            draw.text((76, 1622), "Listen, read the board, and guess the missing word.", font=detail_font, fill=(226, 226, 226, 236), anchor="la")
        else:
            phase = "question" if frame_index < engagement_cut else "answer"
            pointer_phase_t = (frame_index - title_cut) / max(question_cut - title_cut, 1)
            draw_board_quiz(draw, board_rect, source_packet, config, phase, pointer_phase_t)

            footer_top = 1460
            draw_card(draw, (42, footer_top, WIDTH - 42, 1800), fill=(*card_fill_muted, 212), radius=42)
            draw.text((74, footer_top + 46), source_packet["quiz"]["questionCaption"], font=prompt_font, fill=(*base_text, 255), anchor="la")
            translation = source_packet["quiz"].get("answerTranslation") or ""
            if phase == "question":
                wrapped_translation = wrap_text(draw, translation, detail_font, WIDTH - 156)
                line_y = footer_top + 122
                for line in wrapped_translation[:2]:
                    draw.text((76, line_y), line, font=detail_font, fill=(224, 224, 224, 228), anchor="la")
                    line_y += detail_font.size + 12
                if frame_index >= question_cut:
                    draw_card(draw, (74, 1688, WIDTH - 74, 1800), fill=(*accent, 226), radius=54)
                    draw.text(
                        (WIDTH // 2, 1744),
                        source_packet["quiz"]["engagementCaption"],
                        font=load_font(38, bold=True),
                        fill=(255, 255, 255, 255),
                        anchor="mm",
                    )
            else:
                draw.text((76, footer_top + 118), source_packet["quiz"]["revealCaption"], font=load_font(44, bold=True), fill=(*accent_warm, 255), anchor="la")
                answer_details = " · ".join(
                    part for part in [source_packet["quiz"].get("answerRomanization"), source_packet["quiz"].get("answerGloss")] if part
                )
                if answer_details:
                    draw.text((76, footer_top + 182), answer_details, font=detail_font, fill=(236, 236, 236, 226), anchor="la")
                answer_translation = source_packet["quiz"].get("answerTranslation") or ""
                if answer_translation:
                    draw.text((76, footer_top + 236), answer_translation, font=detail_font, fill=(216, 216, 216, 220), anchor="la")
                draw_card(draw, (74, 1688, WIDTH - 74, 1800), fill=(*accent, 230), radius=54)
                draw.text(
                    (WIDTH // 2, 1744),
                    config.get("buttonCaption") or source_packet["quiz"]["ctaCaption"],
                    font=load_font(38, bold=True),
                    fill=(255, 255, 255, 255),
                    anchor="mm",
                )

        frame.save(frames_dir / f"frame-{frame_index:04d}.png")

    final_video = final_dir / f"{slug}.mp4"
    thumb_path = final_dir / f"{slug}-thumb.png"
    first_answer_frame = frames_dir / f"frame-{max(engagement_cut, 0):04d}.png"
    Image.open(first_answer_frame).save(thumb_path)

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

    music_file = str(config.get("musicFile") or "").strip()
    narration_path = build_narration_mix(source_packet, episode_dir, config, duration_seconds)
    mux_video_with_audio(video_only_path, final_video, narration_path=narration_path, music_file=music_file, duration_seconds=duration_seconds)

    publish_packet = build_publish_packet(source_packet, config, final_video, thumb_path)
    publish_packet_path = episode_dir / "publish-packet.json"
    publish_packet_path.write_text(json.dumps(publish_packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"videoFile": str(final_video), "thumbnailFile": str(thumb_path), "publishPacket": str(publish_packet_path)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
