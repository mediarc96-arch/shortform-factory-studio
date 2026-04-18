# Malmoelab Korean Education Template

이 폴더는 `malmoelab` 한글 교육 콘텐츠를 양산할 때 쓰는 기본 템플릿이다.

목표는 하나다.

- `source -> script -> picture -> dub -> typography -> QA -> publish`

즉 영상 생성과 텍스트/음성을 한 번에 섞지 않고, 단계를 분리해서 반복 가능하게 만든다.

## 기본 원칙

- `Malmoelab DB`에서 가져온 예문을 source-of-truth로 쓴다.
- 영상은 먼저 `mute picture lock`으로 완성한다.
- 더빙은 picture lock 이후에 붙인다.
- 한글 예문과 로마자, CTA는 마지막 타이포그래피 단계에서만 넣는다.
- 캐릭터 TTS voice id는 전역 공용이 아니라 `characters/<slug>/voice.json`에서 읽는다.

## 이 폴더의 역할

- 에피소드 패킷 기본 구조를 제공
- Paperclip agent가 따라야 할 작업 순서를 제공
- 다른 교육 콘텐츠에도 재사용 가능한 단계형 제작 방법을 제공

## 파일 구성

- `AGENT_WORKFLOW.md`
  - Malmoelab 한글 교육 콘텐츠 제작 순서
- `PROCESS_REFERENCE.md`
  - 다른 시리즈에도 적용할 수 있는 범용 단계형 제작 절차
- `packet.template.md`
  - 사람 읽는 회차 개요 템플릿
- `source-packet.template.json`
  - source sentence / lesson / asset policy 템플릿
- `episode.schema.template.json`
  - 렌더/정책/자산 경로 템플릿
- `video-generation-job.template.json`
  - picture-only generation job 템플릿
- `voice-slots.template.json`
  - 더빙 슬롯 템플릿
- `typography-slots.template.json`
  - 한글/로마자/빈칸/CTA 타이포 템플릿

## 운영 규칙

- 새 `malmoelab` 교육 에피소드는 이 폴더를 복사해 시작한다.
- character voice id는 회차마다 직접 박지 말고 `characters/<slug>/voice.json`을 우선 사용한다.
- 회차에서 voice를 바꿔야 할 때만 `voice-slots.json`에서 `ttsVoiceEnv`를 override 한다.
- 오프닝/엔딩 승인 음성이 이미 있으면 재생성보다 재사용을 우선한다.

## 현재 표준 포맷

- format profile: `formats/education-dub-after-picture-v1/profile.json`
- 대표 reference episode: `episodes/daehan-pilot-codex-003`
