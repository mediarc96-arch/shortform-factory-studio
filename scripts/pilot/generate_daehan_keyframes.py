#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
RUN_IMAGE_SCRIPT = SCRIPT_DIR / "run_xai_grok_image.py"
PREP_BASE_SCRIPT = SCRIPT_DIR / "prepare_daehan_2d_base.py"
REVIEW_SCRIPT = SCRIPT_DIR / "build_keyframe_review_bundle.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate clean base + keyframes for daehan-pilot-codex-003.")
    parser.add_argument("--episode-dir", required=True)
    parser.add_argument("--env-file", default=".env")
    parser.add_argument("--python-bin", default=sys.executable)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def maybe_run(job_path: Path, output_path: Path, *, python_bin: str, env_file: Path, force: bool) -> None:
    if output_path.exists() and output_path.stat().st_size > 0 and not force:
        print(f"skip  {output_path}")
        return
    run([python_bin, str(RUN_IMAGE_SCRIPT), "--job", str(job_path), "--env-file", str(env_file)])


def main() -> int:
    args = parse_args()
    episode_dir = Path(args.episode_dir).resolve()
    env_file = Path(args.env_file).resolve()
    python_bin = args.python_bin

    keyframe_plan = json.loads((episode_dir / "keyframe-plan.json").read_text(encoding="utf-8"))

    clean_job = episode_dir / "grok-jobs" / "clean-base-remove-text.json"
    clean_out = (clean_job.parent / json.loads(clean_job.read_text(encoding="utf-8"))["runner"]["outputFile"]).resolve()
    maybe_run(clean_job, clean_out, python_bin=python_bin, env_file=env_file, force=args.force)

    rough_out = (episode_dir / keyframe_plan["baseImage"]["widePrepPath"]).resolve()
    if args.force or not rough_out.exists():
        run(
            [
                python_bin,
                str(PREP_BASE_SCRIPT),
                "--input",
                str(clean_out),
                "--output",
                str(rough_out),
            ]
        )
    else:
        print(f"skip  {rough_out}")

    refine_job = episode_dir / "grok-jobs" / "clean-base-refine-wide.json"
    refine_out = (refine_job.parent / json.loads(refine_job.read_text(encoding="utf-8"))["runner"]["outputFile"]).resolve()
    maybe_run(refine_job, refine_out, python_bin=python_bin, env_file=env_file, force=args.force)

    keyframe_ids = [
        "keyframe-01-opening-handoff.json",
        "keyframe-02-lesson-intro.json",
        "keyframe-03-repeat-listen.json",
        "keyframe-04-quiz-point.json",
        "keyframe-05-ending-wave.json",
    ]
    for filename in keyframe_ids:
        job_path = episode_dir / "grok-jobs" / filename
        output_name = filename.replace("keyframe-", "kf-").replace(".json", ".jpg")
        output_name = output_name.replace("01-opening-handoff", "01-opening-handoff")
        output_name = output_name.replace("02-lesson-intro", "02-lesson-intro")
        output_name = output_name.replace("03-repeat-listen", "03-repeat-listen")
        output_name = output_name.replace("04-quiz-point", "04-quiz-point")
        output_name = output_name.replace("05-ending-wave", "05-ending-wave")
        output_path = episode_dir / "keyframes" / output_name
        maybe_run(job_path, output_path, python_bin=python_bin, env_file=env_file, force=args.force)

    run([python_bin, str(REVIEW_SCRIPT), "--episode-dir", str(episode_dir)])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
