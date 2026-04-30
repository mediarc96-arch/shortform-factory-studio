#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]


def slug_to_display(slug: str) -> str:
    return " ".join(part.capitalize() for part in slug.replace("-", " ").replace("_", " ").split())


def relpath(from_dir: Path, to_path: Path) -> str:
    return os.path.relpath(to_path, from_dir).replace("\\", "/")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def scene_prompt(
    scene_id: str,
    provider_expectation: str,
    continuity_notes: list[str],
    display_name: str,
    boundary_to_next: dict | None = None,
    target_end_frame: str = "",
) -> str:
    notes = " ".join(note.strip() for note in continuity_notes if str(note).strip())
    boundary = boundary_to_next or {}
    boundary_mode = str(boundary.get("mode") or "").strip()
    boundary_note = ""
    if boundary_mode == "continuous_handoff":
        boundary_note = "Final frame must be suitable as the next scene's first frame. "
    elif boundary_mode == "transition_cut":
        transition_type = str(boundary.get("transitionType") or "").strip()
        transition_purpose = str(boundary.get("purpose") or "").strip()
        transition_bridge = str(boundary.get("audioVisualBridge") or "").strip()
        boundary_note = (
            "This scene ends before an intentional edit transition. "
            f"Transition type: {transition_type}. Purpose: {transition_purpose}. Bridge: {transition_bridge}. "
        )
    target_note = f"Aim the final frame toward approved end frame file {target_end_frame}. " if target_end_frame else ""
    return (
        f"Use the provided frame as the exact first frame. Keep the same {display_name} teacher identity, "
        "the same empty classroom, the same camera distance, and the same right-quarter composition. "
        f"{provider_expectation.strip()} "
        f"{notes} "
        f"{target_note}"
        f"{boundary_note}"
        "Transition naturally toward the approved target pose and expression. "
        "No camera reset, no tighter crop, and no text anywhere."
    ).strip()


def keyframe_prompt(
    display_name: str,
    render_style: str,
    pose: str,
    avoid: str,
) -> str:
    return (
        f"Keep the exact same {render_style}. "
        f"Use the input image as the canonical base for {display_name}. "
        f"{pose.strip()}. "
        "Keep the teacher on the right quarter of frame and keep the entire chalkboard empty and clean for later typography. "
        f"Avoid: {avoid.strip()}."
    )


def build_clean_base_job(
    *,
    episode_slug: str,
    display_name: str,
    source_image: Path,
    cleaned_path: Path,
    manifest_path: Path,
    grok_jobs_dir: Path,
) -> dict:
    return {
        "_schema": f"xAI image edit job · {episode_slug}",
        "provider": "xai_grok",
        "taskType": "image_edit",
        "request": {
            "model": "grok-imagine-image",
            "prompt": (
                f"Keep the exact same {display_name} teacher identity, same outfit, same classroom, same lighting, "
                "and same overall composition as the input image. Remove all text from the chalkboard if any exists "
                "and keep the board completely empty and clean. Keep the chalk and do not change the character identity."
            ),
            "image": {
                "url": relpath(grok_jobs_dir, source_image),
            },
            "n": 1,
        },
        "runner": {
            "outputFile": relpath(grok_jobs_dir, cleaned_path),
            "manifestFile": relpath(grok_jobs_dir, manifest_path),
        },
    }


def build_refine_wide_job(
    *,
    episode_slug: str,
    display_name: str,
    rough_path: Path,
    refined_path: Path,
    manifest_path: Path,
    grok_jobs_dir: Path,
) -> dict:
    return {
        "_schema": f"xAI image edit job · {episode_slug}",
        "provider": "xai_grok",
        "taskType": "image_edit",
        "request": {
            "model": "grok-imagine-image",
            "prompt": (
                f"This is a 16:9 widescreen base plate for a Korean lesson video. Keep the same {display_name} identity, "
                "teacher outfit, classroom tone, and right-side placement. Smooth out the chalkboard and wall so the "
                "entire frame looks naturally painted as one scene with no seams or stretching artifacts. The left board area "
                "must remain completely empty and clean for later typography. No text anywhere."
            ),
            "image": {
                "url": relpath(grok_jobs_dir, rough_path),
            },
            "n": 1,
        },
        "runner": {
            "outputFile": relpath(grok_jobs_dir, refined_path),
            "manifestFile": relpath(grok_jobs_dir, manifest_path),
        },
    }


def build_keyframe_job(
    *,
    episode_slug: str,
    display_name: str,
    keyframe: dict,
    refined_base_path: Path,
    render_style: str,
    avoid: str,
    output_path: Path,
    manifest_path: Path,
    grok_jobs_dir: Path,
) -> dict:
    return {
        "_schema": f"xAI image edit job · {episode_slug} keyframe",
        "provider": "xai_grok",
        "taskType": "image_edit",
        "request": {
            "model": "grok-imagine-image",
            "prompt": keyframe_prompt(
                display_name=display_name,
                render_style=render_style,
                pose=str(keyframe.get("pose") or ""),
                avoid=avoid,
            ),
            "image": {
                "url": relpath(grok_jobs_dir, refined_base_path),
            },
            "n": 1,
        },
        "runner": {
            "outputFile": relpath(grok_jobs_dir, output_path),
            "manifestFile": relpath(grok_jobs_dir, manifest_path),
        },
    }


def build_scene_job(
    *,
    scene: dict,
    display_name: str,
    global_settings: dict,
    episode_dir: Path,
    scene_jobs_dir: Path,
) -> dict:
    scene_id = str(scene["sceneId"])
    output_path = (episode_dir / "renders" / "picture" / f"{scene_id}.mp4").resolve()
    manifest_path = (episode_dir / "renders" / "grok" / f"{scene_id}.manifest.json").resolve()
    start_seed = (episode_dir / str(scene["startSeed"])).resolve()
    handoff_path = (episode_dir / str(scene["handoffLastFramePath"])).resolve()
    provider_expectation = str(scene.get("providerExpectation") or "")
    continuity_notes = list(scene.get("continuityNotes") or [])
    boundary_to_next = scene.get("boundaryToNext") or {}
    target_end_frame = str(scene.get("targetEndFramePath") or scene.get("endFramePath") or "")

    return {
        "provider": "xai_grok",
        "taskType": "image_to_video",
        "request": {
            "model": "grok-imagine-video",
            "prompt": scene_prompt(
                scene_id=scene_id,
                provider_expectation=provider_expectation,
                continuity_notes=continuity_notes,
                display_name=display_name,
                boundary_to_next=boundary_to_next,
                target_end_frame=target_end_frame,
            ),
            "image": relpath(scene_jobs_dir, start_seed),
            "duration": int(round(float(scene.get("durationSec") or 6.0))),
            "aspect_ratio": str(global_settings.get("aspectRatio") or "16:9"),
            "resolution": "720p",
        },
        "runner": {
            "outputFile": relpath(scene_jobs_dir, output_path),
            "manifestFile": relpath(scene_jobs_dir, manifest_path),
        },
        "handoff": {
            "extractLastFrame": True,
            "lastFramePath": relpath(scene_jobs_dir, handoff_path),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Materialize Grok keyframe and scene jobs for a malmoelab keyframe episode.")
    parser.add_argument("--episode-dir", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    episode_dir = Path(args.episode_dir).resolve()
    keyframe_plan = load_json(episode_dir / "keyframe-plan.json")
    video_job = load_json(episode_dir / "video-generation-job.json")

    episode_slug = str((keyframe_plan.get("episode") or {}).get("slug") or episode_dir.name)
    base_image = keyframe_plan.get("baseImage") or {}
    style_lock = keyframe_plan.get("styleLock") or {}
    global_settings = video_job.get("globalSettings") or {}
    future_scenes = list(video_job.get("futureScenes") or [])

    source_image = (REPO_ROOT / str(base_image["source"])).resolve()
    cleaned_path = (episode_dir / str(base_image["cleanedPath"])).resolve()
    rough_path = (episode_dir / str(base_image["widePrepPath"])).resolve()
    refined_path = (episode_dir / str(base_image["refinedWidePath"])).resolve()

    display_name = slug_to_display(source_image.stem)
    render_style = str(style_lock.get("renderStyle") or f"2D anime illustration matching {source_image.name}")
    avoid = str(style_lock.get("avoid") or global_settings.get("negativePromptCommon") or "text, subtitles, artifacts")

    grok_jobs_dir = episode_dir / "grok-jobs"
    scene_jobs_dir = episode_dir / "scene-jobs"
    (episode_dir / "assets" / "refs").mkdir(parents=True, exist_ok=True)
    (episode_dir / "keyframes").mkdir(parents=True, exist_ok=True)
    (episode_dir / "renders" / "picture").mkdir(parents=True, exist_ok=True)
    (episode_dir / "renders" / "grok").mkdir(parents=True, exist_ok=True)

    write_json(
        grok_jobs_dir / "clean-base-remove-text.json",
        build_clean_base_job(
            episode_slug=episode_slug,
            display_name=display_name,
            source_image=source_image,
            cleaned_path=cleaned_path,
            manifest_path=cleaned_path.with_suffix(".manifest.json"),
            grok_jobs_dir=grok_jobs_dir,
        ),
    )

    write_json(
        grok_jobs_dir / "clean-base-refine-wide.json",
        build_refine_wide_job(
            episode_slug=episode_slug,
            display_name=display_name,
            rough_path=rough_path,
            refined_path=refined_path,
            manifest_path=refined_path.with_suffix(".manifest.json"),
            grok_jobs_dir=grok_jobs_dir,
        ),
    )

    for index, keyframe in enumerate(list(keyframe_plan.get("keyframes") or []), start=1):
        output_path = (episode_dir / str(keyframe["outputPath"])).resolve()
        manifest_path = output_path.with_suffix(".manifest.json")
        future_scene_id = str(keyframe["futureSceneId"])
        if future_scene_id.startswith("scene-"):
            parts = future_scene_id.split("-", 2)
            scene_suffix = parts[2] if len(parts) == 3 else future_scene_id[len("scene-"):]
        else:
            scene_suffix = future_scene_id
        write_json(
            grok_jobs_dir / f"keyframe-{index:02d}-{scene_suffix}.json",
            build_keyframe_job(
                episode_slug=episode_slug,
                display_name=display_name,
                keyframe=keyframe,
                refined_base_path=refined_path,
                render_style=render_style,
                avoid=avoid,
                output_path=output_path,
                manifest_path=manifest_path,
                grok_jobs_dir=grok_jobs_dir,
            ),
        )

    for scene in future_scenes:
        scene_id = str(scene["sceneId"])
        write_json(
            scene_jobs_dir / f"{scene_id}.json",
            build_scene_job(
                scene=scene,
                display_name=display_name,
                global_settings=global_settings,
                episode_dir=episode_dir,
                scene_jobs_dir=scene_jobs_dir,
            ),
        )

    print(episode_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
