# {{EPISODE_SLUG}}

_이 파일은 `episodes/pet-contents-template/packet.template.md` 기반으로 시작한다._

- 작업 유형: `new_episode`
- trigger: `[Pet Contents]`
- 시리즈: `pet-contents`
- 포맷: `pet-contents-vertical-webtoon-v1`
- 생성일: `{{ISO8601_TIMESTAMP}}`

## raw input

- issue title: `{{ISSUE_TITLE}}`
- source narrative: `{{RAW_EPISODE_SUMMARY}}`
- 대본 여부: `{{HAS_NARRATION_SCRIPT}}`

## cast

| 구분 | 이름 | slug | 역할 | 고정 외형/톤 |
|------|------|------|------|---------------|
| primary pet | {{PRIMARY_PET_NAME}} | {{PRIMARY_PET_SLUG}} | {{PRIMARY_PET_ROLE}} | {{PRIMARY_PET_APPEARANCE_LOCK}} |
| supporting pet | {{SUPPORTING_PET_NAME}} | {{SUPPORTING_PET_SLUG}} | {{SUPPORTING_PET_ROLE}} | {{SUPPORTING_PET_APPEARANCE_LOCK}} |
| human | {{HUMAN_NAME}} | - | {{HUMAN_ROLE}} | {{HUMAN_PRESENCE_RULE}} |
| wildlife | {{WILDLIFE_LABEL}} | - | {{WILDLIFE_ROLE}} | {{WILDLIFE_TONE_RULE}} |

## story spine

| 항목 | 값 |
|------|-----|
| setup | {{SETUP}} |
| trigger | {{TRIGGER}} |
| escalation | {{ESCALATION}} |
| climax | {{CLIMAX}} |
| ending | {{ENDING}} |
| comedic_payoff | {{COMEDIC_PAYOFF}} |
| safety_rule | {{SAFETY_RULE}} |

## style lock summary

- format: `9:16`
- style lines:
  - {{STYLE_LINE_1}}
  - {{STYLE_LINE_2}}
  - {{STYLE_LINE_3}}
  - {{STYLE_LINE_4}}
  - {{STYLE_LINE_5}}

## storyboard plan

- provider: `approved operational image provider (e.g. xAI Grok image or OpenAI GPT Image 2)`
- orchestrator: `codex_local`
- cut count: `{{CUT_COUNT}}`
- storyboard plan file: `./storyboard/storyboard-plan.json`
- style lock file: `./storyboard/style-lock.md`
- camera plan file: `./storyboard/camera-plan.md`

## keyframe and render plan

- keyframe plan: `./keyframe-plan.json`
- video job: `./video-generation-job.json`
- continuity rule: `scene-n` 마지막 프레임과 `scene-(n+1)` 시작 상태가 이어져야 함

## post plan

- narration script: `./narration-script.md`
- voice slots: `./voice-slots.json`
- typography slots: `./typography-slots.json`
- post checklist: `./post-production-plan.md`

## 운영 체크

- [ ] cast bible / refs 확인
- [ ] style lock 파일 생성
- [ ] storyboard cut bundle 생성
- [ ] keyframe plan 생성
- [ ] camera plan 생성
- [ ] post-production plan 생성
- [ ] scene-video continuity rule 반영
- [ ] generated footage text-free 유지
