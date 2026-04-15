# malmoelab-ko-quiz-002

## Metadata

- 작업 유형: `new_episode`
- 시리즈: `malmoelab-hangul-quiz`
- 포맷: 15초 한글 빈칸 퀴즈 쇼츠
- 목표 길이 / 비율: `15s` / `9:16`
- 학습 대상: 영어권 초급 한국어 학습자
- source issue: [SHO-20](/SHO/issues/SHO-20)
- 상위 이슈: [SHO-18](/SHO/issues/SHO-18)
- source packet: `./source-packet.json`
- reference packet path: `/home/kindsr/projects/shortform-factory-studio/shared/backgrounds/images/korean/teacher.png`
- protagonist: classroom teacher background plate only; named recurring protagonist 없음
- character mode: `reference-only`
- character training: 사용하지 않음
- disclosure plan: metadata-only disclosure and attribution in publish metadata; visible-frame AI disclosure 없음

## Viewer Promise

- 지금 클릭해야 하는 이유: 15초 안에 실전 한국어 문장에서 빠진 초급 단어 하나를 맞히고 바로 정답과 뜻까지 확인할 수 있다.
- 핵심 약속: 영어권 학습자가 `집`을 문장 맥락으로 익힌다.
- angle: 단어 암기가 아니라 실제 문장 속 빈칸 추론으로 체감 난이도를 낮춘다.
- click test: 제목/썸네일/첫 2초는 모두 "빈칸 퀴즈" 약속을 같은 메시지로 전달해야 한다.

## Source Lock

- focus word: `집`
- romanization: `jip`
- gloss: `house`
- example sentence: `저녁에는 집에서 쉽니다.`
- blanked sentence: `저녁에는 ___에서 쉽니다.`
- sentence translation: `I rest at home in the evening.`
- sentence romanization lock:
  - blanked: `jeonyeokeneun ___eseo swipnida.`
  - full: `jeonyeokeneun jipeseo swipnida.`
- reuse status: `unused_example_selected`
- note: source romanization had bad stored data, so downstream should trust the normalized values in `source-packet.json` and not re-pull romanization manually.

## Hook And Copy Lock

- recommended opening promise: `Which word fits the blank?`
- allowed hook variants:
  - `Can you fill in this Korean blank?`
  - `Beginner Korean quiz: one missing word`
- engagement copy lock: `Double tap if you know it.`
- reveal line lock: `Answer: 집`
- CTA lock: `Learn more at malmoelab.com`
- title card lock:
  - title: `말모이랩 한글공부`
  - subtitle: `15-second fill-in-the-blank quiz`
- copy guardrails:
  - `Double tap` is engagement copy only; do not imply tapping reveals the answer.
  - Do not promise app features or interactivity Shorts does not have.
  - Keep all on-screen English simple enough for quick mobile reading.

## Retention Plan

- `0.0s - 2.0s`: title card establishes this is a fast Korean quiz, not a passive vocab card.
- `2.0s - 9.0s`: blank sentence holds attention; viewer should be solving, not reading a full explanation.
- `9.0s - 11.0s`: honest engagement nudge while the answer remains hidden.
- `11.0s - 15.0s`: reveal the full sentence, answer word, and learning CTA as payoff.
- retention rule: never show `집` in full on the question phase artwork, thumbnail, or first 11 seconds of the edit.

## Structure And Proof

1. Setup
   - Show classroom template with title card.
   - Promise a quick fill-in-the-blank challenge.
2. Question
   - Display `저녁에는 ___에서 쉽니다.` on the board.
   - Keep `Which word fits the blank?` visible as the English prompt.
   - Show romanization support under the Hangul line without crowding the board.
3. Engagement Beat
   - Hold tension with `Double tap if you know it.`
4. Payoff
   - Reveal `Answer: 집`
   - Replace blank with full sentence `저녁에는 집에서 쉽니다.`
   - Keep `house` / sentence meaning legible through reveal context and metadata support.

## Visual And Production Direction

- This episode stays on the established classroom/teacher style; do not escalate to a named character bible or LoRA workflow.
- Use `teacherImage` template path only.
- Do not use Gemini image-generation API for this episode.
- Use `/home/kindsr/projects/shortform-factory-studio/scripts/render_malmoelab_quiz.py` only.
- All Korean text, romanization, English prompt, reveal copy, and CTA must be renderer overlays, not baked into generated imagery.
- Thumbnail should match the quiz promise:
  - classroom/board visual
  - blank sentence or quiz framing visible
  - no revealed answer word on thumbnail

## Asset Requirements

- required inputs:
  - `./source-packet.json`
  - `/home/kindsr/projects/shortform-factory-studio/shared/backgrounds/images/korean/teacher.png`
  - renderer default or episode `render-config.json`
- required outputs:
  - `./final/malmoelab-ko-quiz-002.mp4`
  - `./final/malmoelab-ko-quiz-002-thumb.png`
  - `./publish-packet.json`
- publish packet must include:
  - MalmoeLab source attribution
  - `malmoelab.com` CTA/link
  - any music/background credit used
  - metadata-only AI disclosure if policy requires it

## Risks And Blockers

- No current blocker if production stays template-only.
- Block if anyone swaps in generated panel art, rewrites romanization from another source, or exposes the answer before the reveal beat.
- Block publish if `publish-packet.json` omits MalmoeLab source attribution or CTA.

## Repurpose Notes

- This is already a Shorts-native format; do not stretch it into a talking-head explanation.
- Best reuse path is series continuation: more beginner sentence blanks with the same classroom template and honest quiz framing.
- Preserve consistent opening promise across the series so viewers recognize the format immediately.
