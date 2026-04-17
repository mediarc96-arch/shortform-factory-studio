# Daehan Pilot 002 — 씬 플랜

Grok 씬 3개 + 고정 클립 2개 (opening/ending) + WIPE 2회. 해상도 720p 생성 → 1080p 업스케일.

관련 문서: [source-packet.json](./source-packet.json) · [narration-script.md](./narration-script.md) · [video-generation-job.json](./video-generation-job.json)

---

## Scene 0 — 오프닝 (0.0 – 3.0s)

- 고정 클립 `characters/daehan/01_Opening.mp4` 처음 3초 사용
- 원본 오디오 유지
- 마지막 프레임 추출 → `reference-frames/00-opening-last.png` (Scene 1 seed)

## [WIPE] 3.0 – 3.5s (좌→우)

## Scene 1 — 오늘의 문장 소개 (3.5 – 7.5s, 4s)

**Grok prompt** (image-to-video, seed = 00-opening-last.png):

> Scene begins from the attached reference frame. Daehan stands on the RIGHT SIDE of the frame (30% width). The LEFT 70% is a large clean green chalkboard — COMPLETELY EMPTY, no text or chalk marks. For the first 1.5s he turns toward the board, gestures with an open palm as if presenting today's lesson, then faces the camera with a warm smile for the remaining 2.5s. Keep the chalkboard absolutely empty throughout — any text will be added in post-production. Medium shot, eye-level, 16:9. Warm classroom lighting.

**Post**: typewriter stroke reveal "아기의 옹알이가 하루 종일 이어졌다." 문장을 3.7s부터 한 글자씩, TTS 페이스와 동기 (~0.18s/char). TTS: intro 세그먼트.

**Handoff**: 마지막 프레임 → `reference-frames/01-scene-last.png`

## Scene 2 — 따라해 볼까요? + 낭독 + 묵음 pause (7.5 – 17.5s, 10s)

**Grok prompt** (seed = 01-scene-last.png):

> Scene begins from the attached reference frame. Daehan faces the camera and says "따라해 볼까요?" with an encouraging expression — briefly leaning forward and tilting his head (0s–1.5s). He then pauses with a small nod (1.5s–2.5s). From 2.5s to 6s he articulates carefully with clear lip movements as if reading a sentence aloud, gently tapping the chalkboard once to emphasize rhythm. From 6s to 10s he cups one hand near his ear and leans slightly toward camera with an attentive listening expression, inviting the viewer to repeat. Keep the chalkboard visible behind but completely EMPTY for post-production text overlay. Same composition as Scene 1.

**Post**:
- 씬1에서 표시된 문장 유지
- TTS follow-prompt (8.0s) → pause (9.2–10.2s) → TTS repeat 낭독 (10.3s, ~3.5s) → silent pause 13.8s–17.3s

**Handoff**: 마지막 프레임 → `reference-frames/02-scene-last.png`

## Scene 3 — 빈칸 퀴즈 + malmoelab CTA (17.5 – 26.2s, 9s Grok → 8.7s trim)

**Grok prompt** (seed = 02-scene-last.png):

> Scene begins from the attached reference frame. Daehan turns toward the chalkboard and performs a pointing gesture at the left-centre of the board for the first 2.5s (as if highlighting a blank space — but the board itself stays completely EMPTY, no text). From 2.5s to 5s he faces the camera, taps his chin once with a thoughtful smile, then gestures with open palm toward the bottom of the frame as if inviting viewers to look at a link. From 5s to 9s he stands warmly with a subtle hand-on-chest closing gesture, looking at the camera. Warm classroom lighting, same right-side composition, 16:9. Do not render any text or chalk marks anywhere.

**Post**:
- 씬 시작(17.5s)부터 칠판에 "아기의 ___가 하루 종일 이어졌다." 표시 (문장 유지, 옹알이만 빈칸)
- 19.5s부터 빈칸 위치에 노란 박스 강조 (blink)
- 20.0s TTS CTA: "malmoelab.com에서 더 알아보아요."
- 20.5s부터 화면 하단 중앙에 `malmoelab.com` URL 버튼 타이포 표시 (26.2까지)

**Handoff**: 없음 (엔딩은 독립 클립)

## [WIPE] 26.2 – 26.7s (좌→우)

## Scene 4 — 엔딩 (26.7 – 30.0s)

- 고정 클립 `characters/daehan/02_Ending.mp4` 처음 3.3초
- 원본 비디오 사용, 오디오 없음 (클립에 오디오 스트림 부재 — pilot-001에서 확인)
- pilot-002에서는 엔딩 구간을 TTS로 대체할지 검토 예정 (v3 결정사항)

---

## 씬 연속성 체크리스트

- 전 씬 마지막 프레임 → 다음 씬 seed frame (image-to-video)
- 의상·헤어·배경·라이팅 일관
- WIPE 구간에는 타이포 오버레이 없음 (클린 비디오 경계)
- TTS 볼륨 통일 (compose_final.py의 audio normalize 단계에서 보정)
