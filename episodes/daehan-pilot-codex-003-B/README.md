# daehan-pilot-codex-003-B · 2D 시드 → Grok img2vid 전체

**옵션 B: 2D 키프레임을 시드로 Grok img2vid 전 구간 적용**

오프닝·본편·엔딩 모두 Grok img2vid로 생성. 시드는 공통 `Daehan_2D.jpg`에서 포즈만 바꾼 5개 키프레임.

## 구성 요소

- **베이스 이미지**: `docs/example/Daehan_2D.jpg` 정제판 (칠판 텍스트 제거)
- **5개 키프레임**: A와 동일 생성 → 각각 Grok img2vid의 시드 이미지
- **5개 비디오 클립**: 각 키프레임에서 시작하는 6초 img2vid
  - KF1 → 3초 오프닝 클립
  - KF2 → 6초 follow-me 클립
  - KF3 → 6초 listen 클립
  - KF4 → 6초 quiz 클립
  - KF5 → 3초 엔딩 클립
- **기존 3D 오프닝/엔딩 클립 (`01_Opening.mp4`, `02_Ending.mp4`) 은 사용하지 않음** — 스타일 일관성 위해

## 장점
- 시작 프레임이 명확히 locked → 드리프트 최소화
- 캐릭터 모션 (눈 깜빡임, 입 움직임, 제스처) 자연스러움
- 오프닝·엔딩도 2D 스타일로 통일

## 단점
- Grok 호출 5회 → A 대비 느리고 비용 높음
- Grok이 2D 스타일을 유지할지 불확실 (3D로 drift 가능성)
- 품질 예측 불가 → 재생성 반복 필요할 수 있음

## 파일 구성

| 파일 | 용도 |
|------|------|
| `README.md` | 이 문서 |
| `pilot-spec.md` | 나레이션 스크립트·비트·타이밍 |
| `keyframe-plan.json` | 5개 키프레임 스펙 |
| `grok-jobs/keyframe-0X-*.json` | Grok 이미지 API 호출 5개 (시드 생성) |
| `grok-jobs/video-scene-0X-*.json` | Grok img2vid API 호출 5개 (각 KF → 6초 클립) |

## 사용자 검수 체크포인트

1. 키프레임 5장 생성 → 리뷰 → 승인
2. 승인된 KF 각각을 Grok img2vid에 투입 → 5개 클립 생성 → 리뷰
3. 클립 품질 OK → `compose_final.py`로 타이포·TTS·자막·WIPE 트랜지션 합성
