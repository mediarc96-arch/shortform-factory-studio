# daehan-pilot-codex-003-C · 하이브리드 (정적 오프닝/엔딩 + Grok 본편)

**옵션 C: 오프닝·엔딩은 정적 2D, 본편 3씬만 Grok img2vid**

가장 리스크가 낮은 하이브리드 접근. 짧은 오프닝/엔딩은 정적 2D로 안정적으로 처리하고, 가장 중요한 본편 3씬만 Grok으로 생동감 확보.

## 구성 요소

- **베이스 이미지**: `docs/example/Daehan_2D.jpg` 정제판
- **5개 키프레임**: A/B와 동일 생성
- **2개 정적 블록**: KF1 (오프닝), KF5 (엔딩) — Ken-burns 줌 + TTS만
- **3개 Grok img2vid 클립**: KF2, KF3, KF4 → 각 6초 영상
  - KF2 → follow-me 말하기 (6초)
  - KF3 → follow-me 듣기 (6초)
  - KF4 → quiz 가리키기 (6초)

## 장점
- Grok 호출 3회로 감소 (B 대비 40% 절감)
- 오프닝/엔딩 실패 리스크 없음 (정적)
- 본편에서 캐릭터 모션 확보

## 단점
- 오프닝/엔딩과 본편의 "움직임 양" 격차 느껴질 수 있음 (완화: ken-burns + 자막 페이드로 템포 유지)

## 파일 구성

| 파일 | 용도 |
|------|------|
| `README.md` | 이 문서 |
| `pilot-spec.md` | 나레이션 스크립트·비트·타이밍 |
| `keyframe-plan.json` | 5개 키프레임 스펙 |
| `grok-jobs/keyframe-0X-*.json` | Grok 이미지 API 호출 5개 |
| `grok-jobs/video-scene-02-*.json` | Grok img2vid 호출 (follow-me speak) |
| `grok-jobs/video-scene-03-*.json` | Grok img2vid 호출 (follow-me listen) |
| `grok-jobs/video-scene-04-*.json` | Grok img2vid 호출 (quiz point) |

KF1/KF5는 비디오 호출 없이 정적 이미지 그대로 사용.

## 사용자 검수 체크포인트

1. 키프레임 5장 생성 → 리뷰 → 승인
2. 승인된 KF2/KF3/KF4 각각 Grok img2vid → 3개 클립 → 리뷰
3. 클립 OK → `compose_final.py`로 [정적 KF1 ken-burns] + [3 img2vid 본편] + [정적 KF5 ken-burns] + 타이포·TTS·자막 합성
