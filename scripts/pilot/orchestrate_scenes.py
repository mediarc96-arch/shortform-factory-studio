#!/usr/bin/env python3
"""Walk `video-generation-job.json` and drive Grok scene generation with
frame-handoff continuity.

For each scene in executionOrder:
  1. Build a per-scene job.json compatible with run_xai_grok_scene.py
     (absolute paths so `normalize_request` can base64-embed the images)
  2. Invoke run_xai_grok_scene.py as a subprocess
  3. If handoff.extractLastFrame=true, extract last frame via
     extract_last_frame.py so the next scene can seed off it

Idempotent — scenes whose output .mp4 already exists are skipped unless --force.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]

RUN_GROK_SCRIPT = SCRIPT_DIR / "run_xai_grok_scene.py"
EXTRACT_FRAME_SCRIPT = SCRIPT_DIR / "extract_last_frame.py"


def load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


REPO_ROOT_PREFIXES = ("characters/", "shared/", "episodes/")


def resolve_path(raw: str, *, episode_dir: Path, repo_root: Path) -> Path:
    """Resolve a path that may be relative to either the episode dir or repo root.

    Paths starting with a known repo-root prefix (characters/, shared/, episodes/)
    resolve from repo_root; everything else resolves from episode_dir — including
    handoff frames that don't exist yet.
    """
    p = Path(raw)
    if p.is_absolute():
        return p.resolve()
    if raw.startswith(REPO_ROOT_PREFIXES):
        return (repo_root / p).resolve()
    return (episode_dir / p).resolve()


GROK_SUPPORTED_RESOLUTIONS = {"480p", "720p"}


def build_resolution(raw: str) -> str:
    """Normalize resolution to an xAI-supported value (480p / 720p).

    Grok Video currently rejects anything larger than 720p. We generate at 720p
    and upscale in MoviePy composition.
    """
    raw = raw.lower()
    if raw.endswith("p"):
        candidate = raw
    elif "x" in raw:
        _, height_s = raw.split("x")
        candidate = f"{int(height_s)}p"
    else:
        candidate = raw
    if candidate in GROK_SUPPORTED_RESOLUTIONS:
        return candidate
    return "720p"


def extend_prompt(base_prompt: str, *, composition_rule: str | None, negative_prompt: str | None) -> str:
    parts = [base_prompt.strip()]
    if composition_rule:
        parts.append(f"Composition: {composition_rule.strip()}")
    if negative_prompt:
        parts.append(f"AVOID: {negative_prompt.strip()}")
    return "\n\n".join(parts)


def build_scene_job(scene: dict, *, global_settings: dict, episode_dir: Path, repo_root: Path) -> tuple[dict, Path, Path]:
    ref_paths_raw: list[str] = list(scene.get("referenceImages") or [])
    if not ref_paths_raw:
        raise ValueError(f"Scene {scene['sceneId']} has no referenceImages")

    seed_raw = ref_paths_raw[-1]
    extra_refs_raw = ref_paths_raw[:-1]

    # Seed path may not exist yet at dry-run time (it's the prior scene's handoff
    # frame, produced during execution). run_xai_grok_scene.py will raise when
    # it tries to base64-embed it. Reference images, however, should exist now —
    # they are character bases that must already be on disk.
    seed_path = resolve_path(seed_raw, episode_dir=episode_dir, repo_root=repo_root)
    extra_refs = [
        str(resolve_path(r, episode_dir=episode_dir, repo_root=repo_root))
        for r in extra_refs_raw
    ]
    for ref in extra_refs:
        if not Path(ref).exists():
            raise FileNotFoundError(f"Reference image missing: {ref}  (for scene {scene['sceneId']})")

    renders_dir = episode_dir / "renders" / "grok"
    renders_dir.mkdir(parents=True, exist_ok=True)

    output_path = (episode_dir / scene["outputPath"]).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path = renders_dir / f"{scene['sceneId']}.manifest.json"

    prompt = extend_prompt(
        scene["prompt"],
        composition_rule=global_settings.get("compositionRule"),
        negative_prompt=global_settings.get("negativePromptCommon"),
    )

    # xAI API rejects `image` + `reference_images` together. Continuity seed
    # wins: the previous scene's last frame guarantees motion handoff, while
    # the character ref is already present in that frame.
    request_payload: dict[str, Any] = {
        "model": global_settings.get("model", "grok-imagine-video"),
        "prompt": prompt,
        "image": str(seed_path),
        "duration": int(round(scene["durationSec"])),
        "aspect_ratio": global_settings.get("aspectRatio", "16:9"),
        "resolution": build_resolution(global_settings.get("resolution", "720p")),
    }
    if "seed" in global_settings:
        request_payload["seed"] = global_settings["seed"]

    job = {
        "provider": "xai_grok",
        "taskType": "image_to_video",
        "request": request_payload,
        "runner": {
            "outputFile": str(output_path),
            "manifestFile": str(manifest_path),
        },
    }
    return job, output_path, manifest_path


def run_scene(scene: dict, *, global_settings: dict, episode_dir: Path, repo_root: Path, env_file: Path, python_bin: str, force: bool) -> None:
    job, output_path, _ = build_scene_job(scene, global_settings=global_settings, episode_dir=episode_dir, repo_root=repo_root)

    if output_path.exists() and output_path.stat().st_size > 0 and not force:
        print(f"skip  {scene['sceneId']}: {output_path.relative_to(episode_dir)} exists")
        return

    jobs_dir = episode_dir / "scene-jobs"
    jobs_dir.mkdir(parents=True, exist_ok=True)
    job_path = jobs_dir / f"{scene['sceneId']}.job.json"
    job_path.write_text(json.dumps(job, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"run   {scene['sceneId']}: {job_path.relative_to(episode_dir)}")
    subprocess.run(
        [python_bin, str(RUN_GROK_SCRIPT), "--job", str(job_path), "--env-file", str(env_file)],
        check=True,
    )


def extract_handoff_frame(scene: dict, *, episode_dir: Path, python_bin: str, force: bool) -> None:
    handoff = scene.get("handoff") or {}
    if not handoff.get("extractLastFrame"):
        return
    last_frame_raw = handoff.get("lastFramePath")
    if not last_frame_raw:
        return
    video_path = (episode_dir / scene["outputPath"]).resolve()
    frame_path = (episode_dir / last_frame_raw).resolve()
    if frame_path.exists() and not force:
        print(f"skip  handoff frame: {frame_path.relative_to(episode_dir)} exists")
        return
    print(f"frame {scene['sceneId']} -> {frame_path.relative_to(episode_dir)}")
    subprocess.run(
        [python_bin, str(EXTRACT_FRAME_SCRIPT), "--video", str(video_path), "--output", str(frame_path)],
        check=True,
    )


def extract_opening_frame(job: dict, *, episode_dir: Path, repo_root: Path, python_bin: str, force: bool) -> None:
    fixed_clips = job.get("fixedClips") or {}
    opening = fixed_clips.get("opening") or {}
    source_raw = opening.get("source")
    target_raw = (job.get("globalSettings") or {}).get("openingReferenceFrame")
    if not source_raw or not target_raw:
        print("skip  opening frame: fixedClips.opening.source / globalSettings.openingReferenceFrame missing")
        return
    source_path = resolve_path(source_raw, episode_dir=episode_dir, repo_root=repo_root)
    target_path = (episode_dir / target_raw).resolve()
    if target_path.exists() and not force:
        print(f"skip  opening frame: {target_path.relative_to(episode_dir)} exists")
        return
    print(f"frame opening -> {target_path.relative_to(episode_dir)}")
    subprocess.run(
        [python_bin, str(EXTRACT_FRAME_SCRIPT), "--video", str(source_path), "--output", str(target_path)],
        check=True,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Orchestrate Grok scene generation with frame handoff.")
    parser.add_argument("--job-file", required=True, help="Path to video-generation-job.json")
    parser.add_argument("--env-file", default=".env")
    parser.add_argument("--python-bin", default=sys.executable)
    parser.add_argument("--only", help="Run only scene matching this sceneId")
    parser.add_argument("--force", action="store_true", help="Regenerate even if outputs exist")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    env_file = Path(args.env_file).resolve()
    load_env_file(env_file)

    job_path = Path(args.job_file).resolve()
    job = json.loads(job_path.read_text(encoding="utf-8"))
    episode_dir = job_path.parent
    global_settings = job.get("globalSettings") or {}
    scenes = job.get("scenes") or []
    scenes_by_id = {s["sceneId"]: s for s in scenes}

    def resolve_scene(id_or_prefix: str) -> dict | None:
        if id_or_prefix in scenes_by_id:
            return scenes_by_id[id_or_prefix]
        matches = [s for s in scenes if s["sceneId"].startswith(id_or_prefix + "-") or s["sceneId"] == id_or_prefix]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            raise ValueError(f"Ambiguous scene id prefix: {id_or_prefix} -> {[s['sceneId'] for s in matches]}")
        return None

    execution_order = job.get("executionOrder") or []
    if not execution_order:
        execution_order = [f"generate-{s['sceneId']}" for s in scenes]

    for step in execution_order:
        if step == "extract-opening-last-frame":
            extract_opening_frame(job, episode_dir=episode_dir, repo_root=REPO_ROOT, python_bin=args.python_bin, force=args.force)
        elif step.startswith("generate-"):
            scene_id = step[len("generate-"):]
            scene = resolve_scene(scene_id)
            if not scene:
                print(f"warn  executionOrder references unknown scene: {scene_id}")
                continue
            if args.only and args.only not in (scene["sceneId"], scene_id):
                print(f"skip  {scene['sceneId']}: --only={args.only}")
                continue
            run_scene(
                scene,
                global_settings=global_settings,
                episode_dir=episode_dir,
                repo_root=REPO_ROOT,
                env_file=env_file,
                python_bin=args.python_bin,
                force=args.force,
            )
        elif step.startswith("extract-") and step.endswith("-last-frame"):
            scene_id = step[len("extract-"):-len("-last-frame")]
            scene = resolve_scene(scene_id)
            if not scene:
                continue
            extract_handoff_frame(scene, episode_dir=episode_dir, python_bin=args.python_bin, force=args.force)
        elif step in {"generate-tts-audio", "compose-final"}:
            # Handled by run_pilot.py, not this script.
            continue
        else:
            print(f"warn  unrecognized executionOrder step: {step}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f"error: subprocess failed rc={exc.returncode} cmd={exc.cmd}", file=sys.stderr)
        raise SystemExit(exc.returncode)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise
