# Malmoelab Hangul Repeat — Agent Workflow

이 문서는 `malmoelab-hangul-repeat` 포맷의 영상을 반복 생산할 때  
Paperclip agent가 따라야 할 **전체 실행 순서**를 정의한다.

관련 도큐멘트:
- [MALMOELAB_HANGUL_QUIZ_OPERATING_MODEL.md](../docs/MALMOELAB_HANGUL_QUIZ_OPERATING_MODEL.md)
- [REFERENCE_SHORTFORM_WORKFLOW.md](../docs/REFERENCE_SHORTFORM_WORKFLOW.md)

---

## 포맷 개요

| 항목 | 값 |
|------|-----|
| 시리즈 슬러그 | `malmoelab-hangul-repeat` |
| 포맷 유형 | `fill_blank_repeat` |
| 총 길이 | 30초 |
| 비율 | **16:9 (1920×1080)** |
| 오프닝 소스 | `D:\Work\2025_DevScent\600_Marketing\ShortformFactory\1_Opening.mp4` |
| 영상 생성 도구 | **Grok** (씬별 생성 후 합성) |
| 나레이션 | 한국 남성 TTS (느림) + 영어 여성 TTS |
| 오프닝 | 고정 클립 (`characters/daehan/01_Opening.mp4`), 자막 없음 |
| 엔딩 | 고정 클립 (마무리 인사 "그럼 다음시간에 또 만나요.") |
| 총 길이 | 40~45초 (오프닝 5~7 + 본편 25~27 + 엔딩 3~5) |

기존 15초 퀴즈 포맷(`malmoelab-hangul-quiz`)과 별개의 시리즈다.  
문장은 중복 사용 금지. 단어(choices)는 재사용 허용.

---

## 전체 실행 단계

```
STEP 1  → 에피소드 슬러그 생성
STEP 2  → 말모이랩 DB에서 예문 선택
STEP 3  → 보기 단어(choices) 선택
STEP 4  → source-packet.json 작성
STEP 5  → narration-script.md 작성
STEP 6  → video-generation-job.json 작성
STEP 7  → packet.md 작성
STEP 8  → used_sentences.jsonl 업데이트
STEP 9  → Grok 씬 생성 실행
STEP 10 → 씬 합성 + 오디오 믹싱
STEP 11 → QA 검수
STEP 12 → publish-packet.json 작성
```

---

## STEP 1 — 에피소드 슬러그 생성

형식: `malmoelab-ko-repeat-{단어영문}-{3자리시퀀스}`

예시:
- `malmoelab-ko-repeat-jip-001`
- `malmoelab-ko-repeat-hakgyo-002`

시퀀스 번호는 `episodes/` 폴더 안에 있는 `malmoelab-ko-repeat-*` 에피소드 수를 세어 결정한다.

---

## STEP 2 — 말모이랩 DB 예문 선택

### 2-1. DB 접속

secret key: `MALMOELAB_DATABASE_URL`

read-only 계정으로 접속한다. DB 비밀번호는 Paperclip secret에만 있으며 스크립트나 파일에 적지 않는다.

### 2-2. 후보 조회 SQL

```sql
SELECT
    w.id              AS word_id,
    w.word_text,
    w.romanization,
    w.topik_level,
    w.difficulty_score,
    ws.id             AS sense_id,
    wt.translation    AS english_gloss,
    we.id             AS example_id,
    we.example_text,
    we.translation    AS example_translation
FROM words w
JOIN word_senses ws       ON ws.word_id = w.id
JOIN word_translations wt ON wt.sense_id = ws.id AND wt.language_code = 'en'
JOIN word_examples we     ON we.sense_id = ws.id
LEFT JOIN word_example_translations wet
    ON wet.example_id = we.id AND wet.language_code = 'en'
WHERE
    w.is_published = true
    AND wet.translation IS NOT NULL
    AND w.topik_level <= 2            -- 초급 위주
    AND LENGTH(we.example_text) <= 30 -- 너무 긴 문장 제외
ORDER BY RANDOM()
LIMIT 20;
```

### 2-3. 중복 확인

조회 결과 각 `example_id`를  
`data/used_sentences.jsonl` 의 `exampleId` 필드와 대조한다.

- `status` 가 `rendered` 또는 `reserved` 인 example_id → **제외**
- 아직 없는 example_id → **사용 가능**

### 2-4. 최종 선택 기준

우선순위:
1. `used_sentences.jsonl`에 없는 example
2. `topik_level` 낮은 것 우선
3. 예문 길이 20자 이하 우선
4. `difficulty_score` 낮은 것 우선

---

## STEP 3 — 보기 단어(choices) 선택

정답 단어 1개 + 오답 단어 2개 = 총 3개.

### 3-1. 정답 단어

STEP 2에서 선택한 예문의 focus word (`word_text`).

### 3-2. 오답 단어 2개 선택 기준

```sql
SELECT
    w.id, w.word_text, w.romanization,
    wt.translation AS english_gloss
FROM words w
JOIN word_senses ws       ON ws.word_id = w.id
JOIN word_translations wt ON wt.sense_id = ws.id AND wt.language_code = 'en'
WHERE
    w.is_published = true
    AND w.part_of_speech = '{정답_단어의_part_of_speech}'  -- 같은 품사
    AND w.topik_level <= 2
    AND w.id != '{정답_word_id}'
ORDER BY RANDOM()
LIMIT 10;
```

선택 기준:
- **같은 품사** (명사면 명사, 동사면 동사)
- 일상생활 장소/행동 맥락에서 자연스럽게 헷갈릴 수 있는 단어 우선
- 단어 자체는 이전 에피소드에서 사용됐어도 무방
- 문장 속 빈칸에 넣어도 문법적으로 말이 되는 것 우선

### 3-3. 보기 배열 순서

정답 위치는 매번 랜덤으로 배치 (① ② ③ 중 어디든).

---

## STEP 4 — source-packet.json 작성

`episodes/malmoelab-template/source-packet.template.json` 을 복사한 뒤  
모든 `{{PLACEHOLDER}}` 값을 실제 데이터로 치환한다.

저장 경로: `episodes/{EPISODE_SLUG}/source-packet.json`

---

## STEP 5 — narration-script.md 작성

`episodes/malmoelab-template/narration-script.template.md` 를 복사한 뒤  
모든 `{{PLACEHOLDER}}` 값을 치환한다.

저장 경로: `episodes/{EPISODE_SLUG}/narration-script.md`

TTS 생성이 이 단계에서 가능하면 실행한다.
- `audio/narration-ko.mp3` (한국 남성, speed 0.75×)
- `audio/narration-en.mp3` (영어 여성, speed 0.85×)

---

## STEP 6 — video-generation-job.json 작성

`episodes/malmoelab-template/video-generation-job.template.json` 을 복사한 뒤  
모든 `{{PLACEHOLDER}}` 값을 치환한다.

저장 경로: `episodes/{EPISODE_SLUG}/video-generation-job.json`

Grok 씬 생성은 STEP 9에서 실행한다.

### ⚠️ Grok 프롬프트 작성 필수 규칙

이전 버전(v1)에서 9:16 세로 형식 + 구도 미지정으로 인해  
캐릭터가 프레임을 가득 채우고 칠판이 보이지 않는 문제가 발생했다.

**v2부터 모든 Grok 프롬프트에 반드시 포함해야 할 6가지 요소:**

1. **구도 + 위치 명시** (필수):
   ```
   COMPOSITION: The teacher character stands IN FRONT OF the chalkboard,
   on the RIGHT SIDE of the frame (30-35% width). The chalkboard is visible
   on the LEFT (65-70% width). The teacher is BETWEEN the camera and the chalkboard.
   ```
   ⚠️ "behind" 사용 금지. 반드시 "IN FRONT OF" 사용.

2. **카메라 거리 명시** (필수):
   ```
   Medium shot, waist-up view. The camera is at eye-level,
   like a student sitting at a desk.
   ```

3. **비율 명시** (필수):
   ```
   Horizontal 16:9 widescreen format.
   ```

4. **3D 스타일 명시** (필수):
   ```
   3D anime-style render.
   ```

5. **텍스트 생성 금지** (필수):
   ```
   Do NOT add any text, letters, numbers, subtitles, logos, or watermarks
   anywhere in the image.
   ```

6. **칠판 깨끗하게** (필수):
   ```
   Keep the chalkboard surface clean and empty.
   ```

**금지 사항:**
- `"vertical 9:16"` 을 프롬프트에 넣지 않는다.
- 캐릭터의 얼굴 클로즈업을 요청하지 않는다.
- Grok에게 텍스트/글자 생성을 요청하지 않는다.
- 구도 레퍼런스: `docs/example/mBp3B.jpg` 를 참고 이미지로 활용한다.

---

## STEP 7 — packet.md 작성

`episodes/malmoelab-template/packet.template.md` 를 복사한 뒤  
모든 `{{PLACEHOLDER}}` 값을 치환한다.

저장 경로: `episodes/{EPISODE_SLUG}/packet.md`

---

## STEP 8 — used_sentences.jsonl 업데이트

선택한 예문을 즉시 ledger에 `reserved` 상태로 추가한다.  
렌더 완료 후 `rendered` 로 변경한다.

```jsonc
// 추가할 레코드 형식
{
  "episodeSlug": "{EPISODE_SLUG}",
  "wordId": "{WORD_ID}",
  "senseId": "{SENSE_ID}",
  "exampleId": "{EXAMPLE_ID}",
  "sentenceText": "{SENTENCE_KO}",
  "status": "reserved",
  "selectedAt": "{ISO8601_TIMESTAMP}"
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
