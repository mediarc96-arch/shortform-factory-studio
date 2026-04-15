# malmoelab-ko-quiz-001

- 작업 유형: `new_episode`
- 시리즈: `malmoelab-hangul-quiz`
- 포맷: 15초 한글 빈칸 퀴즈 쇼츠
- 학습 대상: 영어권 한국어 학습자

## Source

- source packet: `./source-packet.json`
- 선택 단어: `병원`
- 영문 gloss: `hospital`
- 예문: `몸이 안 좋아서 병원에 전화했습니다.`
- 영어 번역: `I called the hospital because I was not feeling well.`

## Render

- render config: `./render-config.json`
- 교사/칠판 배경: `/home/kindsr/projects/shortform-factory-studio/shared/backgrounds/images/korean/teacher.png`
- renderer: `/home/kindsr/projects/shortform-factory-studio/scripts/render_malmoelab_quiz.py`
- source fetch tool: `/home/kindsr/projects/shortform-factory-studio/scripts/fetch_malmoelab_source.py`

## Outputs

- final video: `./final/malmoelab-ko-quiz-001.mp4`
- thumbnail: `./final/malmoelab-ko-quiz-001-thumb.png`
- publish packet: `./publish-packet.json`

## Notes

- 온스크린 AI 고지는 넣지 않는다.
- `Double tap` 문구는 좋아요 유도 카피로만 사용한다.
- 업로드 전 QA는 `source-packet.json`, `render-config.json`, 최종 MP4, `publish-packet.json`을 함께 검토해야 한다.
