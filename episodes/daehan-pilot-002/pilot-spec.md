# Daehan Pilot 002 — 개요

pilot-001과 동일한 캐릭터·채널이되, 아래 피드백을 반영한 2차 파일럿:

- **트랜지션**: fadeblack → **WIPE (좌→우)** 로 교체 (오프닝↔컨텐츠, 컨텐츠↔엔딩 경계)
- **컨텐츠 구조 변경**: 풍선 빵→ "아기의 옹알이가 하루 종일 이어졌다." 문장 학습 플로우
- **퀴즈 방식**: 정답 보기 선지 노출 없음. 빈칸 문장 + malmoelab.com CTA 로 유도
- **TTS**: Supertone 클론 Voice 1 (변경 없음), 세그먼트 타이밍을 재설계
- **타이포**: pilot-001에서 어색했던 부분 수정 (폰트 크기↑, 중앙정렬 정밀화, 빈칸 박스 개선)

관련 문서: [source-packet.json](./source-packet.json) · [scene-plan.md](./scene-plan.md) · [narration-script.md](./narration-script.md) · [video-generation-job.json](./video-generation-job.json)

## 30초 타임라인

| 구간 | 시간(s) | 내용 | 매체 |
|------|---------|------|------|
| Opening | 0.0 – 3.0 | "안녕하세요. 대한이에요!" | `characters/daehan/01_Opening.mp4` |
| **WIPE** | 3.0 – 3.5 | 좌→우 wipe (0.5s) | post-production |
| Scene 1 | 3.5 – 7.5 | 오늘의 문장 소개 + 낭독 | Grok (4s) |
| Scene 2 | 7.5 – 17.5 | "따라해 볼까요?" + 문장 + 묵음 pause | Grok (10s) |
| Scene 3 | 17.5 – 26.2 | 빈칸 퀴즈 노출 + malmoelab.com CTA | Grok (9s, 8.7s로 트리밍) |
| **WIPE** | 26.2 – 26.7 | 좌→우 wipe (0.5s) | post-production |
| Ending | 26.7 – 30.0 | "도움이 좀 되셨나요? 그럼 안녕~!" | `characters/daehan/02_Ending.mp4` |

## TTS 세그먼트 (Supertone Voice 1)

| 시작(s) | 세그먼트 | 텍스트 | 속도 | 비고 |
|---------|---------|--------|------|------|
| 3.7 | intro | 아기의 옹알이가 하루 종일 이어졌다. | 0.95× | 문장 소개, 칠판에 동시 표시 |
| 8.0 | follow-prompt | 따라해 볼까요? | 1.0× | 호기심 톤 |
| 10.3 | repeat | 아기의 옹알이가 하루 종일 이어졌다. | 0.95× | 또박또박 낭독 |
| (13.8–17.3) | *silent* | — | — | repeat 길이만큼 시청자 pause |
| 20.0 | cta | malmoelab.com에서 더 알아보아요. | 1.0× | 친근한 안내 톤 |

실제 TTS 길이를 측정한 뒤 타이밍 offset 재조정 (see `audio/narration-timing.json`).

## 타이포그래피 개선 포인트 (vs pilot-001)

1. 칠판 중앙정렬 기준점을 zone 중심으로 재계산 (이전엔 text width 계산이 부정확해 살짝 치우쳤음)
2. Scene 1 문장 표시: **typewriter stroke reveal** (한 글자씩 쓰이는 효과, TTS 페이스에 맞춤)
3. 빈칸 토큰 `___` → 실제 노란 박스 렌더 (밑줄 3개 아님). 박스 안은 비워둠
4. 폰트 크기 상향: 문장 64→84pt, 자막 36→44pt
5. 자막 하단 배경: 반투명 검정 바 깔아서 가독성 확보
6. CTA "malmoelab.com" 하단 컨텐츠 영역에 버튼처럼 표시

## 자동화 관점

pilot-001과 동일한 `run_pilot.py` 엔트리로 `--episode-dir episodes/daehan-pilot-002` 실행만으로 전체 파이프라인 재사용. `compose_final.py` 는 `transitionsBetweenClips` 키의 `type` 필드를 읽어 `wipe` / `fadeblack` 모두 지원하도록 확장.
