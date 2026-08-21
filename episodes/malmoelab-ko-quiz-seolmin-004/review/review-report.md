# Keyframe Review Report

- episode: `malmoelab-ko-quiz-seolmin-004`
- status: `review-ready`
- basis image: `characters/seolmin/Seolmin.png`
- clean base: `assets/refs/seolmin-2d-clean-base-wide-refined.jpg`

## Generated Keyframes

- `kf-01-opening-handoff`: `standard 003 greeting handoff` -> `keyframes/kf-01-opening-handoff.jpg`
- `kf-02-lesson-intro`: `full sentence introduction` -> `keyframes/kf-02-lesson-intro.jpg`
- `kf-03-repeat-listen`: `repeat after me pause` -> `keyframes/kf-03-repeat-listen.jpg`
- `kf-04-quiz-point`: `blank sentence recall check` -> `keyframes/kf-04-quiz-point.jpg`
- `kf-05-ending-wave`: `cta goodbye` -> `keyframes/kf-05-ending-wave.jpg`

## Review Checklist

- 2D 설민 스타일이 characters/seolmin/Seolmin.png와 계속 같아 보이는가
- 왼쪽 칠판이 비어 있고 글자가 전혀 없는가
- 설민이 오른쪽 쿼터 근처에 일관되게 서 있는가
- 모자, 복장, 귀걸이, 붉은 술 장식이 유지되는가
- 5-scene 구조가 scene-1-opening-handoff부터 scene-5-ending-wave까지 유지되는가
- 학교 예문 텍스트는 생성 이미지가 아니라 후반 typography로만 들어가도록 남겨져 있는가
- 다섯 장의 포즈 차이가 한눈에 읽히는가
- 1_Opening_Seolmin.mp4 파일명 불일치가 downstream caveat로 유지되는가

## Next Step

- Approve or reject each keyframe before generating any 6-second scene videos.
- After approval, each scene must declare a start frame, end frame, and boundary mode. Use `continuous_handoff` only when the next scene should start from the previous scene's final frame; use `transition_cut` when a planned edit transition bridges different frames.
