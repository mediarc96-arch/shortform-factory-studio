# Malmoelab vNext Shot Schema

날짜: 2026-04-17
대상 프로젝트: `shortform-factory-studio`
관련 문서: `2026-04-17-malmoelab-vnext-episode-schema.md`

## 1. 목적

이 문서는 `scene`보다 더 세밀한 연속성 단위인 `shot`의 설계 기준을 정의한다.

핵심 의도는 단순하다.

- 같은 교실에서 같은 선생님이 자연스럽게 이어지는 것처럼 보이게 만든다.
- 각 씬이 같은 동작의 반복처럼 보이지 않도록 행동 의도를 분리한다.
- 생성기에 넣을 프롬프트보다, 화면 설계와 연결 규칙을 먼저 고정한다.

이 문서의 기준도 `frame-perfect continuity`가 아니라 `segment continuity`다.

## 2. 장면 단위 구분

### 2.1 Scene

씬은 편집자가 이해하는 큰 의미 단위다.

예:

- `scene-0-opening`
- `scene-1-question`
- `scene-2-thinking`
- `scene-3-answer`
- `scene-4-repeat`
- `scene-5-ending`

### 2.2 Shot

쇼트는 실제 생성과 연결의 기본 단위다.

예:

- `shot-1a-entry-look`
- `shot-1b-board-point`
- `shot-3a-answer-reveal`

vNext에서는 씬을 만들기 전에 쇼트를 먼저 설계한다.

## 3. 필수 필드

모든 쇼트는 아래 필드를 가진다.

```json
{
  "shotId": "shot-1a-entry-look",
  "sceneId": "scene-1-question",
  "role": "question-entry",
  "durationTargetSec": 2.4,
  "previousShotId": "shot-0b-opening-exit",
  "entryFrameSource": "previous-shot-exit-frame",
  "exitFrameExport": "./renders/frames/shot-1a-exit.png",
  "characterRef": "characters/daehan/daehan.jpg",
  "camera": {
    "framing": "medium",
    "angle": "eye-level",
    "teacherPlacement": "right-third",
    "boardPlacement": "left-two-thirds",
    "motion": "static-or-micro-push"
  },
  "performance": {
    "poseIntent": "invite-attention",
    "handAction": "open-palm-toward-viewer",
    "eyeLine": "camera",
    "emotion": "bright-encouraging",
    "tempo": "calm"
  },
  "board": {
    "state": "clean",
    "interactionType": "gesture-only",
    "reservedTypographyArea": "left-center"
  },
  "transitionIn": "match-cut",
  "transitionOut": "match-cut",
  "voiceSlotIds": ["content-question-ko"],
  "textOverlayMode": "post-only",
  "generation": {
    "provider": "grok-or-runway",
    "promptPreset": "question-entry",
    "negativePromptPreset": "daehan-default-negative"
  },
  "qa": {
    "mustPreserve": [
      "silver-white-long-hair",
      "violet-eyes",
      "black-gat",
      "black-durumagi",
      "black-gloves"
    ],
    "watchFor": [
      "text-artifacts",
      "teacher-centered-frame",
      "repeated-hand-pose"
    ]
  }
}
```

## 4. 필드별 설명

### 4.1 식별과 연결

- `shotId`: 쇼트 고유 ID
- `sceneId`: 소속 씬
- `previousShotId`: 바로 앞 쇼트
- `entryFrameSource`: 시작 프레임 기준
- `exitFrameExport`: 다음 쇼트의 시작 참조로 남길 프레임

이 다섯 필드는 쇼트 체인을 설명하기 위한 것이지, 다음 쇼트가 첫 프레임까지 완전히 복제해야 한다는 뜻은 아니다.
`entryFrameSource`는 권장 레퍼런스다.

### 4.2 화면 설계

`camera`는 생성 프롬프트보다 먼저 고정하는 레이아웃 규칙이다.

필수 권장값:

- `teacherPlacement`: `right-third`
- `boardPlacement`: `left-two-thirds`
- `angle`: `eye-level`
- `framing`: `medium` 또는 `medium-wide`

대한 콘텐츠에서는 캐릭터가 중앙을 점유하지 않는 것이 기본이다.

### 4.3 연기 설계

`performance`는 매 씬의 행동이 왜 다른지 설명한다.

예:

- `question-entry`: 시청자를 바라보며 질문을 던짐
- `thinking-pause`: 손을 턱에 대거나 칠판을 보며 기다림
- `answer-reveal`: 칠판 쪽으로 몸을 틀고 정답을 제시
- `repeat-cue`: 발음을 따라 하도록 리듬감 있게 유도

같은 분필 들기 동작을 반복하지 말고, 역할별 행동 의도를 분리한다.

### 4.4 칠판 상태

`board`는 타이포그래피 작업을 위한 안전 영역을 고정한다.

- `state`: `clean`, `guide-mark`, `revealed`
- `interactionType`: `gesture-only`, `writing-mime`, `pointing`
- `reservedTypographyArea`: 실제 오버레이가 들어갈 칠판 영역

생성 단계에서는 글씨를 만들지 않고, "글씨를 쓰는 동작"만 허용한다.

### 4.5 음성 연결

`voiceSlotIds`는 쇼트와 오디오를 느슨하게 연결한다.

장점:

- 영상은 고정한 채 음성만 교체 가능
- 같은 쇼트에서 여러 버전의 대사 실험 가능
- 사람이 녹음한 파일과 외부 성우 파일을 교차 사용 가능

### 4.6 QA 선언

각 쇼트는 생성 전부터 실패 조건을 안고 있어야 한다.

예:

- 중앙 정렬된 선생님
- 반복되는 손 모양
- 캐릭터 복장 글자 아티팩트
- 칠판 반사 때문에 오버레이 영역이 죽는 문제

## 5. 씬별 권장 행동 매핑

같은 수업 장면이라도 씬마다 행동을 분리해야 한다.

### 5.1 `scene-1-question`

- 역할: 문제 제시
- 권장 행동: 카메라를 향해 질문, 손바닥으로 칠판 영역 소개
- 금지: 정답을 이미 알고 있는 듯한 가리키기 자세

### 5.2 `scene-2-thinking`

- 역할: 기다림
- 권장 행동: 턱에 손, 살짝 고개 기울임, 칠판을 보고 생각하는 리듬
- 금지: 질문 장면과 동일한 정면 포즈

### 5.3 `scene-3-answer`

- 역할: 정답 공개
- 권장 행동: 몸을 칠판 쪽으로 틀고 정답 위치를 명확히 가리킴
- 금지: 시청자만 바라보는 정지형 포즈

### 5.4 `scene-4-repeat`

- 역할: 따라 말하기 유도
- 권장 행동: 입 모양이 보이는 반정면, 박자감 있는 손짓
- 금지: `scene-3`와 같은 정답 공개 포즈

## 6. 전환 규칙

### 6.1 오프닝 → 컨텐츠

- 기본값: `dip-to-black-4f`
- 목적: 브랜드 인사와 학습 시작 사이의 경계 부여

### 6.2 컨텐츠 ↔ 컨텐츠

- 기본값: `cut` 또는 `짧은 dissolve`
- 필요 시만 `8f dissolve`
- 검정 페이즈보다 연속 동작 보존이 우선

### 6.3 컨텐츠 → 엔딩

- 기본값: `dip-to-black-4f`
- 목적: 학습 모드에서 CTA 모드로 전환

## 7. 예시 쇼트 시퀀스

아래는 `jeonyeok` 형식에 맞는 최소 쇼트 예시다.

```json
[
  {
    "shotId": "shot-1a-question-entry",
    "sceneId": "scene-1-question",
    "role": "question-entry",
    "durationTargetSec": 2.2,
    "entryFrameSource": "opening-exit-frame",
    "transitionIn": "dip-to-black-4f",
    "transitionOut": "match-cut"
  },
  {
    "shotId": "shot-2a-thinking-wait",
    "sceneId": "scene-2-thinking",
    "role": "thinking-wait",
    "durationTargetSec": 2.8,
    "entryFrameSource": "shot-1a-exit",
    "transitionIn": "match-cut",
    "transitionOut": "match-cut"
  },
  {
    "shotId": "shot-3a-answer-reveal",
    "sceneId": "scene-3-answer",
    "role": "answer-reveal",
    "durationTargetSec": 2.5,
    "entryFrameSource": "shot-2a-exit",
    "transitionIn": "match-cut",
    "transitionOut": "match-cut"
  },
  {
    "shotId": "shot-4a-repeat-cue",
    "sceneId": "scene-4-repeat",
    "role": "repeat-cue",
    "durationTargetSec": 4.0,
    "entryFrameSource": "shot-3a-exit",
    "transitionIn": "match-cut",
    "transitionOut": "dip-to-black-4f"
  }
]
```

## 8. 대한 캐릭터 전용 잠금 규칙

모든 쇼트는 아래 캐릭터 요소를 고정한다.

- 긴 은발
- 보라색 눈동자
- 검은 갓과 금 장식
- 검은 두루마기와 흰 속깃
- 검은 장갑
- 녹색 칠판 배경

그리고 아래 레이아웃을 기본 잠금값으로 둔다.

- 캐릭터 위치: 화면 오른쪽 1/3
- 칠판 위치: 화면 왼쪽 2/3
- 텍스트 영역: 칠판 중심부

## 9. 첫 프로토타입에서 검증할 항목

첫 vNext 실험에서는 완성도보다 구조를 검증한다.

반드시 확인할 것:

- 마지막 프레임에서 다음 쇼트로 자연스럽게 이어지는가
- 씬마다 행동이 명확히 다른가
- 칠판 오버레이 영역이 안정적으로 비어 있는가
- 대한의 얼굴, 의상, 모자가 유지되는가
- 반복 학습 구간에서 입 모양과 손짓이 지나치게 급하지 않은가
