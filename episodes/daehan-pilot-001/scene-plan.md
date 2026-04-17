# Daehan Pilot 001 — 씬 스토리보드

예문: **"풍선을 너무 크게 불었더니 결국 빵 터져 버렸다."**  
Focus word: **빵** (의성어, 터지는 소리)  
영어 번역: "I blew up the balloon too much, and it ended up popping."

관련 문서: [pilot-spec.md](./pilot-spec.md) · [automation-integration.md](./automation-integration.md)

---

## 전체 타임라인 (30초)

| # | 씬 | 시작 | 길이 | 전환 |
|---|----|------|------|------|
| 0 | 오프닝 (`01_Opening.mp4` 재사용) | 0.0s | 3.0s | → 검정 페이드 0.3s |
| 1 | 상황 연기 (풍선 불기) | 3.0s | 5.0s | → 컷 (프레임 매칭) |
| 2 | 결정적 순간 (빵! 터짐) | 8.0s | 4.0s | → 컷 (프레임 매칭) |
| 3 | 칠판 문제 제시 (빈칸 + 보기) | 12.0s | 7.0s | → 컷 (프레임 매칭) |
| 4 | 정답 공개 + 따라하기 | 19.0s | 7.7s | → 검정 페이드 0.3s |
| 5 | 엔딩 (`02_Ending.mp4` 재사용) | 26.7s | 3.3s | 종료 |

총 길이: **30.0s**

---

## 씬 0 — 오프닝 (3.0s)

- **소스**: `characters/daehan/01_Opening.mp4` 앞 3초 트림
- **오디오**: 원본 유지 ("안녕하세요. 대한이에요!")
- **다음 전환**: 검정 페이드아웃 0.3초 (씬1 시작 전)

### 후반 처리
- 씬1로 넘어가기 전 마지막 10~12프레임 `fadeblack`

---

## 씬 1 — 상황 연기 (5.0s)

### 비주얼
- **장면**: 대한이 풍선(빨간색)을 손에 들고 입으로 불어 크게 부풀리는 동작
- **위치**: 화면 오른쪽 1/3 (칠판 없이, 교실 배경은 블러 처리)
- **표정**: 장난스러운 집중, 눈을 살짝 감고 볼을 부풀리며 후~ 부는 표정
- **움직임**: 풍선이 점점 커짐 (작음 → 큼 → 매우 큼)
- **카메라**: 미디엄샷, 풍선이 프레임 중앙에 잘 보이도록

### 오디오
- **나레이션 (한국어, Supertone)**: "풍선을 너무 크게 불었더니…"
- **영어 자막 (MoviePy 타이포)**: "I blew the balloon too big..."
- **SFX**: 숨을 후~ 부는 소리 (3회, 풍선 커짐에 따라 점점 커짐)
- **BGM**: 잔잔한 교실 배경음 (볼륨 0.12)

### Grok 프롬프트 핵심
```
Daehan character (reference: characters/daehan/daehan.jpg + 
reference-frames/00-opening-last.png) standing on the right side 
of the frame, holding a red balloon and blowing it up with cheeks 
puffed playfully. Balloon gradually inflates from small to very 
large over 5 seconds. Medium shot, 16:9, 3D anime style, classroom 
background softly blurred. Character maintains the same outfit: 
black hanbok durumagi, gat, silver long hair, purple eyes, black 
gloves. Scene begins from the attached reference frame. No text.
```

### 참조 이미지
- `characters/daehan/daehan.jpg`
- `reference-frames/00-opening-last.png` (오프닝 마지막 프레임)

### 다음 씬 입력 준비
- 이 씬의 **마지막 프레임** → `reference-frames/01-scene-last.png`
- 씬2가 이 프레임을 시작점으로 사용

---

## 씬 2 — 결정적 순간 (4.0s)

### 비주얼
- **장면**: 풍선이 더 커지다가 **빵!** 터짐. 대한이 놀라서 눈을 크게 뜸
- **위치**: 씬1과 동일 구도 (프레임 매칭)
- **표정**: 0~2초 크게 부풀림 → 2.0~2.3초 풍선 터짐 → 2.3~4.0초 놀라서 입 벌리고 눈 크게 뜸
- **움직임**: 풍선 파편이 잠시 흩어짐 (후반 타이포그래피와 겹치지 않도록 주의)
- **카메라**: 씬1과 동일 미디엄샷

### 오디오
- **나레이션 (한국어, Supertone)**: "결국 빵 터져 버렸다!" ("빵" 강조)
- **영어 자막**: "...and it ended up popping! (ppang!)"
- **SFX**: 풍선 터지는 소리 (2.2초 시점)
- **BGM**: 잔잔하게 유지

### Grok 프롬프트 핵심
```
Scene begins from the attached reference frame (end of previous 
scene). The balloon continues to inflate for 2 seconds, then 
suddenly POPS with confetti/paper pieces scattering. Daehan 
reacts with surprise — eyes wide open, mouth agape, slight 
recoil. Hold the surprised expression for 1.7 seconds. Same 
composition, 16:9, 3D anime style, no text.
```

### 참조 이미지
- `characters/daehan/daehan.jpg`
- `reference-frames/01-scene-last.png`

### 다음 씬 입력 준비
- 마지막 프레임 → `reference-frames/02-scene-last.png`

---

## 씬 3 — 칠판 문제 제시 (7.0s)

### 비주얼
- **장면**: 대한이 칠판 앞으로 이동, 오른쪽에 서서 왼쪽 칠판을 가리키는 동작
- **위치**: 캐릭터 오른쪽 1/3, 칠판 왼쪽 2/3 (표준 구도)
- **표정**: 차분하게 설명하는 표정, 약간의 미소
- **움직임**: 
  - 0~2초: 칠판 앞으로 이동하며 손짓
  - 2~7초: 칠판을 바라보며 설명 (포즈 안정)
- **카메라**: 미디엄샷, 칠판 전체가 보이도록

### 칠판 내용 (후반 MoviePy 합성, Grok은 비워둠)
- 중앙 상단: `풍선을 너무 크게 불었더니 결국 ___ 터져 버렸다`
  - 빈칸 `___`은 노란색 박스 하이라이트, 0.5초 주기로 깜빡임
- 하단 보기 3개 (순차 페이드인, 0.3초 간격):
  - ① 꽝
  - ② 빵
  - ③ 쿵

### 오디오
- **나레이션 (한국어, Supertone)**: "빈칸에 들어갈 말은 무엇일까요?"
- **영어 자막**: "What word goes in the blank?"
- **SFX**: 보기 페이드인 시 작은 "딩" 사운드 (×3)
- **BGM**: 잔잔하게 유지

### Grok 프롬프트 핵심
```
Scene begins from the attached reference frame. Daehan walks 
towards the chalkboard and positions himself on the RIGHT SIDE 
(30% width). The chalkboard takes the LEFT 70% and is COMPLETELY 
EMPTY (no text, no chalk marks). Teacher gestures towards the 
chalkboard with his hand, then stands calmly looking at the 
board. Medium shot, eye-level, 16:9, 3D anime style, warm 
classroom lighting. Keep the chalkboard surface absolutely clean 
for post-production text overlay.
```

### 참조 이미지
- `characters/daehan/daehan.jpg`
- `reference-frames/02-scene-last.png`

### 후반 타이포그래피 스펙
- 문제 문장 스트로크 리빌: 0.12초/자, 씬 시작 0.5초 후
- 보기 ①②③: 순차 페이드인, 씬 시작 3.5초 후부터 0.3초 간격

### 다음 씬 입력 준비
- 마지막 프레임 → `reference-frames/03-scene-last.png`

---

## 씬 4 — 정답 공개 + 따라하기 (7.7s)

### 비주얼
- **장면**: 대한이 칠판 빈칸 앞에 "빵"을 적고, 환하게 웃으며 시청자를 향해 손짓
- **위치**: 캐릭터 오른쪽 1/3, 칠판 왼쪽 2/3
- **표정**: 0~3초 분필로 쓰는 집중 표정 → 3~5초 환하게 웃으며 박수 → 5~7.7초 시청자 향해 따라하기 손짓
- **움직임**:
  - 0~3초: 분필로 빈칸에 "빵" 쓰는 동작
  - 3~5초: 뒤돌아 환하게 웃음, 박수 1~2회
  - 5~7.7초: 시청자와 눈맞춤, 한 손을 귀 옆에 대는 "따라해보세요" 제스처
- **카메라**: 미디엄샷

### 칠판 내용 (후반 MoviePy 합성)
- 빈칸 `___`이 "빵"으로 바뀌는 애니메이션 (씬 시작 2.5초 시점)
  - 스트로크 리빌 효과 (분필로 쓰는 타이밍과 동기화)
  - 색: 노란색 (강조)
- 보기 ②에 동그라미 오버레이 (씬 시작 3.0초 시점)
- 최종 문장: `풍선을 너무 크게 불었더니 결국 빵 터져 버렸다`

### 오디오
- **나레이션 (한국어, Supertone)**:
  - 씬 시작 3.0초: "정답은 빵!" ("빵" 강조)
  - 씬 시작 5.0초: "같이 따라해볼까요? 빵!"
- **영어 자막**:
  - 22.0~24.0s: `The answer is "ppang"!`
  - 24.0~26.7s: `Let's say it together! "Ppang"!`
- **SFX**: 정답 효과음 (씬 시작 3.0초, "딩동")
- **BGM**: 잔잔하게 유지

### Grok 프롬프트 핵심
```
Scene begins from the attached reference frame. Daehan raises a 
piece of white chalk and performs the motion of writing on the 
chalkboard's blank area (but DO NOT actually render any text — 
chalkboard stays empty for post-production overlay). After 3 
seconds, he turns towards the camera with a bright smile, claps 
his hands once or twice, then performs a "repeat after me" 
gesture by cupping one hand near his ear. Medium shot, 16:9, 
3D anime style, cheerful expression.
```

### 참조 이미지
- `characters/daehan/daehan.jpg`
- `reference-frames/03-scene-last.png`

### 후반 타이포그래피 스펙
- "빵" 스트로크 리빌: 씬 시작 2.5초, 0.5초 동안
- ② 동그라미 하이라이트: 씬 시작 3.0초
- 영어 자막 하단: "The answer is 'ppang' (pop sound)" — 6.0~7.7초

### 다음 씬 전환
- 마지막 10~12프레임 검정 페이드아웃 → 엔딩

---

## 씬 5 — 엔딩 (3.3s)

- **소스**: `characters/daehan/02_Ending.mp4` (전체 또는 앞 3.3초)
- **오디오**: 원본 유지 ("도움이 좀 되셨나요? 그럼 안녕~!")
- **전환**: 검정 페이드인 0.3초 (씬4에서 넘어옴)

---

## 프레임 핸드오프 체크리스트

| 씬 경계 | 입력 참조 | 페이드 |
|---------|---------|------|
| 오프닝 → 씬1 | `00-opening-last.png` | 검정 0.3s |
| 씬1 → 씬2 | `01-scene-last.png` | 없음 (프레임 매칭) |
| 씬2 → 씬3 | `02-scene-last.png` | 없음 (프레임 매칭) |
| 씬3 → 씬4 | `03-scene-last.png` | 없음 (프레임 매칭) |
| 씬4 → 엔딩 | (엔딩은 고정 클립) | 검정 0.3s |

---

## MoviePy 합성 타임라인 (요약)

| 시점 | 레이어 | 내용 |
|------|--------|------|
| 0.0~3.0s | 비디오 | `01_Opening.mp4` |
| 2.7~3.0s | 페이드 | 검정 페이드아웃 |
| 3.0~3.3s | 페이드 | 검정 페이드인 |
| 3.0~8.0s | 비디오 | 씬1 |
| 8.0~12.0s | 비디오 | 씬2 |
| 12.0~19.0s | 비디오 | 씬3 |
| 12.5~18.5s | 텍스트 | 문제 문장 스트로크 리빌 |
| 15.5~19.0s | 텍스트 | 보기 ①②③ 페이드인 |
| 19.0~26.7s | 비디오 | 씬4 |
| 21.5~22.0s | 텍스트 | 빈칸 → "빵" 리빌 |
| 22.0~26.7s | 텍스트 | 정답 하이라이트 + 영어 자막 |
| 26.4~26.7s | 페이드 | 검정 페이드아웃 |
| 26.7~27.0s | 페이드 | 검정 페이드인 |
| 26.7~30.0s | 비디오 | `02_Ending.mp4` |

### 오디오 트랙 (합성 후 통합)
| 트랙 | 볼륨 | 구간 |
|------|------|------|
| 오프닝 원본 오디오 | 1.0 | 0.0~3.0s |
| 본편 한국어 나레이션 (Supertone) | 1.0 | 3.0~26.0s (구간별) |
| SFX (후~, 빵!, 딩동) | 0.8 | 지정 시점 |
| BGM (잔잔한 교실) | 0.12 | 3.0~26.7s |
| 엔딩 원본 오디오 | 1.0 | 26.7~30.0s |

**영어 나레이션은 없음.** 영어는 화면 하단 자막(텍스트)으로만 제공.

---

## 다음 작성 대상

1. `source-packet.json` — 예문·정답·오답·focus word 구조화 데이터
2. `narration-script.md` — 한국어·영어 나레이션 대사 확정
3. `video-generation-job.json` — 씬별 Grok 잡 스펙 (본 문서의 프롬프트를 JSON화)
4. `post/chalkboard-text-spec.json` — MoviePy 타이포그래피 타이밍 스펙
