# Final Review: malmoelab-ko-lesson-daehan-001
날짜: 2026-04-28

## 전체 요약

- 상태: `malmoelab-keyframe-dub-after-picture-v1 final export`
- 심각도: 이상 없음
- 판정: QA 승인. `publish-packet.json` 기준 private upload handoff 가능.

## 확인한 산출물

- Source packet: `episodes/malmoelab-ko-lesson-daehan-001/source-packet.json`
- Episode schema: `episodes/malmoelab-ko-lesson-daehan-001/episode.schema.json`
- Render manifest: `episodes/malmoelab-ko-lesson-daehan-001/renders/final/render-manifest.json`
- Final MP4: `episodes/malmoelab-ko-lesson-daehan-001/renders/final/malmoelab-ko-lesson-daehan-001-final.mp4`
- Review bundle: `episodes/malmoelab-ko-lesson-daehan-001/review/final-contact-sheets`
- Publish packet: `episodes/malmoelab-ko-lesson-daehan-001/publish-packet.json`
- Character rights: `characters/daehan/rights.md`

## 패킷 정합성

- Export integrity: 1280x720, 16:9, 30.000s, 30fps, 900 frames 확인.
- Audio stream: AAC stereo, 44.1kHz, 약 29.98s 확인. `review/final-audio-analysis.md`의 mean/max volume 값과 render manifest가 일치함.
- 학습 소스 일치: focus word `수업`, romanization `sueop`, full sentence `수업이 두 시에 끝납니다.`, blank sentence `___이 두 시에 끝납니다.`, English translation `The class ends at two o'clock.`가 `source-packet.json`, `packet.md`, `episode.schema.json`, `typography-slots.json`, `publish-packet.json`에서 일치함.
- 숨은 단어/정답 일치: blank sentence의 정답은 `수업`이고, publish description의 `Focus word: 수업 (sueop, class)` 및 source packet의 `answerWord`와 일치함.
- `scene-4-quiz-blank`가 `scene-5-ending-wave`까지 유지되는 것은 [SHO-54](/SHO/issues/SHO-54#comment-796569ae-a9ef-45c8-a573-54610be15152)와 현재 말모이랩 기본 정책상 허용 항목으로 처리함.
- `thumbnailFile`은 빈 값이지만, `thumbnailMode: youtube-auto-selected`와 [SHO-54](/SHO/issues/SHO-54#comment-b5f77ad9-feea-4686-8fa7-b3fb2c6cc5cc) 정책상 blocker가 아님.
- Disclosure placement와 rights posture는 `publish-packet.json`에 명시되어 있고, description에 AI-assisted disclosure와 MalmoeLab/source attribution, Daehan rights note가 포함됨.
- 별도 music asset은 확인되지 않았고, audio 산출물은 Daehan guide dub 계열 파일만 확인됨.

## 씬별 결과

### scene-1-opening-handoff PASS

- 대한 identity lock 유지: silver-white hair, violet eyes, black gat, black durumagi, black gloves 확인.
- 칠판에 baked-in text 없음.

### scene-2-lesson-intro PASS

- board text `수업이 두 시에 끝납니다.` 및 helper `sueopi du sie kkeutnapnida.`가 source와 일치함.
- full sentence를 먼저 제시하는 lesson-first 구조 유지.

### scene-3-repeat-listen PASS

- repeat cue 이후 같은 full sentence board text가 유지됨.
- 정답을 숨기기 전 full sentence 학습 beat가 명확함.

### scene-4-quiz-point PASS

- blank text `___이 두 시에 끝납니다.`와 helper `___i du sie kkeutnapnida.`가 source packet과 일치함.
- English prompt `Which word fits the blank?`는 recall check로 읽히며, fake feature claim이나 `tap to reveal` 오해 문구 없음.

### scene-5-ending-wave PASS

- blank sentence carryover는 현재 승인 정책상 허용.
- lower-third CTA `malmoelab.com에서 더 알아보아요.`와 publish packet의 Study more / Source link가 정렬됨.
- 대한 캐릭터 continuity와 friendly teacher tone 유지.

## 남은 리스크

- `episode.schema.json`의 `renderTargets.resolution`은 `1920x1080`이나 실제 final/publish spec은 `1280x720`임. 현재 issue와 operating model의 핵심 gate는 `30s / 16:9`이며 publish packet이 실제 파일 spec을 정확히 기록하므로 blocker로 보지 않음. 추후 full-HD가 필수 정책이 되면 별도 export 기준을 잠가야 함.
