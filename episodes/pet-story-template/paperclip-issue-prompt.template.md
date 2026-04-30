# Pet Story Paperclip Issue Prompt

아래 블록은 Paperclip issue 본문에 그대로 붙여넣는 템플릿이다.

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
pet-shortform

## Episode
{{EPISODE_SLUG}}

## Objective
반려동물 일상 에피소드를 `pet-story-short-vertical-v1` 기준으로 제작한다.
최종 목표는 YouTube Shorts 업로드 가능한 episode packet, final render, publish packet이다.

## Operating Rules
- Use `/home/kindsr/projects/shortform-factory-studio` as the production workspace.
- Use `/home/kindsr/projects/shortform-factory-studio/episodes/pet-story-template` as the default episode template root.
- Use `/home/kindsr/projects/shortform-factory-studio/formats/pet-story-short-vertical-v1/profile.json` as the format profile.
- Keep the stage order fixed: `SOURCE -> BRIEF -> SCRIPT -> EDIT -> RENDER -> POST -> QA -> PUBLISH`.
- Keep generated footage text-free. Add captions, typography, and disclosure only in `POST`.
- Use `reference-only` character workflow first. Do not start with LoRA unless continuity fails repeatedly.
- Keep humans as background presence only unless the issue explicitly requires them.
- Do not depict actual dangerous human-food ingestion. The climax is the attempt and the caught reaction, not eating.
- Use Runway API for scene generation unless the issue explicitly approves another provider.
- If this issue or an approved follow-up comment contains `대본:`, treat that section as the authoritative narration source for `POST` dubbing.
- If `대본:` exists, estimate rough narration timing with a local/basic no-paid-API guide TTS or equivalent timing pass before finalizing runtime.
- Do not force pet scenes to `6s` each. Use the default `4 / 4 / 4 / 5 / 5s` baseline only when narration timing does not require a different split.
- For each scene, lock both a start frame and an end frame before scene-video generation.
- For each scene boundary, declare `boundaryMode`:
  - `continuous_handoff`: use the prior scene final frame as the next scene start seed.
  - `transition_cut`: allow the next scene to use its own approved start frame, but define the transition type, duration, reason, and audio/visual bridge.

## Character Canon
- protagonist: `{{PET_NAME}}`
- character slug: `{{CHARACTER_SLUG}}`
- character bible: `characters/{{CHARACTER_SLUG}}/character-bible.md`
- preserve face shape, fur color, ear shape, eye mood, body size, and tail silhouette across all scenes

## Story Truth
- setup: {{SETUP}}
- trigger: {{TRIGGER}}
- escalation: {{ESCALATION}}
- climax: {{CLIMAX}}
- ending: {{ENDING}}

## Scene Beats
1. `scene-1-watchful-wait`
2. `scene-2-coast-clear`
3. `scene-3-chair-approach`
4. `scene-4-climb-and-jump`
5. `scene-5-caught-but-innocent`

## Script Policy
- Do not write a dialogue-heavy script.
- Prefer one short narration beat or one short inner-monologue line per scene.
- Typography should be sparse and reaction-led, not explanatory.
- Keep speech, SFX, and typography in separate slots.
- If `대본:` exists, build the scene timing map from that narration timing first and then fit the visual beats to it.

## 대본:
{{OPTIONAL_NARRATION_SCRIPT}}

## Required Deliverables
- `source-packet.json`
- `packet.md`
- `episode.schema.json`
- `keyframe-plan.json`
- `narration-script.md`
- `voice-slots.json`
- `typography-slots.json`
- `video-generation-job.json`
- keyframe review bundle
- picture lock
- dub lock
- final review bundle
- publish packet

## Quality Gates
- character continuity holds across all scenes
- environment continuity holds across all scenes
- each scene declares `startFrame`, `endFrame`, and `boundaryMode`; `continuous_handoff` boundaries preserve the prior final frame as the next opening state, while `transition_cut` boundaries include a clear transition plan
- no visible text is baked into generated footage
- the climax reads clearly without showing real ingestion
- the final reaction shot lands as the comedic payoff
- QA signoff is required before publish
```
