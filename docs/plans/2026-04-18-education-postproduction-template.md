# Education Postproduction Template

날짜: 2026-04-18
대상 프로젝트: `shortform-factory-studio`
참조 에피소드: `episodes/daehan-pilot-codex-003`
기준 렌더러: `scripts/pilot/render_daehan_pilot_keyframe_review_v1.py`

## 1. 목적

이 템플릿은 `picture lock`이 끝난 교육 영상에 대해 후작업을 반복 가능한 절차로 정리한 것이다.

기본 순서는 아래다.

1. `picture lock` 고정
2. 대사 확정
3. guide dub 또는 업로드 음성 반영
4. `dub lock` 생성
5. 칠판 타이포그래피 합성
6. review bundle 재생성
7. 최종본 확인

핵심 원칙은 두 가지다.

- 영상 구도와 씬 길이는 후작업 단계에서 바꾸지 않는다.
- 음성과 타이포만 바꾸더라도 최종 review bundle은 항상 다시 만든다.

## 2. 입력 파일

후작업에서 직접 만지는 파일은 보통 아래다.

- `episodes/<episode>/voice-slots.json`
- `episodes/<episode>/typography-slots.json`
- `episodes/<episode>/renders/picture-lock/<episode>-picture-lock.mp4`
- `episodes/<episode>/renders/dub-lock/narration-guide/*.mp3`
- `episodes/<episode>/dubbing/guide-audio/*.mp3`

캐릭터 기본 음성 설정은 아래에서 읽는다.

- `characters/<slug>/voice.json`
- 로컬 `.env`

## 3. 대사 수정 규칙

대사 문구를 바꿀 때는 `voice-slots.json`의 `text`를 수정한다.

- `renderText`는 수동 편집 대상이 아니다.
- 렌더 후 스크립트가 `renderText`를 현재 `text` 기준으로 다시 쓴다.
- 사람이 직접 녹음하거나 외부 TTS mp3를 올릴 경우에도 슬롯 id와 파일명은 유지한다.

슬롯별 mp3 파일명은 `voice-slots.json`의 slot id와 1:1로 맞춘다.

예:

- `scene-1-opening-greeting-ko.mp3`
- `scene-2-intro-ko.mp3`
- `scene-3-repeat-cue-ko.mp3`
- `scene-3-sentence-ko.mp3`
- `scene-4-cta-ko.mp3`
- `scene-5-ending-ko.mp3`

## 4. 외부 음성 업로드 규칙

Supertone 또는 사람 더빙 음성을 직접 올릴 때는 같은 파일을 두 경로에 같이 둔다.

- `episodes/<episode>/renders/dub-lock/narration-guide/`
- `episodes/<episode>/dubbing/guide-audio/`

이유는 두 가지다.

- 실제 최종 믹스는 `renders/dub-lock/narration-guide/`를 읽는다.
- 더빙 패키지와 검수용 자료는 `dubbing/guide-audio/`를 참조한다.

두 경로의 파일 해시는 같아야 한다.

## 5. 타이포그래피 규칙

타이포는 반드시 `dub lock` 이후에 반영한다.

현재 운영 기준:

- 칠판 예문은 `NanumSquareRoundB`
- 박스형 카드보다 칠판 직접 필기형을 우선
- CTA 위치는 실제 씬 의도에 맞는 구간에만 노출
- 엔딩 CTA는 엔딩 씬에만 둔다

`daehan-pilot-codex-003` 기준으로는 아래를 지킨다.

- 족자 한글 오버레이는 사용하지 않는다.
- 칠판 본문과 CTA는 후반 합성으로만 넣는다.
- voice 재합성이 필요 없는 타이포 수정은 기존 guide audio를 재사용한다.

## 6. 재렌더 명령

후작업 후 최종본과 review bundle을 다시 만들 때는 아래 명령을 사용한다.

```bash
cd /home/kindsr/projects/shortform-factory-studio
.venv-video-tools/bin/python scripts/pilot/render_daehan_pilot_keyframe_review_v1.py \
  --episode-dir episodes/daehan-pilot-codex-003 \
  --env-file .env
```

이 명령은 아래를 함께 갱신한다.

- `renders/dub-lock/*.m4a`
- `renders/final/*.mp4`
- `review/final-contact-sheets/*.jpg`
- `review/final-review-report.md`

즉 `overview.jpg`만 틀어져도 이 명령으로 전체 review bundle을 다시 맞춘다.

## 7. 검수 체크리스트

최종 검수는 아래 순서로 본다.

1. 음성이 원하는 mp3를 실제로 읽었는지 확인
2. `voice-slots.json`의 `selectedSource`, `selectedAsset` 확인
3. CTA가 올바른 씬에만 뜨는지 확인
4. 칠판 폰트와 정렬 확인
5. `review/final-contact-sheets/overview.jpg`가 최신인지 확인

빠른 확인 경로:

- `renders/final/<episode>-final.mp4`
- `renders/dub-lock/<episode>-guide-dub.m4a`
- `review/final-contact-sheets/overview.jpg`
- `review/final-review-report.md`

## 8. 운영 메모

이번 `003` 작업에서 확인된 운영 규칙은 아래다.

- review 산출물은 사람이 덮어쓰면 쉽게 stale 상태가 되므로 항상 재생성본을 기준으로 본다.
- 타이포 수정만 했는데 목소리가 바뀌면 안 되므로, 기존 guide audio 재사용이 가능한 구조를 유지한다.
- 외부 TTS 크레딧 부족 상황을 대비해 업로드 방식 fallback을 계속 지원한다.

## 9. 다음 표준화 후보

이 템플릿은 `keyframe-review-v1` 기반 후작업 절차다.

앞으로 공용 표준으로 올릴 후보는 아래다.

- 공용 `postproduction` runner 분리
- slot별 mp3 무결성 검사 자동화
- `overview.jpg`와 scene sheet만 재생성하는 가벼운 QA 명령 추가
