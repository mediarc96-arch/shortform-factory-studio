# Malmoelab Korean Education Template

이 폴더는 `malmoelab` 한글 교육 콘텐츠를 만들 때 쓰는 **정식 기본 템플릿**이다.

기준은 `episodes/daehan-pilot-codex-003`이다.

즉 말모이랩 교육 콘텐츠는 특별한 지시가 없는 한 아래 구조를 그대로 따른다.

- `source -> brief -> script -> keyframe review -> picture -> dub -> typography -> QA -> publish`

## 기본 원칙

- `Malmoelab DB`에서 가져온 예문을 source-of-truth로 쓴다.
- `003`처럼 2D 캐릭터 기준 이미지와 5개 keyframe을 먼저 잠근다.
- keyframe 승인 전에는 scene video를 생성하지 않는다.
- video generation 단계에서는 글자를 넣지 않는다.
- picture lock을 먼저 만든다.
- 더빙은 picture lock 이후에 붙인다.
- 한글 예문과 로마자, CTA는 마지막 타이포 단계에서만 넣는다.
- 캐릭터 TTS voice id는 전역 공용이 아니라 `characters/<slug>/voice.json`에서 읽는다.
- 기본 화면 비율은 `16:9`다.
- 기본 구도는 `teacher on right quarter + clean board on left three-quarters`다.

## 표준 scene 구조

기본 scene 구성은 `003`과 같다.

1. `scene-1-opening-handoff`
2. `scene-2-lesson-intro`
3. `scene-3-repeat-listen`
4. `scene-4-quiz-point`
5. `scene-5-ending-wave`

각 씬은 기본 `6초`, 총 기본 길이는 `30초`다.

## 표준 voice 구조

기본 voice slot 구성도 `003`과 같다.

1. opening greeting
2. 오늘의 문장 소개
3. 따라해 볼까요
4. 예문 읽기
5. 빈칸 질문
6. 엔딩

오프닝 문구는 `003` 기준 문장에서 캐릭터 이름만 바꾼다.
엔딩 문구도 `003`와 같은 구조를 기본값으로 쓴다.

## 이 폴더의 역할

- 에피소드 패킷 기본 구조를 제공
- Paperclip agent가 따라야 할 작업 순서를 제공
- 다른 교육 콘텐츠에도 재사용 가능한 단계형 제작 방법을 제공

## 파일 구성

- `AGENT_WORKFLOW.md`
  - Malmoelab 한글 교육 콘텐츠 제작 순서
- `PROCESS_REFERENCE.md`
  - 다른 시리즈에도 적용할 수 있는 범용 단계형 제작 절차
- `packet.template.md`
  - 사람 읽는 회차 개요 템플릿
- `source-packet.template.json`
  - source sentence / lesson / asset policy 템플릿
- `episode.schema.template.json`
  - 에피소드 메타데이터 템플릿
- `keyframe-plan.template.json`
  - keyframe gate 템플릿
- `video-generation-job.template.json`
  - 5-scene picture generation plan 템플릿
- `voice-slots.template.json`
  - `003` 구조의 더빙 슬롯 템플릿
- `typography-slots.template.json`
  - 한글/로마자/빈칸/CTA 타이포 템플릿

## 운영 규칙

- 새 `malmoelab` 교육 에피소드는 이 폴더를 복사해 시작한다.
- character voice id는 회차마다 직접 박지 말고 `characters/<slug>/voice.json`을 우선 사용한다.
- 회차에서 voice를 바꿔야 할 때만 `voice-slots.json`에서 `ttsVoiceEnv`를 override 한다.
- 예외 brief가 없으면 `003` 구조를 유지한다.

## Paperclip child issue 표준

`malmoelab` 교육 에피소드는 아래 child issue 체인을 기본으로 사용한다.

1. `[SOURCE]` source packet
2. `[BRIEF]` packet + schema + keyframe plan
3. `[SCRIPT]` narration + voice + typography slots
4. `[EDIT]` video-generation handoff
5. `[RENDER]` keyframes + picture scene generation
6. `[POST]` dub + typography + final export
7. `[QA]` final review
8. `[PUBLISH]` private upload and analytics

핵심은 `Video Editor`가 `video-generation-job.json`을 만든 뒤 끝나는 것이 아니라, `Video Generation Worker`가 keyframe과 picture scenes를 만들고 다시 `Video Editor`가 후반작업을 받아 `final`까지 닫는 구조라는 점이다.

## 현재 표준 포맷

- format profile: `formats/malmoelab-keyframe-dub-after-picture-v1/profile.json`
- 대표 reference episode: `episodes/daehan-pilot-codex-003`
