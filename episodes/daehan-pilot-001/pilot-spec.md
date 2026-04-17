# Daehan Pilot 001 — 매끄러운 쇼츠 제작 파이프라인 계획

> **자동화 통합 계획은 [automation-integration.md](./automation-integration.md)를 함께 참조한다.**  
> 파일럿은 수동 실행이지만, Shortform Factory의 Video Editor Agent가 나중에 CLI 한 줄로 호출할 수 있도록 껍데기는 자동화 친화적으로 설계한다.

## 1. 배경

기존 `malmoelab-template` 기반 제작의 한계:

1. **씬 간 단절** — 각 Grok 씬이 독립 생성되어 포즈·조명·시선이 끊김
2. **전환 장치 부재** — 오프닝↔본편↔엔딩 사이 공백이 튐
3. **목소리 분리** — `01_Opening.mp4`의 캐릭터 목소리를 본편 나레이션과 이어갈 수단 없음
4. **캐릭터 외형 드리프트** — 오프닝(기존 생성)과 본편(새 Grok 생성) 사이 얼굴·의상·분위기 차이
5. **템플릿 복잡도** — DB·used_sentences 연동이 많아 "일단 한 번 만들어보기"가 무거움

## 2. 파일럿 목표

> "한 편이 컷과 컷 사이, 오프닝과 본편 사이에 끊김 없이 자연스럽게 이어지는가"를 증명.

성공 기준:
- 씬 경계에서 캐릭터 포즈·조명·카메라가 이어져 보임
- 오프닝 → 본편 → 엔딩이 하나의 영상처럼 느껴짐
- 처음부터 끝까지 동일한 목소리
- 칠판 한글 콘텐츠가 후반 타이포그래피로 선명하게 얹힘

## 3. 파일럿 스펙

| 항목 | 값 |
|------|-----|
| 슬러그 | `daehan-pilot-001` |
| 총 길이 | 30초 (오프닝 ~3초 + 본편 ~24초 + 엔딩 ~3초) |
| 비율 | 16:9 (1920×1080) |
| 캐릭터 | 대한 (`characters/daehan/`) |
| 예문 | "풍선을 너무 크게 불었더니 결국 빵 터져 버렸다." |
| 포맷 | 액션 기반 퀴즈 (§8 참조) |
| 영상 생성 | Grok (이미지→비디오, 씬별 생성 + 프레임 핸드오프) |
| 나레이션 (음성) | **Supertone (한국어만, 클론 보이스)** — 영어 TTS 없음 |
| 영어 (자막) | MoviePy 후반 타이포그래피로 하단 고정 자막 (TTS 아님) |
| 오프닝 소스 | `characters/daehan/01_Opening.mp4` (재사용, 단 §7 참조) |
| 엔딩 소스 | `characters/daehan/02_Ending.mp4` (재사용) |
| 엔딩 대사 | "도움이 좀 되셨나요? 그럼 안녕~!" |
| 자막·칠판 타이포 | 후반 작업 오버레이 |

## 4. 폴더 구조

```
episodes/daehan-pilot-001/
├── pilot-spec.md                    # 이 문서
├── scene-plan.md                    # 씬별 스토리보드
├── source-packet.json               # 예문·정답·오답 데이터 (최소)
├── narration-script.md              # 한국어·영어 나레이션 원고
├── video-generation-job.json        # 씬별 Grok 잡 명세
├── reference-frames/
│   ├── 00-opening-last.png          # 01_Opening.mp4 마지막 프레임
│   ├── 01-scene-last.png            # 씬1 마지막 프레임 (씬2 입력)
│   ├── 02-scene-last.png
│   └── ...
├── audio/
│   ├── voice-sample-ko.mp3          # 01_Opening.mp4에서 추출 (Supertone 클론 소스)
│   ├── narration-ko.mp3             # Supertone 클론 보이스로 생성
│   └── narration-en.mp3             # ElevenLabs 영어 보이스
├── renders/
│   ├── scene-1.mp4                  # Grok 결과 (깨끗한 칠판)
│   ├── scene-2.mp4
│   └── ...
├── post/
│   ├── typography-layer.aep         # 또는 .prproj / .drp (편집툴 선택)
│   └── chalkboard-text-spec.md      # 타이포그래피 스펙
└── final/
    ├── daehan-pilot-001.mp4
    └── daehan-pilot-001-thumb.png
```

## 5. 핵심 개선 6가지

### 5.1 프레임 핸드오프 (씬 간 매끄러움)

**문제**: Grok이 씬별로 독립 생성 → 컷이 튐.

**해법**: 매 씬 완료 후 마지막 프레임을 PNG로 추출, 다음 씬의 Grok `image` 파라미터(reference image)로 주입.

- Grok 프롬프트에 고정 블록 추가:
  ```
  This scene begins from the attached reference frame. 
  At frame 1, character pose, lighting, and camera angle 
  match the reference exactly, then naturally transitions 
  into {다음 액션 서술}.
  ```
- 결과: 씬 경계에서 캐릭터가 "같은 자세에서 이어서 움직이는" 것처럼 보임.

**자동화** (§5.6 참조).

### 5.2 전환 효과 표준화

| 구간 | 전환 | 길이 |
|------|------|------|
| 오프닝 → 씬1 | 검정 페이드 | 0.3초 (약 9프레임 @30fps) |
| 씬1 → 씬2 → ... → 마지막 씬 | 프레임 매칭 (페이드 없음) | 0 |
| 마지막 씬 → 엔딩 | 검정 페이드 | 0.3초 |

ffmpeg 처리 예시:
```bash
ffmpeg -i opening.mp4 -i scene-1.mp4 \
  -filter_complex "[0:v][1:v]xfade=transition=fadeblack:duration=0.3:offset={opening_duration-0.3}" \
  ...
```

### 5.3 TTS — Supertone 단일 (한국어만)

| 역할 | 도구 | 비고 |
|------|------|------|
| 한국어 남성 (대한) | **Supertone** | 사용자 클론 보이스 (이미 등록됨) |
| 영어 | **TTS 없음** | 영어는 하단 자막(텍스트)로만 제공 |

ElevenLabs는 파일럿에서 사용하지 않지만, 추후 다국어 채널 확장·보조 내레이션 용도를 위해 환경변수·래퍼 스크립트 자리는 미리 예약해둠.

API 호출 스크립트:
```
scripts/tts/
├── supertone_client.py        # 한국어 클론 (파일럿에서 유일하게 사용)
├── elevenlabs_client.py       # 예약 (v1 이후 확장용)
└── generate_narration.py      # narration-script.md를 읽어 audio/*.mp3 생성
```

환경 변수: `SUPERTONE_API_KEY`, `SUPERTONE_VOICE_ID_DAEHAN`.

### 5.4 후반 타이포그래피 (MoviePy)

- Grok은 **비어 있는 칠판**만 생성
- **MoviePy**로 프로그램적 오버레이 (After Effects 수작업 금지 — 에이전트 자동화를 위해)
- `post/chalkboard-text-spec.json` 스펙을 읽어 `scripts/post/compose_final.py`가 자동 합성
- 합성 요소:
  - 칠판 한글 문장 (스트로크 리빌 0.1~0.2초/자)
  - 빈칸 하이라이트, 보기 ①②③ 순차 페이드인
  - 정답 공개 효과
  - 하단 영어 자막
- 한계 오면 Remotion으로 이식 (v1 이후 검토)
- 상세: [automation-integration.md §5](./automation-integration.md)

### 5.5 캐릭터 일관성 유지 (신규)

**사용자 우려**: 오프닝의 캐릭터와 Grok이 생성한 씬의 캐릭터가 달라 보이지 않을까?

**현실적인 한계**: 100% 일치는 불가능. 하지만 드리프트를 최소화하는 방법:

1. **다중 참조 이미지**
   - 모든 씬의 Grok 잡에 `daehan.jpg` + `00-opening-last.png` 두 장을 함께 참조로 전달
   - 프롬프트에 "Character must match these references exactly" 명시
2. **첫 씬은 오프닝과 직결**
   - 씬1은 반드시 `00-opening-last.png`를 첫 프레임 기준으로 삼아 외형을 "물려받음"
3. **전환 페이드가 보조 장치**
   - 0.3초 검정 페이드가 오프닝→씬1의 미세한 드리프트를 눈치채지 못하게 해줌
4. **드리프트 허용 불가 시 대안** (파일럿 2차)
   - 오프닝·엔딩을 새 파이프라인으로 **재생성** (같은 Grok + daehan.jpg 기준)
   - 장기적으로 캐릭터 LoRA 학습 검토

**이 파일럿의 권장 순서**: 먼저 1+2+3 조합으로 시도 → 드리프트가 눈에 띄면 4번(오프닝 재생성)으로 확장.

### 5.6 프레임 추출·주입 자동화 + CLI 진입점

**사용자 요청**: 사람 손이 적게 타게.  
**자동화 전제**: 모든 단계가 CLI 한 줄로 호출 가능 (→ Video Editor Agent가 나중에 그대로 호출).

**스크립트 구조**:
```
scripts/
├── pilot/
│   ├── extract_last_frame.py      # mp4 → 마지막 프레임 PNG
│   ├── run_scene_pipeline.py      # 씬 생성 오케스트레이션
│   └── run_all.py                 # 파일럿 전체 실행 (편의용)
├── tts/
│   ├── supertone_client.py        # 한국어 클론 보이스
│   ├── elevenlabs_client.py       # 영어 보이스
│   └── generate_narration.py      # narration-script.md → audio/
└── post/
    └── compose_final.py           # MoviePy 타이포그래피 + 페이드 합성
```

`run_scene_pipeline.py` 동작:
1. `video-generation-job.json` 읽어 씬 목록 확보
2. 씬1 Grok 호출 (참조: `00-opening-last.png` + `daehan.jpg`)
3. 결과 저장 → 마지막 프레임 추출 → `01-scene-last.png`
4. 씬2 호출 시 `01-scene-last.png`를 참조로 자동 주입
5. (반복) 씬N까지
6. 각 단계마다 JSON 구조화 로그 기록

모든 스크립트는 idempotent + deterministic seed + exit code 규칙 준수.  
상세: [automation-integration.md §4](./automation-integration.md)

## 6. 액션 기반 퀴즈 포맷 (신규, 기존 정적 퀴즈 대체 제안)

**사용자 질문**: 기존 퀴즈 포맷을 더 자연스럽게 바꾸려면?

**기존 방식의 한계**:
- 캐릭터가 칠판 앞에 서서 문장을 그냥 제시 → 정답 공개 → 따라하기
- 씬마다 캐릭터 포즈가 비슷해 "컷이 붙지 않는" 문제와 맞물려 지루함
- 퀴즈의 재미가 약해 엔게이지먼트 떨어짐

**제안: "연기 → 문장 → 빈칸 퀴즈 → 정답 공개" 4단계 포맷**

예문 "풍선을 너무 크게 불었더니 결국 **빵** 터져 버렸다." (focus word: **빵**)

| 씬 | 길이 | 내용 | 의도 |
|----|------|------|------|
| 오프닝 | 3s | 기존 `01_Opening.mp4` + 검정 페이드 | 인사·도입 |
| **씬1 — 상황 연기** | 5s | 대한이 풍선을 들고 점점 크게 부는 연기. 표정: 장난스러운 집중 | 예문 상황을 시각적으로 각인 |
| **씬2 — 결정적 순간** | 4s | 풍선이 터지고 대한이 놀라는 순간. "빵!" 효과음 | Focus word "빵"의 감각적 기억 |
| **씬3 — 칠판 문제 제시** | 6s | 대한이 칠판 앞에서 "풍선을 너무 크게 불었더니 결국 ___ 터져 버렸다" 빈칸 문장 소개. 보기 ①②③ 제시 | 퀴즈 |
| **씬4 — 정답 공개 + 따라하기** | 6s | 대한이 "정답은 빵!" 외치며 환하게 웃음. 시청자 따라하기 유도 | 보상·학습 |
| 엔딩 | 3s | 기존 `02_Ending.mp4` + 검정 페이드 ("도움이 좀 되셨나요? 그럼 안녕~!") | 마무리 |

**이 포맷의 장점**:
- **자연스러운 움직임**: 씬마다 포즈·표정·감정이 크게 바뀌어 컷이 "이어지는" 게 아니라 "흐르는" 느낌
- **focus word의 감각적 기억**: "빵"을 단어가 아닌 장면으로 먼저 각인
- **퀴즈의 재미**: 시청자는 씬1~2로 답을 거의 눈치채지만, 빈칸 문제로 확인하는 "정답 확신의 즐거움" 제공
- **반복 재생성 가능**: DB에서 가져온 문장마다 "상황 연기 + 결정적 순간"으로 치환 가능 → 일반화된 템플릿 가능

**일반화된 템플릿**:
1. 상황 연기 (focus word가 발생하는 장면을 캐릭터가 연기)
2. 결정적 순간 (focus word의 핵심 감정·효과음)
3. 칠판 문제 (빈칸 + 보기 3개)
4. 정답 공개 + 따라하기

DB에서 가져온 예문마다 focus word의 품사·유형에 따라 연기 패턴만 바꾸면 됨.

## 7. 오프닝·엔딩 재사용 전략

| 전략 | 장점 | 단점 |
|------|------|------|
| **A. 그대로 재사용** | 추가 생성 비용 없음, 목소리 원본 보존 | 본편 캐릭터와 드리프트 가능성 |
| **B. 오프닝 재생성** | 캐릭터 완벽 일관 | 생성 비용 + 원본 목소리 상실 (Supertone 클론으로 복제해야 함) |
| **C. 하이브리드** | 오프닝 재사용 + 0.3s 페이드로 시각적 차이 완화 | 파일럿 1차에 최적 |

**권장**: **C 전략으로 파일럿 1차 진행**. 결과 보고 드리프트 체감 심하면 **B 전략(재생성)** 으로 파일럿 2차.

## 8. 제작 순서 (파일럿 기준)

1. **DB 예문 확정** — 이미 정해짐: "풍선을 너무 크게 불었더니 결국 빵 터져 버렸다."
2. **scene-plan.md 작성** — §6의 4단계 씬별 상세 스토리보드
3. **오프닝 마지막 프레임 추출** — `extract_last_frame.py characters/daehan/01_Opening.mp4`
4. **Supertone 클론 보이스 준비 확인** — 이미 사용자 등록 완료
5. **나레이션 스크립트 작성** — 한국어·영어 각각
6. **TTS 생성** — `generate_narration.py` (Supertone ko + ElevenLabs en)
7. **video-generation-job.json 작성** — 씬1~4 프롬프트 + 참조 이미지 경로
8. **Grok 씬 파이프라인 실행** — `run_scene_pipeline.py`
9. **ffmpeg로 합성 + 페이드 전환** — 오프닝 + 씬1~4 + 엔딩
10. **칠판 타이포그래피 합성** — 편집툴에서 빈칸 문장·정답·자막 오버레이
11. **QA 검수** (§9)
12. **파일럿 회고** — 드리프트·컷 연결·음성 매칭 점수 기록 → 2차 개선 계획

## 9. QA 체크리스트

### 자연스러움
- [ ] 오프닝 → 씬1 경계가 튀지 않음 (0.3초 페이드 정상)
- [ ] 씬1 → 씬2 → 씬3 → 씬4 사이 캐릭터 포즈·조명 이어짐
- [ ] 씬4 → 엔딩 경계가 튀지 않음
- [ ] 전체 영상이 한 편처럼 느껴짐

### 캐릭터 일관성
- [ ] 오프닝과 본편의 대한이 같은 사람으로 보임
- [ ] 갓·두루마기·검은 장갑·은발·보라 눈동자 모든 씬에서 유지
- [ ] 표정 변화는 있어도 외형 드리프트는 없음

### 오디오
- [ ] 한국어 남성 목소리가 오프닝·본편·엔딩 동일 (Supertone 클론)
- [ ] 한국어·영어 나레이션 순차 재생 (겹침 없음)
- [ ] 로마자 TTS 없음

### 콘텐츠
- [ ] 빈칸 문장 정확, 보기 3개 제시
- [ ] 정답 "빵" 공개 시점에 시각·효과음 동기화
- [ ] 엔딩 대사 "도움이 좀 되셨나요? 그럼 안녕~!" 포함

### 포맷
- [ ] 16:9 가로, 1920×1080
- [ ] 총 길이 28~32초
- [ ] 칠판에 AI 생성 텍스트 없음 (후반 타이포만)

## 10. 파일럿 이후 템플릿화 계획

파일럿이 성공하면 범용 템플릿으로 승격:

```
episodes/_template-v2-seamless/
├── AGENT_WORKFLOW_V2.md
├── pilot-spec.template.md
├── scene-plan.template.md
├── source-packet.template.json
├── narration-script.template.md
├── video-generation-job.template.json
└── post/
    └── chalkboard-text-spec.template.md
```

DB 연동(`used_sentences.jsonl`, SQL 쿼리 등)은 v2 템플릿 단계에서 `malmoelab-template`의 워크플로우를 이식.

## 11. 결정 완료 요약

| 항목 | 결정 |
|------|------|
| 폴더 | `episodes/daehan-pilot-001/` |
| 길이 | 30초 |
| 예문 | 풍선을 너무 크게 불었더니 결국 빵 터져 버렸다. |
| 퀴즈 포맷 | 액션 기반 4단계 (§6) |
| 오프닝·엔딩 | 기존 재사용 + 0.3s 페이드 (C 전략, §7) |
| TTS | Supertone(ko) + ElevenLabs(en) 병행 |
| 프레임 매칭 | 자동 스크립트 (`scripts/pilot/`) |
| 페이드 길이 | 0.3초 |
| 엔딩 대사 | "도움이 좀 되셨나요? 그럼 안녕~!" |
| 후반 타이포그래피 도구 | MoviePy (추후 Remotion 이식 가능) |
| CLI 진입점 | 파일럿부터 심어둠 (`scripts/` 하위 각 모듈이 CLI) |
| YouTube 업로드 privacy | `private` (파일럿 이후 단계에서 적용) |

## 12. 다음 액션

사용자 확인 후 착수할 순서:
1. `scene-plan.md` 작성 (씬1~4 세부 스토리보드)
2. `scripts/pilot/extract_last_frame.py`, `run_scene_pipeline.py` 구현
3. `scripts/tts/` 듀얼 TTS 래퍼 구현
4. `video-generation-job.json` 스펙 확정
5. 실제 파일럿 1회차 실행
