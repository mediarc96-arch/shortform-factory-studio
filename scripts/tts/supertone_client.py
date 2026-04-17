#!/usr/bin/env python3
"""Thin wrapper around the Supertone TTS REST API.

Endpoint: POST https://supertoneapi.com/v1/text-to-speech/{voice_id}
Auth header: x-sup-api-key

Reads SUPERTONE_API_KEY and SUPERTONE_VOICE_ID_DAEHAN from env. `.env` at the
repo root is loaded by callers (e.g. generate_narration.py) — this module does
not load it so it stays reusable from scripts that already handle env.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import requests


API_BASE = "https://supertoneapi.com/v1"
DEFAULT_MODEL = "sona_speech_1"  # supports ko + voice_settings (pitch, similarity, etc.)


@dataclass
class VoiceSettings:
    speed: float | None = None
    pitch_shift: float | None = None
    pitch_variance: float | None = None
    similarity: float | None = None
    text_guidance: float | None = None
    duration: float | None = None
    subharmonic_amplitude_control: float | None = None

    def to_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        for key, value in self.__dict__.items():
            if value is not None:
                payload[key] = value
        return payload


@dataclass
class SupertoneClient:
    api_key: str
    voice_id: str
    model: str = DEFAULT_MODEL
    language: str = "ko"
    default_style: str | None = None
    timeout_sec: int = 120
    session: requests.Session = field(default_factory=requests.Session)

    @classmethod
    def from_env(cls, *, voice_id: str | None = None) -> "SupertoneClient":
        api_key = os.environ.get("SUPERTONE_API_KEY")
        if not api_key:
            raise RuntimeError("SUPERTONE_API_KEY not set")
        resolved_voice_id = voice_id or os.environ.get("SUPERTONE_VOICE_ID_DAEHAN")
        if not resolved_voice_id:
            raise RuntimeError("SUPERTONE_VOICE_ID_DAEHAN not set (pass voice_id= to override)")
        return cls(api_key=api_key, voice_id=resolved_voice_id)

    def synthesize(
        self,
        text: str,
        *,
        output_path: Path,
        output_format: str = "mp3",
        style: str | None = None,
        voice_settings: VoiceSettings | None = None,
        language: str | None = None,
        model: str | None = None,
    ) -> Path:
        if len(text) > 300:
            raise ValueError(f"Supertone text limit is 300 chars; got {len(text)}")

        body: dict[str, Any] = {
            "text": text,
            "language": language or self.language,
            "model": model or self.model,
            "output_format": output_format,
        }
        chosen_style = style if style is not None else self.default_style
        if chosen_style:
            body["style"] = chosen_style
        if voice_settings is not None:
            vs_payload = voice_settings.to_payload()
            if vs_payload:
                body["voice_settings"] = vs_payload

        headers = {
            "x-sup-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg" if output_format == "mp3" else "audio/wav",
        }

        url = f"{API_BASE}/text-to-speech/{self.voice_id}"
        response = self.session.post(url, headers=headers, json=body, timeout=self.timeout_sec)
        if response.status_code >= 400:
            raise RuntimeError(
                f"Supertone TTS failed {response.status_code}: {response.text[:500]}"
            )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(response.content)
        return output_path


def _cli() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Single-shot Supertone TTS CLI")
    parser.add_argument("--text", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--voice-id", default=None)
    parser.add_argument("--format", default="mp3", choices=["mp3", "wav"])
    parser.add_argument("--speed", type=float, default=None)
    parser.add_argument("--style", default=None)
    parser.add_argument("--env-file", default=".env")
    args = parser.parse_args()

    _load_env(Path(args.env_file))

    client = SupertoneClient.from_env(voice_id=args.voice_id)
    settings = VoiceSettings(speed=args.speed) if args.speed is not None else None
    output_path = client.synthesize(
        args.text,
        output_path=Path(args.output),
        output_format=args.format,
        style=args.style,
        voice_settings=settings,
    )
    print(str(output_path))
    return 0


def _load_env(env_path: Path) -> None:
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


if __name__ == "__main__":
    try:
        raise SystemExit(_cli())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise
