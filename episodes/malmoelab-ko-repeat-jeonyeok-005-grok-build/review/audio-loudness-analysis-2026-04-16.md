# Audio Loudness Analysis: malmoelab-ko-repeat-jeonyeok-005-grok-build
날짜: 2026-04-16

## 증상
- `scene-0-opening`과 `scene-1-question`의 최종 MP4 구간 음량이 뒤쪽 씬보다 체감상 작게 들림

## 원인
- TTS 세그먼트 파일 자체는 `mean_volume ~= -19 dB`로 정상 정규화되어 있었음
- 문제는 최종 `narration-mix.m4a`를 만들 때 `amix`가 입력 정규화를 적용하면서, 짧은 초반 나레이션 구간이 과하게 눌린 점
- 특히 지연된 다수의 입력이 있는 구조에서 초반 질문 구간 레벨이 지나치게 낮아졌음

## 적용한 수정
- [render_repeat_fill_blank_grok.py](/home/kindsr/projects/shortform-factory-studio/scripts/render_repeat_fill_blank_grok.py:1419)의 `amix`에 `normalize=0`을 추가
- 프레임 렌더는 유지하고 오디오 믹스와 최종 MP4만 재생성

## 수정 후 측정
최종 MP4 구간별 `volumedetect`:

- `scene-0-opening (0.0-6.0s)`: `mean -22.5 dB`, `max -6.6 dB`
- `scene-1-question (6.0-12.0s)`: `mean -27.0 dB`, `max -7.9 dB`
- `scene-3-answer (15.2-21.2s)`: `mean -25.7 dB`, `max -7.9 dB`
- `scene-4-repeat (21.2-37.6s)`: `mean -29.0 dB`, `max -8.0 dB`
- `scene-5-ending (37.6-42.6s)`: `mean -25.9 dB`, `max -4.5 dB`

## 결론
- 사용자가 지적한 초반 구간은 `scene-3-answer`와 `scene-4-repeat`에 근접한 수준으로 맞춰짐
- `scene-5-ending`은 짧은 작별 인사 특성상 약간 더 뜨지만, 전체 흐름상 허용 가능한 범위로 판단
