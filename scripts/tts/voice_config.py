#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path


def load_character_voice_config(root: Path, episode_schema: dict) -> dict:
    reusable_assets = episode_schema.get("reusableAssets") or {}
    candidates: list[Path] = []

    voice_config_rel = reusable_assets.get("voiceConfig")
    if isinstance(voice_config_rel, str) and voice_config_rel.strip():
        candidates.append((root / voice_config_rel).resolve())

    character_root = episode_schema.get("characterRoot")
    if isinstance(character_root, str) and character_root.strip():
        candidates.append((root / character_root / "voice.json").resolve())

    for path in candidates:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    return {}


def resolve_tts_voice_env(
    slot: dict,
    *,
    provider: str,
    root: Path,
    episode_schema: dict,
    prefer_explicit: bool = True,
) -> str | None:
    explicit_env = slot.get("ttsVoiceEnv")
    if prefer_explicit and isinstance(explicit_env, str) and explicit_env.strip():
        return explicit_env.strip()

    config = load_character_voice_config(root, episode_schema)
    provider_config = (config.get("tts") or {}).get(str(provider or "").strip().lower()) or {}
    voice_env = provider_config.get("voiceEnv")
    if isinstance(voice_env, str) and voice_env.strip():
        return voice_env.strip()
    return None
