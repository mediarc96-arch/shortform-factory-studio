# jjiroo-tancheon-duck-chase-002 Post-Production Plan

## 후반작업 경계

- EDIT 단계에서는 final video를 렌더하지 않는다.
- RENDER 단계는 text-free picture clips와 provider manifests, scene별 last-frame handoff refs만 만든다.
- POST 단계에서 narration dubbing, SFX, BGM, typography, color, final assembly를 처리한다.
- `narration-script.md`, `voice-slots.json`, `typography-slots.json`은 SCRIPT lock 산출물이므로 POST에서 그대로 참조한다.
- narration timing은 `20.0s` guide read / 약 `22.4s` conservative read로 잡고, locked `30.0s` picture map 안에서 action pause와 final hold를 유지한다.

## 필수 후반작업 항목

- [ ] 이미지 일관성 보정
  - 찌루의 cream-ivory 털색, upright triangle ears, mint Y-harness와 쫑아의 caramel-brown 털색, floppy ears, peach harness를 전 scene에서 동일하게 맞춘다. 물에 젖은 이후에도 찌루의 silhouette과 harness color가 흐려지면 안 된다.
- [ ] 얼굴 보정
  - scene-03은 `오리 발견`의 집중 시선, scene-10은 `왜 거기 있어?`의 순진한 의문으로 읽혀야 한다. 어머니 얼굴은 supporting reaction만 남겨 주인공 초점을 뺏지 않게 정리한다.
- [ ] 간단한 파츠 애니메이션
  - 귀 perk, 꼬리 flick, 고개 tilt, leash sway, wet fur drip, water ripple 정도만 추가한다. sprint/splash/swim은 identity drift가 생기면 keyframe 기반 limited motion으로 낮춘다.
- [ ] 배경 분리
  - dirt path, grass edge, shallow river, duck rest area, climb-out bank, characters를 가능한 한 분리해 splash, ripple, caption safe-zone 확보가 가능하게 만든다.
- [ ] 상황별 효과
  - scene-03에는 ambience dip + tiny reaction sting, scene-05에는 harness snap + duck flutter accent, scene-06에는 splash impact, scene-07~08에는 water churn과 chase urgency, scene-10에는 small drip hold만 남긴다. 공포성 water FX는 금지한다.
- [ ] 속도 보정 / speed ramp
  - scene-05 -> scene-06 전환만 짧게 가속하고, scene-07~08은 수영 속도보다 거리 차이를 읽히게 한다. scene-10은 최소 `2.5s` 이상 reaction readability를 확보한다.
- [ ] 전환 효과
  - 기본은 straight cut + action match다. whip이나 shake는 chase axis가 분명할 때만 제한적으로 사용한다. scene-09 -> scene-10은 같은 상태의 hold 연장처럼 붙인다.
- [ ] 나레이션 더빙
  - `voice-slots.json`의 `plannedStartSec`와 `plannedDurationSec`를 기준으로 narrator-led Korean narration을 배치한다. scene-10 dub가 길면 `narration-script.md`의 리스크 노트대로 `왜 거기 있어? 하는 눈빛.`까지 압축할 수 있다.
- [ ] 자막 / 타이포그래피
  - generated picture에는 글자를 넣지 않는다. POST에서만 `typography-slots.json`의 5개 slot을 합성한다: scene-03 `오리 발견`, scene-05 `전광석화 돌진`, scene-07 `엄마도 입수`, scene-09 `혼자 다시 올라옴`, scene-10 `왜 거기 있어?`.
- [ ] 효과음 작업
  - paw steps, leash sway, sniffing, harness snap, duck flutter, splash, water churn, wet paw climb-out, drip tail을 분리해서 배치한다. narration overlap을 가리지 않도록 transient 중심으로 둔다.
- [ ] 배경음악
  - 밝고 가벼운 comic anecdote BGM을 유지한다. scene-03에서 살짝 tension을 올리고, scene-10에서는 리듬을 비워 final look과 caption이 먼저 들어오게 한다.
- [ ] 컬러 정리
  - sunny daytime riverside tone을 유지한다. 물 진입 이후에도 화면을 차갑게 밀지 말고, 강물은 깨끗한 낮 톤, grass edge는 밝은 녹색 계열로 유지해 위험 서사처럼 보이지 않게 한다.
- [ ] 최종 조립
  - picture clips는 `renders/picture/scene-01.mp4`부터 `scene-10.mp4`까지 순서대로 붙인다. narration dub, SFX, BGM, typography, color pass 이후 final output과 review bundle을 만든다.
- [ ] QA 리스크 체크
  - duplicate pets, extra animals, wrong fur/harness color, baked text, duck injury, drowning panic, violent capture, scene boundary jump, mother over-centering, Jjonga identity drift를 우선 검수한다.

## Scene별 POST 노트

| scene | picture beat | narration slot | typography slot | SFX/BGM note | QA risk |
|-------|--------------|----------------|-----------------|--------------|---------|
| scene-01 | sunny walk establishing | scene-01-line | none | paw steps, leash sway, soft riverside ambience | 두 강아지와 어머니 관계가 첫 2.5초에 읽히는가 |
| scene-02 | relaxed sniffing | scene-02-line | none | sniffing, collar jingle, light path texture | 찌루/쫑아 구분이 흐려지지 않는가 |
| scene-03 | duck spotting | scene-03-line | scene-03-caption | ambience dip, reaction sting, distant duck flutter | ducks가 trigger로만 보이고 prey tone이 아닌가 |
| scene-04 | stalking tension | scene-04-line | none | leash tension, small paw creep, held breath beat | 공격성이 아니라 호기심 과몰입으로 보이는가 |
| scene-05 | breakaway sprint | scene-05-line | scene-05-pop | harness snap, fast paw burst, duck flutter | extra Jjiroo나 duplicate dog가 생기지 않는가 |
| scene-06 | river entry splash | scene-06-line | none | splash hit, water rush | 입수 지점이 scene-05 bank edge와 이어지는가 |
| scene-07 | mother jumps in | scene-07-line | scene-07-caption | bigger splash, worried human effort | 어머니가 주인공을 가져가지 않고 rescue context로 남는가 |
| scene-08 | Jjiroo swims ahead | scene-08-line | none | steady swim rhythm, water churn | 익수 공포 대신 comic mismatch로 읽히는가 |
| scene-09 | self-recovery climb-out | scene-09-line | scene-09-caption | wet paws, water drip, shake prep | 자력으로 올라오는 사실이 명확한가 |
| scene-10 | puzzled final look | scene-10-line | scene-10-ending-caption | small drip, tiny head tilt, reaction hold | 안전한 결말과 `왜 거기 있어?` 표정이 먼저 읽히는가 |

## QA 전달 메모

- RENDER 산출물 검수 시 `scene-n` final frame과 `scene-(n+1)` opening frame의 pose/camera/geography continuity를 먼저 본다.
- scene-05~08의 motion이 깨지면 더 긴 generative action을 강행하지 말고 approved keyframe limited motion으로 낮춘다.
- final video는 publish-ready로 간주하지 않는다. QA review bundle과 POST checklist 완료 후 publish packet으로 넘어간다.
