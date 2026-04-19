# malmoelab-ko-quiz-seolmin-002

## Metadata

- 작업 유형: `new_episode`
- 시리즈: `malmoelab-hangul-quiz`
- 포맷: `malmoelab-keyframe-dub-after-picture-v1`
- 기준 레퍼런스: `daehan-pilot-codex-003`
- 목표 길이 / 비율: `30s` / `16:9`
- 학습 대상: `영어권 초급 한국어 학습자`
- source issue: [SHO-37](/SHO/issues/SHO-37)
- 상위 이슈: [SHO-36](/SHO/issues/SHO-36)
- protagonist: `seolmin`
- reference packet path: `/home/kindsr/projects/shortform-factory-studio/characters/seolmin`
- character mode: `reference-only`
- character training: `not approved`
- disclosure plan: `metadata-only disclosure and attribution; visible-frame AI disclosure 없음`
- voice inheritance: `characters/seolmin/voice.json`
- rights note: `/home/kindsr/projects/shortform-factory-studio/characters/seolmin/rights.md`
- source packet: `./source-packet.json`
- episode schema: `./episode.schema.json`
- keyframe plan: `./keyframe-plan.json`

## Viewer Promise

- 지금 클릭해야 하는 이유: `30초 안에 설민과 함께 한국어 문장 하나를 듣고, 읽고, 따라하고, 마지막에 빈칸 퀴즈로 다시 확인할 수 있다.`
- 핵심 약속: 영어권 초급 학습자가 `커피`를 단어 카드가 아니라 `아침마다 커피를 마십니다.`라는 생활 문장 맥락으로 익힌다.
- lesson angle: 문장을 먼저 익히고, 따라 읽은 뒤, 마지막에 빈칸 퀴즈로 다시 확인한다.
- click test: 제목, 썸네일, 첫 2초는 모두 `설민과 함께 배우는 짧은 한국어 문장 학습`이라는 같은 약속을 말해야 한다.

## Source Lock

- focus word: `커피`
- romanization: `keopi`
- gloss: `coffee`
- example sentence: `아침마다 커피를 마십니다.`
- blanked sentence: `아침마다 ___를 마십니다.`
- sentence translation: `I drink coffee every morning.`
- sentence romanization lock:
  - blanked: `achimmada ___reul masipnida.`
  - full: `achimmada keopireul masipnida.`
- reuse status: `unused_example_selected`
- source note: 원본 reading/romanization 저장값이 비어 있어 이번 회차는 `source-packet.json`의 fallback romanization을 잠금값으로 사용한다.

## Hook And Packaging Lock

- recommended opening promise: `설민과 함께 오늘의 한국어 문장을 배워요`
- allowed hook variants:
  - `오늘 배울 한국어 문장을 함께 읽어봐요`
  - `설민과 함께 배우는 짧은 한국어 문장`
  - `문장을 익히고 마지막 빈칸 퀴즈까지 확인해요`
- engagement copy lock: `따라해 볼까요?`
- reveal copy lock: `아침마다 ___를 마십니다.`
- CTA lock: `malmoelab.com에서 더 알아보아요.`
- thumbnail/title rule:
  - 설민 + 칠판 + 오늘의 문장 소개 구도는 허용
  - `scene-4-quiz-point` 이전 reveal 구조를 깨는 direct answer hook은 금지
- opening reuse policy:
  - `scene-1-opening-handoff`는 `003` 기준 greeting structure를 유지하고, 캐릭터 이름만 `설민`으로 바꾼다.
  - 오프닝에서 blank quiz를 먼저 던지지 않는다.
  - 음성은 `characters/seolmin/voice.json`를 따른다.

## Retention Plan

- `0.0s - 6.0s`: 설민 greeting으로 수업 진입을 만든다.
- `6.0s - 12.0s`: 오늘의 문장을 full sentence로 소개한다.
- `12.0s - 18.0s`: 따라하기 cue와 full sentence read로 학습 리듬을 만든다.
- `18.0s - 24.0s`: blank sentence로 전환해 학습 내용을 다시 확인한다.
- `24.0s - 30.0s`: CTA와 설민 엔딩 웨이브로 마무리한다.
- retention rule: 기본 spoken flow는 `003` greeting -> lesson intro -> repeat -> blank quiz -> ending을 유지한다.

## Structure And Proof Lock

- `003`의 5-scene, 6초 단위 구조와 spoken flow를 그대로 유지한다.
- scene 순서:
  1. `scene-1-opening-handoff`
  2. `scene-2-lesson-intro`
  3. `scene-3-repeat-listen`
  4. `scene-4-quiz-point`
  5. `scene-5-ending-wave`
- scene intent:
  - `scene-1-opening-handoff`: 설민 greeting으로 수업을 연다.
  - `scene-2-lesson-intro`: `아침마다 커피를 마십니다.` full sentence를 소개한다.
  - `scene-3-repeat-listen`: `따라해 볼까요?` 뒤에 full sentence를 읽는다.
  - `scene-4-quiz-point`: `아침마다 ___를 마십니다.` blank quiz로 학습 내용을 다시 확인한다.
  - `scene-5-ending-wave`: 짧은 CTA와 설민 인사로 닫는다.
- proof plan:
  - full sentence를 먼저 소개하고 따라 읽어 학습 문맥을 만든다.
  - blank quiz는 lesson recall 용도로 scene-4에만 둔다.
  - 설명형 장광설 대신 `greeting -> sentence intro -> repeat -> recall quiz -> CTA` 순서를 유지한다.
- boundary note: 이 문서는 `003` 구조 잠금이다. downstream은 이 순서를 바꾸지 않는다.

## Protagonist And Visual Lock

- 설민은 `/home/kindsr/projects/shortform-factory-studio/characters/seolmin/Seolmin.png` 기준의 2D chibi teacher identity를 유지한다.
- 설민은 항상 화면 오른쪽 쿼터에 서고, 왼쪽 칠판이 학습면이 된다.
- 칠판은 generation 단계에서 비어 있어야 하며, 모든 텍스트는 후반 typography 합성으로만 넣는다.
- 이번 회차는 `reference-only` 유지다. character-training 또는 LoRA escalation은 승인되지 않았다.
- 교실 톤은 밝고 친근해야 하며 공포/실사/3D/과도한 성인 비율 드리프트는 금지한다.
- ending treatment:
  - 설민은 아직 고정 ending asset이 없다.
  - 따라서 `scene-5-ending-wave`는 이번에도 생성형 shot + 후반 dub/typography 조합으로 유지한다.

## Asset And Handoff Requirements

- required strategist outputs:
  - `./packet.md`
  - `./episode.schema.json`
  - `./keyframe-plan.json`
- required downstream inputs:
  - `./source-packet.json`
  - `/home/kindsr/projects/shortform-factory-studio/characters/seolmin/bible.md`
  - `/home/kindsr/projects/shortform-factory-studio/characters/seolmin/prompts.md`
  - `/home/kindsr/projects/shortform-factory-studio/characters/seolmin/voice.json`
- downstream packet must preserve:
  - protagonist: `seolmin`
  - reference packet path: `/home/kindsr/projects/shortform-factory-studio/characters/seolmin`
  - disclosure posture: `metadata-only`
  - production mode: `reference-only`
  - answer hold until `scene-4-quiz-point`

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

- 현재 blocker는 없다.
- assumption: romanization은 `source-packet.json`의 fallback 값이 publish-ready canonical 값으로 취급된다.
- block if:
  - downstream이 정답 `커피`를 reveal 이전 장면이나 썸네일에 노출한다.
  - 생성 단계에서 칠판이나 의상에 텍스트 아티팩트가 baked-in 된다.
  - reference-only 범위를 벗어나 character-training으로 무단 확장한다.

## Repurpose Notes

- 이 회차는 `003` 기준의 lesson-first short-form 포맷으로 유지한다.
- 같은 설민 시리즈 안에서 재사용할 것은 `친근한 호스트 톤`, `오른쪽 교사/왼쪽 칠판 구도`, `greeting -> lesson -> repeat -> blank quiz -> ending` 순서다.
- 재사용하지 말아야 할 것은 이번 회차의 예문, focus word, 그리고 회차별 문장 자체다.
