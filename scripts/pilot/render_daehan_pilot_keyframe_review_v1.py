#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(SCRIPT_DIR.parent))

from build_keyframe_video_preview import build_contact_sheets, build_preview, write_review_metadata  # noqa: E402
from format_profiles import load_profile_for_episode_schema  # noqa: E402
from render_daehan_pilot_final import (  # noqa: E402
    FPS,
    HEIGHT,
    ROOT,
    WIDTH,
    build_review_bundle,
    copy_processed_audio,
    export_reference_scene_clip,
    fit_text,
    load_env_file,
    load_json,
    load_scene_ranges,
    measure_audio_levels,
    media_duration,
    normalize_audio_mean_volume,
    resolve_episode_asset_path,
    resolve_ffmpeg_binary,
    run_ffmpeg,
    synthesize_guide_tts,
    trim_audio_edges,
    write_json,
)
from tts.supertone_client import SupertoneClient, VoiceSettings  # noqa: E402
from tts.voice_config import resolve_tts_voice_env  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render guide dub + typography final export for keyframe-review-v1 daehan pilot.")
    parser.add_argument("--episode-dir", required=True)
    parser.add_argument("--env-file", default=".env")
    return parser.parse_args()


def synthesize_supertone_guide_tts(
    output_path: Path,
    *,
    text: str,
    speed: float,
    pitch_shift: float | None = None,
    voice_id_env: str | None = None,
) -> Path:
    resolved_voice_id = os.environ.get(voice_id_env) if voice_id_env else None
    client = SupertoneClient.from_env(voice_id=resolved_voice_id)
    settings = VoiceSettings(
        speed=speed if abs(speed - 1.0) > 1e-6 else None,
        pitch_shift=pitch_shift,
    )
    if not settings.to_payload():
        settings = None
    client.synthesize(
        text,
        output_path=output_path,
        output_format="mp3",
        voice_settings=settings,
    )
    trim_audio_edges(output_path)
    normalize_audio_mean_volume(output_path, target_mean_db=-19.0, peak_ceiling_db=-2.0)
    return output_path


def synthesize_slot(
    output_path: Path,
    *,
    text: str,
    speed: float,
    pitch_shift: float | None,
    provider: str,
    voice_id_env: str | None = None,
) -> tuple[Path, str]:
    provider_key = str(provider or "").strip().lower()
    if provider_key == "supertone":
        try:
            return (
                synthesize_supertone_guide_tts(
                    output_path,
                    text=text,
                    speed=speed,
                    pitch_shift=pitch_shift,
                    voice_id_env=voice_id_env,
                ),
                "supertone-guide",
            )
        except Exception:
            return synthesize_guide_tts(output_path, text=text, speed=speed, voice_id_env=voice_id_env), "elevenlabs-guide-fallback"
    return synthesize_guide_tts(output_path, text=text, speed=speed, voice_id_env=voice_id_env), "elevenlabs-guide"


def load_font_from_path(font_path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(font_path), size=size)


def wrap_text_with_font(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
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


def fit_text_with_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    *,
    font_path: Path,
    max_size: int,
    min_size: int,
) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    for size in range(max_size, min_size - 1, -2):
        font = load_font_from_path(font_path, size=size)
        lines = wrap_text_with_font(draw, text, font, max_width)
        if len(lines) <= 3:
            return font, lines
    font = load_font_from_path(font_path, size=min_size)
    return font, wrap_text_with_font(draw, text, font, max_width)


def draw_lines(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    *,
    x: int,
    y: int,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
    anchor: str,
    stroke_fill: tuple[int, int, int, int] | None = None,
    stroke_width: int = 0,
    line_gap: int = 8,
) -> None:
    cursor_y = y
    for line in lines:
        draw.text((x, cursor_y), line, font=font, fill=fill, anchor=anchor, stroke_width=stroke_width, stroke_fill=stroke_fill)
        cursor_y += font.size + line_gap


def render_typography_frame(output_path: Path, t: float, slots: list[dict], *, handwriting_font: Path, subtitle_font: Path) -> None:
    board_text = (245, 245, 236, 255)
    board_stroke = (24, 52, 39, 235)
    board_outline = (222, 232, 224, 72)
    board_box_fill = (11, 35, 25, 28)
    subtitle_box = (7, 10, 18, 210)
    subtitle_text = (255, 255, 255, 255)
    subtitle_stroke = (7, 10, 18, 255)
    cta_accent = (255, 213, 120, 255)

    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    active_slots = [slot for slot in slots if float(slot["inTimeSec"]) <= t < float(slot["outTimeSec"])]
    board_slots = [slot for slot in active_slots if slot["surface"] == "chalkboard"]
    subtitle_slots = [slot for slot in active_slots if slot["surface"] == "subtitle-lower-third"]

    if board_slots:
        board_slot = board_slots[0]
        font, lines = fit_text_with_font(draw, board_slot["text"], 660, font_path=handwriting_font, max_size=68, min_size=42)
        panel = (72, 104, 720, 314)
        draw.rounded_rectangle(panel, radius=28, fill=board_box_fill, outline=board_outline, width=2)
        shadow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.rounded_rectangle((panel[0] + 3, panel[1] + 8, panel[2] + 3, panel[3] + 8), radius=28, fill=(0, 0, 0, 42))
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=12))
        overlay.alpha_composite(shadow)
        draw = ImageDraw.Draw(overlay)
        draw.rounded_rectangle(panel, radius=28, fill=board_box_fill, outline=board_outline, width=2)
        draw_lines(
            draw,
            lines,
            x=96,
            y=136,
            font=font,
            fill=board_text,
            anchor="la",
            stroke_fill=board_stroke,
            stroke_width=3,
            line_gap=12,
        )

    if subtitle_slots:
        subtitle = subtitle_slots[0]["text"]
        box_width = 1020
        box_height = 72
        left = (WIDTH - box_width) // 2
        top = HEIGHT - box_height - 34
        rect = (left, top, left + box_width, top + box_height)
        badge = (left + 20, top + 16, left + 176, top + 54)
        text_left = badge[2] + 22
        text_width = rect[2] - text_left - 26
        font, lines = fit_text_with_font(draw, subtitle, text_width, font_path=subtitle_font, max_size=34, min_size=24)
        text_height = len(lines) * font.size + max(0, len(lines) - 1) * 6
        shadow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.rounded_rectangle((rect[0] + 4, rect[1] + 6, rect[2] + 4, rect[3] + 6), radius=30, fill=(0, 0, 0, 74))
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=10))
        overlay.alpha_composite(shadow)
        draw = ImageDraw.Draw(overlay)
        draw.rounded_rectangle(rect, radius=30, fill=subtitle_box, outline=(255, 255, 255, 42), width=2)
        draw.rounded_rectangle(badge, radius=18, fill=cta_accent)
        badge_font, badge_lines = fit_text_with_font(draw, "더 알아보기", 140, font_path=subtitle_font, max_size=24, min_size=20)
        draw_lines(
            draw,
            badge_lines,
            x=(badge[0] + badge[2]) // 2,
            y=int((badge[1] + badge[3]) / 2 - (len(badge_lines) * badge_font.size + max(0, len(badge_lines) - 1) * 2) / 2),
            font=badge_font,
            fill=(34, 36, 30, 255),
            anchor="ma",
            line_gap=2,
        )
        draw_lines(
            draw,
            lines,
            x=text_left,
            y=int((rect[1] + rect[3]) / 2 - text_height / 2),
            font=font,
            fill=subtitle_text,
            anchor="la",
            stroke_fill=subtitle_stroke,
            stroke_width=2,
            line_gap=6,
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    overlay.save(output_path)


def update_slot(
    slot: dict,
    *,
    start_sec: float,
    duration_sec: float,
    render_text: str,
    active_path: Path,
    active_source: str,
    episode_dir: Path,
    scene_id: str,
) -> None:
    slot["selectedSource"] = active_source
    slot["activeRenderAsset"] = str(active_path.relative_to(episode_dir))
    slot["sceneId"] = scene_id
    slot["startSec"] = round(start_sec, 3)
    slot["endSec"] = round(start_sec + duration_sec, 3)
    slot["durationSec"] = round(duration_sec, 3)
    slot["renderText"] = render_text


def main() -> int:
    args = parse_args()
    episode_dir = Path(args.episode_dir).resolve()
    load_env_file((ROOT / args.env_file).resolve())

    episode_schema_path = episode_dir / "episode.schema.json"
    voice_slots_path = episode_dir / "voice-slots.json"
    typography_slots_path = episode_dir / "typography-slots.json"
    packet_path = episode_dir / "packet.md"
    episode_schema = load_json(episode_schema_path)
    voice_slots = load_json(voice_slots_path)
    typography_slots = load_json(typography_slots_path)
    profile_id, _profile_path, profile = load_profile_for_episode_schema(episode_schema)
    if profile_id != "keyframe-review-v1":
        raise ValueError(f"render_daehan_pilot_keyframe_review_v1.py only supports keyframe-review-v1, got {profile_id}")

    ffmpeg = resolve_ffmpeg_binary()
    preview_path = episode_dir / "renders" / "final" / f"{episode_dir.name}-picture-preview.mp4"
    ranges = build_preview(ffmpeg, episode_dir, preview_path)
    write_review_metadata(episode_dir / "review", ranges)
    build_contact_sheets(ffmpeg, episode_dir)
    scene_ranges = load_scene_ranges(episode_dir / "review" / "scene-ranges.csv")
    scene_map = {item.scene_id: item for item in scene_ranges}

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
    for directory in [
        picture_lock_dir,
        dub_lock_dir,
        type_ready_dir,
        final_dir,
        narration_dir,
        selected_audio_dir,
        overlay_dir,
        dubbing_audio_override_dir,
        dubbing_guide_audio_dir,
        dubbing_reference_video_dir,
    ]:
        directory.mkdir(parents=True, exist_ok=True)

    picture_lock_path = picture_lock_dir / f"{episode_dir.name}-picture-lock.mp4"
    shutil.copyfile(preview_path, picture_lock_path)

    handwriting_font = (ROOT / episode_schema["reusableAssets"]["preferredHandwritingFont"]).resolve()
    subtitle_font = (ROOT / "shared" / "fonts" / "NanumGothic-Bold.ttf").resolve()
    if not handwriting_font.exists():
        raise FileNotFoundError(f"Missing handwriting font: {handwriting_font}")
    if not subtitle_font.exists():
        raise FileNotFoundError(f"Missing subtitle font: {subtitle_font}")

    slot_index = {slot["voiceSlotId"]: slot for slot in voice_slots["slots"]}
    for slot in voice_slots["slots"]:
        if slot["kind"] == "episode-line":
            slot.setdefault("recordingTarget", f"dubbing/audio-overrides/{slot['voiceSlotId']}.wav")

    generated_segments: list[dict] = []
    provider_default = str(episode_schema["policies"]["audioPolicy"]["contentTtsProvider"])

    fixed_plan = [
        {
            "voiceSlotId": "scene-1-opening-greeting-ko",
            "sceneId": "scene-1-opening-handoff",
            "startSec": 0.60,
            "defaultSpeed": 1.05,
            "defaultPitchShift": 3.0,
        },
        {
            "voiceSlotId": "scene-2-intro-ko",
            "sceneId": "scene-2-lesson-intro",
            "startSec": 6.55,
            "defaultSpeed": 1.06,
            "defaultPitchShift": 3.2,
        },
        {
            "voiceSlotId": "scene-3-repeat-cue-ko",
            "sceneId": "scene-3-repeat-listen",
            "startSec": 12.55,
            "defaultSpeed": 1.08,
            "defaultPitchShift": 3.4,
        },
        {
            "voiceSlotId": "scene-4-cta-ko",
            "sceneId": "scene-4-quiz-point",
            "startSec": 19.20,
            "defaultSpeed": 1.07,
            "defaultPitchShift": 3.3,
        },
        {
            "voiceSlotId": "scene-5-ending-ko",
            "sceneId": "scene-5-ending-wave",
            "startSec": 26.55,
            "defaultSpeed": 1.04,
            "defaultPitchShift": 3.0,
        },
    ]

    for plan in fixed_plan:
        slot = slot_index[plan["voiceSlotId"]]
        slot_id = plan["voiceSlotId"]
        output_path = narration_dir / f"{slot_id}.mp3"
        recording_target_path = resolve_episode_asset_path(episode_dir, slot.get("recordingTarget"))
        selected_asset_path = resolve_episode_asset_path(episode_dir, slot.get("selectedAsset"))

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
            slot_speed = float(slot.get("speed") or plan["defaultSpeed"])
            slot_pitch = float(slot.get("pitchShift") or plan["defaultPitchShift"])
            slot_provider = str(slot.get("ttsProvider") or provider_default)
            slot_voice_env = resolve_tts_voice_env(slot, provider=slot_provider, root=ROOT, episode_schema=episode_schema)
            active_path, active_source = synthesize_slot(
                output_path,
                text=slot["text"],
                speed=slot_speed,
                pitch_shift=slot_pitch,
                provider=slot_provider,
                voice_id_env=slot_voice_env,
            )
            slot["selectedAsset"] = str(active_path.relative_to(episode_dir))

        guide_package_path = dubbing_guide_audio_dir / output_path.name
        if active_path == output_path and output_path.exists():
            shutil.copyfile(output_path, guide_package_path)
            slot["guideAsset"] = str(guide_package_path.relative_to(episode_dir))

        duration = media_duration(active_path)
        update_slot(
            slot,
            start_sec=float(plan["startSec"]),
            duration_sec=duration,
            render_text=str(slot["text"]),
            active_path=active_path,
            active_source=active_source,
            episode_dir=episode_dir,
            scene_id=plan["sceneId"],
        )
        generated_segments.append({"slotId": slot_id, "path": active_path, "start": float(plan["startSec"]), "volume": 1.0})

    cue_slot = slot_index["scene-3-repeat-cue-ko"]
    sentence_slot = slot_index["scene-3-sentence-ko"]
    sentence_start = round(float(cue_slot["endSec"]) + float(sentence_slot.get("pauseAfterSec") or 1.0), 3)
    sentence_output = narration_dir / "scene-3-sentence-ko.mp3"
    sentence_target = resolve_episode_asset_path(episode_dir, sentence_slot.get("recordingTarget"))
    sentence_selected = resolve_episode_asset_path(episode_dir, sentence_slot.get("selectedAsset"))
    if sentence_target is not None and sentence_target.exists():
        processed_path = selected_audio_dir / f"scene-3-sentence-ko{sentence_target.suffix.lower() or '.wav'}"
        sentence_active = copy_processed_audio(sentence_target, processed_path)
        sentence_source = "human-dub"
        sentence_slot["selectedAsset"] = str(Path(sentence_slot["recordingTarget"]))
    elif (
        sentence_selected is not None
        and sentence_selected.exists()
        and str(sentence_slot.get("selectedSource") or "").strip().lower() in {"human-dub", "actor-dub", "voice-pack"}
    ):
        processed_path = selected_audio_dir / f"scene-3-sentence-ko{sentence_selected.suffix.lower() or '.wav'}"
        sentence_active = copy_processed_audio(sentence_selected, processed_path)
        sentence_source = str(sentence_slot.get("selectedSource") or "voice-pack")
    else:
        sentence_speed = float(sentence_slot.get("speed") or 1.05)
        sentence_pitch = float(sentence_slot.get("pitchShift") or 2.8)
        sentence_provider = str(sentence_slot.get("ttsProvider") or provider_default)
        sentence_voice_env = resolve_tts_voice_env(
            sentence_slot,
            provider=sentence_provider,
            root=ROOT,
            episode_schema=episode_schema,
        )
        sentence_active, sentence_source = synthesize_slot(
            sentence_output,
            text=sentence_slot["text"],
            speed=sentence_speed,
            pitch_shift=sentence_pitch,
            provider=sentence_provider,
            voice_id_env=sentence_voice_env,
        )
        sentence_slot["selectedAsset"] = str(sentence_active.relative_to(episode_dir))
        shutil.copyfile(sentence_output, dubbing_guide_audio_dir / sentence_output.name)
        sentence_slot["guideAsset"] = str((dubbing_guide_audio_dir / sentence_output.name).relative_to(episode_dir))

    sentence_duration = media_duration(sentence_active)
    update_slot(
        sentence_slot,
        start_sec=sentence_start,
        duration_sec=sentence_duration,
        render_text=str(sentence_slot["text"]),
        active_path=sentence_active,
        active_source=sentence_source,
        episode_dir=episode_dir,
        scene_id="scene-3-repeat-listen",
    )
    generated_segments.append({"slotId": "scene-3-sentence-ko", "path": sentence_active, "start": sentence_start, "volume": 1.0})

    voice_slots_path.write_text(json.dumps(voice_slots, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for scene_id in [
        "scene-1-opening-handoff",
        "scene-2-lesson-intro",
        "scene-3-repeat-listen",
        "scene-4-quiz-point",
        "scene-5-ending-wave",
    ]:
        scene = scene_map[scene_id]
        export_reference_scene_clip(
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
                "selected_source",
                "recording_target",
                "guide_asset",
                "reference_video",
            ]
        )
        for slot_id in [
            "scene-1-opening-greeting-ko",
            "scene-2-intro-ko",
            "scene-3-repeat-cue-ko",
            "scene-3-sentence-ko",
            "scene-4-cta-ko",
            "scene-5-ending-ko",
        ]:
            slot = slot_index[slot_id]
            scene = scene_map[slot["sceneId"]]
            writer.writerow(
                [
                    slot_id,
                    slot["sceneId"],
                    f"{scene.start_sec:.3f}",
                    f"{float(slot['startSec']):.3f}",
                    f"{float(slot['endSec']):.3f}",
                    f"{float(slot['durationSec']):.3f}",
                    slot.get("text") or "",
                    slot.get("selectedSource") or "",
                    slot.get("recordingTarget") or "",
                    slot.get("guideAsset") or "",
                    f"dubbing/reference-video/{slot['sceneId']}.mp4",
                ]
            )

    recording_script_lines = [
        "# Recording Script",
        "",
        "사람 더빙이나 성우 녹음을 넣을 때는 `audio-overrides/` 아래 대응 파일명을 그대로 사용하면 된다.",
        "",
    ]
    for slot_id in [
        "scene-1-opening-greeting-ko",
        "scene-2-intro-ko",
        "scene-3-repeat-cue-ko",
        "scene-3-sentence-ko",
        "scene-4-cta-ko",
        "scene-5-ending-ko",
    ]:
        slot = slot_index[slot_id]
        recording_script_lines.extend(
            [
                f"## {slot_id}",
                f"- scene: `{slot['sceneId']}`",
                f"- timing: `{float(slot['startSec']):.2f}s -> {float(slot['endSec']):.2f}s`",
                f"- target file: `{slot.get('recordingTarget', '')}`",
                f"- line: `{slot.get('text', '')}`",
                "",
            ]
        )
    (dubbing_dir / "recording-script.md").write_text("\n".join(recording_script_lines) + "\n", encoding="utf-8")

    (dubbing_dir / "README.md").write_text(
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
        ".venv-video-tools/bin/python scripts/pilot/render_daehan_pilot_keyframe_review_v1.py --episode-dir episodes/daehan-pilot-codex-003 --env-file .env\n"
        "```\n",
        encoding="utf-8",
    )

    typography_slot_index = {slot["slotId"]: slot for slot in typography_slots["slots"]}
    scene2 = scene_map["scene-2-lesson-intro"]
    scene3 = scene_map["scene-3-repeat-listen"]
    scene4 = scene_map["scene-4-quiz-point"]
    scene5 = scene_map["scene-5-ending-wave"]
    typography_slot_index["scene-2-sentence-main"]["inTimeSec"] = round(float(slot_index["scene-2-intro-ko"]["startSec"]) - 0.05, 3)
    typography_slot_index["scene-2-sentence-main"]["outTimeSec"] = round(scene2.end_sec - 0.25, 3)
    typography_slot_index["scene-3-repeat-sentence"]["inTimeSec"] = round(sentence_start - 0.05, 3)
    typography_slot_index["scene-3-repeat-sentence"]["outTimeSec"] = round(min(scene3.end_sec - 0.2, float(sentence_slot["endSec"]) + float(sentence_slot.get("pauseAfterSec") or 1.0)), 3)
    typography_slot_index["scene-4-quiz-blank"]["inTimeSec"] = round(scene4.start_sec + 0.15, 3)
    typography_slot_index["scene-4-quiz-blank"]["outTimeSec"] = round(scene4.end_sec - 0.15, 3)
    typography_slot_index["scene-4-cta-lower-third"]["sceneId"] = "scene-5-ending-wave"
    typography_slot_index["scene-4-cta-lower-third"]["inTimeSec"] = round(max(scene5.start_sec + 0.1, float(slot_index["scene-5-ending-ko"]["startSec"]) - 0.05), 3)
    typography_slot_index["scene-4-cta-lower-third"]["outTimeSec"] = round(min(scene5.end_sec - 0.25, float(slot_index["scene-5-ending-ko"]["endSec"]) + 0.45), 3)
    typography_slots_path.write_text(json.dumps(typography_slots, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    total_duration = scene_ranges[-1].end_sec
    audio_mix_path = dub_lock_dir / f"{episode_dir.name}-guide-dub.m4a"
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
    mix_cmd.extend(["-filter_complex", ";".join(filter_parts), "-map", "[out]", "-c:a", "aac", "-b:a", "192k", str(audio_mix_path)])
    run_ffmpeg(mix_cmd)

    total_frames = int(round(total_duration * FPS))
    for frame_index in range(total_frames):
        render_typography_frame(
            overlay_dir / f"frame-{frame_index:05d}.png",
            frame_index / FPS,
            typography_slots["slots"],
            handwriting_font=handwriting_font,
            subtitle_font=subtitle_font,
        )

    final_video_path = final_dir / f"{episode_dir.name}-final.mp4"
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

    thumb_path = final_dir / f"{episode_dir.name}-final-thumb.jpg"
    extract_time = max(scene4.start_sec + 1.2, 19.2)
    from render_daehan_pilot_final import extract_frame  # noqa: E402
    extract_frame(final_video_path, extract_time, thumb_path)

    review_dir = episode_dir / "review"
    build_review_bundle(final_video_path, review_dir, scene_ranges)

    audio_mean_db, audio_max_db = measure_audio_levels(audio_mix_path)
    audio_report = review_dir / "final-audio-analysis.md"
    audio_report.write_text(
        "# Final Audio Analysis\n\n"
        f"- audio mix: `{audio_mix_path.relative_to(episode_dir)}`\n"
        f"- mean volume: `{audio_mean_db:.1f} dB`\n"
        f"- max volume: `{audio_max_db:.1f} dB`\n"
        f"- content narration provider priority: `{episode_schema['policies']['audioPolicy']['contentTtsProvider']}` -> `{episode_schema['policies']['audioPolicy']['fallbackTtsProvider']}`\n"
        "- all episode lines are currently rendered as post-picture-lock guide dub\n",
        encoding="utf-8",
    )

    final_review_report = review_dir / "final-review-report.md"
    final_review_report.write_text(
        f"# Final Review: {episode_dir.name}\n"
        "날짜: 2026-04-17\n\n"
        "## 전체 요약\n"
        "- 상태: `keyframe-review-v1 final export`\n"
        "- 심각도: `pending visual QA`\n\n"
        "## 확인 항목\n"
        "- picture preview를 picture lock으로 승격해 guide dub + typography를 합성함\n"
        "- 대한 2D 캐릭터 continuity는 picture cut 기준으로 유지함\n"
        "- sentence / repeat sentence / blank quiz / CTA는 post typography로 합성함\n"
        "- 사람 더빙 교체용 `dubbing/audio-overrides/` 패키지를 함께 생성함\n",
        encoding="utf-8",
    )

    episode_schema["status"] = "final-export"
    episode_schema.setdefault("notes", {})
    episode_schema["notes"]["currentExecutionMode"] = "keyframe-review-v1-final"
    episode_schema["notes"]["latestReviewReport"] = "./review/final-review-report.md"
    episode_schema["notes"]["latestReviewSeverity"] = "pending-visual-qa"
    episode_schema["notes"]["pictureLockPath"] = f"./renders/picture-lock/{episode_dir.name}-picture-lock.mp4"
    episode_schema["notes"]["dubMixPath"] = f"./renders/dub-lock/{episode_dir.name}-guide-dub.m4a"
    episode_schema["notes"]["dubbingPackagePath"] = "./dubbing/README.md"
    episode_schema["notes"]["dubbingCuesPath"] = "./dubbing/dubbing-cues.csv"
    episode_schema["notes"]["finalExportPath"] = f"./renders/final/{episode_dir.name}-final.mp4"
    episode_schema["notes"]["thumbnailPath"] = f"./renders/final/{episode_dir.name}-final-thumb.jpg"
    write_json(episode_schema_path, episode_schema)

    packet_text = packet_path.read_text(encoding="utf-8")
    packet_text = packet_text.replace("- 상태: `picture-preview-ready`", "- 상태: `final-export`")
    packet_text = packet_text.replace("- 아직 하지 않은 일: TTS 더빙, 손글씨 칠판 타이포, 최종 음성 합성", "- 더빙 여부: `Supertone` 우선 guide dub 생성 완료, `dubbing/audio-overrides/`로 사람 더빙 교체 가능\n- 타이포 여부: 손글씨 굵은 칠판체와 CTA 하단 배너 합성 완료")
    packet_text = packet_text.replace(
        "1. picture preview를 보고 scene별 motion drift가 더 줄어들어야 하는지 결정한다.\n2. 확정되면 현재 picture cut을 기준으로 `Supertone` 더빙만 얹는다.\n3. 그 다음 손글씨 칠판 타이포를 후반 합성한다.\n",
        "1. 필요하면 `dubbing/audio-overrides/`에 사람 더빙이나 voice-pack 파일을 넣고 재렌더\n2. 문장 또는 CTA 문구만 수정할 경우 `voice-slots.json`, `typography-slots.json`만 갱신 후 재export\n3. 최종 패킷을 정리해 private YouTube upload 흐름으로 연결\n",
    )
    packet_path.write_text(packet_text, encoding="utf-8")

    render_manifest = {
        "episodeSlug": episode_dir.name,
        "formatProfile": profile_id,
        "previewPath": str(preview_path),
        "pictureLockPath": str(picture_lock_path),
        "audioMixPath": str(audio_mix_path),
        "finalVideoPath": str(final_video_path),
        "thumbnailPath": str(thumb_path),
        "reviewOverviewPath": str(review_dir / "final-contact-sheets" / "overview.jpg"),
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
