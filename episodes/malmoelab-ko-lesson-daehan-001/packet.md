# malmoelab-ko-lesson-daehan-001

## Metadata

- 작업 유형: `new_episode`
- 시리즈: `malmoelab-hangul-quiz`
- 포맷: `malmoelab-keyframe-dub-after-picture-v1`
- 기준 레퍼런스: `daehan-pilot-codex-003` (`scene order`, `shot intent`, `ending CTA posture` only)
- 목표 길이 / 비율: `30s` / `16:9`
- 학습 대상: `영어권 초급 한국어 학습자`
- source issue: [SHO-48](/SHO/issues/SHO-48)
- 상위 이슈: [SHO-47](/SHO/issues/SHO-47)
- protagonist: `daehan`
- reference packet path: `/home/kindsr/projects/shortform-factory-studio/characters/daehan`
- character mode: `reference-only`
- character training: `not approved`
- disclosure plan: `description-level disclosure only`
- voice inheritance: `characters/daehan/voice.json`
- voice override: `none requested`
- rights note: `/home/kindsr/projects/shortform-factory-studio/characters/daehan/rights.md`
- source packet: `./source-packet.json`
- episode schema: `./episode.schema.json`
- keyframe plan: `./keyframe-plan.json`

## Viewer Promise

- 지금 클릭해야 하는 이유: `30초 안에 대한 선생님과 함께 교실 맥락의 한국어 문장 하나를 듣고, 따라하고, 마지막 blank recall로 다시 확인할 수 있다.`
- 핵심 약속: 영어권 초급 학습자가 `수업`을 단어 카드가 아니라 `수업이 두 시에 끝납니다.`라는 실제 문장과 시간 표현 맥락으로 익힌다.
- lesson angle: `classroom noun + simple time expression` 조합으로 짧고 바로 이해되는 문장 학습을 만든다.
- click test: 제목, 썸네일, 첫 장면은 모두 `대한과 배우는 짧은 한국어 문장 수업`이라는 같은 약속을 말해야 한다.

## Source Lock

- focus word: `수업`
- romanization: `sueop`
- gloss: `class`
- example sentence: `수업이 두 시에 끝납니다.`
- blanked sentence: `___이 두 시에 끝납니다.`
- sentence translation: `The class ends at two o'clock.`
- sentence romanization lock:
  - blanked: `___i du sie kkeutnapnida.`
  - full: `sueopi du sie kkeutnapnida.`
- reuse status: `unused_example_selected`
- source note: source packet의 romanization은 render fallback이므로 helper 표기일 뿐이다. 학습 신뢰 기준은 자연스러운 한국어 음성과 full sentence meaning이다.

## Hook And Packaging Lock

- recommended opening promise: `대한 선생님과 오늘의 한국어 문장을 배워요`
- allowed hook variants:
  - `30초 안에 교실 한국어 문장 하나를 익혀봐요`
  - `오늘의 한국어 문장을 듣고 마지막에 다시 확인해요`
  - `대한과 함께 배우는 짧은 한국어 교실 문장`
- engagement copy lock: `Double tap if you know it.`
- packaging rule:
  - title, thumbnail, first frame는 `짧은 lesson + 마지막 recall check` 약속을 같이 말해야 한다.
  - 이 회차를 `blind quiz`처럼 과장하지 않는다.
  - scene-2에서 full sentence를 소개하는 구조이므로, downstream packaging은 `learn first, check later` 약속을 깨지 말아야 한다.
- thumbnail/title rule:
  - 대한 + 빈 칠판 + 오늘의 문장 수업 구도는 허용
  - 정답 맞히기만 강조하는 fake urgency copy는 금지
  - AI 기능을 암시하는 가짜 UI 또는 feature claim은 금지

## Retention Plan

- `0.0s - 6.0s`: 대한 greeting으로 친근한 수업 진입을 만든다.
- `6.0s - 12.0s`: full sentence를 바로 소개해 학습 약속을 빠르게 지급한다.
- `12.0s - 18.0s`: repeat cue와 sentence replay로 능동 참여를 만든다.
- `18.0s - 24.0s`: blank sentence recall check로 방금 배운 내용을 다시 확인한다.
- `24.0s - 30.0s`: 짧은 CTA와 farewell wave로 부드럽게 마감한다.
- retention rule: 기본 spoken flow는 `003` 기준 `greeting -> lesson intro -> repeat -> blank quiz -> ending`을 유지한다.

## Structure And Proof Lock

- `003`의 5-scene, 6초 단위 구조와 ending posture를 그대로 유지한다.
- scene 순서:
  1. `scene-1-opening-handoff`
  2. `scene-2-lesson-intro`
  3. `scene-3-repeat-listen`
  4. `scene-4-quiz-point`
  5. `scene-5-ending-wave`
- scene intent:
  - `scene-1-opening-handoff`: 대한 greeting으로 수업을 연다.
  - `scene-2-lesson-intro`: `수업이 두 시에 끝납니다.` full sentence를 소개한다.
  - `scene-3-repeat-listen`: 따라 읽기 리듬을 만들어 문장을 다시 고정한다.
  - `scene-4-quiz-point`: `___이 두 시에 끝납니다.` blank recall로 focus word를 다시 확인한다.
  - `scene-5-ending-wave`: 짧은 service CTA와 대한 인사로 닫는다.
- proof plan:
  - isolated word가 아니라 full sentence를 먼저 제시한다.
  - repeat beat를 넣어 passive watching이 아니라 따라 읽기 동작을 유도한다.
  - quiz beat는 answer discovery가 아니라 lesson recall 용도로 scene-4에 둔다.
  - sentence meaning, time expression, focus word가 서로 따로 놀지 않게 one-sentence lesson으로 고정한다.

## Protagonist And Visual Lock

- 대한의 구조 reference는 `003`이지만, 시각 reference는 `/home/kindsr/projects/shortform-factory-studio/characters/daehan` canon을 따른다.
- visual basis:
  - primary reference: `/home/kindsr/projects/shortform-factory-studio/characters/daehan/daehan.jpg`
  - secondary reference: `/home/kindsr/projects/shortform-factory-studio/characters/daehan/Daehan_KoreanTeacher_3D.jpg`
- visual style target: `warm 3D CG anime teacher`, not `003`의 2D pilot redraw.
- identity lock:
  - silver-white long hair
  - violet eyes
  - black gat with gold band and red tassels
  - black durumagi + white inner collar
  - black gloves
- composition lock:
  - 대한은 항상 화면 오른쪽 쿼터에 선다.
  - 왼쪽 칠판은 학습면으로 비워 둔다.
  - generation 단계에서 칠판과 의상에는 readable text가 baked-in 되면 안 된다.
- production mode:
  - 이번 회차는 `reference-only` 유지다.
  - character-training 또는 LoRA escalation은 승인되지 않았다.
- ending treatment:
  - 고정 ending clip reuse보다 `003` posture를 따른 generated farewell shot을 우선한다.
  - 톤은 밝고 친근해야 하며, 과장된 코미디나 dark fantasy drift는 금지한다.

## Asset And Handoff Requirements

- required strategist outputs:
  - `./packet.md`
  - `./episode.schema.json`
  - `./keyframe-plan.json`
- required downstream inputs:
  - `./source-packet.json`
  - `/home/kindsr/projects/shortform-factory-studio/characters/daehan/bible.md`
  - `/home/kindsr/projects/shortform-factory-studio/characters/daehan/prompts.md`
  - `/home/kindsr/projects/shortform-factory-studio/characters/daehan/voice.json`
- downstream packet must preserve:
  - protagonist: `daehan`
  - reference packet path: `/home/kindsr/projects/shortform-factory-studio/characters/daehan`
  - disclosure posture: `description-level`
  - production mode: `reference-only`
  - structure basis: `003`
  - visual basis: `daehan canon 3D reference pack`
  - voice source: `characters/daehan/voice.json` with no episode-level override unless justified later

## Production Order

1. `source-packet.json` 잠금
2. `packet.md` + `episode.schema.json` + `keyframe-plan.json` 잠금
3. script draft
4. keyframe review
5. picture generation
6. dub
7. typography
8. QA
9. publish packet

## Risks And Assumptions

- assumption: `source-packet.json`의 fallback romanization은 helper copy로만 쓰고, canonical learning signal은 Korean audio + translation pairing으로 본다.
- assumption: `daehan-pilot-codex-003`은 visual canon이 아니라 structural canon이다.
- block if:
  - downstream이 대한을 `003`의 2D look으로 되돌린다.
  - generated frames에 칠판 글씨, 의상 글자, subtitle artifact가 baked-in 된다.
  - source sentence 대신 다른 classroom sentence로 갈아탄다.
  - voice issue가 대한 기본 voice inheritance를 무시하고 override를 넣는다.

## Repurpose Notes

- 재사용할 것:
  - 대한의 warm teacher persona
  - right-quarter teacher / left-board lesson composition
  - `greeting -> lesson -> repeat -> blank recall -> ending` rhythm
- 재사용하지 말 것:
  - 이번 회차의 sentence, focus word, time expression
  - `수업` answer 자체
  - helper romanization fallback을 authoritative teaching claim처럼 쓰는 것
