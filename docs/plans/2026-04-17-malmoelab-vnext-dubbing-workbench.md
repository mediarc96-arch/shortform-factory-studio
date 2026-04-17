# Malmoelab vNext 포맷 및 Dubbing Workbench 제안

날짜: 2026-04-17
대상 프로젝트: `shortform-factory-studio`
범위: `characters/daehan`, `episodes/malmoelab-*`, 차기 `jeonyeok` 포맷 개선

## 0. 세부 설계 문서

- `2026-04-17-malmoelab-vnext-episode-schema.md`
- `2026-04-17-malmoelab-vnext-shot-schema.md`
- `2026-04-17-dubbing-workbench-lite-ia.md`

## 1. 배경

현재 `malmoelab-ko-repeat-jeonyeok-*` 계열은 아래 문제가 반복되고 있다.

- 씬 단위로 영상을 생성한 뒤 이어 붙이기 때문에 장면 연결감이 약하다.
- 오프닝, 컨텐츠, 엔딩이 하나의 자연스러운 쇼츠라기보다 조각난 블록처럼 느껴진다.
- 칠판 텍스트와 타이포그래피 요구가 생성 단계에 너무 일찍 들어가서 영상 자체의 자연스러움을 해친다.
- 대한의 기존 오프닝/엔딩 음성 톤을 유지하고 싶은데, 최근 빌드는 TTS 쪽으로 기울어 있다.
- 매 회차마다 바뀌는 컨텐츠 자산과 반복 재사용 가능한 자산이 명확히 분리되어 있지 않다.
- 결국 "영상 생성"과 "더빙/타이포/후반 편집"이 섞여 있어 수정 비용이 커진다.

핵심은 영상 제작 파이프라인을 더 자유롭게 만드는 것이다.

지금 필요한 것은 "더 좋은 프롬프트 몇 줄"이 아니라, 제작 구조 자체를 바꾸는 일이다.

## 2. 결론 먼저

권장 방향은 다음 두 가지를 같이 가져가는 것이다.

1. `vNext 포맷 설계안`을 새로 정의한다.
2. 그 포맷을 운영하는 내부용 `Dubbing Workbench`를 만든다.

여기서 `vNext 포맷 설계안`은 단순한 새 템플릿이 아니다.
이것은 `malmoelab` 쇼츠를 어떤 단계와 규칙으로 만들지 정의하는 "새 제작 표준"이다.

권장 우선순위:

- 1순위: `picture-first`, `text-later` 구조로 바꾸기
- 2순위: 오프닝/엔딩 음성과 재사용 자산을 별도 관리하기
- 3순위: 사람이 더빙하거나 성우가 녹음할 수 있는 워크벤치를 만들기
- 4순위: 필요 시 ElevenLabs, Supertone 같은 외부 음성 API를 연결하기

## 3. 왜 Dubbing Workbench가 필요한가

현재 병목은 단순 생성 품질이 아니다.
실제 병목은 "좋은 영상이 나와도, 그 뒤의 음성/타이포/재활용 작업이 비효율적"이라는 점이다.

내부용 웹 툴을 만들면 아래가 가능해진다.

- `episodes/malmoelab-*` 폴더를 동적으로 읽어 회차별 상태를 보여준다.
- `characters/daehan`의 캐릭터 자산을 공용 레퍼런스로 사용한다.
- 오프닝/엔딩/효과음/브랜드 타이포를 재사용 자산으로 분리한다.
- 컨텐츠 씬은 회차별 자산으로 따로 관리한다.
- 생성된 무음 또는 가이드 음성 버전 영상을 불러와 장면별로 더빙할 수 있다.
- 사람이 녹음한 파일, 성우 파일, 음성 클론 파일, TTS fallback을 같은 구조로 관리할 수 있다.
- `picture lock` 이후 타이포그래피를 올릴 수 있다.
- 재렌더 없이 음성만 교체하거나, 타이포만 교체할 수 있다.

즉 이 툴은 "영상 생성기"라기보다 "후반 중심 제작 콘솔"에 가깝다.

## 4. 추천 제품 방향

### 추천안: 내부용 Dubbing Workbench

이 방향이 가장 현실적이다.

- 목표는 편집자 1명 또는 소규모 팀이 빠르게 회차를 관리하는 것이다.
- 브라우저에서 회차를 열고, 영상 상태와 자산 상태를 보고, 더빙을 넣고, 최종 출력까지 관리한다.
- Daehan 같은 반복 캐릭터의 재사용 가치가 크다.

### 비추천안: 처음부터 풀 영상 제작 SaaS

이건 너무 크다.

- 생성기
- 에셋 매니저
- 타임라인 편집기
- 더빙 스튜디오
- 타이포 엔진
- QA 툴

이걸 한 번에 만들면 오래 걸리고, 현재 병목을 빨리 해결하지 못한다.

처음에는 "내부용 더빙/자산/출력 관리"가 맞다.

## 5. vNext 포맷 설계안이란 무엇인가

`vNext 포맷 설계안`은 다음을 문서와 데이터 구조로 정의하는 것이다.

- 어떤 자산이 공용 자산인지
- 어떤 자산이 회차별 자산인지
- 어떤 단계에서 영상을 생성하는지
- 어떤 단계에서 음성을 넣는지
- 어떤 단계에서 텍스트를 올리는지
- 어떤 장면 연결 규칙을 쓰는지
- 어떤 출력 산출물을 남기는지

즉 "하나의 에피소드 폴더를 어떤 상태 머신으로 운영할지"를 정하는 작업이다.

## 6. vNext의 핵심 원칙

### 6.1 Picture First

영상 생성 단계에서는 한글, 영문, 로마자를 넣지 않는다.

- 생성 단계 목표: 캐릭터, 구도, 동작, 장면 연결
- 후반 단계 목표: 더빙, 타이포그래피, 효과음, 브랜딩

이 원칙을 지키면 텍스트 아티팩트와 칠판 오염이 줄어든다.

### 6.2 Continuity First

씬은 독립 이미지가 아니라 연속된 숏으로 다뤄야 한다.

- `scene-1` 마지막 프레임을 `scene-2`의 시작 기준 프레임으로 사용
- `scene-2` 마지막 상태를 `scene-3`의 시작 자세 기준으로 사용
- 같은 카메라 높이, 같은 광원, 같은 칠판 위치를 유지

씬 간의 연결 규칙이 없으면 아무리 개별 컷이 좋아도 붙였을 때 어색하다.

### 6.3 Reusable Assets vs Episode Assets

반복 자산과 회차별 자산을 나눠야 한다.

재사용 자산 예:

- `characters/daehan/01_Opening.mp4`
- `characters/daehan/02_Ending.mp4`
- `characters/daehan/daehan.jpg`
- `characters/daehan/bible.md`
- 공용 효과음
- 공용 BGM
- 브랜드 타이포 스타일
- 공용 CTA

회차별 자산 예:

- 씬 프롬프트
- 컨텐츠 영상 클립
- 회차별 더빙
- 회차별 타이포 문안
- review bundle

### 6.4 Human-in-the-loop Voice

대한의 톤을 유지하려면 음성은 사람이 개입할 수 있어야 한다.

우선순위는 아래를 권장한다.

1. 원본 오프닝/엔딩 음성 사용
2. 사람 직접 더빙
3. 외부 성우 파일 업로드
4. 음성 클론 API
5. TTS fallback

## 7. 오디오 전략

### 7.1 오프닝/엔딩

오프닝과 엔딩은 가능하면 원본 음성을 그대로 유지한다.

- 오프닝: `characters/daehan/01_Opening.mp4`
- 엔딩: `characters/daehan/02_Ending.mp4`

이 두 자산은 "반복 브랜드 신호" 역할을 한다.
영상뿐 아니라 목소리도 브랜드다.

### 7.2 컨텐츠 더빙

컨텐츠 구간은 별도 voice stem으로 관리한다.

권장 파일 구조:

```text
episodes/<episode-slug>/
  audio/
    guide/
    human-dub/
    actor-dub/
    cloned-dub/
    mix/
```

### 7.3 효과음과 재사용 음성

효과음도 회차별 복사가 아니라 레지스트리형 재사용이 좋다.

예:

```text
shared/sfx/
shared/music/
shared/voice-packs/
```

반복 문구도 재사용이 가능하다.

- "안녕하세요. 대한이에요!"
- "그럼 다음 시간에 또 만나요."
- "안녕~!"

이런 문구는 승인된 오디오를 `voice-pack`으로 저장해 재사용하는 게 낫다.

## 8. 영상 전환 전략

### 8.1 오프닝 → 컨텐츠

짧은 `dip to black` 권장.

- 4~6 프레임
- 완전한 영화식 페이드가 아니라 가벼운 숨 고르기 용도

### 8.2 컨텐츠 씬 ↔ 컨텐츠 씬

여기는 검정 전환보다 `match cut`이 우선이다.

- 이전 씬의 마지막 자세
- 다음 씬의 첫 자세
- 칠판 위치
- 시선 방향
- 광원

이게 맞지 않으면 검정 전환을 넣어도 부자연스럽다.

### 8.3 컨텐츠 → 엔딩

여기도 짧은 `dip to black` 권장.

이유:

- 정보 전달 구간과 CTA 구간의 성격이 다르다
- 가벼운 경계가 있어야 엔딩이 살아난다

## 9. Dubbing Workbench 기능 제안

### 9.1 Episode Browser

- `episodes/malmoelab-*` 자동 로드
- 회차 상태 표시
- 프롬프트/클립/더빙/타이포/최종본 상태 표시

### 9.2 Asset Resolver

- `characters/<character-slug>` 자동 참조
- Daehan이면 `characters/daehan`에서 이미지, bible, prompts, opening, ending을 가져옴

### 9.3 Scene Viewer

- 씬별 preview
- 마지막 프레임과 다음 씬 첫 프레임 비교
- continuity check panel

### 9.4 Dubbing Recorder / Uploader

- 브라우저 녹음
- wav/mp3 업로드
- take 관리
- 승인 take 지정

### 9.5 Voice Slot System

씬 또는 구간마다 음원 소스를 지정한다.

- `embedded-original`
- `human-recorded`
- `actor-uploaded`
- `voice-clone`
- `tts-fallback`

### 9.6 Typography Pass

영상 완성 후에만 적용한다.

- 칠판 텍스트
- 자막
- CTA
- 단어 카드

### 9.7 Exporter

기존 `episodes/` 폴더 구조로 다시 기록한다.

- `source-packet.json`
- `video-generation-job.json`
- `audio/`
- `review/`
- `final/`

## 10. 권장 폴더 구조

### 10.1 캐릭터 자산

기존 구조를 유지하되 역할을 명확히 한다.

```text
characters/daehan/
  daehan.jpg
  Daehan_KoreanTeacher_3D.jpg
  bible.md
  prompts.md
  01_Opening.mp4
  02_Ending.mp4
```

### 10.2 회차 자산

```text
episodes/<episode-slug>/
  packet.md
  source-packet.json
  video-generation-job.json
  scene-jobs/
  renders/
    generated/
    narration/
    sfx/
  audio/
    guide/
    human-dub/
    actor-dub/
    cloned-dub/
    approved/
    mix/
  typography/
    captions.json
    board-copy.json
  review/
  final/
```

### 10.3 재사용 음성/효과음

```text
shared/
  sfx/
  music/
  voice-packs/
    daehan/
      opening/
      ending/
      reusable-lines/
```

## 11. 첫 프로토타입 범위

처음부터 모든 걸 만들 필요는 없다.

첫 프로토타입은 아래만 목표로 한다.

- 입력 캐릭터는 `daehan` 하나만 사용
- 입력 회차는 `malmoelab-ko-repeat-jeonyeok-001` 계열만 대상으로 삼음
- 생성 단계에서는 텍스트를 완전히 배제
- 컨텐츠 씬 5개를 연속성 중심으로 설계
- 오프닝/엔딩은 원본 음성 우선
- 더빙은 업로드 우선, 브라우저 녹음은 2단계

## 12. 첫 번째 구현 추천 순서

### Phase 1. vNext 문서화

- 새 포맷 규칙 정의
- 자산 구분 규칙 정의
- 장면 연결 규칙 정의

### Phase 2. Picture-only Prototype

- Daehan 자산만 사용
- 텍스트 없는 컨텐츠 숏 제작
- opening / content / ending 전환 규칙 시험

### Phase 3. Dubbing Workbench Lite

- 회차 로더
- 씬 프리뷰
- 음성 업로드
- 승인 take 관리

### Phase 4. Typography Pass

- 칠판 텍스트
- CTA
- 캡션

### Phase 5. Voice API Integration

- ElevenLabs
- Supertone
- 승인된 목소리 프로필 저장

## 13. 추천 결정

지금 당장 가장 좋은 다음 선택은 이것이다.

`vNext 포맷 설계` + `Dubbing Workbench Lite`를 같이 잡는다.

이유:

- 현재 가장 큰 병목은 생성 모델 자체보다 후반 통제력 부족이다.
- Daehan 같은 반복 캐릭터는 재사용 자산 분리가 매우 잘 먹힌다.
- 오프닝/엔딩 원본 음성 재사용 가치가 크다.
- 텍스트를 후반으로 미루면 영상 자연스러움이 올라간다.
- 더빙 툴이 생기면 TTS에 덜 종속된다.

## 14. 열린 결정사항

아래는 다음 설계 단계에서 결정해야 한다.

- `vNext` 기본 비율을 16:9로 시작할지, 9:16으로 바로 갈지
- 더빙 입력을 브라우저 녹음부터 할지, 파일 업로드부터 할지
- 음성 클론 API를 초기에 붙일지, 사람이 직접 녹음하는 운영부터 시작할지
- review bundle과 dubbing workbench를 같은 UI에서 볼지, 분리할지

## 15. 바로 다음 액션

코드 변경 전 기준 다음 액션을 권장한다.

1. `malmoelab-ko-repeat-jeonyeok-vnext-001` 프로토타입 범위를 확정한다.
2. `daehan` 자산만 사용하는 `picture-only` shot list를 만든다.
3. Dubbing Workbench Lite의 최소 화면 3개를 정의한다.
4. 오프닝/엔딩 원본 음성을 어떤 방식으로 stem화할지 정한다.
5. 그 다음에 구현에 들어간다.

이 문서는 방향 문서다.
다음 단계에서는 이 문서를 바탕으로 실제 `shot schema`, `episode schema`, `workbench IA`를 더 세밀하게 정의해야 한다.
