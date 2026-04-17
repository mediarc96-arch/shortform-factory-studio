#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
RUN_SCENE_SCRIPT = SCRIPT_DIR / "run_xai_grok_scene.py"
EXTRACT_LAST_FRAME_SCRIPT = SCRIPT_DIR / "extract_last_frame.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate daehan-pilot-codex-003 picture-only scenes with last-frame handoff.")
    parser.add_argument("--episode-dir", required=True)
    parser.add_argument("--env-file", default=".env")
    parser.add_argument("--python-bin", default=sys.executable)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def main() -> int:
    args = parse_args()
    episode_dir = Path(args.episode_dir).resolve()
    env_file = Path(args.env_file).resolve()
    python_bin = args.python_bin
    jobs_dir = episode_dir / "scene-jobs"

    ordered_jobs = [
        jobs_dir / "scene-1-opening-handoff.json",
        jobs_dir / "scene-2-lesson-intro.json",
        jobs_dir / "scene-3-repeat-listen.json",
        jobs_dir / "scene-4-quiz-point.json",
        jobs_dir / "scene-5-ending-wave.json",
    ]

    for job_path in ordered_jobs:
        job = json.loads(job_path.read_text(encoding="utf-8"))
        output_path = (job_path.parent / job["runner"]["outputFile"]).resolve()
        manifest_path = (job_path.parent / job["runner"]["manifestFile"]).resolve()
        handoff = job.get("handoff") or {}
        handoff_path = (job_path.parent / handoff.get("lastFramePath", "")).resolve() if handoff else None

        if output_path.exists() and output_path.stat().st_size > 0 and not args.force:
            print(f"skip  {output_path}")
        else:
            run([python_bin, str(RUN_SCENE_SCRIPT), "--job", str(job_path), "--env-file", str(env_file)])

        if handoff.get("extractLastFrame") and handoff_path:
            if handoff_path.exists() and not args.force:
                print(f"skip  {handoff_path}")
            else:
                run([python_bin, str(EXTRACT_LAST_FRAME_SCRIPT), "--video", str(output_path), "--output", str(handoff_path)])

        print(str(manifest_path))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
