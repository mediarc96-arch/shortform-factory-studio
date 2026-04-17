# Daehan Pilot Codex 001

## 메타데이터

- 에피소드 슬러그: `daehan-pilot-codex-001`
- 시리즈: `daehan-pilot-codex`
- 주인공: `daehan`
- 포맷 프로필: `legacy-v1`
- 형식: `action-quiz`
- 목표 길이: `30초`
- 비율: `16:9`
- 출력 대상: `episodes/daehan-pilot-codex-001/renders/final/`

## 목적

- `characters/daehan` 자산만으로 segment-continuity 파일럿을 검증한다.
- 오프닝과 엔딩은 기존 고정 자산을 재사용한다.
- 본편은 텍스트 없는 영상으로 먼저 구성하고, 더빙과 타이포그래피는 후반 단계에서 분리한다.
- `voiceSlot`, `typographySlot`, `shot schema` 기반 운영이 실제로 유용한지 확인한다.
- 오프닝/엔딩과 본편 사이에는 전환효과를 허용하고, 본편은 "같은 수업처럼 보이는 일관성"을 우선한다.

## 재사용 자산

- 대표 이미지: `characters/daehan/daehan.jpg`
- 생성 기본 참조: `episodes/daehan-pilot-codex-001/assets/refs/daehan-opening-clean-ref.jpg`
- 캐릭터 바이블: `characters/daehan/bible.md`
- 프롬프트 세트: `characters/daehan/prompts.md`
- 오프닝: `characters/daehan/01_Opening.mp4`
- 엔딩: `characters/daehan/02_Ending.mp4`

## 수업 소스

- 예문: `풍선을 너무 크게 불었더니 결국 빵 터져 버렸다.`
- 빈칸 문장: `풍선을 너무 크게 불었더니 결국 ___ 터져 버렸다.`
- 포커스 단어: `빵`
- 영어 번역: `I blew the balloon too big, and it ended up popping.`

## 장면 구성

1. `scene-0-opening`
   - 기존 오프닝 클립 재사용
   - 원본 음성 유지
   - 본편 진입 전 `dip to black`
2. `scene-1-situation`
   - 대한이 풍선을 점점 크게 부는 연기
   - 칠판 없음
3. `scene-2-climax`
   - 풍선이 터지고 놀라는 리액션
   - 이전 씬 레퍼런스를 참고하되, 첫 프레임 완전 일치는 요구하지 않음
4. `scene-3-question`
   - 칠판이 있는 교실 구도로 전환
   - 캐릭터는 오른쪽 1/3, 칠판은 왼쪽 2/3
   - 칠판 텍스트는 후반 합성
5. `scene-4-reveal-repeat`
   - 정답 공개 동작과 따라하기 유도 동작을 분리
   - 보드 텍스트와 정답 하이라이트는 후반 합성
6. `scene-5-ending`
   - 기존 엔딩 클립 재사용
   - 현재는 클립 오디오가 없어 guide dub fallback 사용
   - 추후 reusable voice-pack 또는 사람 더빙으로 교체 가능

## 운영 파일

- 에피소드 운영 메타데이터: `episode.schema.json`
- 쇼트 설계: `shots.schema.json`
- 음성 슬롯: `voice-slots.json`
- 타이포 슬롯: `typography-slots.json`
- 생성기 입력: `video-generation-job.json`
- 예문 데이터: `source-packet.json`

## 현재 상태

- 상태: `final-export`
- 렌더 여부: 본편 `scene-1`~`scene-4` 생성 완료
- 더빙 여부: ElevenLabs guide dub 합성 완료, `dubbing/audio-overrides/`로 사람 더빙 교체 가능
- 타이포 여부: chalkboard/subtitle typography 합성 완료
- 연속성 목표: `frame-perfect`가 아니라 `same-lesson continuity`
- 최신 리뷰: `review/final-review-report.md` 기준 `✅ pass`

## 다음 작업

1. 필요하면 `voice-slots.json`의 guide dub를 사람 더빙이나 actor dub로 교체
2. subtitle/board text 문구만 수정할 경우 `typography-slots.json`만 갱신 후 재export
3. 최종 업로드 패킷이나 dubbing workbench 입력 포맷으로 확장
