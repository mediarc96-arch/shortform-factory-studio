#!/usr/bin/env python3

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
PREP_SCRIPT = SCRIPT_DIR / "prepare_malmoelab_keyframe_jobs.py"
KEYFRAME_SCRIPT = SCRIPT_DIR / "generate_daehan_keyframes.py"
SCENE_SCRIPT = SCRIPT_DIR / "generate_daehan_keyframe_scenes.py"
PREVIEW_SCRIPT = SCRIPT_DIR / "build_malmoelab_quiz_picture_preview.py"


def default_python_bin() -> str:
    candidate = REPO_ROOT / ".venv-video-tools" / "bin" / "python"
    if candidate.exists():
        return str(candidate)
    return sys.executable


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the malmoelab keyframe render pipeline through picture preview.")
    parser.add_argument("--episode-dir", required=True)
    parser.add_argument("--env-file", default=".env")
    parser.add_argument("--python-bin", default=default_python_bin())
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    episode_dir = Path(args.episode_dir).resolve()
    env_file = Path(args.env_file).resolve()
    python_bin = args.python_bin
    force_flag = ["--force"] if args.force else []

    run([python_bin, str(PREP_SCRIPT), "--episode-dir", str(episode_dir)])
    run(
        [
            python_bin,
            str(KEYFRAME_SCRIPT),
            "--episode-dir",
            str(episode_dir),
            "--env-file",
            str(env_file),
            "--python-bin",
            python_bin,
            *force_flag,
        ]
    )
    run(
        [
            python_bin,
            str(SCENE_SCRIPT),
            "--episode-dir",
            str(episode_dir),
            "--env-file",
            str(env_file),
            "--python-bin",
            python_bin,
            *force_flag,
        ]
    )
    run([python_bin, str(PREVIEW_SCRIPT), "--episode-dir", str(episode_dir)])
    print(episode_dir / "renders" / "final" / f"{episode_dir.name}-picture-preview.mp4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
