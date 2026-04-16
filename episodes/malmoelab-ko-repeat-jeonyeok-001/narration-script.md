# 나레이션 스크립트 — malmoelab-ko-repeat-jeonyeok-001

## 성우 지시사항

| 트랙 | 성우 조건 | 속도 | 톤 |
|------|----------|------|----|
| 🇰🇷 KO | 차분한 한국 남성 | **0.75× — 매우 느리게** | 선생님처럼 또박또박, 권위 있되 따뜻하게 |
| 🇺🇸 EN | 영어권 여성 | 0.85× | 부드럽고 명확, 교육적 |

> ⚠️ 한국어 파트는 **절대 서두르지 말 것**. 학습자가 따라 쓸 수 있을 정도의 속도.

---

## 타임코드별 대사

### [00:03 ~ 00:06] 씬 1 — 문제 제시

```
🇰🇷 KO (남성, 느리게):
  "저녁에는… [1초 정지] …에서 쉽니다."

🇺🇸 EN (여성, 부드럽게):
  "I relax at… [1-second pause] …in the Evening."
```

---

### [00:06 ~ 00:11] 씬 2 — 생각할 시간

```
(나레이션 없음)
🎵 SFX: 또깍 또깍 또깍  (틱톡 시계 소리 3회)
```

---

### [00:11 ~ 00:16] 씬 3 — 정답 공개

```
(나레이션 없음)
🎵 SFX: 또로롱~  (성공 효과음)
(시각적 집중: 선생님이 칠판에 "집" 쓰는 모션)
```

---

### [00:16 ~ 00:17] 씬 4 시작 — 따라하기 안내

```
🇰🇷 KO (남성):
  "따라해 보세요."

🇺🇸 EN (여성):
  "Repeat after me."
```

---

### [00:17 ~ 00:28] 씬 4 — 단어 반복 (각 단어 2회)

#### ▶ 1번 단어: 집

```
[1회차]
🇰🇷 KO: "집"          [0.5초 쉬고]
🇰🇷 KO: "Jip"         [0.5초 쉬고]
🇺🇸 EN: "Jip — House" [0.7초 쉬고]

[2회차]
🇰🇷 KO: "집"
🇰🇷 KO: "Jip"
🇺🇸 EN: "Jip — House"
```

#### ▶ 2번 단어: 회사

```
[1회차]
🇰🇷 KO: "회사"              [0.5초 쉬고]
🇰🇷 KO: "Hoesa"             [0.5초 쉬고]
🇺🇸 EN: "Hoesa — Company"   [0.7초 쉬고]

[2회차]
🇰🇷 KO: "회사"
🇰🇷 KO: "Hoesa"
🇺🇸 EN: "Hoesa — Company"
```

#### ▶ 3번 단어: 화장실

```
[1회차]
🇰🇷 KO: "화장실"                  [0.5초 쉬고]
🇰🇷 KO: "Hwajangsil"              [0.7초 쉬고]
🇺🇸 EN: "Hwajangsil — Bathroom"   [0.7초 쉬고]

[2회차]
🇰🇷 KO: "화장실"
🇰🇷 KO: "Hwajangsil"
🇺🇸 EN: "Hwajangsil — Bathroom"
```

---

### [00:28 ~ 00:30] 씬 5 — 마무리

```
(나레이션 없음)
🎵 BGM 페이드아웃
(선생님 웃으며 손 흔들기)
```

---

## 타이밍 요약표

| 타임코드 | 트랙 | 대사 |
|----------|------|------|
| 00:03 | KO | 저녁에는… |
| 00:04.5 | KO | (1초 정지) |
| 00:05 | KO | …에서 쉽니다. |
| 00:03.5 | EN | I relax at… |
| 00:05 | EN | (1초 정지) |
| 00:05.5 | EN | …in the Evening. |
| 00:11 | SFX | 또로롱~ |
| 00:16 | KO | 따라해 보세요. |
| 00:16.5 | EN | Repeat after me. |
| 00:17 | KO | 집 / Jip |
| 00:18.5 | EN | Jip — House |
| 00:19.5 | KO | 집 / Jip (2회) |
| 00:21 | EN | Jip — House (2회) |
| 00:21.5 | KO | 회사 / Hoesa |
| 00:23 | EN | Hoesa — Company |
| 00:24 | KO | 회사 / Hoesa (2회) |
| 00:25.5 | EN | Hoesa — Company (2회) |
| 00:25.5 | KO | 화장실 / Hwajangsil |
| 00:27 | EN | Hwajangsil — Bathroom |
| 00:27.5 | KO | 화장실 / Hwajangsil (2회) |

---

## TTS 시스템 사용 시 권장 설정

```json
{
  "ko_track": {
    "engine": "Google TTS / Clova Voice / ElevenLabs",
    "voice_style": "calm_male_korean",
    "speed": 0.75,
    "pitch": 0,
    "pause_between_words_ms": 500
  },
  "en_track": {
    "engine": "ElevenLabs / Google TTS",
    "voice_style": "soft_female_english",
    "speed": 0.85,
    "pitch": 0,
    "pause_between_words_ms": 400
  }
}
```
