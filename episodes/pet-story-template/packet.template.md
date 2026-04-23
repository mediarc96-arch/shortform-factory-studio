# {{EPISODE_SLUG}}

_이 파일은 `episodes/pet-story-template/packet.template.md` 기반으로 시작한다._

- 작업 유형: `new_episode`
- 시리즈: `{{SERIES_SLUG}}`
- 캐릭터: `{{CHARACTER_SLUG}}`
- 포맷: `pet-story-short-vertical-v1`
- 생성일: `{{ISO8601_TIMESTAMP}}`

## 한 줄 요약

- 주제: `{{TOPIC_SUMMARY}}`
- 한 줄 약속: `{{VIEWER_PROMISE}}`
- 훅: `{{HOOK}}`
- payoff: `{{ENDING_PAYOFF}}`

## source truth

| 항목 | 값 |
|------|-----|
| pet_name | {{PET_NAME}} |
| species | {{SPECIES}} |
| breed | {{BREED}} |
| home_location | {{HOME_LOCATION}} |
| setup | {{SETUP}} |
| trigger | {{TRIGGER}} |
| escalation | {{ESCALATION}} |
| climax | {{CLIMAX}} |
| ending | {{ENDING}} |
| safety_rule | {{SAFETY_RULE}} |

## scene beats

1. `scene-1-watchful-wait`
   - {{SCENE_1_BEAT}}
2. `scene-2-coast-clear`
   - {{SCENE_2_BEAT}}
3. `scene-3-chair-approach`
   - {{SCENE_3_BEAT}}
4. `scene-4-climb-and-jump`
   - {{SCENE_4_BEAT}}
5. `scene-5-caught-but-innocent`
   - {{SCENE_5_BEAT}}

## 단계별 산출물

| 단계 | 파일 |
|------|------|
| source | `./source-packet.json` |
| schema | `./episode.schema.json` |
| keyframe plan | `./keyframe-plan.json` |
| script | `./narration-script.md` |
| voice | `./voice-slots.json` |
| typography | `./typography-slots.json` |
| picture | `./video-generation-job.json` |
| final | `./renders/final/{{EPISODE_SLUG}}-final.mp4` |

## 운영 체크

- [ ] `characters/{{CHARACTER_SLUG}}/character-bible.md` 존재
- [ ] `characters/{{CHARACTER_SLUG}}/refs/` 존재
- [ ] keyframe 5장 승인 전에는 scene video 생성 금지
- [ ] picture generation에는 텍스트 요청 없음
- [ ] 실제 dangerous ingestion을 payoff로 쓰지 않음
- [ ] narration은 sparse 유지
- [ ] dub lock 이후에만 caption typography 합성
- [ ] final review bundle 재생성 완료
