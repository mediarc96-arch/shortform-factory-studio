# Malmoelab Korean Education — Agent Workflow

이 문서는 `malmoelab` 관련 한글 교육 콘텐츠를 Paperclip agent가 반복 생산할 때 따라야 할 기본 실행 순서를 정의한다.

핵심 원칙:

- `source first`
- `script second`
- `picture lock before dubbing`
- `typography last`
- `voice id per character`

## 이 템플릿이 담당하는 범위

- 말모이랩 예문 기반 한국어 교육 Shorts
- 오프닝/엔딩 재사용형 에피소드
- character-driven classroom format
- Korean line + romanization helper + CTA 후반 합성

## 표준 실행 단계

1. 에피소드 아이디어와 구성 확정
2. 말모이랩 source sentence 선택
3. `source-packet.json` 작성
4. `packet.md` 작성
5. `episode.schema.json` 작성
6. `voice-slots.json`에 대사 슬롯 작성
7. content line TTS 예상 길이 prepass
8. `video-generation-job.json` 작성
9. picture-only scene generation
10. picture lock 조립
11. guide dub 또는 uploaded dub 반영
12. dub lock 생성
13. `typography-slots.json` 작성
14. final typography 합성
15. review bundle 생성
16. publish packet 준비

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
- scene durations는 가능하면 content TTS 길이 기준으로 결정한다.
- 캐릭터 일관성과 칠판 clean surface를 우선한다.

### 4. dub

- 오프닝/엔딩 승인 음성이 있으면 재사용 우선
- content line은 guide TTS 또는 사람 더빙 사용
- 캐릭터 기본 voice id는 `characters/<slug>/voice.json`에서 읽는다

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

## 다른 콘텐츠에도 참고할 때

범용 흐름만 필요하면 `PROCESS_REFERENCE.md`를 본다.

`malmoelab` 전용 정보가 필요하면 이 문서와 아래 템플릿 JSON을 본다.
}
```

파일 경로: `data/used_sentences.jsonl`  
방식: 파일 맨 끝에 한 줄 append.

---

### ⚠️ 나레이션 오디오 순차 재생 규칙

**절대 규칙: 한국어와 영어 나레이션은 동시 재생 금지.**

- 한국어 남성이 먼저 말한다.
- 한국어가 **완전히 끝난 뒤** 0.3~0.5초 간격을 두고 영어 여성이 말한다.
- 로마자(Romanization)는 TTS로 읽지 않는다. 화면에 텍스트로만 표시한다.
- SFX(틱톡, 정답음)는 나레이션이 없는 구간에서만 재생한다.

---

## STEP 9 — Grok 씬 생성 실행

`video-generation-job.json` 의 `scenes` 배열을 순서대로 처리한다.

| sceneId | 방식 | 설명 |
|---------|------|------|
| `scene-0-opening` | 기존 클립 트림 | `1_Opening.mp4` 앞 3초 |
| `scene-1-question` | Grok 생성 | 문제 제시 화면 |
| `scene-2-thinking` | Grok 생성 | 알람시계 대기 |
| `scene-3-answer` | Grok 생성 | 정답 공개 |
| `scene-4-repeat` | Grok 생성 | 따라하기 |
| `scene-5-outro` | Grok 생성 | 마무리 |

각 씬 생성 결과는 `renders/grok/scene-{N}.mp4` 로 저장한다.

**캐릭터 일관성 유지 규칙:**  
씬 1~5 생성 시 `scene-0-opening` 에서 추출한 스틸 프레임을  
Grok의 `image` 파라미터(reference image)로 함께 전달한다.  
→ `renders/frames/opening-ref.png`

**구도 일관성 유지 규칙:**  
모든 씬의 프롬프트에 `COMPOSITION:` 블록을 포함해  
선생님 오른쪽 30~35%, 칠판 왼쪽 65~70% 구도를 유지한다.  
구도 레퍼런스: `docs/example/mBp3B.jpg`

**텍스트 후편집 규칙:**  
Grok은 깨끗한 칠판 영상만 생성한다.  
모든 한국어/영어/로마자 텍스트는 후편집 단계에서 칠판 영역에 합성한다.  
`postProduction.textCompositing.chalkboardZone` 좌표를 참고.

---

## STEP 10 — 씬 합성 + 오디오 믹싱

### 합성 순서

```
scene-0-opening (0~3s)
+ scene-1-question (3~6s)
+ scene-2-thinking (6~11s)
+ scene-3-answer (11~16s)
+ scene-4-repeat (16~28s)
+ scene-5-outro (28~30s)
= final/{{EPISODE_SLUG}}.mp4
```

### 오디오 트랙 레이어

```
[트랙 1] audio/narration-ko.mp3     볼륨 1.0
[트랙 2] audio/narration-en.mp3     볼륨 1.0
[트랙 3] shared/bgm-calm.mp3        볼륨 0.15  (전구간)
[트랙 4] shared/sfx-ticking.mp3     볼륨 0.8   (6~11s 구간)
[트랙 5] shared/sfx-correct.mp3     볼륨 0.8   (11s 시점)
```

SFX 파일 경로:
- `shared/sfx/ticking.mp3`
- `shared/sfx/correct.mp3`
- `shared/music/bgm-calm-classroom.mp3`

---

## STEP 11 — QA 검수

아래 항목을 모두 통과해야 `publish-ready` 로 표시한다.

- [ ] **선생님 위치**: 칠판 앞(IN FRONT OF)에 있는지 확인. 칠판 뒤가 아님.
- [ ] **나레이션 겹침 없음**: 한국어 끝 → 간격 → 영어 순차 재생 확인.
- [ ] **로마자 TTS 없음**: 로마자가 음성으로 읽히지 않는지 확인.
- [ ] **오프닝 자막 없음**: 01_Opening.mp4에 텍스트 오버레이가 없는지 확인.
- [ ] **엔딩 나레이션**: "그럼 다음시간에 또 만나요." 포함 확인.
- [ ] 총 길이 28~32초 범위 내
- [ ] **16:9 가로 형식인지 확인** (세로 9:16 아님)
- [ ] **구도**: 선생님 오른쪽 30~35%, 칠판 왼쪽 65~70% 확인
- [ ] **카메라**: 미디엄샷 (허리 위), 클로즈업 아님
- [ ] **칠판 깨끗**: Grok이 칠판에 텍스트를 생성하지 않았는지 확인
- [ ] 오프닝 클립 캐릭터와 씬 1~5 캐릭터 동일성 (갓, 장갑, 머리색, 눈색)
- [ ] 3D 애니메 스타일 일관 (1_Opening.mp4와 이질감 없는지)
- [ ] 빈칸 문장과 정답 문장 한국어 맞춤법 정확
- [ ] 로마자 표기 일관성
- [ ] 영어 번역 자연스러운지 확인
- [ ] 보기 ①②③ 배열 및 정답 위치 확인
- [ ] 나레이션 속도 (한국어 0.75×, 영어 0.85×)
- [ ] 모든 단어 2회씩 반복 확인
- [ ] CTA 말모이랩 URL 정확 (`malmoelab.com`)
- [ ] used_sentences.jsonl 에 `reserved` 상태로 기록됐는지 확인

---

## STEP 12 — publish-packet.json 작성

```json
{
  "episodeSlug": "{{EPISODE_SLUG}}",
  "title": "{{PUBLISH_TITLE_KO}}",
  "titleEn": "{{PUBLISH_TITLE_EN}}",
  "description": "{{YOUTUBE_DESCRIPTION}}",
  "tags": ["한국어", "Korean", "한글", "KoreanLesson", "MalmoeLab"],
  "ctaUrl": "https://malmoelab.com",
  "thumbnailFile": "./final/{{EPISODE_SLUG}}-thumb.png",
  "finalVideoFile": "./final/{{EPISODE_SLUG}}.mp4",
  "publishStatus": "ready",
  "renderedAt": "{{ISO8601_TIMESTAMP}}"
}
```

---

## 에피소드 폴더 최종 구조

```
episodes/{EPISODE_SLUG}/
├── packet.md                     ← STEP 7
├── source-packet.json            ← STEP 4
├── narration-script.md           ← STEP 5
├── video-generation-job.json     ← STEP 6
├── publish-packet.json           ← STEP 12
├── audio/
│   ├── narration-ko.mp3          ← STEP 5
│   └── narration-en.mp3          ← STEP 5
├── renders/
│   ├── frames/
│   │   └── opening-ref.png       ← STEP 9
│   └── grok/
│       ├── scene-1-question.mp4
│       ├── scene-2-thinking.mp4
│       ├── scene-3-answer.mp4
│       ├── scene-4-repeat.mp4
│       └── scene-5-outro.mp4
└── final/
    ├── {EPISODE_SLUG}.mp4        ← STEP 10
    └── {EPISODE_SLUG}-thumb.png
```
