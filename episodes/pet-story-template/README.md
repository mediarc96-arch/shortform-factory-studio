# Pet Story Short Vertical Template

이 폴더는 반려동물 일상형 Shorts를 만들 때 쓰는 **정식 기본 템플릿**이다.

기준 포맷은 `formats/pet-story-short-vertical-v1/profile.json`이다.

즉 반려동물 리액션형 짧은 에피소드는 특별한 지시가 없는 한 아래 구조를 그대로 따른다.

- `source -> brief -> script -> keyframe review -> picture -> dub/sfx -> typography -> QA -> publish`

## 기본 원칙

- source-of-truth는 실제 관찰된 반려동물 에피소드다.
- source packet에 행동 truth, 공간 continuity, 안전 제약, 권리 상태를 먼저 남긴다.
- canonical character ref와 keyframe 5장을 먼저 잠근다.
- keyframe 승인 전에는 scene video를 생성하지 않는다.
- video generation 단계에서는 글자를 넣지 않는다.
- picture lock을 먼저 만든다.
- 더빙과 SE는 picture lock 이후에 붙인다.
- typography는 마지막 후반 단계에서만 넣는다.
- 기본 화면 비율은 `9:16`이다.
- 기본 길이는 `20~24초`다.
- 기본 scene 수는 `5개`다.
- 기본 pet timing은 교육형처럼 `6초 x 5`가 아니다.
- narration은 sparse가 기본이다.
- actual dangerous human-food ingestion은 보여주지 않는다.
- `대본:`이 있으면 먼저 로컬/basic guide TTS 또는 비-API timing pass로 spoken length를 잡고, 그 다음 total runtime과 scene duration을 확정한다.
- scene cut는 jump cut이 아니라 handoff로 본다. `scene-n` 마지막 프레임과 `scene-(n+1)` 첫 프레임은 같은 상태에서 시작해야 한다.

## 표준 scene 구조

기본 scene 구성은 아래와 같다.

1. `scene-1-watchful-wait`
2. `scene-2-coast-clear`
3. `scene-3-chair-approach`
4. `scene-4-climb-and-jump`
5. `scene-5-caught-but-innocent`

권장 기본 길이:

- `scene-1`: 4초
- `scene-2`: 4초
- `scene-3`: 4초
- `scene-4`: 5초
- `scene-5`: 5초

이 `4 / 4 / 4 / 5 / 5초`는 대본이 없을 때의 baseline이다.
`대본:`이 있으면 narration timing, reaction pause, motion clarity에 맞춰 다시 배분한다.

## 표준 voice 구조

기본 voice slot 구성은 `scene당 0~1개의 짧은 line`이다.

즉 말모이랩처럼 정보량이 많은 구조가 아니라:

1. 상황 setup
2. coast-clear reaction
3. sneak approach reaction
4. climax reaction
5. caught payoff

이 흐름을 기본값으로 본다.

내레이션 모드는 세 가지 중 하나를 고른다.

- narrator
- pet inner monologue
- mostly silent + SFX

## 이 폴더의 역할

- 반려동물 Shorts용 episode packet 기본 구조를 제공
- Paperclip agent가 따라야 할 작업 순서를 제공
- 반복 양산 가능한 vertical reaction workflow를 제공

## 파일 구성

- `AGENT_WORKFLOW.md`
  - Pet story episode 제작 순서
- `packet.template.md`
  - 사람 읽는 회차 개요 템플릿
- `source-packet.template.json`
  - 실제 관찰 에피소드 source packet 템플릿
- `episode.schema.template.json`
  - 에피소드 메타데이터 템플릿
- `keyframe-plan.template.json`
  - keyframe gate 템플릿
- `narration-script.template.md`
  - 짧은 narration/inner monologue 스크립트 템플릿
- `voice-slots.template.json`
  - sparse narration slot 템플릿
- `typography-slots.template.json`
  - reaction-led caption 템플릿
- `video-generation-job.template.json`
  - vertical 5-scene picture generation plan 템플릿
- `paperclip-issue-prompt.template.md`
  - Paperclip issue에 바로 붙여넣을 수 있는 prompt 템플릿

## 운영 규칙

- 새 pet story episode는 이 폴더를 복사해 시작한다.
- recurring pet이라면 `characters/<slug>/character-bible.md`와 `characters/<slug>/refs/`를 먼저 잠근다.
- 별도 지시가 없으면 `reference-only`를 기본값으로 쓴다.
- humans are supporting context, not the protagonist.
- narration과 caption은 설명 과잉이 되지 않도록 sparse하게 유지한다.
- pet issue에 `대본:`이 있으면 POST 전용 나레이션 source-of-truth로 쓰고, timing pass도 그 텍스트 기준으로 잡는다.
- 다음 scene은 직전 scene의 handoff last frame과 동일한 상태에서 시작하도록 seed를 이어야 한다.

## Paperclip child issue 표준

1. `[SOURCE]` source packet
2. `[BRIEF]` packet + schema + keyframe plan
3. `[SCRIPT]` narration script + voice slots + typography slots
4. `[EDIT]` video-generation handoff
5. `[RENDER]` keyframes + picture scene generation
6. `[POST]` dub + SFX + typography + final export
7. `[QA]` final review
8. `[PUBLISH]` private upload and analytics

핵심은 `Video Editor`가 `video-generation-job.json`을 만든 뒤 끝나는 것이 아니라, `Video Generation Worker`가 keyframe과 picture scenes를 만들고 다시 `Video Editor`가 후반작업을 받아 `final`까지 닫는 구조라는 점이다.
