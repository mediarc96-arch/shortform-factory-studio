#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = {
    "teacherImage": str(ROOT / "shared" / "backgrounds" / "images" / "korean" / "teacher.png"),
    "aiAssetGeneration": {
        "enabled": False,
        "model": "gemini-3.1-flash-image-preview",
        "outputDir": "renders/generated-assets",
        "referenceImage": "",
        "apiKeyEnvVar": "GEMINI_IMAGE_API_KEY",
        "imageSize": "2K",
        "stylePrompt": "",
        "negativePrompt": (
            "Do not add any text, letters, Korean writing, English writing, numbers, logos, watermarks, speech bubbles, "
            "interface chrome, stickers, or captions anywhere in the image. Keep the chalkboard visually clean so typography "
            "can be composited later."
        ),
        "promptOverrides": {"title": "", "question": "", "answer": ""},
    },
}

PHASE_FILENAMES = {
    "title": "title-panel.png",
    "question": "question-panel.png",
    "answer": "answer-panel.png",
}
API_URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate MalmoeLab quiz panel images with Gemini image generation.")
    parser.add_argument("--source-packet", required=True)
    parser.add_argument("--render-config", default="")
    parser.add_argument("--episode-dir", default="")
    parser.add_argument("--output-dir", default="")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def merge_config(base: dict, override: dict) -> dict:
    merged = json.loads(json.dumps(base))
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key].update(value)
        else:
            merged[key] = value
    return merged


def resolve_path(base_dir: Path, raw_value: str) -> Path:
    candidate = Path(raw_value).expanduser()
    if not candidate.is_absolute():
        candidate = (base_dir / candidate).resolve()
    return candidate


def choose_api_key(ai_cfg: dict) -> tuple[str, str]:
    preferred_env = str(ai_cfg.get("apiKeyEnvVar") or "GEMINI_IMAGE_API_KEY").strip()
    candidates = [preferred_env, "GEMINI_IMAGE_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY"]
    seen: set[str] = set()
    for name in candidates:
        if not name or name in seen:
            continue
        seen.add(name)
        value = os.getenv(name, "").strip()
        if value:
            return name, value
    raise RuntimeError(
        "Gemini image generation requires an API key. Set GEMINI_IMAGE_API_KEY, GEMINI_API_KEY, or GOOGLE_API_KEY."
    )


def determine_output_dir(args: argparse.Namespace, episode_dir: Path, ai_cfg: dict) -> Path:
    if args.output_dir:
        return resolve_path(episode_dir, args.output_dir)
    configured = str(ai_cfg.get("outputDir") or "renders/generated-assets")
    return resolve_path(episode_dir, configured)


def choose_reference_image(config: dict, episode_dir: Path) -> Path:
    ai_cfg = config.get("aiAssetGeneration") or {}
    preferred = str(ai_cfg.get("referenceImage") or "").strip()
    raw_value = preferred or str(config.get("teacherImage") or "")
    if not raw_value:
        raise RuntimeError("No reference image configured for quiz asset generation.")
    path = resolve_path(episode_dir, raw_value)
    if not path.exists():
        raise RuntimeError(f"Reference image not found: {path}")
    return path


def encode_image_file(path: Path) -> tuple[str, str]:
    mime_type, _ = mimetypes.guess_type(path.name)
    if not mime_type:
        mime_type = "image/png"
    return mime_type, base64.b64encode(path.read_bytes()).decode("ascii")


def build_prompt(packet: dict, ai_cfg: dict, phase: str) -> str:
    source = packet["source"]
    quiz = packet["quiz"]
    override = ((ai_cfg.get("promptOverrides") or {}).get(phase) or "").strip()
    if override:
        return override

    style_prompt = (ai_cfg.get("stylePrompt") or "").strip()
    negative_prompt = (ai_cfg.get("negativePrompt") or "").strip()
    base_prompt = (
        "Create a polished vertical classroom illustration for a 15-second Korean learning short. "
        "Keep the same teacher identity, facial features, hairstyle, clothing palette, and classroom vibe as the reference image. "
        "The teacher should stand beside a large dark green chalkboard with clean empty space so text can be composited later. "
        "Use clean lighting, crisp edges, and an educational but premium social-video aesthetic. "
        "Keep the composition centered for a 1080x1920 short."
    )
    phase_prompt = {
        "title": (
            "The teacher should look welcoming and confident, with a calm opening pose that introduces the lesson. "
            "Keep the chalkboard empty and readable."
        ),
        "question": (
            f"The teacher should actively point toward the chalkboard as if asking a quiz question about the Korean word '{source['wordText']}' "
            f"and the sentence '{quiz['blankedSentence']}'. Keep the board empty enough for the missing-word sentence overlay."
        ),
        "answer": (
            f"The teacher should look pleased and slightly celebratory, as if revealing the correct answer '{source['wordText']}' "
            "to the class. Keep the chalkboard clean for the full sentence overlay and final CTA."
        ),
    }[phase]

    prompt_parts = [base_prompt, phase_prompt]
    if style_prompt:
        prompt_parts.append(style_prompt)
    if negative_prompt:
        prompt_parts.append(negative_prompt)
    return "\n\n".join(prompt_parts)


def extract_image_bytes(payload: dict) -> bytes:
    for candidate in payload.get("candidates", []):
        content = candidate.get("content") or {}
        for part in content.get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data") or {}
            data = inline.get("data")
            if data:
                return base64.b64decode(data)
    raise RuntimeError("Gemini image response did not include inline image data.")


def call_gemini_image_api(
    *,
    api_key: str,
    model: str,
    prompt: str,
    reference_image: Path,
    image_size: str,
) -> dict:
    mime_type, encoded_image = encode_image_file(reference_image)
    body: dict[str, Any] = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": mime_type, "data": encoded_image}},
                ],
            }
        ],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
        },
    }
    if image_size:
        body["generationConfig"]["imageConfig"] = {"imageSize": image_size}

    request = Request(
        API_URL_TEMPLATE.format(model=model),
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Gemini image generation failed with {exc.code}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"Gemini image generation request failed: {exc}") from exc


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main() -> int:
    args = parse_args()
    source_path = Path(args.source_packet).resolve()
    source_packet = load_json(source_path)
    episode_dir = Path(args.episode_dir).resolve() if args.episode_dir else source_path.parent
    config_path = Path(args.render_config).resolve() if args.render_config else episode_dir / "render-config.json"
    config = merge_config(DEFAULT_CONFIG, load_json(config_path) if config_path.exists() else {})
    ai_cfg = config.get("aiAssetGeneration") or {}
    if not bool(ai_cfg.get("enabled")):
        raise RuntimeError("aiAssetGeneration.enabled is false. Enable it in render-config.json before generating Gemini assets.")

    api_key_name, api_key = choose_api_key(ai_cfg)
    output_dir = determine_output_dir(args, episode_dir, ai_cfg)
    output_dir.mkdir(parents=True, exist_ok=True)
    reference_image = choose_reference_image(config, episode_dir)
    model = str(ai_cfg.get("model") or "gemini-3.1-flash-image-preview").strip()
    image_size = str(ai_cfg.get("imageSize") or "2K").strip()

    manifest: dict[str, Any] = {
        "generatedAt": utc_now_iso(),
        "model": model,
        "episodeSlug": source_packet["episodeSlug"],
        "referenceImage": str(reference_image),
        "apiKeySource": api_key_name,
        "imageSize": image_size,
        "assets": {},
    }

    for phase, filename in PHASE_FILENAMES.items():
        target = output_dir / filename
        prompt = build_prompt(source_packet, ai_cfg, phase)
        if target.exists() and not args.force:
            manifest["assets"][phase] = {
                "file": str(target),
                "status": "reused",
                "prompt": prompt,
            }
            continue

        payload = call_gemini_image_api(
            api_key=api_key,
            model=model,
            prompt=prompt,
            reference_image=reference_image,
            image_size=image_size,
        )
        target.write_bytes(extract_image_bytes(payload))
        manifest["assets"][phase] = {
            "file": str(target),
            "status": "generated",
            "prompt": prompt,
        }

    manifest_path = output_dir / "asset-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"assetManifest": str(manifest_path), "outputDir": str(output_dir)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
