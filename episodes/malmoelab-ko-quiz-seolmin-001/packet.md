# malmoelab-ko-quiz-seolmin-001

## Metadata

- 작업 유형: `new_episode`
- 시리즈: `malmoelab-hangul-quiz`
- 포맷: `malmoelab-keyframe-dub-after-picture-v1`
- 기준 레퍼런스: `daehan-pilot-codex-003`
- 목표 길이 / 비율: `30s` / `16:9`
- source issue: [SHO-28](/SHO/issues/SHO-28)
- 상위 이슈: [SHO-27](/SHO/issues/SHO-27)
- protagonist: `seolmin`
- character mode: `reference-only`
- source packet: `./source-packet.json`
- episode schema: `./episode.schema.json`
- keyframe plan: `./keyframe-plan.json`
- voice slots: `./voice-slots.json`
- typography slots: `./typography-slots.json`
- video generation job: `./video-generation-job.json`

## Structure Lock

- `003`와 같은 5-scene lesson형 구조를 유지한다.
- scene 순서:
  1. `scene-1-opening-handoff`
  2. `scene-2-lesson-intro`
  3. `scene-3-repeat-listen`
  4. `scene-4-quiz-point`
  5. `scene-5-ending-wave`
- 각 scene은 기본 `6초`다.
- keyframe 5장을 먼저 승인받고 난 뒤에만 scene video를 생성한다.
- video generation 단계에서는 글자를 넣지 않는다.
- picture lock 뒤에만 더빙과 타이포를 합성한다.

## Lesson Lock

- focus word: `학생`
- sentence: `학생이 학교에 갑니다.`
- blank sentence: `___이 학교에 갑니다.`
- sentence translation: `The student goes to school.`
- sentence romanization: `haksaengi hakgyoe gapnida.`
- blank romanization: `___i hakgyoe gapnida.`
- CTA copy: `malmoelab.com에서 더 알아보아요.`

## Script Lock

- opening line:
  - `안녕하세요. 여러분과 한글을 함께 공부할 설민입니다!`
- lesson intro line:
  - `오늘 배울 문장은 학생이 학교에 갑니다, 입니다.`
- repeat cue:
  - `따라해 볼까요?`
- repeat sentence:
  - `학생이 학교에 갑니다.`
- quiz line:
  - `빈칸에 들어갈 말은 무엇일까요?`
- ending line:
  - `말모이랩닷컴에서 더 알아보아요. 안녕!`

## Visual Lock

- 설민은 `characters/seolmin/Seolmin.png`와 같은 2D chibi teacher identity를 유지한다.
- 설민은 항상 화면 오른쪽 쿼터에 서 있고, 칠판은 왼쪽 학습면으로 남긴다.
- 칠판은 scene generation 단계에서 완전히 비어 있어야 한다.
- `scene-1`은 승인된 `kf-01`로 시작한다.
- `scene-2~5`는 이전 scene 마지막 프레임을 다음 scene 시작 seed로 사용한다.

## Production Order

1. `source-packet.json` 잠금
2. `episode.schema.json` + `packet.md` + `keyframe-plan.json` 잠금
3. `voice-slots.json` + `typography-slots.json` 잠금
4. keyframe 생성 및 review
5. scene video 생성
6. picture preview 확인
7. dub
8. typography
9. final QA

## Notes

- 이번 회차는 기존 15초 micro-quiz 구조를 폐기하고 `003` 구조로 다시 제작한다.
- 설민은 고정 ending asset이 없어도 `scene-5-ending-wave`를 생성형 shot으로 유지한다.
- opening과 ending의 멘트 구조는 `003` 기준을 그대로 사용하고, 이름만 `대한 -> 설민`으로 바꾼다.
