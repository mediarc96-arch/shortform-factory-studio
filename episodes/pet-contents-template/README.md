# Pet Contents Storyboard-First Template

이 폴더는 `[Pet Contents]` 이슈를 받아 richer pet episode를 제작할 때 쓰는 **정식 기본 템플릿**이다.

기준 포맷은 `formats/pet-contents-vertical-webtoon-v1/profile.json`이다.

기존 `pet-story-template`가 짧은 reaction-led pet short에 가깝다면, 이 템플릿은:

- raw episode narrative만 있는 이슈를 받아도 시작할 수 있고
- storyboard/webtoon cuts를 먼저 만들고
- style lock, camera plan, keyframe plan을 고정한 뒤
- scene video와 후반작업으로 이어지는

storyboard-first pet-content path를 정의한다.

## 기본 원칙

- title prefix가 `[Pet Contents]`면 이 템플릿을 우선한다.
- issue body는 raw episode narrative만 있어도 된다.
- `대본:`이 있으면 narration source-of-truth로 사용한다.
- cast가 `characters/<slug>/`에 있으면 canonical bible/ref를 사용한다.
- cast가 아직 없으면 raw narrative 기반 provisional style lock으로 planning을 계속한다.
- storyboard cut bundle이 첫 번째 시각 산출물이다.
- storyboard 승인 전에는 scene video를 만들지 않는다.
- style lock은 별도 문서로 저장하고 storyboard, keyframe, video 전부에 재사용한다.
- scene video는 storyboard와 keyframe에서 파생되어야 한다.
- scene cut는 jump cut이 아니라 handoff로 본다.
- generated footage에는 텍스트를 넣지 않는다.
- dubbing, SFX, BGM, typography, color pass는 모두 `POST` 단계에서 처리한다.

## 표준 실행 순서

1. `source-packet.json` 작성
2. `storyboard/style-lock.md` 작성
3. `storyboard/storyboard-plan.json` 작성
4. `storyboard/webtoon-cuts/*.png` 생성
5. `packet.md`와 `episode.schema.json` 작성
6. `keyframe-plan.json` 작성
7. `storyboard/camera-plan.md` 작성
8. `narration-script.md`, `voice-slots.json`, `typography-slots.json` 작성
9. `post-production-plan.md` 작성
10. `video-generation-job.json` 작성
11. picture render
12. dub / SFX / BGM / typography / color / QA

## 표준 child issue 체인

1. `[SOURCE]`
2. `[STORYBOARD]`
3. `[BRIEF]`
4. `[SCRIPT]`
5. `[EDIT]`
6. `[RENDER]`
7. `[POST]`
8. `[QA]`
9. `[PUBLISH]`

즉 storyboard가 별도 gate다.

## 파일 구성

- `AGENT_WORKFLOW.md`
  - agent execution order
- `source-packet.template.json`
  - raw episode narrative intake template
- `packet.template.md`
  - operator-facing episode packet
- `episode.schema.template.json`
  - episode metadata and file map
- `storyboard-plan.template.json`
  - storyboard/webtoon cut plan
- `style-lock.template.md`
  - reusable style lock prompt
- `camera-plan.template.md`
  - cut-by-cut camera working plan
- `keyframe-plan.template.json`
  - motion-ready keyframe and handoff plan
- `narration-script.template.md`
  - narration script template
- `voice-slots.template.json`
  - dubbing slot template
- `typography-slots.template.json`
  - caption and comic-pop slot template
- `post-production-plan.template.md`
  - post checklist template
- `video-generation-job.template.json`
  - sequential scene-video generation plan
- `paperclip-issue-prompt.template.md`
  - issue body template

## 운영 규칙

- storyboard cuts는 `codex_local` agent가 현재 런타임에서 실제로 사용 가능한 approved image provider를 고르는 경로를 기본으로 본다.
- `xAI Grok image`와 `OpenAI GPT Image 2`는 모두 허용 가능한 storyboard provider다. 현재 workspace에서 실제로 동작하는 쪽을 고른다.
- `Duct Tape`는 이 템플릿에서 canonical production model로 직접 지정하지 않는다.
- recurring cast가 있으면 `characters/<slug>/character-bible.md`와 `refs/`를 먼저 본다.
- recurring cast 파일이 아직 없더라도 episode 내부 일관성을 위한 provisional style lock은 반드시 만든다.
- canonical character art나 승인된 reference drawing style이 이미 있으면, storyboard·keyframe·scene 결과물은 그 원본 그림체를 살려서 유지해야 한다. 임의로 다른 화풍으로 미화하거나 재해석하지 않는다.
- style lock은 아래 성격을 가져야 한다:
  - 화면비
  - 화풍
  - 선 질감
  - 색감
  - 분위기
  - 캐릭터별 고정 외형
  - negative prompt
  - 캐릭터별 허용 개체 수
  - 금지 변형 요소
- storyboard plan에는 컷마다 어떤 캐릭터가 몇 개체까지 등장 가능한지 적어야 한다.
- 같은 scene에서 모델이 승인되지 않은 추가 강아지, 추가 개체, 잘못된 색의 복제 캐릭터를 만들면 drift로 보고 폐기한다.
- negative prompt에는 최소한 `extra dog`, `duplicate pet`, `extra animal`, `extra limbs`, `wings`, `merged face`, `second version of same dog`, `wrong fur color`, `style drift`를 포함한다.
- camera plan은 각 cut의 movement, intensity, purpose를 함께 적어야 한다.
- post-production plan은 consistency, face correction, simple animation, background separation, FX, sound, color, QA를 빠짐없이 적어야 한다.
- 점프, 돌진, 수영처럼 drift가 잘 나는 액션은 긴 single shot보다 더 짧은 beat로 쪼개거나 approved keyframe 기반 limited-motion으로 풀어야 한다.
- pet identity를 깨는 과한 whip, shake, zoom은 shot intensity를 낮춰서 다시 잡는다.
