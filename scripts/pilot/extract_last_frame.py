#!/usr/bin/env python3

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg


def ffmpeg_bin() -> str:
    return imageio_ffmpeg.get_ffmpeg_exe()


def extract_last_frame(video: Path, output: Path, *, tail_sec: float = 1.0) -> None:
    """Seek `tail_sec` from end, then write each decoded frame to `output` with
    -update 1 so the final PNG = the true last frame. Avoids needing ffprobe
    (not bundled with imageio-ffmpeg)."""
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            ffmpeg_bin(),
            "-y",
            "-sseof", f"-{tail_sec:.3f}",
            "-i", str(video),
            "-update", "1",
            "-q:v", "1",
            str(output),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract the final frame of a video as a PNG.")
    parser.add_argument("--video", required=True, help="Input video path")
    parser.add_argument("--output", required=True, help="Output PNG path")
    parser.add_argument("--tail-sec", type=float, default=1.0, help="Seek `tail_sec` from end, then stream-update (default 1.0s)")
    args = parser.parse_args()

    video = Path(args.video).resolve()
    output = Path(args.output).resolve()
    if not video.exists():
        raise FileNotFoundError(f"Video not found: {video}")

    extract_last_frame(video, output, tail_sec=args.tail_sec)
    print(str(output))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise
