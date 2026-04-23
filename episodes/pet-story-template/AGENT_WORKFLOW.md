# Pet Story Vertical Shorts — Agent Workflow

이 문서는 반려동물 일상형 vertical Shorts를 Paperclip agent가 반복 생산할 때 따라야 할 기본 실행 순서를 정의한다.

핵심 기준은 `reaction-led pet episode`다.

핵심 원칙:

- `source truth first`
- `brief second`
- `beat script third`
- `keyframe review before video`
- `picture lock before dubbing`
- `sfx and narration before typography`
- `render and post are separate issues`
- `대본:`이 있으면 post dub source-of-truth로 사용
- `대본:`이 있으면 먼저 비-API local/basic guide timing으로 전체 길이를 잡음

## 이 템플릿이 담당하는 범위

- 반복 가능한 반려동물 일상형 Shorts
- 세로 `9:16`
- `20~24초`
- 캐릭터형 recurring pet format
- 행동/표정 중심 코미디
- sparse narration + sparse typography 후반 합성
- 기본 pet timing baseline은 `4 / 4 / 4 / 5 / 5초`

## 표준 실행 단계

1. 에피소드 truth와 한 줄 약속 확정
2. `source-packet.json` 작성
3. `packet.md` 작성
4. `episode.schema.json` 작성
5. `keyframe-plan.json` 작성
6. `narration-script.md` 작성
7. `voice-slots.json` 작성
8. `typography-slots.json` 초안 작성
9. `대본:`이 있으면 local/basic no-paid-API guide timing pass로 rough timing map 작성
10. `video-generation-job.json` 작성
11. keyframe generation
12. keyframe review bundle 생성
13. picture-only scene generation
14. picture preview / picture lock 조립
15. guide dub 또는 uploaded dub 반영
16. SFX/music 반영
17. dub lock 생성
18. final typography 합성
19. review bundle 생성
20. publish packet 준비

## Paperclip 표준 child issue 체인

1. `[SOURCE]`
   - assignee: `Content Strategist`
   - 산출물: `source-packet.json`
2. `[BRIEF]`
   - assignee: `Content Strategist`
   - 산출물: `packet.md`, `episode.schema.json`, `keyframe-plan.json`
3. `[SCRIPT]`
   - assignee: `Script Writer`
   - 산출물: `narration-script.md`, `voice-slots.json`, `typography-slots.json`
4. `[EDIT]`
   - assignee: `Video Editor`
   - 산출물: `video-generation-job.json`
   - 역할: render handoff packet까지 준비
5. `[RENDER]`
   - assignee: `Video Generation Worker`
   - 산출물: `keyframes/*.jpg`, `keyframes/*.manifest.json`, `assets/refs/scene-*-last-frame.jpg`, `renders/picture/*.mp4`, provider manifests
   - 역할: `video-generation-job.json`을 실행해 keyframe과 picture assets 생성
6. `[POST]`
  - assignee: `Video Editor`
  - 산출물: picture lock, dub lock, final export, review bundle
  - 역할: 더빙, SE, 타이포그래피, final assembly
  - `대본:`이 issue 본문이나 승인된 follow-up comment에 있으면 그 본문을 기준으로 narration dub을 만든다
7. `[QA]`
   - assignee: `Quality & Fact Checker`
   - 산출물: 최종 검수 comment, 필요 시 수정 요청
8. `[PUBLISH]`
   - assignee: `Channel Publisher & Analyst`
   - 산출물: publish packet, private upload, analytics kickoff

## issue별 완료 기준

### `[EDIT]`

- `video-generation-job.json`이 존재한다.
- JSON 문법 검증을 통과한다.
- 5-scene vertical 구조가 유지된다.
- scene duration, continuity, render provider가 명시된다.
- `scene-1-watchful-wait`부터 `scene-5-caught-but-innocent`까지 모두 정의된다.
- pet baseline이 필요하면 `4 / 4 / 4 / 5 / 5초`를 쓰되, `대본:` timing이 있으면 그 timing으로 duration이 재배분된다.
- `scene-n` 마지막 프레임과 `scene-(n+1)` 첫 프레임이 같은 상태에서 이어지도록 start seed와 handoff frame이 맞물린다.
- 다음 `[RENDER]` issue가 이어질 수 있도록 handoff comment를 남긴다.

### `[RENDER]`

- 승인 가능한 `keyframes/*.jpg`가 존재한다.
- scene handoff frame이 존재한다.
- `renders/picture/*.mp4`가 모두 생성된다.
- provider manifest가 `succeeded` 상태다.
- render 실패 시 provider 에러와 manifest path를 그대로 남긴다.

### `[POST]`

- picture lock이 조립된다.
- `voice-slots.json` 기준 guide dub 또는 human dub가 반영된다.
- chair creak, paw steps, rustle 같은 SE가 필요한 경우 이 단계에서 반영된다.
- `typography-slots.json` 기준 sparse caption이 합성된다.
- final export와 review bundle이 생성된다.
- typography 수정만으로 TTS가 바뀌지 않도록 기존 오디오 재사용 정책을 지킨다.

### `[PUBLISH]`

- `publish-packet.json`은 `videoFile`을 필수로 포함해야 한다.
- 커스텀 썸네일은 선택값이다.
- title, description, disclosure, source truth, protagonist가 서로 일치해야 한다.

## 양산을 위한 고정 규칙

### 1. source

- source-of-truth는 실제 관찰된 episode truth다.
- `setup`, `trigger`, `escalation`, `climax`, `ending`을 packet에 항상 남긴다.
- room, props, food, chair, table continuity를 packet에 남긴다.
- 안전 제약과 권리 상태를 packet에 남긴다.

### 2. script

- scene당 최대 한 줄 정도의 짧은 line이 기본이다.
- 설명문보다 반응문을 우선한다.
- 자막 문구와 spoken line을 처음부터 같은 파일로 묶지 않는다.

### 3. picture

- generated video에는 글자를 넣지 않는다.
- 기본 scene 구조는 5개다.
- 캐릭터 일관성과 방/식탁 continuity를 우선한다.
- 기본 비율은 `9:16`이다.
- keyframe review를 통과하기 전에는 scene video 생성으로 넘어가지 않는다.
- actual dangerous ingestion shot을 climax로 쓰지 않는다.
- 다음 scene은 직전 scene의 handoff last frame과 동일한 상태에서 시작해야 한다.

### 4. dub and sfx

- narration은 sparse가 기본
- issue에 `대본:`이 있으면 sparse 여부보다 그 대본을 우선 source-of-truth로 삼는다
- issue에 `대본:`이 있으면 local/basic no-paid-API guide timing으로 rough runtime을 먼저 잡고 그 뒤 dubbing/final cut으로 간다
- inner monologue는 과장하지 않는다
- SE는 chair, floor, paw, rustle 정도의 현실감 보강용으로만 쓴다
- typography 수정만 하는 경우 기존 guide audio를 재사용한다

### 5. typography

- reaction caption
- short payoff caption
- ending CTA

이 세 가지는 모두 후반 합성에서 넣는다.

## Paperclip agent 지시용 해석

Paperclip agent는 pet-story episode를 만들 때 이 폴더를 source of process로 본다.

즉, 다음을 의미한다.

- episode tree를 만들 때 여기 있는 템플릿을 복사해서 시작
- `source -> brief -> beat script -> keyframe -> picture -> dub/sfx -> typography` 순서를 유지
- 그림 생성 단계에서 텍스트를 직접 생성하지 않음
- `EDIT`에서 끝내지 않고 `RENDER -> POST -> QA -> PUBLISH`까지 child issue를 이어서 만든다
