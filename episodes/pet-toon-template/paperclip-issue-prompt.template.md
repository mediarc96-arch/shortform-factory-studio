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
manual-chatgpt-prompt-handoff

## Series
pet-toon

## Format Profile
pet-toon-image-only-v1

## Objective
raw pet episode narrative를 사람이 ChatGPT에 붙여넣을 수 있는 웹툰 이미지 생성 프롬프트로 정리한다.
최종 에이전트 산출물은 `chatgpt-image-prompt.md`다. 영상 제작과 이미지 API 호출은 하지 않는다.

## Operating Rules
- Use `/home/kindsr/projects/shortform-factory-studio` as the production workspace.
- Use `/home/kindsr/projects/shortform-factory-studio/episodes/pet-toon-template` as the default episode template root.
- Use `/home/kindsr/projects/shortform-factory-studio/formats/pet-toon-image-only-v1/profile.json` as the format profile.
- Keep the stage order fixed: `SOURCE -> STYLE_LOCK -> PLAN -> PROMPT_HANDOFF -> MANIFEST`.
- Stop after prompt handoff. Do not create video, keyframe, camera, dubbing, SFX, typography, or publish packets.
- Do not call Paperclip image generation API or OpenAI API from the agent.
- If cast members already exist under `characters/<slug>/`, derive the shared style-lock prompt from their bibles and refs before writing the ChatGPT prompt.
- Preserve the original approved drawing style almost exactly. Do not reinterpret the character into a new art style.
- If a new character appears without a canonical definition, define a stable first-appearance lock in `storyboard/character-continuity.json` and instruct the human to reuse the first generated result later.
- Save the human-facing ChatGPT prompt under `chatgpt-image-prompt.md`.
- Save the reusable style lock prompt under `storyboard/style-lock.md`.
- The prompt must ask ChatGPT for one full vertical webtoon strip and separate cut images.
- The prompt must tell the human to save cut images under `images/cuts/` and the full strip under `images/episode-strip.png`.
- Keep requested images text-free. No subtitles, logos, watermarks, or readable text.
- Default to exactly one instance of each named character per cut unless the issue explicitly says otherwise.

## 주인공
{{PROTAGONIST_NAME}} (`{{PROTAGONIST_SLUG}}`)

## 에피소드 내용
{{RAW_EPISODE_NARRATIVE}}

## 컷 수
{{CUT_COUNT}}

## 추가 등장 캐릭터
{{OPTIONAL_SUPPORTING_CAST_OR_EMPTY}}

## 참고 이미지
{{OPTIONAL_REFERENCE_PATHS_OR_EMPTY}}
```
