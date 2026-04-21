#!/usr/bin/env python3

from __future__ import annotations

import os
import shutil
from pathlib import Path

try:
    import imageio_ffmpeg
except Exception:  # pragma: no cover
    imageio_ffmpeg = None


def resolve_ffmpeg_binary() -> str:
    candidates = [
        Path(os.environ.get("SHORTFORM_FFMPEG", "")).expanduser(),
        Path("/tmp/paperclip-ffmpeg/node_modules/ffmpeg-static/ffmpeg"),
        Path("/tmp/shortform-factory-bin/ffmpeg"),
    ]
    for candidate in candidates:
        if str(candidate).strip() and candidate.is_file():
            return str(candidate)
    if imageio_ffmpeg is not None:
        try:
            return imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            pass
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg
    raise RuntimeError("No usable ffmpeg binary found. Set SHORTFORM_FFMPEG.")
