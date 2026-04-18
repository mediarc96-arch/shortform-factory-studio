# {{EPISODE_SLUG}}

_이 파일은 `episodes/malmoelab-template/packet.template.md` 기반으로 시작한다._

- 작업 유형: `new_episode`
- 시리즈: `{{SERIES_SLUG}}`
- 캐릭터: `{{CHARACTER_SLUG}}`
- 포맷: `education-dub-after-picture-v1`
- 생성일: `{{ISO8601_TIMESTAMP}}`

## 한 줄 요약

- 주제: `{{TOPIC_SUMMARY}}`
- 학습 문장: `{{SENTENCE_KO}}`
- 정답 포커스: `{{FOCUS_WORD}}`
- CTA: `{{SERVICE_CTA_KO}}`

## source

| 항목 | 값 |
|------|-----|
| word_id | {{WORD_ID}} |
| sense_id | {{SENSE_ID}} |
| example_id | {{EXAMPLE_ID}} |
| sentence_ko | {{SENTENCE_KO}} |
| sentence_en | {{SENTENCE_EN}} |
| sentence_romanized | {{SENTENCE_ROMANIZED}} |
| blank_sentence_ko | {{SENTENCE_BLANK_KO}} |
| focus_word | {{FOCUS_WORD}} |

## 단계별 산출물

| 단계 | 파일 |
|------|------|
| source | `./source-packet.json` |
| schema | `./episode.schema.json` |
| picture | `./video-generation-job.json` |
| dub | `./voice-slots.json` |
| typography | `./typography-slots.json` |
| final | `./renders/final/{{EPISODE_SLUG}}-final.mp4` |

## 운영 체크

- [ ] `characters/{{CHARACTER_SLUG}}/voice.json` 존재
- [ ] picture generation에는 텍스트 요청 없음
- [ ] 오프닝/엔딩 재사용 여부 확인
- [ ] content line TTS prepass로 씬 길이 계산
- [ ] dub lock 이후에만 칠판 타이포 합성
- [ ] final review bundle 재생성 완료
