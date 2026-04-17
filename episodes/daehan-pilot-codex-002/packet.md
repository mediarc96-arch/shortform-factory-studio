# Daehan Pilot Codex 002

## 메타데이터

- 에피소드 슬러그: `daehan-pilot-codex-002`
- 시리즈: `daehan-pilot-codex`
- 주인공: `daehan`
- 포맷 프로필: `wipe-cta-v2`
- 형식: `sentence-teaser-quiz`
- 목표 길이: `30초`
- 비율: `16:9`
- 출력 대상: `episodes/daehan-pilot-codex-002/renders/final/`

## 목적

- 기존 `legacy-v1`을 유지한 채, 새 `wipe-cta-v2` 포맷을 독립 실험한다.
- 오프닝과 컨텐츠, 컨텐츠와 엔딩 경계는 `wipe`로 처리한다.
- 본편은 `문장 소개 -> 따라하기 -> 퀴즈 CTA`로 단순화한다.
- 본편 영상에는 텍스트를 넣지 않고, 문장과 CTA는 후반 typography로 합성한다.
- 본편 TTS는 `Supertone`을 우선 사용하고, 필요시 `ElevenLabs`를 fallback으로 둔다.

## 재사용 자산

- 대표 이미지: `characters/daehan/daehan.jpg`
- 생성 기본 참조: `episodes/daehan-pilot-codex-002/assets/refs/daehan-opening-clean-ref.jpg`
- 캐릭터 바이블: `characters/daehan/bible.md`
- 프롬프트 세트: `characters/daehan/prompts.md`
- 오프닝: `characters/daehan/01_Opening.mp4`
- 엔딩: `characters/daehan/02_Ending.mp4`

## 수업 소스

- 예문: `아기의 옹알이가 하루 종일 이어졌다.`
- 빈칸 문장: `아기의 ___가 하루 종일 이어졌다.`
- 포커스 단어: `옹알이`
- 서비스 CTA: `malmoelab.com에서 더 알아보아요.`

## 장면 구성

1. `scene-0-opening`
   - 기존 오프닝 클립 재사용
   - 원본 음성 유지
   - 본편 진입은 `wipe-left`
2. `scene-1-lesson-intro`
   - 대한이 오늘 배울 문장을 소개
   - 오른쪽 1/3에 서고, 왼쪽 보드는 후반 typography용으로 비워 둠
3. `scene-2-guided-repeat`
   - `따라해 볼까요?` 후 1초 쉬고 문장을 다시 말하는 장면
   - 문장 후에도 1초 텀을 두어 사용자가 따라 말할 시간을 확보
4. `scene-3-quiz-cta`
   - `아기의 ___가 하루 종일 이어졌다.` 문장을 칠판에 띄우는 퀴즈 장면
   - CTA는 `malmoelab.com에서 더 알아보아요.`
5. `scene-4-ending`
   - 기존 엔딩 클립 재사용
   - 본편 종료 후 `wipe-left`로 진입

## 운영 파일

- 에피소드 운영 메타데이터: `episode.schema.json`
- 쇼트 설계: `shots.schema.json`
- 음성 슬롯: `voice-slots.json`
- 타이포 슬롯: `typography-slots.json`
- 생성기 입력: `video-generation-job.json`
- 예문 데이터: `source-packet.json`

## 현재 상태

- 상태: `final-export`
- 렌더 여부: preview/final 렌더 완료
- 더빙 여부: `Supertone` 우선 guide dub 생성 완료, `dubbing/audio-overrides/`로 사람 더빙 교체 가능
- 타이포 여부: sentence/blank/CTA typography 합성 완료
- 연속성 목표: `same-lesson continuity`

## 다음 작업

1. 필요하면 `dubbing/audio-overrides/`에 사람 더빙이나 voice-pack 파일을 넣고 재렌더
2. scene 동작/연속성 수정이 필요하면 `scene-jobs/`를 조정해 재생성
3. CTA 문구와 sentence typography만 바꿀 경우 `typography-slots.json`만 수정 후 재export
