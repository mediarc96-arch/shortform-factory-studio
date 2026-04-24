# Pet Toon Manual Prompt Handoff — Agent Workflow

이 문서는 `[Pet Toon]` pet episode를 영상이 아닌 웹툰형 이미지 prompt handoff로 제작할 때 따라야 할 기본 실행 순서를 정의한다.

에이전트는 이미지 생성 API를 호출하지 않는다. 사람이 ChatGPT에 그대로 입력할 수 있는 `chatgpt-image-prompt.md`를 만들면 이슈를 완료한다.

핵심 원칙:

- `raw episode -> source packet`
- `source packet -> strict style lock`
- `style lock -> storyboard plan`
- `storyboard plan -> ChatGPT image prompt md`
- 여기서 종료한다. 이미지 API 호출이나 영상 제작 단계로 넘기지 않는다.

## Trigger

- issue title starts with `[Pet Toon]`
- issue body may be minimal if it includes character and episode
- required: `주인공:` and `에피소드 내용:`
- preferred: `캐릭터 slug:`, `컷 수:`, `참조 이미지:`
- `대본:` is ignored unless the issue explicitly asks for captions in a later non-generation layer

## 표준 실행 단계

1. raw issue narrative에서 protagonist, cast, 장소, 사건 순서, 컷 수, 안전 리스크를 추출한다.
2. `source-packet.json`에 story truth를 정리한다.
3. cast가 `characters/<slug>/`에 있으면 bible, prompts, reference images를 읽는다.
4. 캐노니컬 캐릭터가 있으면 사람이 ChatGPT에 업로드할 reference image 목록을 적는다. 재해석, 스타일 변경, photorealistic 변환, glossy 3D 변환은 금지한다.
5. 신규 인물이나 캐릭터가 필요하면 stable slug를 만들고 첫 등장 설명을 `storyboard/character-continuity.json`에 잠근다.
6. `storyboard/style-lock.md`를 만든다.
7. `storyboard/storyboard-plan.json`을 만든다.
8. storyboard plan에는 cut별 출연 캐릭터와 허용 개체 수를 적어 duplicate drift를 먼저 막는다.
9. style lock에는 최소한 `duplicate pet`, `second version of same character`, `extra animal`, `extra limbs`, `wings`, `merged face`, `wrong fur color`, `wrong ear shape`, `style drift`, `text`, `subtitle`, `watermark`, `logo` 금지 항목을 넣는다.
10. `chatgpt-image-prompt.md`를 만든다.
11. prompt md에는 사람이 업로드할 reference images, 전체 웹툰 strip 생성 프롬프트, cut별 개별 이미지 생성 프롬프트, 저장 파일명을 모두 포함한다.
12. `pet-toon-manifest.json` 상태를 `prompt_ready`로 기록한다.
13. 이슈를 완료한다. 실제 이미지는 사람이 ChatGPT에서 받아 `images/cuts/`와 `images/episode-strip.png`에 저장한다.

## 금지 단계

`[Pet Toon]`에서는 다음 파일이나 단계를 만들지 않는다.

- `keyframe-plan.json`
- `storyboard/camera-plan.md`
- `video-generation-job.json`
- `openai-image-jobs/*.json`
- scene video
- dubbing
- SFX
- BGM
- typography overlay
- publish packet

## 완료 기준

### `[SOURCE]`

- raw narrative가 packet 구조로 정리됨
- protagonist와 reference folder가 명시됨
- episode output policy가 `image-only`로 고정됨

### `[STYLE_LOCK]`

- `storyboard/style-lock.md` 존재
- 기존 캐릭터의 canonical refs가 명시됨
- 신규 캐릭터의 first-appearance lock 정책이 명시됨

### `[PLAN]`

- `storyboard/storyboard-plan.json` 존재
- cut별 prompt, setting, emotion, cast cardinality, negative prompt가 있음

### `[PROMPT_HANDOFF]`

- `chatgpt-image-prompt.md` 존재
- 사람이 업로드할 reference image 목록이 있음
- 전체 웹툰 strip 생성 프롬프트가 있음
- cut별 개별 이미지 생성 프롬프트가 있음
- 저장할 파일명이 `images/cuts/cut-XX.png`, `images/episode-strip.png`로 명시됨
- 같은 캐릭터가 다른 그림체, 다른 털색, 다른 얼굴 구조로 바뀌지 않게 하는 고정 문구가 있음

## 완료 기준

`chatgpt-image-prompt.md`와 `pet-toon-manifest.json`의 `prompt_ready` 상태가 있으면 완료다. API key 부재는 blocker가 아니다.
