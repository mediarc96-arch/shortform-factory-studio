# Daehan Pilot Codex 003

## 메타데이터

- 에피소드 슬러그: `daehan-pilot-codex-003`
- 시리즈: `daehan-pilot-codex`
- 주인공: `daehan`
- 포맷 프로필: `keyframe-review-v1`
- 형식: `2d-keyframe-review-first`
- 목표 길이: `30초`
- 비율: `16:9`
- 출력 대상: `episodes/daehan-pilot-codex-003/`

## 이번 실험의 핵심 변화

- 기존 3D 대한이 아니라 `docs/example/Daehan_2D.jpg`를 주인공 기준 이미지로 사용한다.
- 오프닝/본편/엔딩을 한 번에 만들지 않고, 먼저 `clean base + 5 keyframe`을 생성해 사용자 검수 후 다음 단계로 넘어간다.
- 영상 생성 단계에서는 음성과 한글 텍스트를 넣지 않는다.
- 후반 작업에서만 `Supertone` 더빙과 `손글씨 느낌의 굵은 칠판 타이포`를 올린다.
- 최종 영상은 `scene-1` 시작을 승인된 `keyframe-01`로 두고, 이후 각 씬의 마지막 프레임을 다음 씬의 첫 프레임 seed로 사용하는 연속성 방식을 목표로 한다.

## 재사용 자산

- 기준 이미지: `docs/example/Daehan_2D.jpg`
- 캐릭터 바이블: `characters/daehan/bible.md`
- 프롬프트 세트: `characters/daehan/prompts.md`
- 폰트: `shared/fonts/NanumPenScript-Regular.ttf`, `shared/fonts/NanumGothic-Bold.ttf`

## 대본 소스

- `daehan-pilot-codex-002`의 대본을 그대로 재사용한다.
- 예문: `아기의 옹알이가 하루 종일 이어졌다.`
- 빈칸 문장: `아기의 ___가 하루 종일 이어졌다.`
- 정답 단어: `옹알이`
- CTA: `malmoelab.com에서 더 알아보아요.`

## 키프레임 구성

1. `kf-01-opening-handoff`
   - 오프닝 종료 느낌의 차분한 미소
2. `kf-02-lesson-intro`
   - 오늘 배울 문장을 소개하는 말하기 포즈
3. `kf-03-repeat-listen`
   - 따라하기를 유도하는 경청 포즈
4. `kf-04-quiz-point`
   - 빈칸 퀴즈 쪽을 가리키는 포즈
5. `kf-05-ending-wave`
   - 엔딩 인사 포즈

## 현재 상태

- 상태: `picture-preview-ready`
- clean base: `assets/refs/daehan-2d-clean-base-wide-refined.jpg`
- keyframes: `keyframes/*.jpg`
- picture scenes: `renders/picture/*.mp4`
- picture preview: `renders/final/daehan-pilot-codex-003-picture-preview.mp4`
- review bundle: `review/review-report.md`, `review/picture-review-report.md`, `review/contact-sheets/overview.jpg`
- 아직 하지 않은 일: TTS 더빙, 손글씨 칠판 타이포, 최종 음성 합성

## 다음 단계

1. picture preview를 보고 scene별 motion drift가 더 줄어들어야 하는지 결정한다.
2. 확정되면 현재 picture cut을 기준으로 `Supertone` 더빙만 얹는다.
3. 그 다음 손글씨 칠판 타이포를 후반 합성한다.
