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
6. storyboard plan에는 cut별 출연 캐릭터와 허용 개체 수를 적어 duplication drift를 먼저 막는다.
7. style lock에는 최소한 `extra dog`, `duplicate pet`, `extra animal`, `extra limbs`, `wings`, `merged face`, `second version of same dog`, `wrong fur color`, `style drift` 금지 항목을 넣는다.
8. 고위험 액션 비트는 긴 shot 하나로 몰지 말고 더 짧은 motion beat로 분해한다.
9. `codex_local` agent가 현재 런타임에서 실제로 사용 가능한 approved image provider를 골라 `storyboard/webtoon-cuts/*.png`를 만든다.
10. `xAI Grok image`와 `OpenAI GPT Image 2`는 모두 허용 가능한 provider다. `GPT Image 2`가 없다고 바로 막지 말고, working provider를 선택한다.
11. 이 workflow에서는 `Duct Tape`를 default 직접 선택 모델로 보지 않는다. 다른 이미지 툴은 이슈에서 명시적으로 승인된 경우에만 예외로 쓴다.
12. storyboard bundle이 episode를 정확히 전달하는지 확인한다.
13. storyboard를 motion-friendly `keyframe-plan.json`으로 다시 정리한다.
14. `storyboard/camera-plan.md`를 만든다.
15. `대본:`이 있으면 local/basic no-paid-API timing pass로 rough runtime을 계산한다.
16. `narration-script.md`, `voice-slots.json`, `typography-slots.json`을 만든다.
17. `post-production-plan.md`를 만든다.
18. `video-generation-job.json`을 만든다.
19. sequential scene video를 생성한다.
20. picture lock을 만든다.
21. dub, SFX, BGM, typography, color pass를 적용한다.
22. QA와 publish packet으로 넘긴다.

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
- cut별 출연 개체 수가 잠겨 있고, 같은 강아지가 중복 등장하지 않음

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
- 각 scene의 start frame과 end frame이 잠겨 있음
- 각 scene boundary가 `continuous_handoff` 또는 `transition_cut`으로 명시됨
- `continuous_handoff` boundary는 scene-n final frame과 scene-(n+1) first frame이 이어짐
- `transition_cut` boundary는 전환 방식, 전환 길이, 목적, 오디오/시각 브리지가 명시됨
- provider manifest가 남음
- 날개, 추가 다리, 복제 강아지, 잘못된 털색 같은 비의도 변형이 없음

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
