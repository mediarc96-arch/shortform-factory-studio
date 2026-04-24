#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_NEGATIVE_PROMPT = (
    "duplicate pet, second version of same character, extra animal, extra limbs, wings, "
    "merged face, wrong fur color, wrong ear shape, changed eye style, photorealism, "
    "realistic fur, glossy 3D render, unrelated manga style, unrelated anime style, "
    "text, subtitle, watermark, logo, cluttered background"
)


def load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def read_text_if_exists(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def rel(path: Path, base: Path) -> str:
    return os.path.relpath(path.resolve(), base.resolve())


def character_refs(character_slug: str) -> list[Path]:
    folder = REPO_ROOT / "characters" / character_slug
    preferred = [
        folder / f"{character_slug}.png",
        folder / f"{character_slug}_stand.png",
        folder / f"{character_slug}_laydown.png",
    ]
    refs = [path for path in preferred if path.exists()]
    if not refs:
        refs = sorted(folder.glob("*.png"))[:4]
    example = REPO_ROOT / "docs" / "example" / "찌루_쫑아_웹툰_파일럿.png"
    if example.exists():
        refs.append(example)
    return refs


def build_default_cuts(protagonist_name: str, episode_text: str, cut_count: int) -> list[dict[str, str]]:
    core = [
        {
            "title": "rainy reluctance",
            "beat": f"{protagonist_name} hesitates at the doorway on a rainy day, wearing a simple raincoat and looking suspicious about going outside.",
            "emotion": "watchful, reluctant, slightly annoyed"
        },
        {
            "title": "first step outside",
            "beat": f"{protagonist_name} carefully steps onto the wet sidewalk, keeping the same tense posture and sharp little dot eyes.",
            "emotion": "cautious curiosity"
        },
        {
            "title": "puddle discovery",
            "beat": f"{protagonist_name} notices a small puddle and leans forward with a clever, alert expression, still exactly the same brown dog character.",
            "emotion": "focused discovery"
        },
        {
            "title": "splash payoff",
            "beat": f"{protagonist_name} happily splashes in the small puddle with wet paws, proud and playful while preserving the canonical hand-drawn style.",
            "emotion": "playful payoff"
        },
        {
            "title": "after-rain pride",
            "beat": f"{protagonist_name} stands beside the puddle with a satisfied look, raincoat slightly damp, still one stable version of the same character.",
            "emotion": "small proud victory"
        }
    ]
    selected = core[: max(1, min(cut_count, len(core)))]
    if cut_count > len(core):
        for index in range(len(core) + 1, cut_count + 1):
            selected.append(
                {
                    "title": f"episode beat {index}",
                    "beat": f"{protagonist_name} continues the episode action from this narrative: {episode_text}",
                    "emotion": "consistent character acting"
                }
            )
    return selected


def build_style_lock(
    protagonist_slug: str,
    protagonist_name: str,
    bible_text: str,
    prompt_text: str,
    refs: list[Path],
    episode_dir: Path,
) -> str:
    ref_lines = "\n".join(f"- `{rel(path, episode_dir)}`" for path in refs)
    return f"""# Pet Toon Style Lock — {protagonist_name}

## Reference Mode

`reference-only`

## Canonical Character

- Name: {protagonist_name} (`{protagonist_slug}`)
- Reference folder: `characters/{protagonist_slug}`
- Reference images:
{ref_lines or "- no image refs found; block before generation"}

## Character Bible

{bible_text.strip() or "_No bible file found._"}

## Prompt Notes

{prompt_text.strip() or "_No prompt file found._"}

## Hard Identity Rules

- Preserve the approved character drawing style almost exactly.
- Do not reinterpret, polish, photorealize, 3D-render, or convert the character into a different comic/anime style.
- Keep brown fur, small black dot eyes, small nose, asymmetric rounded ear silhouette, rough black outline, soft pastel fill, and tense alert posture stable.
- Default cast cardinality is exactly one `{protagonist_slug}` per cut.
- Generated images must contain no readable text, subtitles, logos, or watermarks.

## New Character Rule

If an undefined person or character appears:

1. assign a stable slug,
2. record its first appearance in `storyboard/character-continuity.json`,
3. save the first generated image path as that character's lock image,
4. reuse that lock description and image for every later cut.

## Negative Prompt Core

{DEFAULT_NEGATIVE_PROMPT}
"""


def build_cut_prompt(
    protagonist_slug: str,
    protagonist_name: str,
    episode_text: str,
    beat: dict[str, str],
    cut_index: int,
    cut_count: int,
) -> str:
    return f"""Create one clean vertical webtoon panel, no text.

Episode premise: {episode_text}
Cut {cut_index:02d}/{cut_count:02d}: {beat["beat"]}
Emotion: {beat["emotion"]}

Character lock:
- Draw exactly one {protagonist_name} (`{protagonist_slug}`).
- Preserve the same canonical brown small dog from the reference images.
- Preserve the rough black outline, simple 2D hand-drawn pastel style, small black dot eyes, small nose, asymmetric rounded/floppy ears, and alert smart expression.
- Do not redesign the character, do not switch art style, do not make a realistic dog, and do not create a second copy of the dog.

Composition:
- 2:3 vertical webtoon panel, soft everyday background, simple readable staging.
- Keep the panel text-free: no captions, no speech bubbles, no signs, no logos, no watermark.
"""


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def stack_webtoon(cut_paths: list[Path], output_path: Path) -> bool:
    existing = [path for path in cut_paths if path.exists()]
    if len(existing) != len(cut_paths):
        return False
    try:
        from PIL import Image
    except ImportError:
        return False

    images = [Image.open(path).convert("RGB") for path in existing]
    width = min(image.width for image in images)
    resized = []
    for image in images:
        if image.width != width:
            height = int(image.height * (width / image.width))
            resized.append(image.resize((width, height), Image.Resampling.LANCZOS))
        else:
            resized.append(image)

    gutter = 24
    height = sum(image.height for image in resized) + gutter * (len(resized) - 1)
    strip = Image.new("RGB", (width, height), (255, 255, 255))
    y = 0
    for image in resized:
        strip.paste(image, (0, y))
        y += image.height + gutter
    output_path.parent.mkdir(parents=True, exist_ok=True)
    strip.save(output_path)
    return True


def run_openai_jobs(job_paths: list[Path], env_file: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    runner = REPO_ROOT / "scripts" / "pilot" / "run_openai_gpt_image.py"
    for job_path in job_paths:
        proc = subprocess.run(
            [sys.executable, str(runner), "--job", str(job_path), "--env-file", str(env_file)],
            cwd=str(REPO_ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        results.append(
            {
                "jobPath": rel(job_path, REPO_ROOT),
                "returncode": proc.returncode,
                "stdout": proc.stdout.strip(),
                "stderr": proc.stderr.strip()
            }
        )
        if proc.returncode != 0:
            break
    return results


def is_uuid_like(value: str | None) -> bool:
    if not value:
        return False
    import re
    return bool(re.match(r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$", value, re.I))


def paperclip_image_service_configured() -> bool:
    required = [
        "PAPERCLIP_API_URL",
        "PAPERCLIP_API_KEY",
        "PAPERCLIP_COMPANY_ID",
        "PAPERCLIP_PROJECT_WORKSPACE_ID",
    ]
    return all(os.environ.get(key, "").strip() for key in required)


def _job_image_paths_relative_to_repo(job_path: Path, request_payload: dict[str, Any]) -> list[str]:
    image_value = request_payload.get("image") or request_payload.get("reference_images") or []
    if isinstance(image_value, str):
        image_values = [image_value]
    else:
        image_values = list(image_value) if isinstance(image_value, list) else []
    result = []
    for value in image_values:
        image_path = Path(str(value))
        if not image_path.is_absolute():
            image_path = job_path.parent / image_path
        result.append(rel(image_path, REPO_ROOT))
    return result


def run_paperclip_image_jobs(job_paths: list[Path], episode_dir: Path) -> list[dict[str, Any]]:
    api_url = os.environ["PAPERCLIP_API_URL"].rstrip("/")
    api_key = os.environ["PAPERCLIP_API_KEY"]
    company_id = os.environ["PAPERCLIP_COMPANY_ID"]
    project_workspace_id = os.environ["PAPERCLIP_PROJECT_WORKSPACE_ID"]
    issue_id = os.environ.get("PAPERCLIP_TASK_ID")
    run_id = os.environ.get("PAPERCLIP_RUN_ID")
    endpoint = f"{api_url}/api/companies/{company_id}/image-generations"

    results: list[dict[str, Any]] = []
    for job_path in job_paths:
        job = json.loads(job_path.read_text(encoding="utf-8"))
        request_payload = job["request"]
        runner = job["runner"]
        output_file = (job_path.parent / runner["outputFile"]).resolve()
        manifest_file = (job_path.parent / runner["manifestFile"]).resolve()
        body = {
            "projectWorkspaceId": project_workspace_id,
            "taskType": job.get("taskType", "image_edit"),
            "model": request_payload.get("model", "gpt-image-2"),
            "prompt": request_payload["prompt"],
            "referenceImagePaths": _job_image_paths_relative_to_repo(job_path, request_payload),
            "outputPath": rel(output_file, REPO_ROOT),
            "manifestPath": rel(manifest_file, REPO_ROOT),
            "size": request_payload.get("size", "1024x1536"),
            "quality": request_payload.get("quality", "high"),
            "outputFormat": request_payload.get("output_format", "png"),
            "title": job_path.stem,
            "metadata": {
                "episodeDir": rel(episode_dir, REPO_ROOT),
                "jobPath": rel(job_path, REPO_ROOT),
                "source": "pet-toon-generator",
            },
        }
        if is_uuid_like(issue_id):
            body["issueId"] = issue_id

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        if is_uuid_like(run_id):
            headers["X-Paperclip-Run-Id"] = str(run_id)
        req = Request(
            endpoint,
            data=json.dumps(body).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urlopen(req, timeout=300) as response:
                payload = json.loads(response.read().decode("utf-8"))
            results.append(
                {
                    "jobPath": rel(job_path, REPO_ROOT),
                    "returncode": 0,
                    "provider": "paperclip_image_service",
                    "stdout": json.dumps(payload, ensure_ascii=False),
                    "stderr": "",
                }
            )
        except HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            results.append(
                {
                    "jobPath": rel(job_path, REPO_ROOT),
                    "returncode": 1,
                    "provider": "paperclip_image_service",
                    "stdout": "",
                    "stderr": f"HTTP {exc.code}: {error_body}",
                }
            )
            break
        except URLError as exc:
            results.append(
                {
                    "jobPath": rel(job_path, REPO_ROOT),
                    "returncode": 1,
                    "provider": "paperclip_image_service",
                    "stdout": "",
                    "stderr": str(exc),
                }
            )
            break
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Pet Toon image-only episode packet and optionally run GPT Image 2 jobs.")
    parser.add_argument("--episode-dir", default="episodes/pet-toon-jjonga-rainy-walk-001")
    parser.add_argument("--protagonist-slug", default="jjonga")
    parser.add_argument("--protagonist-name", default="쫑아")
    parser.add_argument("--episode-title", default="비 오는 날 산책")
    parser.add_argument(
        "--episode-text",
        default="비 오는 날 산책을 싫어하던 쫑아가 우비를 입고 나가서 작은 물웅덩이를 발견하고 신나게 노는 이야기.",
    )
    parser.add_argument("--cut-count", type=int, default=4)
    parser.add_argument("--env-file", default=".env")
    parser.add_argument("--generate", action="store_true", help="Run OpenAI image jobs after writing the episode packet")
    args = parser.parse_args()

    episode_dir = (REPO_ROOT / args.episode_dir).resolve()
    storyboard_dir = episode_dir / "storyboard"
    jobs_dir = episode_dir / "openai-image-jobs"
    cuts_dir = episode_dir / "images" / "cuts"
    strip_path = episode_dir / "images" / "episode-strip.png"
    env_file = (REPO_ROOT / args.env_file).resolve()

    load_env_file(env_file)

    character_dir = REPO_ROOT / "characters" / args.protagonist_slug
    bible_text = read_text_if_exists(character_dir / "bible.md")
    prompt_text = read_text_if_exists(character_dir / "prompts.md")
    refs = character_refs(args.protagonist_slug)

    episode_dir.mkdir(parents=True, exist_ok=True)
    storyboard_dir.mkdir(parents=True, exist_ok=True)
    jobs_dir.mkdir(parents=True, exist_ok=True)
    cuts_dir.mkdir(parents=True, exist_ok=True)

    source_packet = {
        "workType": "new_pet_toon_episode",
        "channelLane": "pet",
        "projectLane": "pet-toon",
        "outputPolicy": "image-only",
        "series": "pet-toon",
        "formatProfile": "pet-toon-image-only-v1",
        "episode": {
            "slug": episode_dir.name,
            "title": args.episode_title,
            "rawNarrative": args.episode_text,
            "cutCount": args.cut_count
        },
        "protagonist": {
            "name": args.protagonist_name,
            "slug": args.protagonist_slug,
            "referenceFolder": f"characters/{args.protagonist_slug}",
            "referenceMode": "reference-only",
            "referenceImages": [rel(path, REPO_ROOT) for path in refs]
        },
        "outputs": {
            "cutImages": "images/cuts/*.png",
            "webtoonStrip": "images/episode-strip.png",
            "manifest": "pet-toon-manifest.json"
        },
        "hardRules": [
            "Preserve the canonical character drawing style almost exactly.",
            "Do not create video outputs.",
            "Do not add text, subtitles, logos, or watermarks inside generated images.",
            "Lock any undefined character's first generated design for later reuse."
        ]
    }
    write_json(episode_dir / "source-packet.json", source_packet)

    packet_md = f"""# {args.episode_title}

## Work Type

new_pet_toon_episode

## Output Policy

image-only

## Protagonist

{args.protagonist_name} (`{args.protagonist_slug}`)

## Episode

{args.episode_text}

## Required Outputs

- `images/cuts/cut-XX.png`
- `images/episode-strip.png`
- `pet-toon-manifest.json`
"""
    (episode_dir / "packet.md").write_text(packet_md, encoding="utf-8")

    style_lock = build_style_lock(args.protagonist_slug, args.protagonist_name, bible_text, prompt_text, refs, episode_dir)
    (storyboard_dir / "style-lock.md").write_text(style_lock, encoding="utf-8")

    continuity = {
        "policy": "first appearance of any undefined person or character becomes canonical for later cuts",
        "characters": {
            args.protagonist_slug: {
                "name": args.protagonist_name,
                "source": f"characters/{args.protagonist_slug}",
                "referenceMode": "reference-only",
                "canonicalReferenceImages": [rel(path, REPO_ROOT) for path in refs],
                "lockedFromCut": None,
                "status": "canonical"
            }
        },
        "newCharacterInstructions": [
            "Assign a stable slug before generation.",
            "Record first generated design and output image path.",
            "Reuse the same locked description and image in later cuts."
        ]
    }
    write_json(storyboard_dir / "character-continuity.json", continuity)

    cuts = []
    job_paths: list[Path] = []
    beats = build_default_cuts(args.protagonist_name, args.episode_text, args.cut_count)
    ref_paths_for_job = [rel(path, jobs_dir) for path in refs]
    for index, beat in enumerate(beats, start=1):
        cut_id = f"cut-{index:02d}"
        output_file = Path("..") / "images" / "cuts" / f"{cut_id}.png"
        manifest_file = Path("..") / "images" / "cuts" / f"{cut_id}.manifest.json"
        prompt = build_cut_prompt(args.protagonist_slug, args.protagonist_name, args.episode_text, beat, index, len(beats))
        cuts.append(
            {
                "id": cut_id,
                "title": beat["title"],
                "cast": [
                    {
                        "slug": args.protagonist_slug,
                        "name": args.protagonist_name,
                        "count": 1
                    }
                ],
                "prompt": prompt,
                "negativePrompt": DEFAULT_NEGATIVE_PROMPT,
                "referenceImages": [rel(path, REPO_ROOT) for path in refs],
                "outputFile": f"images/cuts/{cut_id}.png"
            }
        )
        job = {
            "provider": "openai",
            "taskType": "image_edit",
            "_endpoint": "POST https://api.openai.com/v1/images/edits",
            "request": {
                "model": os.environ.get("OPENAI_IMAGE_MODEL") or "gpt-image-2",
                "prompt": f"{prompt}\n\nNegative prompt: {DEFAULT_NEGATIVE_PROMPT}",
                "image": ref_paths_for_job,
                "size": "1024x1536",
                "quality": "high",
                "output_format": "png"
            },
            "runner": {
                "outputFile": str(output_file),
                "manifestFile": str(manifest_file)
            }
        }
        job_path = jobs_dir / f"{cut_id}.json"
        write_json(job_path, job)
        job_paths.append(job_path)

    storyboard_plan = {
        "episodeSlug": episode_dir.name,
        "title": args.episode_title,
        "formatProfile": "pet-toon-image-only-v1",
        "outputPolicy": "image-only",
        "provider": "openai",
        "model": os.environ.get("OPENAI_IMAGE_MODEL") or "gpt-image-2",
        "size": "1024x1536",
        "quality": "high",
        "outputFormat": "png",
        "referenceMode": "reference-only",
        "cuts": cuts
    }
    write_json(storyboard_dir / "storyboard-plan.json", storyboard_plan)

    status = "planned"
    blocker = None
    run_results: list[dict[str, Any]] = []
    if args.generate:
        if not refs:
            status = "blocked_missing_character_refs"
            blocker = f"No reference images found for characters/{args.protagonist_slug}."
        elif paperclip_image_service_configured():
            run_results = run_paperclip_image_jobs(job_paths, episode_dir)
            if run_results and run_results[-1]["returncode"] != 0:
                status = "blocked_image_generation_failed"
                blocker = run_results[-1]["stderr"] or run_results[-1]["stdout"]
            else:
                status = "succeeded"
        elif os.environ.get("OPENAI_API_KEY"):
            run_results = run_openai_jobs(job_paths, env_file)
            if run_results and run_results[-1]["returncode"] != 0:
                status = "blocked_image_generation_failed"
                blocker = run_results[-1]["stderr"] or run_results[-1]["stdout"]
            else:
                status = "succeeded"
        else:
            status = "blocked_missing_image_generation_service"
            blocker = (
                "Paperclip central image generation env is not configured "
                "(PAPERCLIP_API_URL, PAPERCLIP_API_KEY, PAPERCLIP_COMPANY_ID, PAPERCLIP_PROJECT_WORKSPACE_ID), "
                "and OPENAI_API_KEY direct fallback is not configured."
            )

    cut_paths = [episode_dir / cut["outputFile"] for cut in cuts]
    strip_created = False
    if status == "succeeded":
        strip_created = stack_webtoon(cut_paths, strip_path)
        if not strip_created:
            status = "blocked_strip_assembly_failed"
            blocker = "Cut images exist but Pillow is unavailable or strip assembly failed."

    manifest = {
        "status": status,
        "blocker": blocker,
        "episodeDir": rel(episode_dir, REPO_ROOT),
        "sourcePacket": "source-packet.json",
        "styleLock": "storyboard/style-lock.md",
        "storyboardPlan": "storyboard/storyboard-plan.json",
        "characterContinuity": "storyboard/character-continuity.json",
        "imageJobs": [rel(path, episode_dir) for path in job_paths],
        "cutImages": [cut["outputFile"] for cut in cuts],
        "webtoonStrip": "images/episode-strip.png" if strip_created else None,
        "runResults": run_results,
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    write_json(episode_dir / "pet-toon-manifest.json", manifest)

    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
