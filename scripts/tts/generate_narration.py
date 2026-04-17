#!/usr/bin/env python3
"""Generate per-scene Korean narration mp3 files for a Daehan pilot episode.

Source of truth: episodes/<slug>/narration-script.md (human-authored).
This script encodes the "TTS 생성용 세그먼트 요약" table into `SEGMENTS`
and drives scripts/tts/supertone_client.py for each segment.

Idempotent — existing outputs skipped unless --force.
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from tts.supertone_client import SupertoneClient, VoiceSettings, _load_env  # noqa: E402


@dataclass
class Segment:
    filename: str
    text: str
    speed: float = 1.0
    style: str | None = None
    # startSec on the final master timeline (seconds). Used only by --write-timing.
    start_sec: float = 0.0


# Mirrors episodes/daehan-pilot-001/narration-script.md §"TTS 생성용 세그먼트 요약".
# Opening (0.0-3.0) and Ending (26.7-30.0) reuse original clip audio, not TTS.
SEGMENTS: list[Segment] = [
    Segment("narration-ko-scene1.mp3", "풍선을 너무 크게 불었더니…",      speed=1.0, start_sec=3.5),
    Segment("narration-ko-scene2.mp3", "결국 빵 터져 버렸다!",            speed=0.9, start_sec=9.6),
    Segment("narration-ko-scene3.mp3", "빈칸에 들어갈 말은 무엇일까요?",  speed=1.0, start_sec=12.3),
    Segment("narration-ko-scene4-1.mp3", "정답은 빵!",                    speed=1.0, start_sec=22.0),
    Segment("narration-ko-scene4-2.mp3", "같이 따라해볼까요? 빵!",         speed=1.0, start_sec=24.0),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Daehan pilot TTS narration clips.")
    parser.add_argument("--episode-dir", required=True, help="e.g. episodes/daehan-pilot-001")
    parser.add_argument("--env-file", default=".env")
    parser.add_argument("--force", action="store_true", help="Regenerate even if file exists")
    parser.add_argument("--voice-id", default=None, help="Override voice ID (defaults to env)")
    parser.add_argument(
        "--write-timing",
        action="store_true",
        help="Also write audio/narration-timing.json with per-segment startSec offsets",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    _load_env(Path(args.env_file))

    episode_dir = Path(args.episode_dir).resolve()
    if not episode_dir.exists():
        raise FileNotFoundError(f"Episode dir not found: {episode_dir}")

    audio_dir = episode_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    client = SupertoneClient.from_env(voice_id=args.voice_id)

    generated: list[Path] = []
    for seg in SEGMENTS:
        output = audio_dir / seg.filename
        if output.exists() and not args.force:
            print(f"skip  {output.name}  (exists)")
            generated.append(output)
            continue

        settings = VoiceSettings(speed=seg.speed) if seg.speed != 1.0 else None
        client.synthesize(
            seg.text,
            output_path=output,
            output_format="mp3",
            style=seg.style,
            voice_settings=settings,
        )
        print(f"wrote {output.name}  ({output.stat().st_size // 1024} KB)")
        generated.append(output)

    if args.write_timing:
        import json

        timing = {
            "segments": [
                {
                    "file": f"audio/{seg.filename}",
                    "text": seg.text,
                    "speed": seg.speed,
                    "startSec": seg.start_sec,
                }
                for seg in SEGMENTS
            ],
        }
        timing_path = audio_dir / "narration-timing.json"
        timing_path.write_text(
            json.dumps(timing, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"wrote {timing_path.relative_to(episode_dir)}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise
