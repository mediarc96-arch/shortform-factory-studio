# Daehan Pilot 001 — 나레이션 스크립트

- **언어**: 한국어만 (TTS: Supertone, 클론 보이스)
- **화자**: 대한 (30대 초반, 밝고 활발한 선생님)
- **속도**: 기본 1.0× (필요시 "빵" 강조 구간만 0.9×로 느리게)
- **톤**: 공손한 존댓말 기본, 정답 공개·따라하기 구간은 친근하게
- **영어 자막**: 별도 텍스트로 화면 하단에 MoviePy 오버레이 (TTS 아님)

관련 문서: [scene-plan.md](./scene-plan.md) · [source-packet.json](./source-packet.json)

---

## 씬 0 — 오프닝 (0.0~3.0s)

`01_Opening.mp4` 원본 오디오 그대로 사용.

```
안녕하세요. 대한이에요!
```

영어 자막 (0.0~3.0s): `Hello, I'm Daehan!`

---

## 씬 1 — 상황 연기 (3.0~8.0s)

TTS 생성 대상. 타이밍: 씬 시작 0.5초 후부터 발화.

```
풍선을 너무 크게 불었더니…
```

영어 자막 (3.5~7.5s): `I blew the balloon too big...`

---

## 씬 2 — 결정적 순간 (8.0~12.0s)

TTS 생성 대상. 타이밍: 풍선 터지는 2.2초 시점과 싱크. "빵" 발음 강조.

```
결국 빵 터져 버렸다!
```

- "빵" 부분은 Supertone API의 강조 파라미터 사용 (또는 속도 0.9×로 느리게)
- 터지는 SFX와 맞추기 위해 "빵" 첫 글자 발화가 **10.2초 지점**에 오도록 오디오 조정

영어 자막 (8.5~11.8s): `...and it ended up popping! (ppang!)`

---

## 씬 3 — 칠판 문제 제시 (12.0~19.0s)

TTS 생성 대상. 타이밍:
- 12.3s: "빈칸에 들어갈 말은…"
- 15.5s: "무엇일까요?"

```
빈칸에 들어갈 말은 무엇일까요?
```

영어 자막 (12.3~18.5s): `What word goes in the blank?`

보기 3개는 TTS로 읽지 않음. 화면에 타이포로만 표시 (딩 사운드와 함께 순차 페이드인).

---

## 씬 4 — 정답 공개 + 따라하기 (19.0~26.7s)

TTS 생성 대상. 2개 문장으로 분리.

### 4-1. 정답 공개 (씬 시작 3.0s 지점, 절대시간 22.0s)

```
정답은 빵!
```

영어 자막 (22.0~24.0s): `The answer is "ppang"!`

### 4-2. 따라하기 (씬 시작 5.0s 지점, 절대시간 24.0s)

```
같이 따라해볼까요? 빵!
```

영어 자막 (24.0~26.7s): `Let's say it together! "Ppang"!`

---

## 씬 5 — 엔딩 (26.7~30.0s)

`02_Ending.mp4` 원본 오디오 그대로 사용.

```
도움이 좀 되셨나요? 그럼 안녕~!
```

영어 자막 (26.7~30.0s): `Hope this helps. See you next time!`

---

## TTS 생성용 세그먼트 요약

`scripts/tts/generate_narration.py`가 이 표를 읽어 씬별 개별 mp3로 생성.

| 파일 | 대사 | 속도 | 강조 |
|------|------|------|------|
| `audio/narration-ko-scene1.mp3` | 풍선을 너무 크게 불었더니… | 1.0× | - |
| `audio/narration-ko-scene2.mp3` | 결국 빵 터져 버렸다! | 0.9× | "빵" |
| `audio/narration-ko-scene3.mp3` | 빈칸에 들어갈 말은 무엇일까요? | 1.0× | - |
| `audio/narration-ko-scene4-1.mp3` | 정답은 빵! | 1.0× | "빵" |
| `audio/narration-ko-scene4-2.mp3` | 같이 따라해볼까요? 빵! | 1.0× | "빵" |

씬1·씬5(오프닝·엔딩)는 원본 클립 오디오를 쓰므로 TTS 생성 제외.

---

## 자막 파일 포맷

영어 자막은 `post/subtitles-en.srt` 로 생성하여 MoviePy가 읽어들임. 별도 TTS 아님.

```srt
1
00:00:00,000 --> 00:00:03,000
Hello, I'm Daehan!

2
00:00:03,500 --> 00:00:07,500
I blew the balloon too big...

3
00:00:08,500 --> 00:00:11,800
...and it ended up popping! (ppang!)

4
00:00:12,300 --> 00:00:18,500
What word goes in the blank?

5
00:00:22,000 --> 00:00:24,000
The answer is "ppang"!

6
00:00:24,000 --> 00:00:26,700
Let's say it together! "Ppang"!

7
00:00:26,700 --> 00:00:30,000
Hope this helps. See you next time!
```
