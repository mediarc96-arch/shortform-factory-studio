# 에피소드 브리프: `jjiroo-tancheon-duck-chase-001`

- 작업 유형: `new_episode`
- 소스 이슈: [SHO-60](/SHO/issues/SHO-60)
- 현재 브리프 이슈: [SHO-63](/SHO/issues/SHO-63)
- 시리즈: `pet-contents`
- 포맷: `pet-contents-vertical-webtoon-v1`
- 제작 모드: `reference-only`
- protagonist: `찌루`
- supporting pet: `쫑아`
- reference packet path: `characters/jjiroo` 미존재, 이번 회차는 `./storyboard/style-lock.md`를 episode-local provisional canon으로 사용
- disclosure plan: `metadata-only disclosure and attribution; visible-frame AI disclosure 없음`
- target aspect ratio: `9:16`
- target duration: `30s spine / 34s ceiling`
- storyboard basis: `./storyboard/storyboard-plan.json` 승인안 10컷
- keyframe bridge: `./keyframe-plan.json`

## 시청자 약속

- 대상 시청자: 반려견 실화 해프닝, 성격 드러나는 강아지 반전 표정, 짧은 코미디형 펫 숏츠를 좋아하는 시청자
- viewer promise: 평화로운 탄천 산책이 갑자기 오리 추격전으로 커지고, 마지막에는 젖은 엄마보다 태연한 찌루 표정이 웃음으로 남는다.
- why click now: `강에 먼저 뛰어든 강아지보다 엄마가 더 당황한 실화`라는 구조가 첫 1초부터 상황 설명 없이도 바로 이해되고, payoff가 명확하다.
- angle: `위험 서사`가 아니라 `너무 자신만만한 찌루 vs 더 난감해진 엄마`의 관찰형 아이러니로 간다.

## 훅 옵션

1. `오리 쫓다 강에 뛰어든 찌루... 근데 더 젖은 건 엄마였어요`
2. `탄천 산책하다 오리 본 찌루의 표정이 모든 사건의 시작이었어요`
3. `혼자 강에 들어갔다가 혼자 올라온 찌루가 엄마를 본 표정`

## 패키징 정렬

- opening promise: `오리 보고 폭주한 찌루, 결국 엄마만 다 젖은 날`
- thumbnail / first-frame target: 찌루가 강가 또는 물가 쪽을 노려보는 순간, 또는 마지막 `왜 거기 있어?` 표정
- payoff promise: 찌루는 무사히 자력으로 올라오고, 젖은 엄마를 이상하게 쳐다보는 반전 표정으로 끝난다.
- packaging rule: 제목과 첫 장면 모두 `오리 추격 -> 물 진입 -> 반전 표정` 축을 벗어나지 말 것

## 리텐션 설계

- `0s-5s`: 날씨 좋은 산책과 찌루/쫑아의 생활감을 빠르게 잠가서 이후 급변 대비를 만든다.
- `5s-10s`: 찌루가 오리를 발견하고 시선이 박히는 순간을 명확히 보여 준다.
- `10s-16s`: 살금살금 접근하다가 하네스를 끊고 돌진하는 전환으로 첫 큰 상승을 만든다.
- `16s-23s`: 강 진입과 엄마의 추격으로 상황 스케일을 한 단계 더 키운다.
- `23s-30s`: 찌루의 자력 탈출과 `왜 거기 있어?` 반응으로 clean laugh를 회수한다.
- hard ceiling `34s`: narration timing 때문에 여유가 필요하면 마지막 reaction hold만 늘리고, 중반 chase를 늘어뜨리지는 않는다.

## proof plan

- 단순 headline이 아니라 실제 사건처럼 읽히게 하기 위해 아래 사실 비트를 반드시 시각적으로 증명한다.
- 평온한 탄천 산책 지형
- 찌루와 쫑아의 산책 상태와 하네스
- 오리 발견과 시선 고정
- 하네스 breakaway 이후 돌진
- 오리들의 회피와 강 진입
- 엄마의 뒤늦은 입수
- 찌루의 수영 자신감과 거리 차이
- 찌루의 자력 climb-out
- 젖은 엄마를 보는 puzzled expression

## story structure

| scene | source cut | duration intent | beat | retention job |
|------|------------|-----------------|------|---------------|
| scene-01 | `cut-01` | `2.5s` | 밝은 탄천 산책 establishing | 장소와 인물 관계를 즉시 잠근다 |
| scene-02 | `cut-02` | `2.5s` | 냄새 맡고 걷는 생활감 | 평온함을 쌓아 반전 대비를 만든다 |
| scene-03 | `cut-03` | `2.5s` | 찌루가 오리를 발견 | 사건 trigger를 한눈에 꽂는다 |
| scene-04 | `cut-04` | `2.8s` | 살금살금 접근 | 폭발 직전 긴장을 만든다 |
| scene-05 | `cut-05` | `3.0s` | 하네스 breakaway + 돌진 | 첫 acceleration peak |
| scene-06 | `cut-06` | `3.0s` | 찌루의 강 입수 | scale-up과 놀라움을 만든다 |
| scene-07 | `cut-07` | `3.4s` | 엄마도 강에 뛰어듦 | comic mismatch 시작 |
| scene-08 | `cut-08` | `3.4s` | 찌루는 앞서가고 엄마는 허둥댐 | middle retention peak |
| scene-09 | `cut-09` | `3.0s` | 찌루가 스스로 올라옴 | 안도와 payoff 준비 |
| scene-10 | `cut-10` | `3.9s` | 젖은 엄마를 보는 반전 표정 | final laugh와 replay value |

## protagonist and visual lock

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
- human rule: 어머니는 구조자이지만 화면 감정의 중심은 아니다.
- wildlife rule: 오리는 놀라서 피하는 야생동물이며 공포/사냥 톤으로 보이면 안 된다.
- visual style target: 따뜻한 관찰형 반려동물 웹툰 일러스트, 부드러운 채색, 밝은 낮 공기, 읽기 쉬운 강변 지형
- production decision: recurring-character 포맷이지만 이번 회차는 `reference-only` 유지. `character-training`으로 escalate 하지 않는다.

## asset and packaging requirements

- style lock: `./storyboard/style-lock.md`
- storyboard plan: `./storyboard/storyboard-plan.json`
- storyboard cuts: `./storyboard/webtoon-cuts/cut-01.png` ~ `cut-10.png`
- camera plan reference: `./storyboard/camera-plan.md`
- keyframe plan output: `./keyframe-plan.json`
- generated footage에는 텍스트, 숫자, 로고, 자막을 넣지 않는다.
- river entry point와 climb-out bank는 같은 장소로 읽혀야 한다.
- 같은 회차 안에서 찌루/쫑아의 털색, 귀 모양, 하네스 색, 꼬리 실루엣을 흔들지 않는다.

## downstream handoff notes

- `Script Writer`: issue 본문의 `대본:`은 길어서 그대로 읽으면 늘어진다. `오리 발견 -> breakaway -> 물 진입 -> 엄마 입수 -> puzzled look` 축만 남기고 압축해야 한다.
- `Thumbnail & Packaging Director`: 첫 인상은 `오리 발견 직전의 집중 표정` 또는 `마지막 반전 표정` 중 하나로 고른다. 둘 다 안 되면 이 에피소드의 click value가 약해진다.
- `Video Editor`: middle chase보다 geography legibility가 더 중요하다. 강가 위치가 흔들리면 payoff가 약해진다.
- `Quality & Fact Checker`: 동물 위협, 익수 공포, 오리 피해처럼 읽히는 순간이 없는지 먼저 본다.

## repurpose notes

- 15초 재가공 버전은 `cut-03`부터 시작해 `오리 발견 -> 돌진 -> 입수 -> 엄마 입수 -> final look`만 남기는 압축형으로 가능하다.
- community/post copy용 한 줄 요약: `오리 잡으러 뛰어든 찌루보다 엄마가 더 놀란 날`
- long caption 방향: 실화 톤 유지, 과장된 영웅 서사나 위험 자극 카피 금지

## brief completeness check

- protagonist 명시됨
- reference folder / provisional style lock 명시됨
- disclosure plan 명시됨
- duration / aspect ratio 명시됨
- hook / payoff / retention / asset requirements 명시됨
