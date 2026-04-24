#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_NEGATIVE_PROMPT = (
    "duplicate pet, second version of same character, extra animal, extra limbs, wings, "
    "merged face, wrong fur color, wrong ear shape, changed eye style, photorealism, "
    "realistic fur, glossy 3D render, unrelated manga style, unrelated anime style, "
    "text, subtitle, speech bubble, watermark, logo, cluttered background"
)


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
            "emotion": "watchful, reluctant, slightly annoyed",
        },
        {
            "title": "first step outside",
            "beat": f"{protagonist_name} carefully steps onto the wet sidewalk, keeping the same tense posture and sharp little dot eyes.",
            "emotion": "cautious curiosity",
        },
        {
            "title": "puddle discovery",
            "beat": f"{protagonist_name} notices a small puddle and leans forward with a clever, alert expression, still exactly the same brown dog character.",
            "emotion": "focused discovery",
        },
        {
            "title": "splash payoff",
            "beat": f"{protagonist_name} happily splashes in the small puddle with wet paws, proud and playful while preserving the canonical hand-drawn style.",
            "emotion": "playful payoff",
        },
        {
            "title": "after-rain pride",
            "beat": f"{protagonist_name} stands beside the puddle with a satisfied look, raincoat slightly damp, still one stable version of the same character.",
            "emotion": "small proud victory",
        },
    ]
    selected = core[: max(1, min(cut_count, len(core)))]
    if cut_count > len(core):
        for index in range(len(core) + 1, cut_count + 1):
            selected.append(
                {
                    "title": f"episode beat {index}",
                    "beat": f"{protagonist_name} continues the episode action from this narrative: {episode_text}",
                    "emotion": "consistent character acting",
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

`manual-chatgpt-reference-upload`

## Canonical Character

- Name: {protagonist_name} (`{protagonist_slug}`)
- Reference folder: `characters/{protagonist_slug}`
- Reference images for the human operator to upload to ChatGPT:
{ref_lines or "- no image refs found; the issue must provide a reference image or character description"}

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
2. describe its first appearance in the prompt,
3. after ChatGPT creates that first image, reuse the same description and image as the reference for every later cut.

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
- Preserve the same canonical brown small dog from the uploaded reference images.
- Preserve the rough black outline, simple 2D hand-drawn pastel style, small black dot eyes, small nose, asymmetric rounded/floppy ears, and alert smart expression.
- Do not redesign the character, do not switch art style, do not make a realistic dog, and do not create a second copy of the dog.

Composition:
- 2:3 vertical webtoon panel, soft everyday background, simple readable staging.
- Keep the panel text-free: no captions, no speech bubbles, no signs, no logos, no watermark.

Avoid:
{DEFAULT_NEGATIVE_PROMPT}
"""


def build_chatgpt_prompt(
    protagonist_slug: str,
    protagonist_name: str,
    episode_title: str,
    episode_text: str,
    refs: list[Path],
    cuts: list[dict[str, Any]],
) -> str:
    ref_lines = "\n".join(f"- `{rel(path, REPO_ROOT)}`" for path in refs)
    cut_summary = "\n".join(
        f"{cut['id']}: {cut['title']} - {cut['beat']} Emotion: {cut['emotion']}"
        for cut in cuts
    )
    individual_prompts = "\n\n".join(
        f"### {cut['id']} 개별 이미지 프롬프트\n\n```text\n{cut['prompt'].strip()}\n```"
        for cut in cuts
    )
    return f"""# ChatGPT Image Prompt — {episode_title}

이 파일은 사람이 ChatGPT에 직접 붙여넣어 Pet Toon 이미지를 받기 위한 handoff prompt다.
이 이슈의 완료 산출물은 자동 생성된 이미지가 아니라 이 프롬프트 파일이다.

## 사용 방법

1. ChatGPT 새 대화를 연다.
2. 아래 reference images를 먼저 업로드한다.
3. `전체 웹툰 strip 생성 프롬프트`를 붙여넣어 {len(cuts)}컷 세로 웹툰 이미지를 요청한다.
4. 이어서 `컷별 개별 이미지 프롬프트`를 하나씩 붙여넣어 cut별 이미지를 따로 요청한다.
5. 받은 파일은 사람이 아래 경로명으로 저장한다.

## Reference Images To Upload

{ref_lines or "- reference image missing; upload the best available canonical image for the protagonist before prompting"}

## 저장 파일명

- 전체 웹툰 strip: `images/episode-strip.png`
{chr(10).join(f"- {cut['id']} 개별 이미지: `images/cuts/{cut['id']}.png`" for cut in cuts)}

## 전체 웹툰 strip 생성 프롬프트

```text
You are creating a Pet Toon webtoon image.

Use the uploaded reference images as the strict visual source for the recurring character.
The most important requirement is character consistency: preserve the exact same drawing style, face structure, fur color, eye style, nose, ear silhouette, outline roughness, pastel fill texture, and personality posture from the uploaded references.

Episode title: {episode_title}
Protagonist: {protagonist_name} (`{protagonist_slug}`)
Episode premise: {episode_text}

Create one vertical webtoon strip made of {len(cuts)} stacked panels.
Each panel should be a clean 2D hand-drawn webtoon panel with the same character design in every panel.
Do not add captions, subtitles, speech bubbles, logos, watermarks, readable signs, or decorative text.

Panel plan:
{cut_summary}

Character lock:
- Draw exactly one {protagonist_name} in each panel unless the panel plan explicitly says otherwise.
- Do not create a second version of the same dog.
- Do not change the dog into a realistic animal, a 3D render, a different manga/anime style, or a polished unrelated mascot.
- Keep the character close to the uploaded artist-like reference style.

Output:
- One vertical webtoon strip.
- No text inside the image.
- Clear panel separation.
- Soft everyday pet-comedy tone.

Avoid:
{DEFAULT_NEGATIVE_PROMPT}
```

## 컷별 개별 이미지 프롬프트

아래 프롬프트를 하나씩 붙여넣어 각 컷 이미지를 따로 생성한다. ChatGPT가 이전 이미지를 참조할 수 있으면 직전 결과와 업로드한 reference images를 계속 참조하라고 말한다.

{individual_prompts}
"""


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Pet Toon manual ChatGPT prompt handoff packet.")
    parser.add_argument("--episode-dir", default="episodes/pet-toon-jjonga-rainy-walk-001")
    parser.add_argument("--protagonist-slug", default="jjonga")
    parser.add_argument("--protagonist-name", default="쫑아")
    parser.add_argument("--episode-title", default="비 오는 날 산책")
    parser.add_argument(
        "--episode-text",
        default="비 오는 날 산책을 싫어하던 쫑아가 우비를 입고 나가서 작은 물웅덩이를 발견하고 신나게 노는 이야기.",
    )
    parser.add_argument("--cut-count", type=int, default=4)
    parser.add_argument("--generate", action="store_true", help="Deprecated. Pet Toon now writes a manual ChatGPT prompt only.")
    args = parser.parse_args()

    episode_dir = (REPO_ROOT / args.episode_dir).resolve()
    storyboard_dir = episode_dir / "storyboard"
    prompt_path = episode_dir / "chatgpt-image-prompt.md"

    character_dir = REPO_ROOT / "characters" / args.protagonist_slug
    bible_text = read_text_if_exists(character_dir / "bible.md")
    prompt_text = read_text_if_exists(character_dir / "prompts.md")
    refs = character_refs(args.protagonist_slug)

    episode_dir.mkdir(parents=True, exist_ok=True)
    storyboard_dir.mkdir(parents=True, exist_ok=True)

    source_packet = {
        "workType": "new_pet_toon_episode",
        "channelLane": "pet",
        "projectLane": "pet-toon",
        "outputPolicy": "manual-chatgpt-prompt-handoff",
        "series": "pet-toon",
        "formatProfile": "pet-toon-image-only-v1",
        "episode": {
            "slug": episode_dir.name,
            "title": args.episode_title,
            "rawNarrative": args.episode_text,
            "cutCount": args.cut_count,
        },
        "protagonist": {
            "name": args.protagonist_name,
            "slug": args.protagonist_slug,
            "referenceFolder": f"characters/{args.protagonist_slug}",
            "referenceMode": "manual-chatgpt-reference-upload",
            "referenceImages": [rel(path, REPO_ROOT) for path in refs],
        },
        "outputs": {
            "chatgptPrompt": "chatgpt-image-prompt.md",
            "humanSavedCutImages": "images/cuts/*.png",
            "humanSavedWebtoonStrip": "images/episode-strip.png",
            "manifest": "pet-toon-manifest.json",
        },
        "hardRules": [
            "The agent writes prompts only; it does not call image generation APIs.",
            "Preserve the canonical character drawing style almost exactly.",
            "Do not create video outputs.",
            "Do not add text, subtitles, logos, or watermarks inside generated images.",
            "Lock any undefined character's first generated design for later reuse.",
        ],
    }
    write_json(episode_dir / "source-packet.json", source_packet)

    packet_md = f"""# {args.episode_title}

## Work Type

new_pet_toon_episode

## Output Policy

manual-chatgpt-prompt-handoff

## Protagonist

{args.protagonist_name} (`{args.protagonist_slug}`)

## Episode

{args.episode_text}

## Required Agent Output

- `chatgpt-image-prompt.md`
- `storyboard/style-lock.md`
- `storyboard/storyboard-plan.json`
- `storyboard/character-continuity.json`
- `pet-toon-manifest.json`

## Human Output Paths After ChatGPT Generation

- `images/cuts/cut-XX.png`
- `images/episode-strip.png`
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
                "referenceMode": "manual-chatgpt-reference-upload",
                "canonicalReferenceImages": [rel(path, REPO_ROOT) for path in refs],
                "lockedFromCut": None,
                "status": "canonical",
            }
        },
        "newCharacterInstructions": [
            "Assign a stable slug before prompting ChatGPT.",
            "Describe first generated design and output image path after the human receives it.",
            "Reuse the same locked description and image in later cuts.",
        ],
    }
    write_json(storyboard_dir / "character-continuity.json", continuity)

    beats = build_default_cuts(args.protagonist_name, args.episode_text, args.cut_count)
    cuts: list[dict[str, Any]] = []
    for index, beat in enumerate(beats, start=1):
        cut_id = f"cut-{index:02d}"
        prompt = build_cut_prompt(args.protagonist_slug, args.protagonist_name, args.episode_text, beat, index, len(beats))
        cuts.append(
            {
                "id": cut_id,
                "title": beat["title"],
                "beat": beat["beat"],
                "emotion": beat["emotion"],
                "cast": [
                    {
                        "slug": args.protagonist_slug,
                        "name": args.protagonist_name,
                        "count": 1,
                    }
                ],
                "prompt": prompt,
                "negativePrompt": DEFAULT_NEGATIVE_PROMPT,
                "referenceImages": [rel(path, REPO_ROOT) for path in refs],
                "plannedHumanOutputFile": f"images/cuts/{cut_id}.png",
            }
        )

    storyboard_plan = {
        "episodeSlug": episode_dir.name,
        "title": args.episode_title,
        "formatProfile": "pet-toon-image-only-v1",
        "outputPolicy": "manual-chatgpt-prompt-handoff",
        "provider": "chatgpt_manual",
        "referenceMode": "manual-chatgpt-reference-upload",
        "promptFile": "chatgpt-image-prompt.md",
        "plannedHumanOutputs": {
            "cutImages": "images/cuts/*.png",
            "webtoonStrip": "images/episode-strip.png",
        },
        "cuts": cuts,
    }
    write_json(storyboard_dir / "storyboard-plan.json", storyboard_plan)

    chatgpt_prompt = build_chatgpt_prompt(
        args.protagonist_slug,
        args.protagonist_name,
        args.episode_title,
        args.episode_text,
        refs,
        cuts,
    )
    prompt_path.write_text(chatgpt_prompt, encoding="utf-8")

    manifest = {
        "status": "prompt_ready",
        "blocker": None,
        "episodeDir": rel(episode_dir, REPO_ROOT),
        "sourcePacket": "source-packet.json",
        "styleLock": "storyboard/style-lock.md",
        "storyboardPlan": "storyboard/storyboard-plan.json",
        "characterContinuity": "storyboard/character-continuity.json",
        "chatgptPrompt": "chatgpt-image-prompt.md",
        "plannedHumanCutImages": [cut["plannedHumanOutputFile"] for cut in cuts],
        "plannedHumanWebtoonStrip": "images/episode-strip.png",
        "generatedImagesByAgent": [],
        "note": "Pet Toon is complete when this ChatGPT prompt handoff exists. A human operator generates and saves images separately.",
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    write_json(episode_dir / "pet-toon-manifest.json", manifest)

    if args.generate:
        print("Note: --generate is deprecated for Pet Toon and was ignored.", file=sys.stderr)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
