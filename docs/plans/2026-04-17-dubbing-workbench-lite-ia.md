# Dubbing Workbench Lite IA

날짜: 2026-04-17
대상 프로젝트: `shortform-factory-studio`
관련 문서:

- `2026-04-17-malmoelab-vnext-dubbing-workbench.md`
- `2026-04-17-malmoelab-vnext-episode-schema.md`
- `2026-04-17-malmoelab-vnext-shot-schema.md`

## 1. 목적

`Dubbing Workbench Lite`는 영상 생성기 대체품이 아니다.
이 도구의 목적은 생성된 영상과 에피소드 폴더를 읽어 후반 제작을 빠르게 운영하는 것이다.

핵심 기능은 네 가지다.

- 회차별 상태를 동적으로 읽는다.
- 오프닝/엔딩/효과음/재사용 음성을 분리 관리한다.
- 사람이 직접 더빙하거나 외부 음성을 업로드한다.
- picture lock 이후 타이포그래피와 최종 믹스를 관리한다.

## 2. 문제 정의

현재 병목은 "좋은 프롬프트"보다 "후반 제작 구조 부재"에 가깝다.

반복되는 문제:

- 영상은 나왔는데 더빙 교체가 느리다.
- 오프닝/엔딩과 컨텐츠 음성이 한 덩어리로 취급된다.
- 고정 인사와 효과음을 매 회차 재활용하기 어렵다.
- 생성기 단계에서 자막까지 넣으려다 영상 품질이 떨어진다.
- 에피소드 폴더는 있지만 작업 상태가 한눈에 보이지 않는다.

## 3. 설계 원칙

### 3.1 File-System Native

도구는 별도 CMS보다 현재 `shortform-factory-studio` 폴더 구조를 우선 진실 원천으로 삼는다.

즉:

- `characters/*`는 재사용 자산 레지스트리
- `episodes/*`는 회차 작업 공간
- `shared/*`는 공통 오디오/브랜드 자산

### 3.2 Picture Lock First

도구는 "영상을 만드는 곳"보다 "잠긴 영상에 음성과 텍스트를 올리는 곳"에 가깝다.

### 3.3 Reusable Line Packs

반복 문구는 매번 새로 녹음하지 않고 승인된 `voice-pack`으로 관리한다.

예:

- "안녕하세요. 대한이에요!"
- "그럼 다음 시간에 또 만나요."
- "안녕~!"

### 3.4 Human-Friendly

성우나 편집자가 개발자가 아니어도 바로 사용할 수 있어야 한다.

필수 조건:

- 폴더를 직접 뒤지지 않아도 상태가 보인다.
- 영상과 파형이 같이 보인다.
- 재녹음 포인트가 명확하다.
- 어떤 대사가 재사용 가능하고 어떤 대사가 회차 전용인지 구분된다.

## 4. 정보 구조

### 4.1 전역 네비게이션

Lite 버전은 아래 5개 영역이면 충분하다.

1. `Episodes`
2. `Assets`
3. `Voice Packs`
4. `Typography`
5. `Review`

### 4.2 Episodes

역할:

- `episodes/malmoelab-*` 자동 스캔
- 회차 상태 표시
- picture lock, dub lock, type lock 여부 표시
- 마지막 수정 시각과 최종 출력물 링크 제공

목록에서 보여줄 최소 컬럼:

- episode slug
- character
- format version
- current status
- picture lock 여부
- dub lock 여부
- final output 여부

### 4.3 Episode Workspace

한 회차를 열면 아래 탭으로 나눈다.

1. `Overview`
2. `Media`
3. `Dubbing`
4. `Typography`
5. `QA`
6. `Export`

#### Overview

- 회차 기본 정보
- 캐릭터 참조 경로
- 재사용 자산 연결 상태
- 경고 항목

#### Media

- 오프닝, 컨텐츠, 엔딩 클립 타임라인
- 씬/쇼트 목록
- 마지막 프레임과 다음 쇼트 시작 프레임 비교

#### Dubbing

- `voiceSlot` 단위 목록
- 녹음 버튼
- 오디오 업로드 버튼
- 재사용 음성 선택
- 가이드 TTS 미리듣기

#### Typography

- 칠판 오버레이 텍스트 입력
- 폰트 스타일 프리셋
- 타이밍 오프셋 조정

#### QA

- contact sheet
- frame map
- 체크리스트
- 이슈 메모

#### Export

- 음성 믹스 실행
- 타이포 합성 실행
- 최종 MP4 출력
- 리뷰 번들 생성

## 5. 핵심 데이터 모델

Lite 버전은 거대한 DB보다 파일 기반 인덱스로 시작하는 것이 맞다.

### 5.1 Episode Index

도구가 에피소드를 읽을 때 필요한 최소 요약 정보다.

```json
{
  "episodeSlug": "malmoelab-ko-repeat-jeonyeok-vnext-001",
  "characterSlug": "daehan",
  "status": "dub-ready",
  "pictureLockPath": "episodes/.../renders/picture-lock/content-lock.mp4",
  "finalOutputPath": null,
  "voiceSlots": 7,
  "typographySlots": 4
}
```

### 5.2 Voice Slot

```json
{
  "voiceSlotId": "ending-bye",
  "kind": "reusable-line",
  "text": "안녕~!",
  "speaker": "daehan",
  "preferredSources": [
    "voice-pack",
    "human-dub",
    "actor-dub"
  ],
  "selectedAsset": "shared/voice-packs/daehan/ending-bye.wav"
}
```

### 5.3 Typography Slot

```json
{
  "slotId": "scene-3-answer-board-text",
  "sceneId": "scene-3-answer",
  "surface": "chalkboard",
  "text": "집",
  "stylePreset": "malmoelab-board-large",
  "inTimeSec": 12.3,
  "outTimeSec": 15.9
}
```

## 6. 주요 사용자 흐름

### 6.1 기존 에피소드 열기

1. `Episodes`에서 회차 선택
2. picture lock 존재 여부 확인
3. 연결된 캐릭터와 재사용 자산 확인
4. 부족한 음성 슬롯과 타이포 슬롯 확인

### 6.2 사람 직접 더빙

1. `Dubbing` 탭에서 voice slot 선택
2. 기준 영상 구간 반복 재생
3. 브라우저 녹음 또는 파일 업로드
4. 선택된 take 저장
5. 잠정 믹스 미리듣기

### 6.3 반복 문구 재사용

1. `Voice Packs`에서 캐릭터별 승인 라인 조회
2. `opening-greeting` 또는 `ending-bye` 같은 슬롯에 매핑
3. 회차 전용 파일 없이 바로 참조

### 6.4 타이포 적용

1. `Typography` 탭에서 칠판 텍스트 입력
2. 안전 영역 프리뷰 확인
3. 등장/퇴장 시점 조정
4. 오버레이 렌더

### 6.5 최종 출력

1. 선택된 음성 슬롯으로 오디오 믹스
2. 타이포 그래픽 합성
3. 최종 MP4 생성
4. 리뷰 번들 생성

## 7. 재사용 자산 운영 방식

### 7.1 캐릭터 레이어

`characters/daehan`은 캐릭터의 기준 폴더다.

우선 연결할 자산:

- `characters/daehan/daehan.jpg`
- `characters/daehan/bible.md`
- `characters/daehan/prompts.md`
- `characters/daehan/01_Opening.mp4`
- `characters/daehan/02_Ending.mp4`

### 7.2 공통 오디오 레이어

권장 신규 구조:

```text
shared/
  music/
  sfx/
  voice-packs/
    daehan/
      opening-greeting.wav
      ending-see-you.wav
      ending-bye.wav
```

이 구조가 있으면 오프닝과 엔딩은 회차별로 다시 녹음하지 않아도 된다.

### 7.3 회차 전용 오디오 레이어

회차별 문장과 단어는 `episodes/<slug>/audio/` 아래에서 관리한다.

예:

- 질문 대사
- 정답 공개 대사
- 따라 말하기 유도 대사

## 8. MVP 범위

Lite 버전에서 당장 필요한 것은 편집기 전체가 아니다.

필수:

- 에피소드 자동 스캔
- picture lock 미리보기
- voice slot 기반 녹음/업로드
- reusable voice-pack 매핑
- basic typography slot 편집
- final mix/export 실행

후순위:

- 다중 사용자 권한
- 정교한 타임라인 편집기
- 고급 파형 편집
- 클라우드 협업

## 9. 구현 제안

웹 서비스로 만든다면 우선 내부 툴 수준이면 충분하다.

권장 방향:

- UI: 간단한 웹 앱
- 데이터 원천: 로컬 파일 시스템
- 미디어 처리: 기존 렌더 스크립트와 ffmpeg 재사용
- 상태 파일: `episode.schema.json`, `shots.schema.json`, `voice-slots.json`, `typography-slots.json`

즉 새 서비스는 기존 파이프라인을 버리는 것이 아니라, `episodes/`를 다루는 운영 레이어가 된다.

## 10. 첫 검증 시나리오

첫 테스트는 `daehan`만 대상으로 한다.

시나리오:

1. `characters/daehan/01_Opening.mp4`를 오프닝 재사용 자산으로 연결
2. `characters/daehan/02_Ending.mp4`를 엔딩 재사용 자산으로 연결
3. 컨텐츠 영상만 새로 생성
4. 사람이 직접 컨텐츠 대사를 더빙하거나 임시 성우 파일을 업로드
5. `"안녕하세요. 대한이에요!"`, `"안녕~!"`는 reusable voice pack으로 재사용
6. picture lock 이후 칠판 타이포를 얹어 최종 출력

이 시나리오가 돌아가면, 이후 ElevenLabs나 Supertone 같은 외부 음성 API는 `voice source` 선택지로 추가하면 된다.
