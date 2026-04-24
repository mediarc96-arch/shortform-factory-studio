# Pet Toon Paperclip Issue Prompt

아래 블록은 `[Pet Toon]` issue 본문에 그대로 붙여넣는 canonical 템플릿이다.

```md
## Work Type
new_pet_toon_episode

## channelLane
pet

## projectLane
pet-toon

## outputPolicy
image-only

## Series
pet-toon

## Format Profile
pet-toon-image-only-v1

## Objective
raw pet episode narrative를 GPT Image 2 reference-image workflow로 웹툰형 이미지 파일 묶음으로 제작한다.
최종 목표는 cut별 PNG 이미지와 세로 웹툰 strip 이미지뿐이다. 영상 제작은 하지 않는다.

## Operating Rules
- Use `/home/kindsr/projects/shortform-factory-studio` as the production workspace.
- Use `/home/kindsr/projects/shortform-factory-studio/episodes/pet-toon-template` as the default episode template root.
- Use `/home/kindsr/projects/shortform-factory-studio/formats/pet-toon-image-only-v1/profile.json` as the format profile.
- Keep the stage order fixed: `SOURCE -> STYLE_LOCK -> PLAN -> IMAGE -> MANIFEST`.
- Stop after image outputs. Do not create video, keyframe, camera, dubbing, SFX, typography, or publish packets.
- Use Paperclip's central image generation API for OpenAI GPT Image 2 (`gpt-image-2`) image generation.
- If cast members already exist under `characters/<slug>/`, derive the shared style-lock prompt from their bibles and refs before image generation.
- Preserve the original approved drawing style almost exactly. Do not reinterpret the character into a new art style.
- If a new character appears without a canonical definition, lock its first generated design in `storyboard/character-continuity.json` and reuse that lock later.
- Save cut images under `images/cuts/`.
- Save the full vertical webtoon image under `images/episode-strip.png`.
- Save the reusable style lock prompt under `storyboard/style-lock.md`.
- Save OpenAI image jobs under `openai-image-jobs/`.
- Submit image jobs to `/api/companies/:companyId/image-generations` when Paperclip runtime env is present. The agent must not need direct access to `OPENAI_API_KEY`.
- Keep generated images text-free. No subtitles, logos, watermarks, or readable text.
- Default to exactly one instance of each named character per cut unless the issue explicitly says otherwise.

## 주인공
{{PROTAGONIST_NAME}} (`{{PROTAGONIST_SLUG}}`)

## 에피소드 내용
{{RAW_EPISODE_NARRATIVE}}

## 컷 수
{{CUT_COUNT}}
```
