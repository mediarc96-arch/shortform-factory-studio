# 나레이션 스크립트 — {{EPISODE_SLUG}}

_이 파일은 `narration-script.template.md` 기반으로 자동 생성됩니다._  
_모든 `{{PLACEHOLDER}}` 는 `source-packet.json` 의 값으로 치환됩니다._

---

## ⚠️ 핵심 규칙

1. **나레이션은 절대 동시 재생 금지.** 순차 재생만 허용.
2. **영어, 로마자는 TTS로 읽지 않음.** 화면에 텍스트로만 표시.
3. 각 세그먼트 사이 최소 0.3초 간격.

---

## 성우 / TTS 지시사항

| 트랙 | 조건 | 속도 | 톤 |
|------|------|------|----|
| 🇰🇷 KO | 차분한 한국 남성 | **0.75× — 매우 느리게** | 또박또박, 권위 있되 따뜻하게 |

> ⚠️ 한국어 파트는 절대 서두르지 말 것. 학습자가 따라 쓸 수 있을 정도의 속도.

---

## 타임코드별 대사

### [오프닝] 0~7초 — 고정 클립
🇰🇷 KO: "안녕하세요. 여러분과 한글 공부를 같이 할 대한입니다."
(자막 없음. 영상에 내장된 나레이션.)

---

### [00:07 ~ 00:10] 씬 1 — 문제 제시

```
🇰🇷 KO (남성, 느리게):
  "{{BLANKED_NARRATION_KO}}"
  예: "저녁에는… [1초 정지] …에서 쉽니다."
```

> 규칙: 빈칸 위치에서 반드시 **1초 정지** 삽입.  
> 빈칸 앞 문구와 뒤 문구를 분리해서 녹음.

---

### [00:06 ~ 00:11] 씬 2 — 생각할 시간

```
(나레이션 없음)
🎵 SFX: 또깍 또깍 또깍  (ticking 3회 — 3초)
```

---

### [00:11 ~ 00:16] 씬 3 — 정답 공개

```
(나레이션 없음)
🎵 SFX: 또로롱~  (정답 공개 효과음)
```

---

### [00:16 ~ 00:17] 씬 4 시작 — 따라하기 안내

```
🇰🇷 KO: "따라해 보세요."
```

---

### [00:17 ~ 00:28] 씬 4 — 단어 반복 (각 단어 2회)

#### ▶ 1번 단어 (정답: {{ANSWER_WORD}})

> 로마자(Jip, Hoesa, Hwajangsil)는 오디오로 읽지 않음. 화면 표시만.

```
[1회차]
🇰🇷 KO: "{{ANSWER_WORD}}"           [0.5초]
  → 간격 1.3~1.5초
[2회차]
🇰🇷 KO: "{{ANSWER_WORD}}"
  → 간격 1.3~1.5초
```

#### ▶ 2번 단어 ({{CHOICE_DISTRACTORA_KO}})

```
[1회차]
🇰🇷 KO: "{{CHOICE_DISTRACTORA_KO}}"            [0.5초]
  → 간격 1.3~1.5초

[2회차]
🇰🇷 KO: "{{CHOICE_DISTRACTORA_KO}}"
  → 간격 1.3~1.5초
```

#### ▶ 3번 단어 ({{CHOICE_DISTRACTORB_KO}})

```
[1회차]
🇰🇷 KO: "{{CHOICE_DISTRACTORB_KO}}"            [0.5초]
  → 간격 1.3~1.5초

[2회차]
🇰🇷 KO: "{{CHOICE_DISTRACTORB_KO}}"
  → 간격 1.3~1.5초
```

> 단어 순서: choices 배열의 ① ② ③ 번호 순서가 아닌  
> **정답 → distractor A → distractor B** 순서로 고정한다.

---

### [엔딩] — 고정 클립
🇰🇷 KO: "그럼 다음시간에 또 만나요."
🎵 BGM 페이드아웃

---

## TTS 생성 설정

```json
{
  "_rule": "한국어 순차 재생. 영어,로마자는 TTS 없음(화면 표시만).",
  "ko_track": {
    "text_segments": [
      "{{BLANKED_NARRATION_KO_PART1}}",
      "[PAUSE:1000ms]",
      "{{BLANKED_NARRATION_KO_PART2}}",
      "[PAUSE:500ms]",
      "따라해 보세요.",
      "[PAUSE:400ms]",
      "{{ANSWER_WORD}}",
      "[PAUSE:1500ms]",
      "{{ANSWER_WORD}}",
      "[PAUSE:700ms]",
      "{{CHOICE_DISTRACTORA_KO}}",
      "[PAUSE:1500ms]",
      "{{CHOICE_DISTRACTORA_KO}}",
      "[PAUSE:700ms]",
      "{{CHOICE_DISTRACTORB_KO}}",
      "[PAUSE:1500ms]",
      "{{CHOICE_DISTRACTORB_KO}}"
    ],
    "voice": "Korean male, calm",
    "speed": 0.75,
    "outputFile": "./audio/narration-ko.mp3",
    "note": "영어,로마자(Romanization)는 TTS로 읽지 않는다. 화면에만 표시."
  }
}
```

---

## 플레이스홀더 매핑 참조

| 플레이스홀더 | source-packet.json 경로 |
|------------|------------------------|
| `{{EPISODE_SLUG}}` | `.episodeSlug` |
| `{{BLANKED_NARRATION_KO}}` | `.lesson.blankedSentenceKo` (빈칸 앞뒤 분리) |
| `{{ANSWER_WORD}}` | `.lesson.answerWord` |
| `{{ANSWER_ROMANIZATION}}` | `.lesson.answerRomanization` |
| `{{ANSWER_GLOSS}}` | `.lesson.answerGloss` |
| `{{CHOICE_DISTRACTORA_KO}}` | `.choices[]` 에서 `isAnswer=false` 첫 번째 |
| `{{CHOICE_DISTRACTORB_KO}}` | `.choices[]` 에서 `isAnswer=false` 두 번째 |
