# Pet Contents Paperclip Issue Prompt

아래 블록은 `[Pet Contents]` issue 본문에 그대로 붙여넣는 canonical 템플릿이다.

```md
## Work Type
new_episode

## channelLane
pet

## projectLane
pet

## publishTarget
youtube-pets

## Series
pet-contents

## Format Profile
pet-contents-vertical-webtoon-v1

## Objective
raw pet episode narrative를 storyboard-first workflow로 제작한다.
최종 목표는 storyboard cut bundle, motion-ready keyframe plan, final render, publish packet이다.

## Operating Rules
- Use `/home/kindsr/projects/shortform-factory-studio` as the production workspace.
- Use `/home/kindsr/projects/shortform-factory-studio/episodes/pet-contents-template` as the default episode template root.
- Use `/home/kindsr/projects/shortform-factory-studio/formats/pet-contents-vertical-webtoon-v1/profile.json` as the format profile.
- Keep the stage order fixed: `SOURCE -> STORYBOARD -> BRIEF -> SCRIPT -> EDIT -> RENDER -> POST -> QA -> PUBLISH`.
- The first visual deliverable is a storyboard/webtoon cut bundle.
- Generate storyboard cuts through the `codex_local` agent using any approved image-capable provider that is actually operational in the current runtime.
- `xAI Grok image` and `OpenAI GPT Image 2` are both acceptable storyboard providers.
- Treat `Duct Tape` as a non-canonical test-line reference, not as the default directly selected production model for this workflow.
- If cast members already exist under `characters/<slug>/`, derive the shared style-lock prompt from their bibles and refs before storyboard generation.
- If canonical character files do not exist yet, derive a provisional style lock from the raw episode narrative and continue planning instead of blocking intake.
- Save storyboard cut images under `storyboard/webtoon-cuts/`.
- Save the reusable style lock prompt under `storyboard/style-lock.md`.
- Save the camera plan under `storyboard/camera-plan.md`.
- Save the post-production plan under `post-production-plan.md`.
- Keep generated footage text-free. Add captions and typography only in `POST`.
- If this issue or an approved follow-up comment contains `대본:`, treat that section as the authoritative narration source for dubbing.
- If `대본:` exists, estimate rough narration timing with a local/basic no-paid-API guide TTS or equivalent timing pass before finalizing runtime and scene durations.
- Scene video must follow approved storyboard cuts and motion keyframes rather than fresh prose prompts.
- Require `scene-n` final frame and `scene-(n+1)` opening frame to begin from the same visual state.

## Story Input
{{RAW_EPISODE_NARRATIVE}}

## 대본:
{{OPTIONAL_NARRATION_SCRIPT}}
```
