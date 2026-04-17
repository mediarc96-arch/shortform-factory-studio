#!/usr/bin/env python3
"""Top-level orchestrator for the Daehan pilot pipeline.

Pipeline (mirrors video-generation-job.json::executionOrder):
  1. extract_last_frame.py  → reference-frames/00-opening-last.png
  2. orchestrate_scenes.py  → renders/scene-{1..4}.mp4 + reference-frames/{01..03}-scene-last.png
  3. generate_narration.py  → audio/narration-ko-*.mp3 + audio/narration-timing.json
  4. compose_final.py       → renders/daehan-pilot-001.mp4

All steps are idempotent. Pass --force to regenerate.

The only step that costs money is (2) — orchestrate_scenes.py calls the xAI Grok
API. Use --skip-grok to dry-run the rest.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]

STEP_ORCHESTRATE = SCRIPT_DIR / "orchestrate_scenes.py"
STEP_NARRATION = REPO_ROOT / "scripts" / "tts" / "generate_narration.py"
STEP_COMPOSE = REPO_ROOT / "scripts" / "post" / "compose_final.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Daehan pilot pipeline end-to-end.")
    parser.add_argument("--episode-dir", required=True)
    parser.add_argument("--env-file", default=".env")
    parser.add_argument("--python-bin", default=sys.executable)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--skip-grok", action="store_true", help="Skip orchestrate_scenes (no xAI API calls)")
    parser.add_argument("--skip-tts", action="store_true", help="Skip generate_narration (no Supertone API calls)")
    parser.add_argument("--skip-compose", action="store_true", help="Skip final MoviePy composition")
    return parser.parse_args()


def run_step(cmd: list[str], *, label: str) -> None:
    print(f"\n===== {label} =====")
    print("  $", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main() -> int:
    args = parse_args()
    episode_dir = Path(args.episode_dir).resolve()
    if not episode_dir.exists():
        raise FileNotFoundError(f"Episode dir missing: {episode_dir}")

    python = args.python_bin
    force_flag = ["--force"] if args.force else []

    if not args.skip_grok:
        run_step(
            [
                python,
                str(STEP_ORCHESTRATE),
                "--job-file", str(episode_dir / "video-generation-job.json"),
                "--env-file", args.env_file,
                "--python-bin", python,
                *force_flag,
            ],
            label="1–2. Frame handoff + Grok scenes",
        )
    else:
        print("\nskip  orchestrate_scenes.py (--skip-grok)")

    if not args.skip_tts:
        run_step(
            [
                python,
                str(STEP_NARRATION),
                "--episode-dir", str(episode_dir),
                "--env-file", args.env_file,
                "--write-timing",
                *force_flag,
            ],
            label="3. Supertone TTS narration",
        )
    else:
        print("\nskip  generate_narration.py (--skip-tts)")

    if not args.skip_compose:
        run_step(
            [
                python,
                str(STEP_COMPOSE),
                "--episode-dir", str(episode_dir),
                "--env-file", args.env_file,
            ],
            label="4. MoviePy composition",
        )
    else:
        print("\nskip  compose_final.py (--skip-compose)")

    print("\nDone.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f"\nerror: step failed rc={exc.returncode}", file=sys.stderr)
        raise SystemExit(exc.returncode)
    except Exception as exc:
        print(f"\nerror: {exc}", file=sys.stderr)
        raise
