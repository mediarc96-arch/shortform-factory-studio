#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
RUN_IMAGE_SCRIPT = SCRIPT_DIR / "run_xai_grok_image.py"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def summarize_style_lock(style_lock_path: Path) -> str:
    if not style_lock_path.exists():
        return ""
    lines: list[str] = []
    for raw_line in style_lock_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        lower = line.lower()
        if "negative prompt" in lower or "reusable prompt block" in lower:
            continue
        lines.append(line.strip("-* ").strip())
    return " ".join(line for line in lines if line)[:900]


def resolve_repo_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (REPO_ROOT / path).resolve()


def infer_reference_episode_dir(source_packet: dict) -> Path:
    candidates = [
        str((source_packet.get("characterAssetStatus") or {}).get("provisionalStyleBasis") or "").strip(),
        str((source_packet.get("styleLockInputs") or {}).get("characterPromptSource") or "").strip(),
    ]
    for candidate in candidates:
        if not candidate:
            continue
        style_lock_path = resolve_repo_path(candidate)
        if style_lock_path.exists():
            return style_lock_path.parents[1]
    raise FileNotFoundError("Could not infer the reference episode directory from source-packet.json")


def cast_lock_text(cast_cardinality: dict) -> str:
    present: list[str] = []
    absent: list[str] = []
    labels = {
        "jjiroo": "Jjiroo",
        "jjonga": "Jjonga",
        "mother": "mother",
        "ducks": "ducks",
    }
    for key in ("jjiroo", "jjonga", "mother", "ducks"):
        count = int(cast_cardinality.get(key, 0) or 0)
        label = labels[key]
        if count > 0:
            noun = label if count == 1 else label
            present.append(f"exactly {count} {noun}")
        else:
            absent.append(label)
    parts: list[str] = []
    if present:
        parts.append("Cast lock: show " + ", ".join(present) + ".")
    if absent:
        parts.append("Do not show " + ", ".join(absent) + ".")
    return " ".join(parts)


def build_prompt(*, cut: dict, style_summary: str, forbidden: list[str]) -> str:
    parts = [
        "Use the input image as the approved original-style storyboard cut for this same beat.",
        "Preserve the exact same pet identity, harness colors, readable Tancheon geography, and warm observational webtoon drawing style from the input image.",
        "Do not beautify, repaint, photorealize, or reinterpret the art style.",
        "Create a clean vertical 9:16 storyboard/webtoon cut.",
        cast_lock_text(cut.get("castCardinality") or {}),
    ]

    for field_name, prefix in (
        ("beat", "Story beat"),
        ("cameraConcept", "Camera concept"),
        ("emotion", "Emotion"),
        ("continuityGoal", "Continuity goal"),
        ("promptCore", "Core action"),
    ):
        value = str(cut.get(field_name) or "").strip()
        if value:
            parts.append(f"{prefix}: {value}.")

    if style_summary:
        parts.append(f"Style lock: {style_summary}")

    if forbidden:
        parts.append("Forbidden: " + ", ".join(forbidden) + ".")

    parts.append("Keep the tone comic, safe, and readable, never violent or panic-driven.")
    parts.append("No text of any kind anywhere in frame, including captions, subtitles, corner labels, numbers, logos, or watermarks.")
    parts.append("No duplicate pets, extra animals, wings, extra limbs, merged faces, or wrong fur colors.")
    return " ".join(part for part in parts if part)


def build_job(*, episode_dir: Path, reference_episode_dir: Path, episode_slug: str, cut: dict, style_summary: str, forbidden: list[str]) -> tuple[Path, dict]:
    cut_id = str(cut["id"])
    job_dir = episode_dir / "grok-jobs"
    reference_image = reference_episode_dir / "storyboard" / "webtoon-cuts" / f"{cut_id}.png"
    if not reference_image.exists():
        raise FileNotFoundError(f"Missing reference cut for {cut_id}: {reference_image}")

    output_path = episode_dir / str(cut["outputPath"])
    manifest_path = output_path.with_suffix(".manifest.json")
    job_path = job_dir / f"{cut_id}.json"

    payload = {
        "_schema": f"xAI image edit job · {episode_slug} storyboard {cut_id}",
        "provider": "xai_grok",
        "taskType": "image_edit",
        "request": {
            "model": "grok-imagine-image",
            "prompt": build_prompt(cut=cut, style_summary=style_summary, forbidden=forbidden),
            "image": {
                "url": os.path.relpath(reference_image, job_dir),
            },
            "n": 1,
        },
        "runner": {
            "outputFile": os.path.relpath(output_path, job_dir),
            "manifestFile": os.path.relpath(manifest_path, job_dir),
        },
    }
    return job_path, payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare and run pet-contents storyboard cut bundle generation with xAI Grok image.")
    parser.add_argument("--episode-dir", required=True)
    parser.add_argument("--env-file", default=".env")
    parser.add_argument("--python-bin", default=sys.executable)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--cut-ids", nargs="*", help="Optional subset of cut ids to render, for example cut-01 cut-02")
    return parser.parse_args()


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def should_render(output_path: Path, *, force: bool) -> bool:
    if force:
        return True
    return not output_path.exists() or output_path.stat().st_size == 0


def main() -> int:
    args = parse_args()
    episode_dir = Path(args.episode_dir).resolve()
    env_file = Path(args.env_file).resolve()
    python_bin = args.python_bin

    source_packet = load_json(episode_dir / "source-packet.json")
    storyboard_plan = load_json(episode_dir / "storyboard" / "storyboard-plan.json")
    style_lock_path = episode_dir / "storyboard" / "style-lock.md"
    style_summary = summarize_style_lock(style_lock_path)
    reference_episode_dir = infer_reference_episode_dir(source_packet)
    episode_slug = str((storyboard_plan.get("episode") or {}).get("slug") or episode_dir.name)
    forbidden = [str(item).strip() for item in list((storyboard_plan.get("globalPromptRules") or {}).get("forbid") or []) if str(item).strip()]

    selected_cut_ids = {item.strip() for item in list(args.cut_ids or []) if item.strip()}
    cuts = list(storyboard_plan.get("cuts") or [])
    if selected_cut_ids:
        cuts = [cut for cut in cuts if str(cut.get("id") or "") in selected_cut_ids]
    if not cuts:
        raise ValueError("No cuts selected for storyboard generation")

    for cut in cuts:
        job_path, payload = build_job(
            episode_dir=episode_dir,
            reference_episode_dir=reference_episode_dir,
            episode_slug=episode_slug,
            cut=cut,
            style_summary=style_summary,
            forbidden=forbidden,
        )
        write_json(job_path, payload)

        output_path = episode_dir / str(cut["outputPath"])
        if not should_render(output_path, force=args.force):
            print(f"skip  {output_path}")
            continue

        run([python_bin, str(RUN_IMAGE_SCRIPT), "--job", str(job_path), "--env-file", str(env_file)])
        print(f"done  {output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
