# Education Content Template

날짜: 2026-04-18
대상 프로젝트: `shortform-factory-studio`
기준 포맷: `formats/education-dub-after-picture-v1/profile.json`
참조 실험: `episodes/daehan-pilot-codex-003`

## 1. 결론

앞으로 교육 콘텐츠는 아래 순서로 만든다.

1. 오프닝/엔딩 영상과 오프닝/엔딩 대사를 재사용 자산으로 둔다.
2. `Malmoelab DB`에서 가져온 예문으로 content line TTS 길이를 먼저 잰다.
3. 그 길이를 기준으로 씬 길이를 정한다.
4. 영상을 먼저 무음으로 완성해 `picture lock`을 만든다.
5. 그 다음 더빙을 붙여 `dub lock`을 만든다.
6. 마지막으로 칠판 타이포그래피를 올려 최종본을 낸다.

핵심 원칙은 `picture first`, `dub second`, `typography last`다.

## 2. 표준 제작 순서

### 2.1 Reusable Assets

반복 자산은 회차 밖에서 관리한다.

- 오프닝 영상
- 엔딩 영상
- 오프닝 대사
- 엔딩 대사
- 캐릭터별 voice id 설정
- 캐릭터 bible / prompt set
- 손글씨 칠판체 / stroke font

이 자산은 매회 새로 만들지 않는다.

`voice id`는 전역 공용으로 두지 않는다.

- `characters/<slug>/voice.json`에 캐릭터별 기본 voice env를 둔다.
- 회차 `voice-slots.json`은 필요한 경우에만 `ttsVoiceEnv`를 override 한다.

### 2.2 Content Planning

회차별로 바뀌는 것은 아래다.

- Malmoelab DB에서 가져온 예문
- 정답 단어
- 빈칸 문장
- content 구간의 씬별 동작
- content 구간의 더빙

### 2.3 Duration Prepass

콘텐츠 구간은 먼저 TTS 길이를 잰다.

- 예문 소개 line
- 따라하기 cue
- 예문 읽기 line
- 퀴즈 line

이 길이에 발표 여유 시간을 더해 씬 길이를 정한다.

권장 규칙:

- 소개 씬: `tts duration + 1.5s`
- 따라하기 cue 씬: `tts duration + pause + 1.0s`
- 예문 읽기 씬: `tts duration + 1.0s`
- 퀴즈 씬: `tts duration + 1.5s`
- 엔딩 씬: 재사용 ending line 길이에 맞춤

즉 `고정 6초`보다 `내용 길이 기반`이 우선이다.

### 2.4 Picture Stage

영상 생성 단계에서는 글자를 넣지 않는다.

- 칠판에 문장 생성 금지
- 자막 생성 금지
- lower third 생성 금지

여기서 목표는 아래뿐이다.

- 캐릭터 일관성
- 씬 연결감
- 구도 안정성
- 동작 자연스러움

이 단계의 결과물이 `picture lock`이다.

### 2.5 Dub Stage

더빙은 picture lock 이후에 넣는다.

- 오프닝 대사: 재사용 voice pack
- 엔딩 대사: 재사용 voice pack
- content 대사: human dub / actor dub / TTS

즉 오프닝/엔딩은 고정 자산, 컨텐츠만 회차별로 바뀐다.
그리고 TTS를 쓰더라도 `voice id`는 캐릭터별 기본값을 따른다.

### 2.6 Typography Stage

타이포그래피는 dub lock 이후에 넣는다.

- 칠판 예문
- 빈칸 문장
- CTA 문구

스타일은 `굵은 손글씨 칠판체` 기준으로 한다.

타이포는 음성 길이에 맞춰 노출 시간을 맞춘다.

## 3. 이번 003 실험과의 관계

`daehan-pilot-codex-003`은 이 템플릿을 만드는 데 가장 가까운 참고본이다.

정렬되는 점:

- 영상 먼저 생성
- 더빙 후반 적용
- 타이포 후반 적용
- 생성 단계 무음 / no text
- character continuity를 먼저 검수

다른 점:

- `003`은 오프닝/엔딩도 TTS로 다시 만들었다.
- 새 템플릿은 오프닝/엔딩 대사를 재사용하는 쪽이 기준이다.
- `003`은 씬 길이를 대부분 `6초 고정`으로 다뤘다.
- 새 템플릿은 `예문 TTS 길이 측정 -> 씬 길이 결정`이 기준이다.
- `003`은 키프레임 승인 실험이 들어갔다.
- 새 템플릿에서는 키프레임 리뷰는 선택사항이고, 핵심은 `picture lock before dub`이다.
- `003`은 음성 기본값이 사실상 대한 기준으로 굳어 있었다.
- 새 템플릿은 `voice id per character`를 기본 규칙으로 둔다.

## 4. 사용 규칙

앞으로 교육 콘텐츠에서 지킬 기본 규칙은 아래다.

- 영상 생성 단계에서 텍스트를 넣지 않는다.
- 오프닝/엔딩 대사는 재사용한다.
- voice id는 캐릭터별 설정을 쓴다.
- content line 길이를 먼저 재고 씬 길이를 잡는다.
- picture lock 전에는 음성 싱크를 맞추려 하지 않는다.
- dub lock 이후에만 칠판 타이포를 얹는다.

## 5. 사용자 프롬프트와 실제 작업의 차이

이번 사용자 요구는 아래였다.

- 영상을 만들고 나서 더빙
- 오프닝/엔딩 대사는 그대로 사용
- DB 예문 길이를 TTS로 측정해 씬 길이 결정
- 마지막에 칠판 타이포 작업

이 프롬프트에서 실제 작업과 다른 부분은 두 가지였다.

1. 실제 `003`에서는 오프닝/엔딩 대사도 TTS로 다시 만들었다.
2. 실제 `003`에서는 씬 길이를 내용 길이 기반이 아니라 거의 `6초 고정`으로 유지했다.
3. 실제 `003`에서는 기본 voice id가 캐릭터 공용 체계로 정리돼 있지 않았다.

반대로 같은 부분은 아래다.

- 영상 먼저 완성
- 더빙 후반 적용
- 칠판 타이포 마지막 합성
- 생성 단계에서 no-text 유지

즉 사용자 프롬프트는 `003 실험`을 조금 더 운영 가능한 표준으로 다듬은 버전이다.

## 6. 앞으로의 기본 선택

교육 콘텐츠는 앞으로 `education-dub-after-picture-v1`을 기준으로 본다.

실험용 포맷은 계속 따로 둘 수 있다.

- `keyframe-review-v1`: 실험 / 검수용
- `education-dub-after-picture-v1`: 운영용 표준
