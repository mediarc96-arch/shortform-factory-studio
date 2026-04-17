#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FORMATS_ROOT = REPO_ROOT / "formats"


def profile_path(profile_id: str) -> Path:
    return FORMATS_ROOT / profile_id / "profile.json"


def load_profile(profile_id: str) -> dict:
    path = profile_path(profile_id)
    if not path.exists():
        raise FileNotFoundError(f"Format profile not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_profile_for_episode_schema(schema: dict) -> tuple[str, Path, dict]:
    profile_id = str(schema.get("formatProfile") or "").strip()
    if not profile_id:
        raise ValueError("episode schema is missing formatProfile")
    path = profile_path(profile_id)
    profile = load_profile(profile_id)
    return profile_id, path, profile
