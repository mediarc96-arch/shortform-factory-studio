# Pet Contents Storyboard-First — Agent Workflow

이 문서는 `[Pet Contents]` pet-content episode를 Paperclip agent가 반복 생산할 때 따라야 할 기본 실행 순서를 정의한다.

핵심 원칙:

- `raw episode -> source packet`
- `source packet -> style lock`
- `style lock -> storyboard cuts`
- `storyboard cuts -> motion keyframes`
- `keyframes -> camera plan -> scene video`
- `picture lock -> dub/sfx/bgm -> typography -> QA`

## Trigger

- issue title starts with `[Pet Contents]`
- issue body may be raw episode narrative only
- `대본:` is optional but authoritative if present

## 표준 실행 단계

1. raw issue narrative에서 cast, 장소, 사건 순서, 안전 리스크를 추출한다.
2. `source-packet.json`에 story truth를 정리한다.
3. cast가 `characters/<slug>/`에 있으면 bible과 refs를 읽고, 없으면 narrative 기반 provisional lock을 만든다.
4. reusable `storyboard/style-lock.md`를 만든다.
5. `storyboard/storyboard-plan.json`을 만든다.
6. `codex_local` agent가 OpenAI `GPT Image 2`를 호출해 `storyboard/webtoon-cuts/*.png`를 만든다.
7. 이 workflow에서는 `Duct Tape`를 default 직접 선택 모델로 보지 않는다. 다른 이미지 툴은 이슈에서 명시적으로 승인된 경우에만 예외로 쓴다.
8. storyboard bundle이 episode를 정확히 전달하는지 확인한다.
9. storyboard를 motion-friendly `keyframe-plan.json`으로 다시 정리한다.
10. `storyboard/camera-plan.md`를 만든다.
11. `대본:`이 있으면 local/basic no-paid-API timing pass로 rough runtime을 계산한다.
12. `narration-script.md`, `voice-slots.json`, `typography-slots.json`을 만든다.
13. `post-production-plan.md`를 만든다.
14. `video-generation-job.json`을 만든다.
15. sequential scene video를 생성한다.
16. picture lock을 만든다.
17. dub, SFX, BGM, typography, color pass를 적용한다.
18. QA와 publish packet으로 넘긴다.

## 완료 기준

### `[SOURCE]`

- raw narrative가 packet 구조로 정리됨
- cast와 setting continuity가 정리됨
- primary risk와 safety tone이 명시됨

### `[STORYBOARD]`

- `storyboard/style-lock.md` 존재
- `storyboard/storyboard-plan.json` 존재
- `storyboard/webtoon-cuts/`에 cut 이미지 존재
- 컷 흐름만 봐도 episode가 읽힘

### `[BRIEF]`

- `packet.md` 존재
- `episode.schema.json` 존재
- `keyframe-plan.json` 존재
- storyboard와 keyframe plan이 같은 story spine을 유지

### `[SCRIPT]`

- `대본:`이 있으면 narration source-of-truth 반영
- `voice-slots.json`과 `typography-slots.json` 동기화
- narration timing pass 결과를 반영

### `[EDIT]`

- `storyboard/camera-plan.md` 존재
- `post-production-plan.md` 존재
- `video-generation-job.json` 존재
- scene boundary handoff 규칙이 명시됨

### `[RENDER]`

- storyboard / keyframe / style lock을 반영한 scene video가 생성됨
- scene-n final frame과 scene-(n+1) first frame이 이어짐
- provider manifest가 남음

### `[POST]`

- narration dub 반영
- SFX / BGM / typography / color pass 반영
- post-production checklist가 모두 처리됨

## 후반작업 최소 체크

- image consistency correction
- face correction
- simple parts animation
- background separation
- situation-specific FX
- speed ramp
- subtitle placement
- SFX
- BGM
- color treatment
- QA risk check
