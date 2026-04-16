# {{EPISODE_SLUG}}

_이 파일은 `packet.template.md` 기반으로 자동 생성됩니다._

- 작업 유형: `new_episode`
- 시리즈: `malmoelab-hangul-repeat`
- 포맷: **30초 빈칸 + 따라하기 복합 (16:9 가로)**
- 학습 대상: 영어권 한국어 학습자
- 생성일: {{ISO8601_TIMESTAMP}}

---

## 학습 콘텐츠

| 항목 | 내용 |
|------|------|
| 학습 문장 (한국어) | {{SENTENCE_KO}} |
| 학습 문장 (영어) | {{SENTENCE_EN}} |
| 학습 문장 (로마자) | {{SENTENCE_ROMANIZATION}} |
| 빈칸 문장 | {{BLANKED_SENTENCE_KO}} |
| 정답 단어 | {{ANSWER_WORD}} ({{ANSWER_ROMANIZATION}} / {{ANSWER_GLOSS}}) |
| TOPIK 레벨 | {{TOPIK_LEVEL}} |
| 난이도 점수 | {{DIFFICULTY_SCORE}} |

### 보기 단어

| 번호 | 한국어 | 로마자 | 영어 | 정답 |
|------|--------|--------|------|------|
| ① | {{CHOICE_1_KO}} | {{CHOICE_1_ROMANIZATION}} | {{CHOICE_1_GLOSS}} | {{CHOICE_1_IS_ANSWER}} |
| ② | {{CHOICE_2_KO}} | {{CHOICE_2_ROMANIZATION}} | {{CHOICE_2_GLOSS}} | {{CHOICE_2_IS_ANSWER}} |
| ③ | {{CHOICE_3_KO}} | {{CHOICE_3_ROMANIZATION}} | {{CHOICE_3_GLOSS}} | {{CHOICE_3_IS_ANSWER}} |

---

## 말모이랩 소스

| 항목 | 값 |
|------|-----|
| word_id | {{WORD_ID}} |
| sense_id | {{SENSE_ID}} |
| example_id | {{EXAMPLE_ID}} |
| 출처 | [malmoelab.com](https://malmoelab.com) |

---

## 영상 사양

| 항목 | 값 |
|------|-----|
| 총 길이 | 30초 |
| 해상도 | 720×1280 (9:16) |
| FPS | 30 |
| 배경 | 교실, 녹색 칠판 |
| 영상 생성 도구 | Grok (씬별 생성 + 합성) |
| 오프닝 소스 | `1_Opening.mp4` 앞 3초 트림 |

---

## 타임라인

| 씬 | 구간 | 내용 |
|----|------|------|
| 0 — 오프닝 | 0~3초 | `1_Opening.mp4` 트림 |
| 1 — 문제 제시 | 3~6초 | 빈칸 문장 + 보기 3개 표시, 선생님 소개 제스처 |
| 2 — 생각 대기 | 6~11초 | 알람시계 카운트다운, 틱톡 효과음 |
| 3 — 정답 공개 | 11~16초 | 선생님 칠판에 정답 필기, 성공 효과음 |
| 4 — 따라하기 | 16~28초 | 3단어 각 2회 반복 나레이션 |
| 5 — 마무리 | 28~30초 | 인사 제스처, CTA 배너 |

---

## 산출물

| 파일 | 경로 |
|------|------|
| 최종 영상 | `./final/{{EPISODE_SLUG}}.mp4` |
| 썸네일 | `./final/{{EPISODE_SLUG}}-thumb.png` |
| 소스 패킷 | `./source-packet.json` |
| 나레이션 스크립트 | `./narration-script.md` |
| Grok 생성 설정 | `./video-generation-job.json` |
| 발행 패킷 | `./publish-packet.json` |

---

## QA 체크리스트

- [ ] 총 길이 28~32초 범위 내
- [ ] 오프닝 캐릭터와 씬 1~5 캐릭터 동일성 확인 (갓, 장갑, 머리색, 눈색)
- [ ] `{{BLANKED_SENTENCE_KO}}` 빈칸 위치 정확
- [ ] `{{ANSWER_WORD}}` 정답 필기 모션 자연스러운지 확인
- [ ] 보기 ①②③ 중 정답 위치 확인
- [ ] 한국어 나레이션 속도 0.75× 충분히 느린지 확인
- [ ] 모든 단어 2회 반복 확인 ({{ANSWER_WORD}} / {{CHOICE_DISTRACTORA_KO}} / {{CHOICE_DISTRACTORB_KO}})
- [ ] 로마자 표기 일관성
- [ ] 영어 번역 자연스러운지 확인
- [ ] CTA `malmoelab.com` 정확 표기
- [ ] `used_sentences.jsonl` 에 `reserved` 상태 기록 확인
- [ ] 렌더 완료 후 `used_sentences.jsonl` 상태를 `rendered` 로 업데이트

---

## Notes

- 온스크린 AI 고지 문구 넣지 않는다.
- 설명란에서 음악/배경/권리 출처를 처리한다.
- `used_sentences.jsonl` 업데이트는 source 선택 즉시 `reserved`, 렌더 완료 시 `rendered` 로 변경.
