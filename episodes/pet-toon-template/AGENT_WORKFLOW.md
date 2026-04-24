# Pet Toon Image-Only — Agent Workflow

이 문서는 `[Pet Toon]` pet episode를 영상이 아닌 웹툰형 이미지 파일 묶음으로 제작할 때 따라야 할 기본 실행 순서를 정의한다.

핵심 원칙:

- `raw episode -> source packet`
- `source packet -> strict style lock`
- `style lock -> storyboard plan`
- `storyboard plan -> GPT Image 2 cut images`
- `cut images -> webtoon strip`
- 여기서 종료한다. 영상 제작 단계로 넘기지 않는다.

## Trigger

- issue title starts with `[Pet Toon]`
- issue body may be raw episode narrative only
- `주인공:` and `에피소드 내용:` are preferred
- `대본:` is ignored unless the issue explicitly asks for captions in a later non-generation layer

## 표준 실행 단계

1. raw issue narrative에서 protagonist, cast, 장소, 사건 순서, 컷 수, 안전 리스크를 추출한다.
2. `source-packet.json`에 story truth를 정리한다.
3. cast가 `characters/<slug>/`에 있으면 bible, prompts, reference images를 읽는다.
4. 캐노니컬 캐릭터가 있으면 `reference-only`로 유지한다. 재해석, 스타일 변경, photorealistic 변환, glossy 3D 변환은 금지한다.
5. 신규 인물이나 캐릭터가 필요하면 stable slug를 만들고 첫 등장 설명을 `storyboard/character-continuity.json`에 잠근다.
6. `storyboard/style-lock.md`를 만든다.
7. `storyboard/storyboard-plan.json`을 만든다.
8. storyboard plan에는 cut별 출연 캐릭터와 허용 개체 수를 적어 duplicate drift를 먼저 막는다.
9. style lock에는 최소한 `duplicate pet`, `second version of same character`, `extra animal`, `extra limbs`, `wings`, `merged face`, `wrong fur color`, `wrong ear shape`, `style drift`, `text`, `subtitle`, `watermark`, `logo` 금지 항목을 넣는다.
10. `openai-image-jobs/*.json`을 만든다.
11. Paperclip 중앙 이미지 생성 API(`/api/companies/:companyId/image-generations`)로 GPT Image 2 edit/reference-image 요청을 실행한다.
12. 개별 컷은 `images/cuts/cut-XX.png`에 저장한다.
13. 모든 컷이 생성되면 `images/episode-strip.png`에 세로 웹툰형 이미지로 합친다.
14. `pet-toon-manifest.json`에 source, refs, cut outputs, provider manifests, blocker를 기록한다.

## 금지 단계

`[Pet Toon]`에서는 다음 파일이나 단계를 만들지 않는다.

- `keyframe-plan.json`
- `storyboard/camera-plan.md`
- `video-generation-job.json`
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

### `[IMAGE]`

- `images/cuts/`에 cut 이미지 존재
- `images/episode-strip.png` 존재
- 각 컷의 provider manifest가 존재
- 같은 캐릭터가 다른 그림체, 다른 털색, 다른 얼굴 구조로 바뀌지 않음

## API 키 blocker

Paperclip agent 환경에 `PAPERCLIP_API_URL`, `PAPERCLIP_API_KEY`, `PAPERCLIP_COMPANY_ID`, `PAPERCLIP_PROJECT_WORKSPACE_ID`가 없고 직접 fallback용 `OPENAI_API_KEY`도 없으면 source packet, style lock, storyboard plan, image job까지 만들고 `pet-toon-manifest.json`을 `blocked_missing_image_generation_service` 상태로 남긴다.
