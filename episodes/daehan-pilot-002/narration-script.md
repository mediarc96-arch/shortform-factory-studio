# Daehan Pilot 002 — 나레이션 스크립트

- **언어**: 한국어만 (TTS: Supertone, 클론 Voice 1)
- **화자**: 대한
- **톤**: 존댓말, 차분하지만 활기 있는 선생님 톤
- **영어 자막**: 별도 텍스트로 화면 하단 (MoviePy 오버레이, TTS 아님)

관련 문서: [scene-plan.md](./scene-plan.md) · [source-packet.json](./source-packet.json)

---

## 씬 0 — 오프닝 (0.0 – 3.0s)

`01_Opening.mp4` 원본 오디오 그대로 사용. TTS 생성 대상 아님.

## 씬 1 — 문장 소개 (3.5 – 7.5s)

TTS 생성 대상. 3.7s부터 발화 시작 (wipe 완료 후 0.2s 간격).

```
아기의 옹알이가 하루 종일 이어졌다.
```

영어 자막 (3.7 – 7.3s): `The baby's babbling continued all day.`

## 씬 2 — 따라해 볼까요 + 낭독 + 묵음 pause (7.5 – 17.5s)

세 개의 TTS 세그먼트 + 의도적 묵음.

### 2-a. 따라해 볼까요 (8.0s 시작)

```
따라해 볼까요?
```

영어 자막 (8.0 – 9.3s): `Let's try together!`

### 2-b. 문장 낭독 (10.3s 시작 — 1초 prompt pause 후)

```
아기의 옹알이가 하루 종일 이어졌다.
```

영어 자막 (10.3 – 13.8s): `The baby's babbling continued all day.`

### 2-c. 묵음 pause (13.8 – 17.3s)

낭독 길이 약 3.5s와 동일한 묵음. 시청자가 따라 말해볼 시간. 영어 자막도 비움.

## 씬 3 — 빈칸 퀴즈 + CTA (17.5 – 26.2s)

### 3-a. 퀴즈 정적 노출 (17.5 – 26.2s, TTS 없음)

화면에 "아기의 ___가 하루 종일 이어졌다." 표시. 19.5s부터 빈칸에 노란 박스가 깜빡임.

### 3-b. CTA (20.0s 시작)

```
malmoelab.com에서 더 알아보아요.
```

영어 자막 (20.0 – 23.0s): `Learn more at malmoelab.com.`

## 씬 4 — 엔딩 (26.7 – 30.0s)

`02_Ending.mp4` 영상만 사용 (오디오 스트림 없음). TTS 생성 대상 아님.

---

## TTS 생성용 세그먼트 요약

`scripts/tts/generate_narration.py`의 pilot-002 세그먼트 정의에 반영.

| 파일 | 대사 | 속도 | startSec |
|------|------|------|----------|
| `audio/narration-ko-intro.mp3` | 아기의 옹알이가 하루 종일 이어졌다. | 0.95× | 3.7 |
| `audio/narration-ko-follow-prompt.mp3` | 따라해 볼까요? | 1.00× | 8.0 |
| `audio/narration-ko-repeat.mp3` | 아기의 옹알이가 하루 종일 이어졌다. | 0.95× | 10.3 |
| `audio/narration-ko-cta.mp3` | malmoelab.com에서 더 알아보아요. | 1.00× | 20.0 |

실제 클립 길이는 `audio/narration-timing.json`에 기록하여 타이포 페이싱에 활용.

---

## SRT 자막 (영어)

```srt
1
00:00:00,000 --> 00:00:03,000
Hello, I'm Daehan!

2
00:00:03,700 --> 00:00:07,300
The baby's babbling continued all day.

3
00:00:08,000 --> 00:00:09,300
Let's try together!

4
00:00:10,300 --> 00:00:13,800
The baby's babbling continued all day.

5
00:00:20,000 --> 00:00:23,000
Learn more at malmoelab.com.

6
00:00:26,700 --> 00:00:30,000
See you next time!
```
