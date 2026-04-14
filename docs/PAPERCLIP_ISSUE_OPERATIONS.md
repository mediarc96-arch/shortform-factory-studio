# Paperclip 이슈 운영 규칙

이 문서는 `Shortform Factory`에서 Paperclip 이슈를 어떻게 써야 하는지 정리한 운영 규칙이다.

핵심 목표는 두 가지다.

- 새 에피소드와 기존 에피소드 수정을 명확히 구분한다.
- 이미 존재하는 에피소드를 다시 만들지 않고, 올바른 이슈나 코멘트에 작업을 이어 붙인다.

## 기본 규칙

- 새 에피소드 제작은 `new issue`로 시작한다.
- 아직 게시되지 않은 기존 에피소드 수정은 기존 이슈의 `comment`로 요청한다.
- 이미 게시된 영상을 다시 렌더하거나 다시 업로드해야 하면 새 이슈를 만든다.
- 제목, 설명, privacy 같은 메타데이터만 바꾸는 일은 기존 이슈의 `comment`로 처리할 수 있다.

## 작업 유형

모든 새 이슈나 수정 코멘트에는 아래 항목을 반드시 넣는다.

```md
작업 유형: new_episode | revise_episode | publish_only | metadata_update
에피소드 슬러그:
기존 이슈:
기존 업로드 URL:
새 업로드 필요: yes | no
주인공:
참조 폴더:
배경 자산 경로:
수정 범위:
완료 조건:
```

## 작업 유형 해석

### `new_episode`

- 완전히 새 편을 만든다.
- 새 episode 폴더와 새 산출물을 만든다.
- 기본적으로 `new issue`로 시작한다.

### `revise_episode`

- 같은 에피소드 슬러그를 유지한 채 기존 산출물을 수정한다.
- 아직 게시 전이거나, 같은 에피소드 폴더 안에서 재렌더만 하면 되는 경우에 쓴다.
- 기본적으로 기존 이슈의 `comment`로 요청한다.

### `publish_only`

- 렌더는 이미 끝났고 업로드만 필요하다.
- 최종 파일과 publish packet이 이미 있는 상태를 전제로 한다.
- 업로드 대상과 privacy를 명시한다.

### `metadata_update`

- 기존 업로드의 제목, 설명, privacy, pinned comment, playlist만 수정한다.
- 새 렌더나 새 업로드는 하지 않는다.
- 기본적으로 기존 이슈의 `comment`로 요청한다.

## 언제 새 이슈를 만들까

아래 중 하나면 새 이슈를 만든다.

- 새 에피소드
- 이미 게시된 영상을 다시 편집해서 새 업로드가 필요한 경우
- 다른 주인공, 다른 시리즈, 다른 포맷으로 갈아타는 경우
- 기존 에피소드를 파생시켜 새 편으로 분리하는 경우

## 언제 기존 이슈 코멘트로 남길까

아래 조건이면 기존 이슈의 코멘트로 남긴다.

- 같은 에피소드 슬러그를 유지한다
- 아직 게시 전이다
- 같은 산출물을 다듬는 수준이다
- 새 YouTube video ID가 필요하지 않다

## Assignee 선택 규칙

### `Head of Content`

기본값이다. 아래 작업은 대부분 `Head of Content`에 넣는다.

- 새 에피소드 제작
- 기존 에피소드 수정
- 캐릭터, 배경, 렌더, QA, publish가 같이 얽힌 일반 제작 요청

### `Channel Publisher & Analyst`

업로드 실행만 필요할 때 쓴다.

- `publish_only`
- `metadata_update`
- 승인된 packet을 실제 업로드하거나 업로드 메타데이터를 수정하는 작업

### `CEO`

전략 판단이 필요한 경우만 쓴다.

- 새 시리즈 승인
- 반복 캐릭터 프랜차이즈 승인
- 참조 이미지 방식에서 character LoRA로 넘어갈지 결정
- 채널 방향이나 브랜딩 수준의 변경

## Project 선택 규칙

### `Weekly Production Engine`

기본값이다.

- 대부분의 새 에피소드 제작
- 기존 에피소드 수정
- 반복 생산 작업
- 일반적인 업로드 실행

### `Channel Launch Engine`

운영체계나 시리즈 구조를 바꾸는 일에 쓴다.

- 새 캐릭터 시스템 설계
- 새 시리즈 프레임 설계
- 채널 운영 방식 변경
- 장기 포맷/브랜딩 실험

## 권장 템플릿

### 새 에피소드 이슈

```md
제목:
[NEW] nabi-korea-trip-002 15초 쇼츠 제작 및 private 업로드

본문:
작업 유형: new_episode
에피소드 슬러그: nabi-korea-trip-002
기존 이슈:
기존 업로드 URL:
새 업로드 필요: yes
주인공: nabi
참조 폴더: /home/kindsr/projects/shortform-factory-studio/characters/nabi/refs
배경 자산 경로: /home/kindsr/projects/shortform-factory-studio/shared/backgrounds/images
수정 범위: 새 에피소드 전체 제작
완료 조건:
- 15초 최종 mp4 생성
- publish packet 생성
- YouTube private 업로드
- 결과 URL 코멘트 기록
```

### 기존 에피소드 수정 코멘트

```md
## Revision Request

작업 유형: revise_episode
에피소드 슬러그: nabi-korea-trip-001
기존 이슈: SHO-8
기존 업로드 URL:
새 업로드 필요: no
주인공: nabi
참조 폴더: /home/kindsr/projects/shortform-factory-studio/characters/nabi/refs
배경 자산 경로: /home/kindsr/projects/shortform-factory-studio/shared/backgrounds/images
수정 범위:
- 실제 서울/부산/제주 사진 사용
- 3번 쇼트 자막 수정
- 색감 자연스럽게 재조정
완료 조건:
- 같은 에피소드 폴더에서 재렌더
- 변경점 요약 코멘트 남기기
```

### 업로드만 요청하는 이슈 또는 코멘트

```md
작업 유형: publish_only
에피소드 슬러그: nabi-korea-trip-001
기존 이슈: SHO-8
기존 업로드 URL:
새 업로드 필요: yes
주인공: nabi
참조 폴더: /home/kindsr/projects/shortform-factory-studio/characters/nabi/refs
배경 자산 경로:
수정 범위: final/nabi-korea-trip-001-v2.mp4를 private 업로드
완료 조건:
- 업로드 완료
- URL 기록
```

## 운영상 한 줄 기준

- 제작과 수정은 `Head of Content`
- 업로드만은 `Channel Publisher & Analyst`
- 전략과 시리즈 결정은 `CEO`
- 대부분의 실행 프로젝트는 `Weekly Production Engine`
