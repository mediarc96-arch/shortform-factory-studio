# 나레이션 스크립트 — {{EPISODE_SLUG}}

_이 파일은 `narration-script.template.md` 기반으로 자동 생성됩니다._  
_모든 `{{PLACEHOLDER}}` 는 `source-packet.json` 의 값으로 치환됩니다._

---

## 성우 / TTS 지시사항

| 트랙 | 조건 | 속도 | 톤 |
|------|------|------|----|
| 🇰🇷 KO | 차분한 한국 남성 | **0.75× — 매우 느리게** | 또박또박, 권위 있되 따뜻하게 |
| 🇺🇸 EN | 영어권 여성 | **0.85×** | 부드럽고 명확, 교육적 |

> ⚠️ 한국어 파트는 절대 서두르지 말 것. 학습자가 따라 쓸 수 있을 정도의 속도.

---

## 타임코드별 대사

### [00:03 ~ 00:06] 씬 1 — 문제 제시

```
🇰🇷 KO (남성, 느리게):
  "{{BLANKED_NARRATION_KO}}"
  예: "저녁에는… [1초 정지] …에서 쉽니다."

🇺🇸 EN (여성, 부드럽게):
  "{{BLANKED_NARRATION_EN}}"
  예: "I relax at… [1-second pause] …in the Evening."
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
🇺🇸 EN: "Repeat after me."
```

---

### [00:17 ~ 00:28] 씬 4 — 단어 반복 (각 단어 2회)

#### ▶ 1번 단어 (정답: {{ANSWER_WORD}})

```
[1회차]
🇰🇷 KO: "{{ANSWER_WORD}}"           [0.5초]
🇰🇷 KO: "{{ANSWER_ROMANIZATION}}"   [0.5초]
🇺🇸 EN: "{{ANSWER_ROMANIZATION}} — {{ANSWER_GLOSS}}"  [0.7초]

[2회차]
🇰🇷 KO: "{{ANSWER_WORD}}"
🇰🇷 KO: "{{ANSWER_ROMANIZATION}}"
🇺🇸 EN: "{{ANSWER_ROMANIZATION}} — {{ANSWER_GLOSS}}"
```

#### ▶ 2번 단어 ({{CHOICE_DISTRACTORA_KO}})

```
[1회차]
🇰🇷 KO: "{{CHOICE_DISTRACTORA_KO}}"            [0.5초]
🇰🇷 KO: "{{CHOICE_DISTRACTORA_ROMANIZATION}}"   [0.5초]
🇺🇸 EN: "{{CHOICE_DISTRACTORA_ROMANIZATION}} — {{CHOICE_DISTRACTORA_GLOSS}}"  [0.7초]

[2회차]
🇰🇷 KO: "{{CHOICE_DISTRACTORA_KO}}"
🇰🇷 KO: "{{CHOICE_DISTRACTORA_ROMANIZATION}}"
🇺🇸 EN: "{{CHOICE_DISTRACTORA_ROMANIZATION}} — {{CHOICE_DISTRACTORA_GLOSS}}"
```

#### ▶ 3번 단어 ({{CHOICE_DISTRACTORB_KO}})

```
[1회차]
🇰🇷 KO: "{{CHOICE_DISTRACTORB_KO}}"            [0.5초]
🇰🇷 KO: "{{CHOICE_DISTRACTORB_ROMANIZATION}}"   [0.7초]
🇺🇸 EN: "{{CHOICE_DISTRACTORB_ROMANIZATION}} — {{CHOICE_DISTRACTORB_GLOSS}}"  [0.7초]

[2회차]
🇰🇷 KO: "{{CHOICE_DISTRACTORB_KO}}"
🇰🇷 KO: "{{CHOICE_DISTRACTORB_ROMANIZATION}}"
🇺🇸 EN: "{{CHOICE_DISTRACTORB_ROMANIZATION}} — {{CHOICE_DISTRACTORB_GLOSS}}"
```

> 단어 순서: choices 배열의 ① ② ③ 번호 순서가 아닌  
> **정답 → distractor A → distractor B** 순서로 고정한다.

---

### [00:28 ~ 00:30] 씬 5 — 마무리

```
(나레이션 없음)
🎵 BGM 페이드아웃
```

---

## TTS 생성 설정

```json
{
  "ko_track": {
    "text_segments": [
      "{{BLANKED_NARRATION_KO_PART1}}",
      "[PAUSE:1000ms]",
      "{{BLANKED_NARRATION_KO_PART2}}",
      "[PAUSE:500ms]",
      "따라해 보세요.",
      "[PAUSE:300ms]",
      "{{ANSWER_WORD}}",
      "[PAUSE:500ms]",
      "{{ANSWER_ROMANIZATION}}",
      "[PAUSE:500ms]",
      "{{ANSWER_WORD}}",
      "[PAUSE:500ms]",
      "{{ANSWER_ROMANIZATION}}",
      "[PAUSE:700ms]",
      "{{CHOICE_DISTRACTORA_KO}}",
      "[PAUSE:500ms]",
      "{{CHOICE_DISTRACTORA_ROMANIZATION}}",
      "[PAUSE:500ms]",
      "{{CHOICE_DISTRACTORA_KO}}",
      "[PAUSE:500ms]",
      "{{CHOICE_DISTRACTORA_ROMANIZATION}}",
      "[PAUSE:700ms]",
      "{{CHOICE_DISTRACTORB_KO}}",
      "[PAUSE:500ms]",
      "{{CHOICE_DISTRACTORB_ROMANIZATION}}",
      "[PAUSE:500ms]",
      "{{CHOICE_DISTRACTORB_KO}}",
      "[PAUSE:500ms]",
      "{{CHOICE_DISTRACTORB_ROMANIZATION}}"
    ],
    "voice": "Korean male, calm",
    "speed": 0.75,
    "outputFile": "./audio/narration-ko.mp3"
  },
  "en_track": {
    "text_segments": [
      "{{BLANKED_NARRATION_EN_PART1}}",
      "[PAUSE:1000ms]",
      "{{BLANKED_NARRATION_EN_PART2}}",
      "[PAUSE:500ms]",
      "Repeat after me.",
      "[PAUSE:300ms]",
      "{{ANSWER_ROMANIZATION}} — {{ANSWER_GLOSS}}",
      "[PAUSE:700ms]",
      "{{ANSWER_ROMANIZATION}} — {{ANSWER_GLOSS}}",
      "[PAUSE:700ms]",
      "{{CHOICE_DISTRACTORA_ROMANIZATION}} — {{CHOICE_DISTRACTORA_GLOSS}}",
      "[PAUSE:700ms]",
      "{{CHOICE_DISTRACTORA_ROMANIZATION}} — {{CHOICE_DISTRACTORA_GLOSS}}",
      "[PAUSE:700ms]",
      "{{CHOICE_DISTRACTORB_ROMANIZATION}} — {{CHOICE_DISTRACTORB_GLOSS}}",
      "[PAUSE:700ms]",
      "{{CHOICE_DISTRACTORB_ROMANIZATION}} — {{CHOICE_DISTRACTORB_GLOSS}}"
    ],
    "voice": "English female, soft",
    "speed": 0.85,
    "outputFile": "./audio/narration-en.mp3"
  }
}
```

---

## 플레이스홀더 매핑 참조

| 플레이스홀더 | source-packet.json 경로 |
|------------|------------------------|
| `{{EPISODE_SLUG}}` | `.episodeSlug` |
| `{{BLANKED_NARRATION_KO}}` | `.lesson.blankedSentenceKo` (빈칸 앞뒤 분리) |
| `{{BLANKED_NARRATION_EN}}` | `.lesson.blankedSentenceEn` (빈칸 앞뒤 분리) |
| `{{ANSWER_WORD}}` | `.lesson.answerWord` |
| `{{ANSWER_ROMANIZATION}}` | `.lesson.answerRomanization` |
| `{{ANSWER_GLOSS}}` | `.lesson.answerGloss` |
| `{{CHOICE_DISTRACTORA_KO}}` | `.choices[]` 에서 `isAnswer=false` 첫 번째 |
| `{{CHOICE_DISTRACTORB_KO}}` | `.choices[]` 에서 `isAnswer=false` 두 번째 |
