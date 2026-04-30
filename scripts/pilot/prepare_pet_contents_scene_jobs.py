#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def summarize_style_lock(style_lock_path: Path) -> str:
    if not style_lock_path.exists():
        return ""
    lines: list[str] = []
    for raw_line in style_lock_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        lower = line.lower()
        if "negative prompt" in lower or "재사용 prompt 블록" in line or "사용 규칙" in line:
            continue
        lines.append(line.strip("-* ").strip())
    compact = " ".join(line for line in lines if line)
    return compact[:600]


def ensure_keyframe_from_storyboard(source_path: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source_path) as image:
        image.convert("RGB").save(output_path, format="JPEG", quality=95)


def keyframe_output_path(keyframe: dict, key: str) -> str:
    value = keyframe.get(key)
    if isinstance(value, dict):
        value = value.get("outputPath")
    return str(value or "").strip()


def keyframe_source_cut_id(keyframe: dict, key: str = "sourceCutId") -> str:
    value = keyframe.get(key)
    if isinstance(value, dict):
        value = value.get("sourceCutId")
    return str(value or keyframe.get("sourceCutId") or "").strip()


def scene_prompt(
    *,
    protagonist_name: str,
    source_cut: dict | None,
    keyframe: dict | None,
    scene: dict,
    global_settings: dict,
    style_summary: str,
) -> str:
    parts = [
        "Use the provided frame as the exact first frame.",
        f"Keep the same {protagonist_name} identity, the same approved original drawing style, and the same storyboard-established geography.",
        "Preserve the approved pet design exactly. Do not reinterpret the character into a different art style.",
    ]

    provider_expectation = str(scene.get("providerExpectation") or "").strip()
    if provider_expectation:
        parts.append(provider_expectation)

    cut_beat = str((source_cut or {}).get("beat") or "").strip()
    if cut_beat:
        parts.append(f"Story beat: {cut_beat}")

    keyframe_pose = str((keyframe or {}).get("pose") or "").strip()
    if keyframe_pose:
        parts.append(f"Approved start pose: {keyframe_pose}")

    keyframe_end_pose = str((keyframe or {}).get("endPose") or "").strip()
    if keyframe_end_pose:
        parts.append(f"Approved end pose: {keyframe_end_pose}")

    target_end_frame = str(scene.get("targetEndFramePath") or scene.get("endFramePath") or "").strip()
    if target_end_frame:
        parts.append(f"Aim the final frame toward the approved end frame file: {target_end_frame}.")

    camera_intent = str(scene.get("cameraIntent") or "").strip()
    if camera_intent:
        parts.append(f"Camera intent: {camera_intent}")

    boundary = scene.get("boundaryToNext") or {}
    boundary_mode = str(boundary.get("mode") or scene.get("boundaryMode") or "").strip()
    if boundary_mode:
        parts.append(f"Boundary mode after this scene: {boundary_mode}.")
    if boundary_mode == "continuous_handoff":
        parts.append("Final frame must be suitable as the next scene's first frame.")
    elif boundary_mode == "transition_cut":
        transition_type = str(boundary.get("transitionType") or "").strip()
        transition_purpose = str(boundary.get("purpose") or "").strip()
        transition_bridge = str(boundary.get("audioVisualBridge") or "").strip()
        if transition_type or transition_purpose or transition_bridge:
            parts.append(
                "Transition note: "
                + " ".join(
                    value
                    for value in [
                        f"type={transition_type}" if transition_type else "",
                        f"purpose={transition_purpose}" if transition_purpose else "",
                        f"bridge={transition_bridge}" if transition_bridge else "",
                    ]
                    if value
                )
            )

    continuity_notes = [str(note).strip() for note in list(scene.get("continuityNotes") or []) if str(note).strip()]
    if continuity_notes:
        parts.append("Continuity notes: " + " ".join(continuity_notes))

    if style_summary:
        parts.append(f"Style lock: {style_summary}")

    parts.append("No text, subtitles, logos, or watermarks anywhere in frame.")
    parts.append("Keep the tone comic, readable, safe, and non-violent.")
    return " ".join(part for part in parts if part)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare pet-contents scene orchestration jobs from storyboard cuts.")
    parser.add_argument("--episode-dir", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    episode_dir = Path(args.episode_dir).resolve()

    keyframe_plan = load_json(episode_dir / "keyframe-plan.json")
    video_job = load_json(episode_dir / "video-generation-job.json")
    storyboard_plan = load_json(episode_dir / "storyboard" / "storyboard-plan.json")
    source_packet = load_json(episode_dir / "source-packet.json")

    future_scenes = list(video_job.get("futureScenes") or [])
    if not future_scenes:
        raise ValueError("video-generation-job.json is missing futureScenes for pet contents render")

    cuts_by_id = {str(cut["id"]): cut for cut in list(storyboard_plan.get("cuts") or [])}
    keyframes = list(keyframe_plan.get("keyframes") or [])
    keyframes_by_scene = {str(keyframe["futureSceneId"]): keyframe for keyframe in keyframes}

    primary_pets = list((source_packet.get("cast") or {}).get("primaryPets") or [])
    protagonist_name = str((primary_pets[0] or {}).get("name") or "pet protagonist")
    global_settings = video_job.get("globalSettings") or {}
    style_summary = summarize_style_lock(episode_dir / str(global_settings.get("styleLockFile") or "storyboard/style-lock.md"))

    for keyframe in keyframes:
        source_cut_id = keyframe_source_cut_id(keyframe)
        source_cut = cuts_by_id.get(source_cut_id)
        if not source_cut:
            continue
        source_path = (episode_dir / str(source_cut["outputPath"])).resolve()
        start_output = keyframe_output_path(keyframe, "outputPath") or keyframe_output_path(keyframe, "startFrame")
        if start_output:
            ensure_keyframe_from_storyboard(source_path, (episode_dir / start_output).resolve())

        end_source_cut_id = keyframe_source_cut_id(keyframe, "endSourceCutId")
        end_source_cut = cuts_by_id.get(end_source_cut_id) if end_source_cut_id else source_cut
        end_output = keyframe_output_path(keyframe, "endFramePath") or keyframe_output_path(keyframe, "endFrame")
        if end_output and end_source_cut:
            end_source_path = (episode_dir / str(end_source_cut["outputPath"])).resolve()
            ensure_keyframe_from_storyboard(end_source_path, (episode_dir / end_output).resolve())

    scenes: list[dict] = []
    execution_order: list[str] = []

    for scene in future_scenes:
        scene_id = str(scene["sceneId"])
        keyframe = keyframes_by_scene.get(scene_id)
        source_cut = cuts_by_id.get(str(scene.get("sourceCutId") or (keyframe or {}).get("sourceCutId") or ""))
        output_path = str(scene.get("outputClipPath") or scene.get("outputPath") or "").strip()
        if not output_path:
            raise ValueError(f"{scene_id} is missing outputClipPath/outputPath")
        handoff_path = str(scene.get("handoffLastFramePath") or f"assets/refs/{scene_id}-last-frame.jpg")
        start_seed = str(scene.get("startSeed") or keyframe_output_path(keyframe or {}, "outputPath") or "").strip()
        if not start_seed:
            raise ValueError(f"{scene_id} is missing startSeed")
        target_end_frame = str(
            scene.get("targetEndFramePath")
            or scene.get("endFramePath")
            or keyframe_output_path(keyframe or {}, "endFramePath")
            or ""
        ).strip()
        boundary = scene.get("boundaryToNext") or (keyframe or {}).get("boundaryToNext") or {}

        scene_payload = {
            "sceneId": scene_id,
            "durationSec": float(scene.get("durationSec") or 3.0),
            "prompt": scene_prompt(
                protagonist_name=protagonist_name,
                source_cut=source_cut,
                keyframe=keyframe,
                scene={**scene, "targetEndFramePath": target_end_frame, "boundaryToNext": boundary},
                global_settings=global_settings,
                style_summary=style_summary,
            ),
            "referenceImages": [start_seed],
            "outputPath": output_path,
            "handoff": {
                "extractLastFrame": True,
                "lastFramePath": handoff_path,
            },
        }
        if target_end_frame:
            scene_payload["targetEndFramePath"] = target_end_frame
        if boundary:
            scene_payload["boundaryToNext"] = boundary
        scenes.append(scene_payload)
        execution_order.extend([f"generate-{scene_id}", f"extract-{scene_id}-last-frame"])

    orchestration_job = {
        "_schema": "pet contents xai scene orchestration",
        "globalSettings": {
            "model": "grok-imagine-video",
            "aspectRatio": str(global_settings.get("aspectRatio") or "9:16"),
            "resolution": str(global_settings.get("resolution") or "1080x1920"),
            "seed": global_settings.get("seed"),
            "compositionRule": global_settings.get("compositionRule"),
            "negativePromptCommon": global_settings.get("negativePromptCommon"),
        },
        "scenes": scenes,
        "executionOrder": execution_order,
    }

    write_json(episode_dir / "scene-orchestration-job.json", orchestration_job)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
