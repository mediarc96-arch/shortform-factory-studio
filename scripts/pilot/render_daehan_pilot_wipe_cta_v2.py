#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(SCRIPT_DIR.parent))

from build_preview_bundle_wipe_cta import build_contact_sheets, build_preview, write_review_metadata  # noqa: E402
from format_profiles import load_profile_for_episode_schema  # noqa: E402
from render_daehan_pilot_final import (  # noqa: E402
    FPS,
    HEIGHT,
    ROOT,
    WIDTH,
    build_review_bundle,
    copy_processed_audio,
    draw_centered_lines,
    draw_left_lines,
    export_reference_scene_clip,
    extract_audio_segment,
    extract_frame,
    fit_text,
    load_env_file,
    load_json,
    load_scene_ranges,
    measure_audio_levels,
    media_duration,
    media_has_audio,
    normalize_audio_mean_volume,
    resolve_episode_asset_path,
    resolve_ffmpeg_binary,
    run_ffmpeg,
    synthesize_guide_tts,
    trim_audio_edges,
    write_json,
)
from tts.supertone_client import SupertoneClient, VoiceSettings  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render wipe-cta-v2 final dub+type export for a daehan pilot.")
    parser.add_argument("--episode-dir", required=True)
    parser.add_argument("--env-file", default=".env")
    return parser.parse_args()


def synthesize_supertone_guide_tts(output_path: Path, *, text: str, speed: float) -> Path:
    client = SupertoneClient.from_env()
    settings = VoiceSettings(speed=speed) if abs(speed - 1.0) > 1e-6 else None
    client.synthesize(
        text,
        output_path=output_path,
        output_format="mp3",
        voice_settings=settings,
    )
    trim_audio_edges(output_path)
    normalize_audio_mean_volume(output_path, target_mean_db=-19.0, peak_ceiling_db=-2.0)
    return output_path


def synthesize_slot(output_path: Path, *, text: str, speed: float, provider: str) -> tuple[Path, str]:
    provider_key = str(provider or "").strip().lower()
    if provider_key == "supertone":
        try:
            return synthesize_supertone_guide_tts(output_path, text=text, speed=speed), "supertone-guide"
        except Exception:
            return synthesize_guide_tts(output_path, text=text, speed=speed), "elevenlabs-guide-fallback"
    return synthesize_guide_tts(output_path, text=text, speed=speed), "elevenlabs-guide"


def render_typography_frame(output_path: Path, t: float, slots: list[dict]) -> None:
    board_text = (247, 246, 240, 255)
    board_muted = (220, 233, 226, 255)
    board_stroke = (22, 51, 38, 225)
    subtitle_box = (7, 10, 18, 210)
    subtitle_text = (255, 255, 255, 255)
    subtitle_stroke = (7, 10, 18, 255)
    cta_accent = (255, 211, 111, 255)

    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    active_slots = [slot for slot in slots if float(slot["inTimeSec"]) <= t < float(slot["outTimeSec"])]
    board_slots = [slot for slot in active_slots if slot["surface"] == "chalkboard"]
    subtitle_slots = [slot for slot in active_slots if slot["surface"] == "subtitle-lower-third"]

    if board_slots:
        board_slot = board_slots[0]
        font, lines = fit_text(draw, board_slot["text"], 640, max_size=52, min_size=38, bold=True)
        draw_left_lines(
            draw,
            lines,
            x=92,
            y=134,
            font=font,
            fill=board_text,
            stroke_fill=board_stroke,
            stroke_width=3,
            line_gap=12,
        )
        draw.rounded_rectangle((84, 118, 710, 286), radius=28, outline=(235, 245, 239, 80), width=2)

    if subtitle_slots:
        subtitle = subtitle_slots[0]["text"]
        font, lines = fit_text(draw, subtitle, 980, max_size=38, min_size=28, bold=True)
        text_height = len(lines) * font.size + max(0, len(lines) - 1) * 8
        box_width = 1060
        box_height = text_height + 38
        left = (WIDTH - box_width) // 2
        top = HEIGHT - box_height - 34
        rect = (left, top, left + box_width, top + box_height)

        shadow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.rounded_rectangle((rect[0] + 4, rect[1] + 6, rect[2] + 4, rect[3] + 6), radius=30, fill=(0, 0, 0, 72))
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=10))
        overlay.alpha_composite(shadow)
        draw = ImageDraw.Draw(overlay)
        draw.rounded_rectangle(rect, radius=30, fill=subtitle_box, outline=(255, 255, 255, 42), width=2)
        badge = (left + 22, top + 14, left + 186, top + 52)
        draw.rounded_rectangle(badge, radius=18, fill=cta_accent)
        draw_centered_lines(
            draw,
            ["더 알아보기"],
            x=(badge[0] + badge[2]) // 2,
            y=badge[1] + 8,
            font=fit_text(draw, "더 알아보기", 150, max_size=24, min_size=20, bold=True)[0],
            fill=(34, 36, 30, 255),
            line_gap=2,
        )
        draw_centered_lines(
            draw,
            lines,
            x=WIDTH // 2,
            y=top + 64,
            font=font,
            fill=subtitle_text,
            stroke_fill=subtitle_stroke,
            stroke_width=2,
            line_gap=8,
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    overlay.save(output_path)


def update_slot(slot: dict, *, start_sec: float, duration_sec: float, render_text: str, active_path: Path, active_source: str, episode_dir: Path, scene_id: str) -> None:
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
    if profile_id != "wipe-cta-v2":
        raise ValueError(f"render_daehan_pilot_wipe_cta_v2.py only supports wipe-cta-v2, got {profile_id}")

    ffmpeg = resolve_ffmpeg_binary()
    preview_path = episode_dir / "renders" / "final" / f"{episode_dir.name}-preview-cut.mp4"
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
        dubbing_audio_override_dir,
        dubbing_guide_audio_dir,
        dubbing_reference_video_dir,
    ]:
        directory.mkdir(parents=True, exist_ok=True)

    picture_lock_path = picture_lock_dir / f"{episode_dir.name}-picture-lock.mp4"
    shutil.copyfile(preview_path, picture_lock_path)

    opening_video = ROOT / "characters" / "daehan" / "01_Opening.mp4"
    ending_video = ROOT / "characters" / "daehan" / "02_Ending.mp4"
    opening_audio = extract_audio_segment(opening_video, dub_lock_dir / "opening-embedded.m4a", start=0.0, duration=3.0)
    ending_audio: Path | None = None
    if media_has_audio(ending_video):
        ending_audio = extract_audio_segment(ending_video, dub_lock_dir / "ending-embedded.m4a", start=0.0, duration=4.0)

    slot_index = {slot["voiceSlotId"]: slot for slot in voice_slots["slots"]}
    generated_segments: list[dict] = [
        {"slotId": "opening-embedded", "path": opening_audio, "start": 0.0, "volume": 1.0},
    ]

    scene1 = scene_map["scene-1-lesson-intro"]
    scene2 = scene_map["scene-2-guided-repeat"]
    scene3 = scene_map["scene-3-quiz-cta"]
    scene4 = scene_map["scene-4-ending"]
    repeat_pause = float(profile["audioPolicy"]["timingRules"]["repeatCuePauseSec"])
    post_sentence_pause = float(profile["audioPolicy"]["timingRules"]["postSentencePauseSec"])

    dynamic_plan = [
        {
            "voiceSlotId": "scene-1-intro-ko",
            "sceneId": "scene-1-lesson-intro",
            "startSec": round(scene1.start_sec + 1.0, 3),
            "provider": "supertone",
            "speed": float(slot_index["scene-1-intro-ko"].get("speed") or 1.0),
        },
        {
            "voiceSlotId": "scene-2-repeat-cue-ko",
            "sceneId": "scene-2-guided-repeat",
            "startSec": round(scene2.start_sec + 0.8, 3),
            "provider": "supertone",
            "speed": float(slot_index["scene-2-repeat-cue-ko"].get("speed") or 1.0),
        },
    ]

    plan_outputs: dict[str, Path] = {}
    plan_sources: dict[str, str] = {}
    plan_durations: dict[str, float] = {}

    for plan in dynamic_plan:
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
            active_path, active_source = synthesize_slot(
                output_path,
                text=slot["text"],
                speed=float(plan["speed"]),
                provider=str(slot.get("ttsProvider") or episode_schema["policies"]["audioPolicy"]["contentTtsProvider"]),
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
        plan_outputs[slot_id] = active_path
        plan_sources[slot_id] = active_source
        plan_durations[slot_id] = duration

    cue_end = float(slot_index["scene-2-repeat-cue-ko"]["endSec"])
    sentence_start = round(cue_end + repeat_pause, 3)
    sentence_slot = slot_index["scene-2-sentence-ko"]
    sentence_output = narration_dir / "scene-2-sentence-ko.mp3"
    sentence_active, sentence_source = synthesize_slot(
        sentence_output,
        text=sentence_slot["text"],
        speed=float(sentence_slot.get("speed") or 1.0),
        provider=str(sentence_slot.get("ttsProvider") or episode_schema["policies"]["audioPolicy"]["contentTtsProvider"]),
    )
    sentence_duration = media_duration(sentence_active)
    shutil.copyfile(sentence_output, dubbing_guide_audio_dir / sentence_output.name)
    sentence_slot["guideAsset"] = str((dubbing_guide_audio_dir / sentence_output.name).relative_to(episode_dir))
    sentence_slot["selectedAsset"] = str(sentence_active.relative_to(episode_dir))
    update_slot(
        sentence_slot,
        start_sec=sentence_start,
        duration_sec=sentence_duration,
        render_text=str(sentence_slot["text"]),
        active_path=sentence_active,
        active_source=sentence_source,
        episode_dir=episode_dir,
        scene_id="scene-2-guided-repeat",
    )
    generated_segments.append({"slotId": "scene-2-sentence-ko", "path": sentence_active, "start": sentence_start, "volume": 1.0})

    cta_slot = slot_index["scene-3-cta-ko"]
    cta_output = narration_dir / "scene-3-cta-ko.mp3"
    cta_start = round(max(scene3.start_sec + 1.0, sentence_start + sentence_duration + post_sentence_pause), 3)
    cta_active, cta_source = synthesize_slot(
        cta_output,
        text=cta_slot["text"],
        speed=float(cta_slot.get("speed") or 1.0),
        provider=str(cta_slot.get("ttsProvider") or episode_schema["policies"]["audioPolicy"]["contentTtsProvider"]),
    )
    cta_duration = media_duration(cta_active)
    shutil.copyfile(cta_output, dubbing_guide_audio_dir / cta_output.name)
    cta_slot["guideAsset"] = str((dubbing_guide_audio_dir / cta_output.name).relative_to(episode_dir))
    cta_slot["selectedAsset"] = str(cta_active.relative_to(episode_dir))
    update_slot(
        cta_slot,
        start_sec=cta_start,
        duration_sec=cta_duration,
        render_text=str(cta_slot["text"]),
        active_path=cta_active,
        active_source=cta_source,
        episode_dir=episode_dir,
        scene_id="scene-3-quiz-cta",
    )
    generated_segments.append({"slotId": "scene-3-cta-ko", "path": cta_active, "start": cta_start, "volume": 1.0})

    opening_slot = slot_index["opening-embedded"]
    opening_slot["selectedAsset"] = "characters/daehan/01_Opening.mp4#audio"
    opening_slot["selectedSource"] = "original-clip-audio"
    opening_slot["startSec"] = 0.0
    opening_slot["durationSec"] = round(media_duration(opening_audio), 3)

    ending_slot = slot_index["ending-embedded"]
    if ending_audio is not None:
        ending_slot["selectedAsset"] = "characters/daehan/02_Ending.mp4#audio"
        ending_slot["selectedSource"] = "original-clip-audio"
        ending_slot["activeRenderAsset"] = str(ending_audio.relative_to(episode_dir))
        ending_slot["startSec"] = round(scene4.start_sec, 3)
        ending_slot["durationSec"] = round(media_duration(ending_audio), 3)
        ending_slot["endSec"] = round(scene4.start_sec + media_duration(ending_audio), 3)
        generated_segments.append({"slotId": "ending-embedded", "path": ending_audio, "start": scene4.start_sec, "volume": 1.0})
    else:
        ending_output = narration_dir / "ending-embedded.mp3"
        ending_provider = str(ending_slot.get("fallbackTtsProvider") or "supertone")
        ending_active, ending_source = synthesize_slot(
            ending_output,
            text=ending_slot["text"],
            speed=0.94,
            provider=ending_provider,
        )
        shutil.copyfile(ending_output, dubbing_guide_audio_dir / ending_output.name)
        ending_slot["guideAsset"] = str((dubbing_guide_audio_dir / ending_output.name).relative_to(episode_dir))
        ending_slot["selectedAsset"] = str(ending_active.relative_to(episode_dir))
        update_slot(
            ending_slot,
            start_sec=scene4.start_sec,
            duration_sec=media_duration(ending_active),
            render_text=str(ending_slot["text"]),
            active_path=ending_active,
            active_source=ending_source,
            episode_dir=episode_dir,
            scene_id="scene-4-ending",
        )
        generated_segments.append({"slotId": "ending-embedded", "path": ending_active, "start": scene4.start_sec, "volume": 1.0})

    voice_slots_path.write_text(json.dumps(voice_slots, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    slot_id_to_scene = {
        "scene-1-intro-ko": "scene-1-lesson-intro",
        "scene-2-repeat-cue-ko": "scene-2-guided-repeat",
        "scene-2-sentence-ko": "scene-2-guided-repeat",
        "scene-3-cta-ko": "scene-3-quiz-cta",
        "ending-embedded": "scene-4-ending",
    }
    for scene_id in ["scene-1-lesson-intro", "scene-2-guided-repeat", "scene-3-quiz-cta", "scene-4-ending"]:
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
                "reference_video",
            ]
        )
        for slot_id, scene_id in slot_id_to_scene.items():
            slot = slot_index[slot_id]
            scene = scene_map[scene_id]
            writer.writerow(
                [
                    slot_id,
                    scene_id,
                    f"{scene.start_sec:.3f}",
                    f"{float(slot['startSec']):.3f}",
                    f"{float(slot.get('endSec', float(slot['startSec']) + float(slot['durationSec']))):.3f}",
                    f"{float(slot['durationSec']):.3f}",
                    slot.get("text") or "",
                    slot.get("selectedSource") or "",
                    slot.get("recordingTarget") or "",
                    f"dubbing/reference-video/{scene_id}.mp4",
                ]
            )

    recording_script_lines = [
        "# Recording Script",
        "",
        "사람 더빙이나 성우 녹음을 넣을 때는 `audio-overrides/` 아래 대응 파일명을 그대로 사용하면 된다.",
        "",
    ]
    for slot_id in ["scene-1-intro-ko", "scene-2-repeat-cue-ko", "scene-2-sentence-ko", "scene-3-cta-ko", "ending-embedded"]:
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
        ".venv-video-tools/bin/python scripts/pilot/render_daehan_pilot_wipe_cta_v2.py --episode-dir episodes/daehan-pilot-codex-002 --env-file .env\n"
        "```\n",
        encoding="utf-8",
    )

    typography_slot_index = {slot["slotId"]: slot for slot in typography_slots["slots"]}
    typography_slot_index["scene-1-sentence-main"]["inTimeSec"] = round(scene1.start_sec + 0.8, 3)
    typography_slot_index["scene-1-sentence-main"]["outTimeSec"] = round(scene1.end_sec - 0.2, 3)
    typography_slot_index["scene-2-repeat-sentence"]["inTimeSec"] = round(sentence_start - 0.05, 3)
    typography_slot_index["scene-2-repeat-sentence"]["outTimeSec"] = round(min(scene2.end_sec - 0.2, sentence_start + sentence_duration + post_sentence_pause), 3)
    typography_slot_index["scene-3-quiz-blank"]["inTimeSec"] = round(scene3.start_sec + 0.3, 3)
    typography_slot_index["scene-3-quiz-blank"]["outTimeSec"] = round(scene3.end_sec - 0.2, 3)
    typography_slot_index["scene-3-cta-lower-third"]["inTimeSec"] = round(cta_start - 0.05, 3)
    typography_slot_index["scene-3-cta-lower-third"]["outTimeSec"] = round(min(scene3.end_sec - 0.2, cta_start + cta_duration + 1.0), 3)
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
        render_typography_frame(overlay_dir / f"frame-{frame_index:05d}.png", frame_index / FPS, typography_slots["slots"])

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
    extract_frame(final_video_path, scene3.start_sec + 1.2, thumb_path)

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
        "- opening source: `embedded original clip audio`\n"
        + ("- ending source: `embedded original clip audio`\n" if ending_audio is not None else "- ending source: `guide dub fallback`\n"),
        encoding="utf-8",
    )

    final_review_report = review_dir / "final-review-report.md"
    final_review_report.write_text(
        f"# Final Review: {episode_dir.name}\n"
        "날짜: 2026-04-17\n\n"
        "## 전체 요약\n"
        "- 상태: `wipe-cta-v2 final export`\n"
        "- 심각도: `pending visual QA`\n\n"
        "## 확인 항목\n"
        "- opening -> content 경계는 `wipe-left`\n"
        "- content -> ending 경계는 `wipe-left`\n"
        "- 본편은 문장 소개 -> 따라하기 -> blank quiz CTA 흐름을 사용함\n"
        "- guide dub는 `Supertone` 우선, 필요시 `ElevenLabs` fallback 사용\n"
        "- blank question과 CTA는 post typography로 합성함\n",
        encoding="utf-8",
    )

    episode_schema["status"] = "final-export"
    episode_schema.setdefault("notes", {})
    episode_schema["notes"]["currentExecutionMode"] = "wipe-cta-v2-final"
    episode_schema["notes"]["latestReviewReport"] = "./review/final-review-report.md"
    episode_schema["notes"]["latestReviewSeverity"] = "pending-visual-qa"
    episode_schema["notes"]["pictureLockPath"] = f"./renders/picture-lock/{episode_dir.name}-picture-lock.mp4"
    episode_schema["notes"]["previewCutPath"] = f"./renders/final/{episode_dir.name}-preview-cut.mp4"
    episode_schema["notes"]["dubMixPath"] = f"./renders/dub-lock/{episode_dir.name}-guide-dub.m4a"
    episode_schema["notes"]["finalExportPath"] = f"./renders/final/{episode_dir.name}-final.mp4"
    episode_schema["notes"]["thumbnailPath"] = f"./renders/final/{episode_dir.name}-final-thumb.jpg"
    episode_schema["notes"]["dubbingPackagePath"] = "./dubbing/README.md"
    episode_schema["notes"]["dubbingCuesPath"] = "./dubbing/dubbing-cues.csv"
    write_json(episode_schema_path, episode_schema)

    packet_text = packet_path.read_text(encoding="utf-8")
    packet_text = packet_text.replace("- 상태: `profile-seeded`", "- 상태: `final-export`")
    packet_text = packet_text.replace("- 렌더 여부: 아직 생성 전", "- 렌더 여부: preview/final 렌더 완료")
    packet_text = packet_text.replace("- 더빙 여부: `Supertone` 기준 슬롯 정의 완료, 실제 오디오 미생성", "- 더빙 여부: `Supertone` 우선 guide dub 생성 완료, `dubbing/audio-overrides/`로 사람 더빙 교체 가능")
    packet_text = packet_text.replace("- 타이포 여부: sentence/blank/CTA slot 정의 완료", "- 타이포 여부: sentence/blank/CTA typography 합성 완료")
    packet_text = packet_text.replace(
        "1. `scene-jobs/` 기준으로 본편 3개 scene 생성\n2. `wipe-cta-v2` 규칙에 맞는 preview builder 작성 또는 기존 builder 확장\n3. `Supertone`으로 guide dub 생성\n4. picture lock 후 typography와 CTA를 합성\n",
        "1. 필요하면 `dubbing/audio-overrides/`에 사람 더빙이나 voice-pack 파일을 넣고 재렌더\n2. scene 동작/연속성 수정이 필요하면 `scene-jobs/`를 조정해 재생성\n3. CTA 문구와 sentence typography만 바꿀 경우 `typography-slots.json`만 수정 후 재export\n",
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
