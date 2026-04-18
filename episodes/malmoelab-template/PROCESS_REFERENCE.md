# Stage Reference

이 문서는 `malmoelab` 전용이 아니라 다른 콘텐츠에도 참고할 수 있는 **단계형 제작 절차**만 정리한 것이다.

권장 순서는 아래다.

1. 구성
2. 대본 작성
3. 영상 제작
4. TTS 또는 사람 더빙
5. 한글 타이포그래피
6. QA
7. 업로드 패킷 작성

## 1. 구성

여기서 정하는 것:

- 누가 주인공인지
- 무엇을 가르치거나 보여주는지
- 한 회차의 한 줄 약속
- 오프닝/컨텐츠/엔딩 구조

산출물:

- source packet
- episode packet

## 2. 대본 작성

여기서 정하는 것:

- 실제로 말할 문장
- scene별 대사 순서
- pause와 cue
- CTA 문구

중요:

- 대사는 영상 후반 합성과 분리한다.
- 자막 문구와 spoken line을 처음부터 같은 파일로 묶지 않는다.

산출물:

- `voice-slots.json`
- `recording-script.md`

## 3. 영상 제작

여기서 정하는 것:

- shot prompt
- scene duration
- continuity
- 전환

중요:

- 이 단계에서는 글자와 음성을 넣지 않는다.
- 목표는 `picture lock`이다.

산출물:

- picture scenes
- picture lock

## 4. TTS 또는 사람 더빙

여기서 정하는 것:

- 캐릭터 voice id
- guide dub
- human dub override

중요:

- voice id는 캐릭터 단위로 관리한다.
- 회차별 override는 예외일 때만 쓴다.

산출물:

- `guide-audio/*.mp3`
- `narration-guide/*.mp3`
- dub lock

## 5. 한글 타이포그래피

여기서 정하는 것:

- 한글 문장
- 로마자 도움말
- 빈칸 문장
- CTA 위치

중요:

- 타이포는 dub lock 이후에만 올린다.
- generated video 안에 글자를 직접 박으려 하지 않는다.

산출물:

- `typography-slots.json`
- final overlay frames

## 6. QA

검수 항목:

- 대사와 타이밍 일치
- 글자 위치와 가독성
- character continuity
- scene transition
- final contact sheet 최신 상태

## 7. 업로드 패킷 작성

최종 단계:

- title
- description
- disclosure
- source attribution
- visibility

## 왜 이 순서가 효과적인가

- source 수정이 영상 전체를 다시 깨지 않는다.
- 대사 수정이 영상 생성 단계까지 되돌아가지 않는다.
- typography 수정이 TTS를 다시 만들지 않아도 된다.
- character voice id를 캐릭터별로 재사용할 수 있다.

즉, 양산하려면 `단계 분리`가 가장 중요하다.
