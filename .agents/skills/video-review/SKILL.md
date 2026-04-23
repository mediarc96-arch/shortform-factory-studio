---
name: video-review
version: 1.0.0
description: |
  Review AI-generated video episodes (Grok, Runway, etc.) using contact sheets,
  frame maps, and episode packets. Produces structured scene-by-scene feedback
  in the standard format: scene-id / frame N / issue description.
  Use when the user wants to QA a rendered video, check character consistency,
  verify text overlays, or approve an episode before publish.
allowed-tools:
  - Read
  - Glob
  - Bash
  - AskUserQuestion
---

# Video Review Skill

이 스킬은 Grok, Runway 등 AI 도구로 생성된 단편 영상 에피소드를 리뷰합니다.
contact sheet(장면별 이미지 그리드), frame-map.csv, scene-ranges.csv, 에피소드 패킷을 함께 읽어
구조화된 피드백을 생성합니다.

---

## Step 1 — 리뷰 대상 확인

사용자가 경로를 주지 않으면 아래 순서로 탐색합니다.

```bash
# 최근 수정된 review 폴더 찾기
find . -type d -name "review" | sort
```

review 폴더가 여럿이면 `AskUserQuestion`으로 어느 에피소드를 리뷰할지 물어봅니다.

---

## Step 2 — 에피소드 패킷 로드

review 폴더의 상위 에피소드 디렉터리에서 `packet.md`를 찾아 읽습니다.

```
<episode-dir>/packet.md        (또는 narration-script.md)
```

없으면 건너뜁니다. 패킷이 있으면 다음 항목을 기억해 둡니다:
- 에피소드 제목, 목표
- 씬 목록과 각 씬의 예상 내용
- 캐릭터 이름, 의상, 표정 지시사항
- 자막/텍스트 오버레이 내용

---

## Step 3 — 씬 범위 로드

```bash
cat <review-dir>/scene-ranges.csv
```

출력 형식 예시:
```
scene_id,start_sec,end_sec,start_frame,end_frame
scene-0-opening,0.000,6.000,0,179
```

각 씬 ID와 프레임 범위를 기억합니다.

---

## Step 4 — Contact Sheet 시각 분석

overview 이미지를 먼저 읽고, 씬별 이미지를 순서대로 읽습니다.

```
<review-dir>/contact-sheets/overview.jpg
<review-dir>/contact-sheets/scene-0-opening.jpg
<review-dir>/contact-sheets/scene-1-question.jpg
... (이하 씬 순서대로)
```

각 이미지를 읽으면서 아래 항목을 체크합니다.

### 시각 체크리스트

| 항목 | 체크 포인트 |
|------|-------------|
| **캐릭터 일관성** | 얼굴, 의상, 헤어가 씬 간 동일한가 |
| **화면 구도** | 피사체 위치, 여백, 텍스트 공간 확보 여부 |
| **텍스트/자막** | 오버레이가 너무 높거나 낮지 않은가, 가독성 |
| **조명·색조** | 씬 간 급격한 색온도 변화 없는가 |
| **모션·자연스러움** | 뭉개진 손, 얼굴 왜곡, 불자연스러운 움직임 |
| **배경 일관성** | 배경 오브젝트가 씬 중간에 사라지거나 변하지 않는가 |
| **씬 전환** | 컷 포인트에서 급격한 점프 없는가 |

패킷이 있으면 추가 체크:
- 자막 텍스트가 패킷의 대사와 일치하는가
- 씬 순서가 스크립트 순서와 일치하는가
- 정답 텍스트, 퀴즈 문장이 정확하게 표시되는가

---

## Step 5 — 피드백 작성

이슈는 반드시 아래 형식으로 작성합니다.

```
<scene-id> / frame <N> / <이슈 설명>
```

또는 타임코드 형식:

```
<MM:SS.mmm> / <scene-id> / <이슈 설명>
```

예시:
```
scene-3-answer / frame 492 / 칠판 텍스트가 너무 위쪽에 배치됨
scene-1-question / frame 210 / 선생님 오른손 손가락 왜곡
00:16.400 / scene-3-answer / 자막 폰트가 이전 씬과 다름
```

이슈가 없는 씬은 `scene-0-opening / PASS` 처럼 표기합니다.

---

## Step 6 — 요약 리포트 출력

아래 구조로 리뷰 리포트를 마크다운으로 출력합니다.

```markdown
# Video Review: <episode-id>
날짜: <오늘 날짜>

## 전체 요약
- 총 씬 수: N
- 이슈 있는 씬: N
- PASS 씬: N
- 심각도: 🔴 블로커 / 🟡 주의 / ✅ 이상 없음

## 씬별 결과

### scene-0-opening ✅
PASS

### scene-3-answer 🔴
- frame 492 / 칠판 텍스트가 너무 위쪽에 배치됨
- frame 510 / 손가락 왜곡

## 권고 사항
- 재렌더 필요 씬: [list]
- 포스트 편집으로 수정 가능: [list]
- 무시 가능: [list]
```

심각도 기준:
- 🔴 **블로커**: 캐릭터 얼굴 심각 왜곡, 잘못된 자막 텍스트, 씬 누락
- 🟡 **주의**: 구도 어색함, 경미한 손 왜곡, 색조 차이
- ✅ **PASS**: 문제 없음

---

## 선택적 — review 폴더에 리포트 저장

사용자가 저장을 원하면:

```bash
# review 폴더에 리포트 파일로 저장
cat > <review-dir>/review-report.md << 'EOF'
<리포트 내용>
EOF
```

---

## 참고: 이 프로젝트의 표준 review 폴더 구조

```
episodes/<episode-id>/review/
├── README.md
├── scene-ranges.csv
├── frame-map.csv
└── contact-sheets/
    ├── overview.jpg
    ├── scene-0-opening.jpg
    ├── scene-1-question.jpg
    └── ...
```

review 폴더가 없다면 사용자에게 먼저 contact sheet 생성 스크립트를 실행하도록 안내합니다.
