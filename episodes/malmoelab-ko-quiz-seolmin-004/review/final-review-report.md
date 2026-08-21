# Final Review: malmoelab-ko-quiz-seolmin-004
날짜: 2026-08-05

## 전체 요약
- 상태: `malmoelab-keyframe-dub-after-picture-v1 final export`
- 총 씬 수: 5
- 심각도: `ready-for-qa`

## POST 완료 항목
- [x] `futureScenes[].startSec` clip-local `0.0` 보정 후 ~30s picture lock 재생성
- [x] picture lock → Supertone guide dub → typography → final export
- [x] blank quiz는 scene-4부터, CTA lower-third는 scene-5만
- [x] 사람 더빙 교체용 `dubbing/audio-overrides/` 패키지 생성

## 씬별 스팟체크
- scene-1: greeting / 칠판 비움 유지
- scene-2: full sentence `학교 앞에서 친구를 만납니다.` + romanization
- scene-3: full sentence 유지 (blank 선공개 없음)
- scene-4: blank `___ 앞에서 친구를 만납니다.`
- scene-5: blank 유지 + CTA `malmoelab.com에서 더 알아보아요.`

## 산출물
- `renders/picture-lock/malmoelab-ko-quiz-seolmin-004-picture-lock.mp4` (30.0s)
- `renders/dub-lock/malmoelab-ko-quiz-seolmin-004-guide-dub.m4a`
- `renders/final/malmoelab-ko-quiz-seolmin-004-final.mp4` (30.0s, 1280x720, h264+aac)
- `renders/final/malmoelab-ko-quiz-seolmin-004-final-thumb.jpg` (1280x720)
- `review/final-contact-sheets/overview.jpg`
- `renders/final/render-manifest.json`

## QA revision (2026-08-05)
- Export truth mismatch 해소: 패킷 선언을 실제 Grok 720p export에 맞춰 `1280x720`으로 정렬
- 변경: `render-config.json`, `episode.schema.json`, `video-generation-job.json`, `keyframe-plan.json` canvas, `renders/final/render-manifest.json`
- 재렌더 없음 (scene-jobs / grok manifests 이미 `720p`)

## 다음 단계
- [SHO-133] QA re-check after resolution alignment
- [SHO-134] PUBLISH는 CEO OAuth hold 유지
