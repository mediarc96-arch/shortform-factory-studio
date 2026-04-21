# Malmoelab vNext Episode Schema

날짜: 2026-04-17
대상 프로젝트: `shortform-factory-studio`
관련 문서: `2026-04-17-malmoelab-vnext-dubbing-workbench.md`

## 1. 목적

이 문서는 `malmoelab-*` 계열 에피소드를 앞으로 어떤 데이터 구조와 제작 단계로 운영할지 정의한다.

핵심 목표는 세 가지다.

- 재사용 자산과 회차별 자산을 명확히 분리한다.
- 영상 생성, 더빙, 타이포그래피, QA를 서로 독립된 단계로 분리한다.
- 씬 단위 조립이 아니라 연속성을 가진 컨텐츠 블록을 중심으로 제작한다.

## 2. 기본 원칙

### 2.1 Picture First

영상 생성 단계에서는 텍스트를 넣지 않는다.

- 생성 단계: 캐릭터, 구도, 동작, 연속성 확보
- 후반 단계: 더빙, 타이포그래피, 효과음, 자막, CTA

### 2.2 Continuity First

컨텐츠 씬은 독립 장면이 아니라 같은 수업 안의 연속 숏으로 취급한다.

- 목표는 `frame-perfect continuity`가 아니라 `segment continuity`다.
- 오프닝과 엔딩은 짧은 전환효과를 써도 된다.
- 컨텐츠 씬끼리는 같은 캐릭터, 같은 교실 톤, 비슷한 카메라 높이와 레이아웃을 유지하면 충분하다.
- 이전 씬 마지막 프레임은 다음 씬의 강제 시작점이 아니라 선택적 참고 이미지로 본다.

### 2.3 Human-in-the-loop Voice

음성은 생성기 내부 기능이 아니라 후반 파이프라인의 독립 자산으로 다룬다.

우선순위는 아래 순서를 권장한다.

1. 기존 오프닝/엔딩 원본 음성 재사용
2. 사람 직접 더빙
3. 외부 성우 파일 업로드
4. 음성 클론 API
5. 임시 TTS

## 3. 자산 분류

### 3.1 재사용 자산

반복 사용되는 자산은 회차 폴더에 복사하지 않고 참조형으로 관리한다.

주요 위치:

- `characters/daehan/daehan.jpg`
- `characters/daehan/bible.md`
- `characters/daehan/prompts.md`
- `characters/daehan/01_Opening.mp4`
- `characters/daehan/02_Ending.mp4`
- `shared/sfx/*`
- `shared/music/*`
- `shared/voice-packs/*`

### 3.2 회차별 자산

에피소드마다 바뀌는 자산은 `episodes/<episode-slug>/` 아래에 둔다.

예:

- 수업 원문
- 쇼트/씬 계획
- 생성 프롬프트
- 컨텐츠 영상 클립
- 회차별 더빙
- 회차별 타이포 문안
- 리뷰 번들

## 4. 권장 폴더 구조

```text
episodes/<episode-slug>/
  packet.md
  source-packet.json
  episode.schema.json
  shots.schema.json
  assets/
    refs/
    boards/
    typography/
  renders/
    picture/
    picture-lock/
    final/
  audio/
    guide/
    human-dub/
    actor-dub/
    cloned-dub/
    reused-lines/
    mix/
  review/
    contact-sheets/
    frame-map/
    notes/
```

이 구조에서 중요한 점은 `renders/picture`와 `audio/*`를 분리하는 것이다.
영상이 먼저 잠기고, 이후 음성과 텍스트가 교체 가능해야 한다.

## 5. 에피소드 상태 머신

권장 상태는 아래와 같다.

1. `packet-draft`
2. `picture-ready`
3. `picture-lock`
4. `dub-ready`
5. `dub-lock`
6. `type-ready`
7. `type-lock`
8. `final-export`
9. `review-pass`

보정 작업이 발생하면 항상 직전 잠금 단계로 되돌린다.

예:

- 음성만 수정: `dub-ready`로 롤백
- 자막만 수정: `type-ready`로 롤백
- 장면 연결 수정: `picture-ready`로 롤백

## 6. 에피소드 매니페스트 스키마

vNext에서는 `source-packet.json` 외에 후반 제작 중심 메타데이터를 담는 `episode.schema.json`을 둔다.

예시:

```json
{
  "formatVersion": "malmoelab-vnext-episode@0.1",
  "episodeSlug": "malmoelab-ko-repeat-jeonyeok-vnext-001",
  "seriesSlug": "malmoelab-ko-repeat-jeonyeok",
  "characterSlug": "daehan",
  "characterRoot": "characters/daehan",
  "status": "picture-lock",
  "reusableAssets": {
    "openingClip": "characters/daehan/01_Opening.mp4",
    "endingClip": "characters/daehan/02_Ending.mp4",
    "characterImage": "characters/daehan/daehan.jpg",
    "bible": "characters/daehan/bible.md",
    "promptSet": "characters/daehan/prompts.md"
  },
  "lesson": {
    "topicType": "fill_blank_repeat",
    "sourceRef": "malmoelab.word_example",
    "wordText": "저녁",
    "sentenceKo": "저녁에 집에 가요.",
    "sentenceEn": "I go home in the evening."
  },
  "policies": {
    "continuityPolicy": {
      "target": "segment-continuity",
      "contentSceneLink": "cut-or-short-dissolve",
      "openingBoundary": "dip-to-black-4f",
      "endingBoundary": "dip-to-black-4f"
    },
    "audioPolicy": {
      "openingVoiceSource": "reuse-original-clip-audio",
      "endingVoiceSource": "reuse-original-clip-audio-or-approved-voice-pack",
      "contentVoiceSourcePriority": [
        "human-dub",
        "actor-dub",
        "cloned-dub",
        "tts-guide"
      ]
    },
    "textPolicy": {
      "generationStage": "no-text-in-video",
      "typographyStage": "post-picture-lock"
    }
  },
  "voiceSlots": [
    {
      "voiceSlotId": "opening-greeting",
      "kind": "reusable-line",
      "text": "안녕하세요. 대한이에요!",
      "preferredSource": "voice-pack"
    },
    {
      "voiceSlotId": "content-question-ko",
      "kind": "episode-line",
      "text": "따라해보세요."
    },
    {
      "voiceSlotId": "ending-bye",
      "kind": "reusable-line",
      "text": "안녕~!",
      "preferredSource": "voice-pack"
    }
  ],
  "scenes": [
    {
      "sceneId": "scene-0-opening",
      "role": "opening",
      "sourceMode": "reusable-clip"
    },
    {
      "sceneId": "scene-1-question",
      "role": "content",
      "sourceMode": "generated-shot-sequence"
    },
    {
      "sceneId": "scene-5-ending",
      "role": "ending",
      "sourceMode": "reusable-clip"
    }
  ]
}
```

## 7. 주요 필드 정의

### 7.1 식별자

- `formatVersion`: 포맷 호환성 기준
- `episodeSlug`: 회차 고유 식별자
- `seriesSlug`: 시리즈 단위 식별자
- `characterSlug`: 캐릭터 식별자

### 7.2 `reusableAssets`

에피소드가 직접 소유하지 않는 공용 자산 포인터다.

- 오프닝/엔딩 원본 영상
- 대표 캐릭터 이미지
- 캐릭터 바이블
- 프롬프트 세트

### 7.3 `policies`

후반 제작에서 반복 확인할 규칙을 선언한다.

- `continuityPolicy`: 씬 연결 규칙
- `audioPolicy`: 어떤 음원을 우선 사용할지
- `textPolicy`: 텍스트를 언제 넣는지

여기서 중요한 점은 `continuityPolicy`가 "첫 프레임 복제"를 의미하지 않는다는 것이다.
핵심은 "같은 수업처럼 보이는가"다.

### 7.4 `voiceSlots`

오디오를 장면이 아니라 대사 단위로 관리하기 위한 슬롯이다.

장점:

- 같은 대사를 여러 회차에서 재사용 가능
- 사람 녹음과 성우 녹음을 쉽게 교체 가능
- picture lock 이후에도 음성만 교체 가능

### 7.5 `scenes`

씬은 큰 편집 단위이고 실제 연속성 관리는 별도 `shots.schema.json`에서 한다.

즉:

- 에피소드 스키마: 운영 메타데이터
- 쇼트 스키마: 실제 화면 설계

## 8. v3에서 vNext로 달라지는 점

기존 `source-packet.json`은 생성기 중심 구조였다.
vNext는 여기에 후반 제작 계층을 추가한다.

주요 차이:

- 오프닝/엔딩을 독립된 재사용 자산으로 명시
- 컨텐츠 음성을 `voiceSlots`로 분리
- 텍스트를 생성 단계에서 제거
- 씬 사이 전환 규칙을 정책으로 선언
- 에피소드 상태를 명시적으로 운영

## 9. 대한 캐릭터 적용 기준

첫 번째 실험 대상은 `characters/daehan`으로 고정한다.

필수 기준:

- 대표 참조 이미지는 `characters/daehan/daehan.jpg`
- 캐릭터 규칙은 `characters/daehan/bible.md`
- 장면 프롬프트의 기본 규칙은 `characters/daehan/prompts.md`
- 오프닝과 엔딩은 가능하면 기존 클립 음성을 보존

## 10. 첫 프로토타입 범위

첫 vNext 프로토타입은 완성본보다 제작 구조 검증이 목적이다.

권장 범위:

- 오프닝 1개
- 컨텐츠 씬 4개 또는 5개
- 엔딩 1개
- 컨텐츠 음성은 사람이 넣거나 가이드 TTS로 대체 가능
- 타이포는 picture lock 후 별도 패스에서 합성

첫 프로토타입의 합격 기준은 아래다.

- 씬 간 연결이 튀지 않는다.
- 대한의 외형과 톤이 유지된다.
- 오프닝/엔딩이 매 회차 재사용 가능하다.
- 더빙과 자막만 교체해서 재출력이 가능하다.
