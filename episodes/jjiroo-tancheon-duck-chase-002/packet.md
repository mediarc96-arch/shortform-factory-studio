# 에피소드 브리프: `jjiroo-tancheon-duck-chase-002`

- 작업 유형: `new_episode`
- 소스 이슈: [SHO-72](/SHO/issues/SHO-72)
- storyboard gate: [SHO-74](/SHO/issues/SHO-74)
- 현재 브리프 이슈: [SHO-75](/SHO/issues/SHO-75)
- 시리즈: `pet-contents`
- 포맷: `pet-contents-vertical-webtoon-v1`
- 제작 모드: `reference-only`
- protagonist: `찌루`
- supporting pet: `쫑아`
- reference packet path: `characters/jjiroo` 미존재, `characters/jjonga` 미존재. 이번 회차는 승인된 `./storyboard/style-lock.md`를 episode-local provisional canon으로 사용
- disclosure plan: `metadata-only disclosure and attribution; visible-frame AI disclosure 없음`
- target aspect ratio: `9:16`
- target duration: `30s spine / 34s ceiling`
- storyboard basis: `./storyboard/storyboard-plan.json` 승인안 10컷
- approved storyboard bundle: `./storyboard/webtoon-cuts/cut-01.png` ~ `cut-10.png` with matching manifest files, rendered via approved `xAI Grok image` path
- keyframe bridge: `./keyframe-plan.json`

## 시청자 약속

- 대상 시청자: 반려견 실화 해프닝, 표정 좋은 강아지 반전 엔딩, 관찰형 펫 코미디 숏츠를 좋아하는 시청자
- viewer promise: 평화로운 탄천 산책이 오리 발견 한 번으로 추격전이 되고, 마지막에는 엄마만 흠뻑 젖은 채 찌루가 태연한 표정을 던지는 반전까지 한 번에 본다.
- why click now: `오리 본 강아지가 혼자 강에 들어갔다가 혼자 올라오고 엄마만 젖는 실화`라는 클릭 이유가 첫 장면과 마지막 장면에서 모두 바로 증명된다.
- angle: `위험 사고`가 아니라 `호기심 과몰입한 찌루 vs 더 난감해진 엄마`의 clean ironic anecdote로 간다.

## 훅 옵션

1. `오리 보자마자 달려든 찌루... 결국 더 젖은 건 엄마였어요`
2. `산책하다 오리 본 찌루, 혼자 강에 들어갔다가 혼자 올라왔어요`
3. `엄마는 흠뻑 젖었는데 찌루 표정은 왜 거기 있어? 였어요`

## 패키징 정렬

- opening promise: `오리 본 찌루가 탄천에 뛰어든 날, 결국 엄마만 다 젖었어요`
- thumbnail / first-frame target: `cut-03`의 wide-eyed duck spotting reaction 또는 `cut-10`의 puzzled final look
- payoff promise: 찌루는 자력으로 땅에 올라오고, 물에 남은 엄마를 향해 `왜 거기 있어?`처럼 보이는 태연한 표정을 준다.
- packaging rule: 제목, 첫 프레임, 마지막 payoff가 모두 `오리 발견 -> 물 진입 -> 엄마만 젖음` 축을 공유해야 한다.

## 리텐션 설계

- `0s-5s`: 밝은 탄천 산책과 두 강아지 identity를 빠르게 잠가서 이후 급변 대비를 만든다.
- `5s-10s`: `cut-03`의 시선 고정으로 사건 trigger를 즉시 꽂는다.
- `10s-16.3s`: stalking에서 breakaway, river entry까지 가속을 끊기지 않게 이어 첫 retention peak를 만든다.
- `16.3s-23.1s`: 엄마가 뒤늦게 입수하고 찌루가 더 빠르게 앞서가며 middle escalation peak를 만든다.
- `23.1s-30s`: 찌루의 자력 climb-out과 puzzled reaction으로 clean laugh를 회수한다.
- hard ceiling `34s`: 여유가 필요하면 `cut-10` reaction hold만 늘리고, 중반 chase나 수영 구간을 반복하지 않는다.

## Proof Plan

- 단순 headline이 아니라 실제 사건처럼 읽히게 하기 위해 아래 사실 비트를 반드시 시각적으로 증명한다.
- 밝은 탄천 산책 지형과 같은 강변 동선
- 찌루/쫑아의 분리된 실루엣과 고정 하네스 색
- 오리 발견 순간의 집중 시선
- curiosity-driven stalking과 breakaway
- 같은 bank geography 위의 river entry
- 찌루가 먼저 물에 들어가고 엄마가 나중에 따라가는 순서
- 찌루가 panic이 아니라 swim confidence로 앞서가는 상태
- 찌루의 자력 climb-out
- 엄마만 물에 남고 찌루가 puzzled look을 주는 final irony

## Story Structure

| scene | source cut | duration intent | beat | retention job |
|------|------------|-----------------|------|---------------|
| scene-01 | `cut-01` | `2.5s` | 밝은 탄천 산책 establishing | 장소와 cast를 즉시 잠근다 |
| scene-02 | `cut-02` | `2.5s` | 냄새 맡고 걷는 slice-of-life | 평온함을 쌓아 반전 대비를 만든다 |
| scene-03 | `cut-03` | `2.5s` | 찌루가 오리를 발견 | 클릭 이유를 한 프레임으로 증명한다 |
| scene-04 | `cut-04` | `2.8s` | 살금살금 접근 | 폭발 직전 긴장을 만든다 |
| scene-05 | `cut-05` | `3.0s` | breakaway sprint + duck scatter | 첫 acceleration peak |
| scene-06 | `cut-06` | `3.0s` | 찌루의 강 입수 | 스케일을 키우고 놀라움을 만든다 |
| scene-07 | `cut-07` | `3.4s` | 엄마도 강에 뛰어듦 | comic mismatch를 연다 |
| scene-08 | `cut-08` | `3.4s` | 찌루는 앞서가고 엄마는 뒤처짐 | middle retention peak |
| scene-09 | `cut-09` | `3.0s` | 찌루가 스스로 올라옴 | 안도와 payoff 준비 |
| scene-10 | `cut-10` | `3.9s` | 젖은 엄마를 보는 반전 표정 | final laugh와 replay value |

## Protagonist And Visual Lock

- protagonist: `찌루`
  - small cream-ivory dog
  - upright triangle ears
  - mint Y-harness
  - curious, fast, water-confident, never aggressive
- supporting pet: `쫑아`
  - smaller caramel-brown dog
  - floppy ears
  - peach harness
  - calm observer energy
- human rule: 어머니는 supporting guardian이며, 당황은 크지만 화면 감정 중심은 끝까지 찌루다.
- wildlife rule: 오리는 놀라서 피하는 야생동물이며, 피해·포획·공포 prey 톤으로 보이면 안 된다.
- visual style target: `001`의 original drawing style을 보존한 따뜻한 관찰형 반려동물 웹툰 일러스트, 밝은 낮 공기, 읽기 쉬운 강변 geography
- production decision: recurring-character 포맷이지만 이번 회차도 `reference-only` 유지. `character-training`으로 escalate 하지 않는다.

## Asset And Packaging Requirements

- source packet: `./source-packet.json`
- style lock: `./storyboard/style-lock.md`
- storyboard plan: `./storyboard/storyboard-plan.json`
- approved storyboard cuts: `./storyboard/webtoon-cuts/cut-01.png` ~ `cut-10.png`
- storyboard manifests: `./storyboard/webtoon-cuts/cut-01.manifest.json` ~ `cut-10.manifest.json`
- provider job bundle: `./grok-jobs/cut-01.json` ~ `cut-10.json`
- keyframe plan output: `./keyframe-plan.json`
- generated imagery에는 텍스트, 숫자, 로고, 자막을 넣지 않는다.
- river entry point와 climb-out bank는 같은 장소로 읽혀야 한다.
- duplicate pet, extra animal, wings, extra limbs, merged face, wrong fur color, wrong harness color, style drift를 downstream에서도 계속 금지한다.
- action-heavy 수영 컷에서 identity drift가 생기면 motion span을 줄이고 approved storyboard/keyframe 기준으로 제한 모션 처리한다.

## Downstream Handoff Notes

- `Script Writer`: issue 본문의 긴 `대본:`을 그대로 읽지 말고 `오리 발견 -> breakaway -> 강 입수 -> 엄마 입수 -> final puzzled look` spine만 남겨 압축한다.
- `Thumbnail & Packaging Director`: public-facing hero는 `cut-03`의 duck spotting eyes 또는 `cut-10`의 puzzled look 둘 중 하나여야 한다. 이 둘이 아니면 click value가 약해진다.
- `Video Editor`: chase spectacle보다 river geography legibility가 중요하다. entry bank와 climb-out bank가 흐려지면 payoff가 약해진다.
- `Quality & Fact Checker`: animal harm, drowning panic, duck capture success처럼 읽히는 순간이 없는지 먼저 본다.

## Repurpose Notes

- 15초 재가공 버전은 `cut-03`부터 시작해 `오리 발견 -> 돌진 -> 입수 -> 엄마 입수 -> final look`만 남기는 압축형으로 가능하다.
- community/post copy용 한 줄 요약: `오리 쫓으러 뛰어든 찌루보다 엄마가 더 놀란 날`
- long caption 방향: 실화 톤 유지, 과장된 영웅 서사나 fake danger 카피 금지

## Brief Completeness Check

- protagonist 명시됨
- reference folder 부재와 episode-local reference path 명시됨
- disclosure plan 명시됨
- duration / aspect ratio 명시됨
- hook / payoff / retention / asset requirements 명시됨
- reference-only vs character-training decision 명시됨
