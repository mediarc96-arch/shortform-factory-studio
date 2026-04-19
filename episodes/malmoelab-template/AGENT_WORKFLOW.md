# Malmoelab Korean Education — Agent Workflow

이 문서는 `malmoelab` 한글 교육 콘텐츠를 Paperclip agent가 반복 생산할 때 따라야 할 기본 실행 순서를 정의한다.

핵심 기준은 `episodes/daehan-pilot-codex-003`이다.

핵심 원칙:

- `source first`
- `script second`
- `keyframe review before video`
- `picture lock before dubbing`
- `typography last`
- `voice id per character`
- `render and post are separate issues`

## 이 템플릿이 담당하는 범위

- 말모이랩 예문 기반 한국어 교육 Shorts
- `003` 구조의 5-scene lesson형 에피소드
- character-driven classroom format
- Korean line + romanization helper + CTA 후반 합성

## 표준 실행 단계

1. 에피소드 아이디어와 구성 확정
2. 말모이랩 source sentence 선택
3. `source-packet.json` 작성
4. `packet.md` 작성
5. `episode.schema.json` 작성
6. `keyframe-plan.json` 작성
7. `narration-script.md` 작성
8. `voice-slots.json` 작성
9. `typography-slots.json` 초안 작성
10. `video-generation-job.json` 작성
11. keyframe generation
12. keyframe review bundle 생성
13. picture-only scene generation
14. picture preview / picture lock 조립
15. guide dub 또는 uploaded dub 반영
16. dub lock 생성
17. final typography 합성
18. review bundle 생성
19. publish packet 준비

## Paperclip 표준 child issue 체인

`malmoelab` 교육 에피소드는 아래 child issue 순서를 기본으로 사용한다.

1. `[SOURCE]`
   - assignee: `Sentence Source Operator`
   - 산출물: `source-packet.json`
2. `[BRIEF]`
   - assignee: `Content Strategist`
   - 산출물: `packet.md`, `episode.schema.json`, `keyframe-plan.json`
3. `[SCRIPT]`
   - assignee: `Script Writer`
   - 산출물: `narration-script.md`, `voice-slots.json`, `typography-slots.json`
4. `[EDIT]`
   - assignee: `Video Editor`
   - 산출물: `video-generation-job.json`
   - 역할: render handoff packet까지 준비
5. `[RENDER]`
   - assignee: `Video Generation Worker`
   - 산출물: `keyframes/*.jpg`, `keyframes/*.manifest.json`, `assets/refs/scene-*-last-frame.jpg`, `renders/picture/*.mp4`, `renders/grok/*.manifest.json`
   - 역할: `video-generation-job.json`을 실행해 keyframe과 picture assets 생성
6. `[POST]`
   - assignee: `Video Editor`
   - 산출물: picture lock, dub lock, final export, review bundle
   - 역할: 더빙, 타이포그래피, final assembly
7. `[QA]`
   - assignee: `Quality & Fact Checker`
   - 산출물: 최종 검수 comment, 필요 시 수정 요청
8. `[PUBLISH]`
   - assignee: `Channel Publisher & Analyst`
   - 산출물: publish packet, private upload, analytics kickoff

## issue별 완료 기준

### `[EDIT]`

- `video-generation-job.json`이 존재한다.
- JSON 문법 검증을 통과한다.
- `003`의 5-scene 구조가 유지된다.
- scene duration, continuity, render provider가 명시된다.
- `scene-1-opening-handoff`부터 `scene-5-ending-wave`까지 모두 정의된다.
- 다음 `[RENDER]` issue가 이어질 수 있도록 handoff comment를 남긴다.
- 사람이 직접 점검할 때도 `scene-1 greeting -> scene-2 full sentence intro -> scene-3 repeat -> scene-4 blank quiz -> scene-5 ending` 순서를 벗어나면 완료로 넘기지 않는다.

### `[RENDER]`

- 승인 가능한 `keyframes/*.jpg`가 존재한다.
- scene handoff frame이 존재한다.
- `renders/picture/*.mp4`가 모두 생성된다.
- `renders/grok/*.manifest.json`이 `succeeded` 상태다.
- render 실패 시 provider 에러와 manifest path를 그대로 남긴다.

### `[POST]`

- picture lock이 조립된다.
- `voice-slots.json` 기준 guide dub 또는 human dub가 반영된다.
- `typography-slots.json` 기준 한글/로마자/빈칸/CTA가 합성된다.
- final export와 review bundle이 생성된다.
- typography 수정만으로 TTS가 바뀌지 않도록 기존 오디오 재사용 정책을 지킨다.
- 기본 lesson형 포맷에서는 blank sentence가 `scene-4`에서 시작해 `scene-5` 엔딩까지 칠판에 유지된다.
- 사람이 직접 Paperclip에서 진행할 때도 final review bundle 기준으로 `scene-2/3 = full sentence`, `scene-4 = blank sentence`, `scene-5 = ending CTA`를 다시 확인한다.

## 양산을 위한 고정 규칙

### 1. source

- source-of-truth는 말모이랩 DB sentence다.
- focus word, sentence, translation, romanization, source id를 packet에 항상 남긴다.
- 같은 문장 중복 사용 정책은 series ledger에서 관리한다.

### 2. script

- spoken line과 screen text를 같은 단계에서 섞지 않는다.
- 대본은 `voice-slots.json` 기준으로 관리한다.
- 한글 예문과 로마자는 타이포 단계에서 넣는다.

### 3. picture

- generated video에는 글자를 넣지 않는다.
- 기본 scene 구조는 `003`의 5개 6초 씬이다.
- 캐릭터 일관성과 칠판 clean surface를 우선한다.
- 기본 비율은 `16:9`다. 세로 `9:16`은 실험 이슈에서만 명시적으로 허용한다.
- 기본 구도는 `teacher on right quarter`, `board on left three-quarters`다.
- picture generation이 끝나기 전에는 TTS 타이밍을 잠그지 않는다.
- keyframe review를 통과하기 전에는 scene video 생성으로 넘어가지 않는다.

### 4. dub

- 오프닝/엔딩 승인 음성이 있으면 재사용 우선
- content line은 guide TTS 또는 사람 더빙 사용
- 캐릭터 기본 voice id는 `characters/<slug>/voice.json`에서 읽는다
- typography 수정만 하는 경우 기존 guide audio를 재사용한다

### 5. typography

- 칠판 예문
- 로마자 발음 도움말
- 빈칸 문장
- CTA

이 네 가지는 모두 후반 합성에서 넣는다.

## 캐릭터 음성 정책

- 각 캐릭터는 `characters/<slug>/voice.json`을 가진다.
- 회차 `voice-slots.json`은 기본적으로 그 설정을 상속한다.
- 특정 회차에서만 다른 voice를 써야 할 때만 `ttsVoiceEnv` override를 허용한다.

## Paperclip agent 지시용 해석

Paperclip agent는 `malmoelab` 교육 에피소드를 만들 때 이 폴더를 source of process로 본다.

즉, 다음을 의미한다.

- episode tree를 만들 때 여기 있는 템플릿을 복사해서 시작
- `구성 -> 대본 -> 영상 -> TTS -> 한글 타이포그래피` 순서를 유지
- 그림 생성 단계에서 한글을 직접 생성하지 않음
- voice id를 캐릭터별로 해석
- `EDIT`에서 끝내지 않고 `RENDER -> POST -> QA -> PUBLISH`까지 child issue를 이어서 만든다

## 다른 콘텐츠에도 참고할 때

범용 흐름만 필요하면 `PROCESS_REFERENCE.md`를 본다.

`malmoelab` 전용 정보가 필요하면 이 문서와 아래 템플릿 JSON을 본다.
