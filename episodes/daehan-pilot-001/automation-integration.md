# Automation Integration — Shortform Factory

`daehan-pilot-001` 파일럿과 `pc.devscent.com` 상의 **Shortform Factory** 자동화 파이프라인을 연결하기 위한 설계 문서.

파일럿은 수동 실행이지만, 껍데기는 자동화 친화적으로 설계되어 향후 Paperclip 이슈 → Video Editor Agent → YouTube 업로드까지 end-to-end로 확장 가능해야 한다.

관련 문서:
- [pilot-spec.md](./pilot-spec.md)
- [../../docs/PAPERCLIP_ISSUE_OPERATIONS.md](../../docs/PAPERCLIP_ISSUE_OPERATIONS.md)
- [../../docs/YOUTUBE_CHANNEL_SETUP.md](../../docs/YOUTUBE_CHANNEL_SETUP.md)
- [../../docs/MALMOELAB_HANGUL_QUIZ_OPERATING_MODEL.md](../../docs/MALMOELAB_HANGUL_QUIZ_OPERATING_MODEL.md)
- [../malmoelab-template/AGENT_WORKFLOW.md](../malmoelab-template/AGENT_WORKFLOW.md)

## 1. 전체 파이프라인

```
[Paperclip 이슈 생성]
  작업 유형: new_episode
  Assignee: Head of Content
       │
       ▼
[Video Editor Agent 작업 착수]
  1. malmoelab DB 쿼리 → 미사용 예문 1개
  2. used_sentences.jsonl 'reserved' 기록
  3. episode 폴더 생성 + 산출물 자동 작성
     - source-packet.json
     - narration-script.md
     - video-generation-job.json
  4. TTS (Supertone 한국어만) → audio/*.mp3 — 영어는 자막 텍스트로만
  5. Grok 씬 파이프라인 (프레임 핸드오프 자동)
     - scene-N.mp4 + reference-frames/
  6. ffmpeg 합성 + 검정 페이드 (0.3s)
  7. MoviePy 후반 타이포그래피 합성
     - 칠판 한글 + 스트로크 리빌
     - 하단 영어 자막
  8. QA 자동 검수 (video-review 스킬)
  9. used_sentences.jsonl 'rendered' 업데이트
 10. publish-packet.json 작성
       │
       ▼
[Channel Publisher & Analyst 작업 인계]
 11. YouTube 업로드 (privacy=private, 기존 설정)
 12. 업로드 URL 이슈에 기록
       │
       ▼
[Paperclip 이슈 종료]
```

## 2. 역할 매핑 (기존 Paperclip 구조 준수)

| 역할 | 담당 범위 | 파일럿 단계 |
|------|---------|----------|
| **Head of Content** | 에피소드 기획·제작·QA 총괄 (기본값) | 파일럿 전 과정 |
| **Video Editor Agent** | CLI 호출·렌더·합성 실행 | 파일럿 `scripts/` 실행 |
| **Channel Publisher & Analyst** | YouTube 업로드·메타데이터 관리 | 파일럿 이후 단계 |
| **CEO** | 새 시리즈·전략 승인 | 파일럿에 관여 없음 |

## 3. 파일럿과 자동화의 관계

### 파일럿에 포함 (v0)
- CLI 진입점 설계
- 산출물 폴더 구조 (자동화와 동일한 컨벤션)
- 프레임 핸드오프 스크립트
- TTS 듀얼 래퍼
- MoviePy 타이포그래피 파이프라인
- 환경변수 기반 시크릿
- JSON 구조화 로그

### 파일럿에서 제외 (v1 이후)
- Paperclip 이슈 파서
- malmoelab DB 자동 쿼리
- `used_sentences.jsonl` 갱신 자동화
- `video-review` 스킬 연동
- YouTube 업로드 실행

단, **모든 제외 항목은 파일럿의 인터페이스에서 "수동 입력 → 자동 입력"으로만 바뀌면 되도록** 설계한다.

## 4. CLI 계약 (원자 단위)

Video Editor Agent가 호출할 명령은 반드시 CLI 한 줄로 완결되어야 한다.

### 4.1 예상 인터페이스

```bash
# 새 에피소드 전체 파이프라인
python -m shortform_factory.produce \
  --issue-id ISSUE-123 \
  --series malmoelab-ko-repeat \
  --character daehan \
  --example-id <EXAMPLE_ID>

# 재렌더 (같은 슬러그 유지)
python -m shortform_factory.produce \
  --episode-slug malmoelab-ko-repeat-pung-042 \
  --mode revise

# 업로드만
python -m shortform_factory.publish \
  --episode-slug malmoelab-ko-repeat-pung-042 \
  --privacy private
```

### 4.2 파일럿 단계의 CLI 진입점 (v0)

`shortform_factory` 패키지 이전에, 파일럿에서 미리 쪼개진 CLI를 만든다:

```bash
# 프레임 추출
python scripts/pilot/extract_last_frame.py \
  --input characters/daehan/01_Opening.mp4 \
  --output episodes/daehan-pilot-001/reference-frames/00-opening-last.png

# TTS 나레이션 생성
python scripts/tts/generate_narration.py \
  --script episodes/daehan-pilot-001/narration-script.md \
  --output-dir episodes/daehan-pilot-001/audio/

# 씬 파이프라인 (프레임 핸드오프 자동)
python scripts/pilot/run_scene_pipeline.py \
  --episode-dir episodes/daehan-pilot-001/

# MoviePy 후반 합성
python scripts/post/compose_final.py \
  --episode-dir episodes/daehan-pilot-001/

# 전체 파일럿 오케스트레이션
python scripts/pilot/run_all.py \
  --episode-dir episodes/daehan-pilot-001/
```

이들을 나중에 `shortform_factory.produce`가 감싸면 v1 완성.

### 4.3 CLI 요구사항

| 요구 | 설명 |
|------|------|
| **Idempotent** | 같은 입력 두 번 호출해도 안전 (기존 파일 존재 시 `--force` 플래그로만 재생성) |
| **Deterministic seed** | 재실행 시 같은 결과 (랜덤 시드 고정, 로그에 기록) |
| **Exit code** | 성공=0, 복구 가능한 실패=2, 치명적 실패=1 |
| **JSON 로그** | `stdout`은 사람용, `stderr` 또는 별도 파일에 구조화 JSON |
| **파일 기반 입력** | CLI 플래그는 경로 위주, 내용은 `*.json` / `*.md`에서 읽음 |
| **환경변수 시크릿** | API 키는 플래그로 받지 않음 |

### 4.4 에이전트가 해석할 JSON 로그 형식

```json
{
  "step": "scene-2-generate",
  "status": "ok",
  "durationSec": 42.1,
  "artifacts": {
    "video": "renders/scene-2.mp4",
    "lastFrame": "reference-frames/02-scene-last.png"
  },
  "warnings": [],
  "timestamp": "2026-04-17T10:22:11Z"
}
```

## 5. 후반 타이포그래피 — MoviePy

**결정**: MoviePy로 시작. 품질 한계 오면 Remotion 이식.

### 5.1 MoviePy가 처리할 것

| 요소 | 구현 방식 |
|------|---------|
| 칠판 한글 문장 | `TextClip` + `CompositeVideoClip` |
| 스트로크 리빌 | 글자 단위 `TextClip` + `set_start` 타이밍 어긋나기 |
| 빈칸 하이라이트 | 네모 박스 오버레이 + 깜빡임 |
| 보기 ①②③ | 순차 페이드인 |
| 정답 공개 효과 | 확대·컬러 전환 |
| 하단 영어 자막 | `TextClip` 하단 정렬 |

### 5.2 타이포그래피 스펙 파일

각 에피소드는 `post/chalkboard-text-spec.json`을 가진다:

```json
{
  "chalkboardZone": { "x": 120, "y": 80, "w": 1200, "h": 600 },
  "subtitleZone":   { "x": 60,  "y": 940, "w": 1800, "h": 120 },
  "sentences": [
    {
      "sceneId": "scene-3",
      "startSec": 13.5,
      "text": "풍선을 너무 크게 불었더니 결국 ___ 터져 버렸다",
      "blankToken": "___",
      "font": "NanumGothic-Bold",
      "fontSize": 64,
      "color": "white",
      "strokeRevealSec": 0.12
    }
  ],
  "choices": [
    { "label": "①", "text": "꽝", "sceneId": "scene-3", "startSec": 15.0 },
    { "label": "②", "text": "빵", "sceneId": "scene-3", "startSec": 15.3 },
    { "label": "③", "text": "쿵", "sceneId": "scene-3", "startSec": 15.6 }
  ],
  "reveal": {
    "sceneId": "scene-4",
    "startSec": 22.0,
    "correctLabel": "②",
    "correctText": "빵"
  },
  "subtitles": [
    { "startSec": 0, "endSec": 3, "textEn": "Hello, I'm Daehan!" }
  ]
}
```

이 스펙을 `compose_final.py`가 읽어 자동 합성.

### 5.3 폰트 자산

`shared/fonts/` 에 한글 폰트 배치:
- `NanumGothic-Bold.ttf` (문제 문장)
- `NanumPenScript.ttf` (정답 공개 감정 연출)
- 서브타이틀용 라틴 폰트 1~2종

## 6. 자동화 단계 로드맵

| 단계 | 목표 | 산출물 |
|------|------|--------|
| **v0** | 파일럿 1편 수동 완성 | `daehan-pilot-001/final/*.mp4` |
| **v1** | 범용 템플릿화 | `episodes/_template-v2-seamless/` |
| **v2** | CLI 패키지 통합 | `shortform_factory/` 파이썬 패키지 |
| **v3** | malmoelab DB 쿼리 자동화 | SQL + `used_sentences.jsonl` 자동 갱신 |
| **v4** | QA 자동 검수 | `video-review` 스킬 연동 |
| **v5** | YouTube 자동 업로드 | `Channel Publisher & Analyst` 통합 |
| **v6** | Paperclip 이슈 end-to-end | 이슈 생성 → 완결 자동 |

각 단계는 이전 단계를 건드리지 않고 **감싸는 방식**으로 확장 (Open-Closed).

## 7. 시크릿·환경변수 (통합)

`.env.example`:

```bash
# AI 영상 생성
GROK_API_KEY=
GROK_MODEL=grok-video-latest

# TTS
SUPERTONE_API_KEY=
SUPERTONE_VOICE_ID_DAEHAN=         # 클론된 대한 목소리
ELEVENLABS_API_KEY=
ELEVENLABS_VOICE_ID_EN_FEMALE=

# malmoelab DB
MALMOELAB_DATABASE_URL=            # read-only

# YouTube (기존)
YOUTUBE_CHANNEL_ID=
YOUTUBE_OAUTH_CLIENT_ID=
YOUTUBE_OAUTH_CLIENT_SECRET=
YOUTUBE_OAUTH_REFRESH_TOKEN=
YOUTUBE_DEFAULT_PRIVACY_STATUS=private
YOUTUBE_DEFAULT_CATEGORY_ID=22
YOUTUBE_DISCLOSURE_TEXT=AI로 만들어진 영상입니다.
YOUTUBE_NOTIFY_SUBSCRIBERS=false

# Paperclip (v6)
PAPERCLIP_BASE_URL=https://pc.devscent.com
PAPERCLIP_API_TOKEN=
```

## 8. YouTube 업로드 정책

**결정**: 업로드는 **항상 `private`** 로 진행 (기존 `YOUTUBE_DEFAULT_PRIVACY_STATUS=private` 설정 유지).

- 에이전트가 자율 업로드해도 공개 전에 인간 검수 단계 확보
- 공개 전환은 별도 `metadata_update` 이슈로 처리 (`PAPERCLIP_ISSUE_OPERATIONS.md` §작업유형)
- 파일럿 1차 결과도 동일 정책 (업로드는 파일럿 이후 단계)

## 9. 결정 완료 요약

| 항목 | 결정 |
|------|------|
| 후반 타이포그래피 도구 | **MoviePy** (Remotion 이식은 추후) |
| CLI 진입점 | 파일럿부터 미리 심어둠 |
| YouTube 업로드 privacy | **private** (자동화 전 단계부터 기본값) |
| 자동화 확장 전략 | v0→v6 단계별 감싸기 (Open-Closed) |
| 시크릿 관리 | 환경변수 전용, 플래그로 전달 금지 |
| 로그 포맷 | JSON 구조화 + stdout 사람용 분리 |

## 10. 파일럿 폴더에 추가될 보조 문서

```
episodes/daehan-pilot-001/
├── pilot-spec.md                    # 파일럿 전체 스펙
├── automation-integration.md        # 이 문서
├── scene-plan.md                    # 씬 스토리보드 (다음 작성)
├── source-packet.json
├── narration-script.md
├── video-generation-job.json
└── post/
    └── chalkboard-text-spec.json    # MoviePy 합성용 (§5.2)
```
