# 말모이랩 한글 빈칸 퀴즈 쇼츠 운영 모델

이 문서는 `Shortform Factory`가 말모이랩 데이터를 이용해 영어권 학습자 대상 한글 교육 쇼츠를 반복 생산할 때 따라야 할 제작 기준을 정리한다.

## 목표

- 영어권 학습자가 한국어 예문 속 핵심 단어를 맞히는 15초 쇼츠를 만든다.
- 예문은 말모이랩의 실제 학습 데이터에서 가져온다.
- 형식은 반복 가능해야 하고, 에피소드 간 품질 편차를 낮춰야 한다.
- 이미 사용한 예문은 가능하면 재사용을 피한다.

## 대상 시청자

- 영어를 모국어 또는 주 사용 언어로 쓰는 한국어 학습자
- 초급에서 중급 초반까지의 학습자
- 15초 안에 문제를 이해하고 정답을 확인할 수 있는 쇼츠 선호 시청자

## 영상 포맷

기본 길이는 15초다.

### 권장 타임라인

- `0.0s - 2.0s`
  - 타이틀 카드
  - 예: `말모이랩 한글공부`
- `2.0s - 9.0s`
  - 칠판 영역에 빈칸 문장 표시
  - 하단 또는 보조 캡션에 영어 질문 표시
  - 예: `Which word fits the blank?`
- `9.0s - 11.0s`
  - 참여 유도 문구 표시
  - 예: `Double tap if you know it.`
- `11.0s - 15.0s`
  - 정답 공개
  - 완성 문장 + 정답 단어 강조
  - `Learn more at malmoelab.com` CTA 오버레이

## 영상 레이아웃 규칙

- 배경의 칠판 영역이 실제 문제판 역할을 한다.
- 한글 예문은 칠판에 직접 적힌 것처럼 보여야 한다.
- 빠진 단어는 `_` 또는 시각적으로 분명한 빈칸으로 처리한다.
- 로마자 표기는 한글보다 작은 크기로 표시한다.
  - 예: 칠판 한글이 `14` 크기라면 로마자 표기는 `10` 정도
- 영어 설명 캡션은 칠판 텍스트를 가리지 않는 영역에 배치한다.
- 정답 공개 전까지는 완전한 정답 문장을 노출하지 않는다.

## 시각 연출 규칙

- 선생님 캐릭터 또는 선생님 이미지가 칠판을 가리키는 장면을 포함할 수 있다.
- 팔 움직임은 생성형으로 매번 새로 만들기보다, 포즈 변형이나 짧은 모션 루프를 재사용하는 방식이 우선이다.
- 배경/선생님/칠판은 반복 사용 가능한 템플릿 자산으로 관리한다.
- 예문, 빈칸, 정답, 보조 캡션만 episode별로 바뀌는 형태를 기본으로 한다.

## Nano Banana 2 자산 생성 규칙

`Video Editor`는 `Nano Banana 2`에 해당하는 Gemini 이미지 모델(`gemini-3.1-flash-image-preview`)을 **영상 자체 생성**이 아니라 **패널용 이미지 자산 생성**에 사용한다.

하지만 현재 기본 운영 모드는 이 단계 없이 진행한다.

- 기본값: `teacherImage` 기반 template-only 렌더
- 선택값: API key가 준비된 경우에만 Gemini 패널 자산 생성 사용

즉 `GEMINI_IMAGE_API_KEY`가 없다고 해서 제작 파이프라인이 막히면 안 된다.

권장 순서:

1. `source-packet.json` 생성
2. 기본 모드면 `scripts/render_malmoelab_quiz.py` 실행
3. 생성형 자산을 쓸 때만 `render-config.json`에서 `aiAssetGeneration.enabled=true`
4. 그 경우 `scripts/generate_gemini_quiz_assets.py` 실행 후 다시 렌더

생성 결과:

- `title-panel.png`
- `question-panel.png`
- `answer-panel.png`
- `asset-manifest.json`

운영 원칙:

- 생성형 이미지에는 칠판 위 문자, 로고, 자막을 직접 그리지 않는다.
- 실제 한글 문장, 로마자, 영어 질문, 정답 공개 문구는 최종 렌더러가 오버레이한다.
- 즉 이미지 생성 모델은 선생님 포즈, 교실 분위기, 칠판의 빈 시각 공간만 만든다.

권장 secret / env:

- `GEMINI_IMAGE_API_KEY`

대체 허용:

- `GEMINI_API_KEY`
- `GOOGLE_API_KEY`

`GEMINI_IMAGE_API_KEY`를 우선 권장하는 이유는, `gemini_local` CLI 로그인과 별도로 이미지 생성 API 키를 분리해 관리하기 쉽기 때문이다.

현재 운영 방침:

- 우선은 template-only 모드로 제작
- 반복 제작 포맷이 안정화된 뒤 필요할 때만 Gemini 패널 자산 생성 추가

## 참여 유도 문구 규칙

`Double tap` 문구는 좋아요 유도용 참여 카피로만 쓴다.

- 허용:
  - `Double tap if you know it.`
  - `Double tap when you get it.`
- 금지:
  - 탭하면 정답이 공개되는 것처럼 오해시키는 문구
  - 예: `Double tap to reveal the answer.`

즉, 실제 기능이 없는 상호작용을 약속하면 안 된다.

## TTS 언어 규칙

- TTS는 시청자의 모국어가 아니라 **교육 대상 언어**를 읽어야 한다.
- 영어권 사용자 대상 한글 교육 쇼츠라도, 음성은 한국어 문장과 한국어 정답을 한국어 발음으로 읽는다.
- learner-facing 질문, 보조 캡션, CTA는 영어로 유지할 수 있다.
- 즉 `caption language`와 `narration language`는 분리될 수 있다.
- `contentLanguageCode`는 교육 대상 언어를 뜻하고, `learnerLanguageCode`는 시청자 보조 언어를 뜻한다.
- `malmoelab-ko-quiz-*`는 기본적으로:
  - `contentLanguageCode = ko`
  - `learnerLanguageCode = en`
  - `narrationLanguageCode = ko`

운영 원칙:

- 수동 영어 TTS 세그먼트를 episode마다 복사해서 쓰지 않는다.
- source packet 또는 render config의 언어 코드를 기준으로 자동 내레이션을 만든다.
- voice 선택도 `contentLanguageCode`를 우선 기준으로 한다.
- 나중에 일본어, 영어, 중국어 교육 포맷으로 확장하더라도 같은 규칙을 유지한다.

## AI 고지 규칙

- 온스크린 영상 텍스트에는 `AI로 만들어진 영상입니다.` 같은 문구를 넣지 않는다.
- 설명란에는 채널 정책상 필요할 때만 AI 고지를 넣는다.
- 출처 고지는 설명란에서 처리한다.

## 설명란 규칙

설명란에는 아래를 자동으로 포함할 수 있어야 한다.

- 말모이랩 링크
- 음악 출처
- 배경 이미지 출처
- 캐릭터/배경 rights.md 기반 크레딧
- 필요 시 AI 고지 문구

## 말모이랩 데이터 소싱 기준

핵심 데이터는 아래 구조를 따른다.

- `words`
  - `word_text`
  - `romanization`
  - `reading_text`
  - `part_of_speech`
  - `topik_level`
  - `difficulty_score`
  - `is_published`
- `word_senses`
- `word_translations`
  - 영어 gloss
- `word_examples`
  - 예문 텍스트
  - 예문 번역
  - 번역 언어 코드
  - register label

현재 코드와 문서 기준으로, 교육 쇼츠 제작에는 `word_examples` 기반 예문 소싱이 가장 실용적이다.

관련 참고 경로:

- [malmoelab_service_standards.md](/home/kindsr/projects/devscent-malmoelab-main/docs/malmoelab_service_standards.md)
- [malmoelab_system_design.md](/home/kindsr/projects/devscent-malmoelab-main/docs/malmoelab_system_design.md)
- [word_metadata_repository.py](/home/kindsr/projects/devscent-malmoelab-main/backend/app/adapters/repositories/word_metadata_repository.py)
- [learn_sentences.py](/home/kindsr/projects/devscent-malmoelab-main/backend/app/adapters/api/learn_sentences.py)

## 말모이랩 예문 선택 규칙

- 게시된 데이터만 사용한다.
- 영어 번역이 있는 예문만 사용한다.
- 지나치게 긴 문장은 피한다.
- 목표 레벨보다 너무 어려운 문장은 피한다.
- 동일 sentence 또는 동일 example_text는 가급적 재사용하지 않는다.
- 같은 단어를 다시 써도 되지만, 예문은 최대한 겹치지 않게 한다.

## 권장 SQL 조회 방향

실제 구현은 read-only 계정으로 진행한다.

기본 조회는 아래 정보를 얻을 수 있어야 한다.

- focus word
- focus word romanization or reading
- English gloss
- example sentence
- English translation
- register label
- source item id

개념적으로는 아래 조합이다.

- `words`
- `word_senses`
- `word_translations`
- `word_examples`

필요하면 `topik_level`, `difficulty_score`, `is_published` 조건을 함께 쓴다.

## 중복 방지 규칙

반복 제작을 위해 사용 이력을 별도 ledger로 남긴다.

권장 파일:

- `/home/kindsr/projects/shortform-factory-studio/data/used_sentences.jsonl`

권장 필드:

```json
{"episodeSlug":"malmoelab-ko-quiz-001","wordId":"...","exampleId":"...","sentenceText":"...","publishedVideoId":"...","publishedAt":"2026-04-15T00:00:00Z"}
```

새 episode를 만들 때는:

1. 말모이랩 DB 후보 조회
2. `used_sentences.jsonl` 확인
3. 아직 쓰지 않은 example 우선 선택
4. 없을 때만 재사용

## 음악/자산 출처 규칙

- 저작권 안전한 무료 음악만 사용한다.
- 음악은 출처 URL과 라이선스를 함께 기록한다.
- 배경 이미지나 캐릭터에 `rights.md`가 있으면 설명란에 출처를 포함한다.
- 설명란에 출처가 누락되면 publish-ready로 간주하지 않는다.

## CTA 규칙

영상 안에서는 시각적 CTA 버튼 오버레이를 쓸 수 있다.

예:

- `Learn more at malmoelab.com`
- `Study more on MalmoeLab`

다만 YouTube Shorts 안에서 외부 사이트로 직접 클릭 이동하는 실제 버튼 기능은 기대하지 않는다.

운영상 추천:

- Shorts 영상에 시각적 CTA만 넣기
- 설명란에 `malmoelab.com` 링크 넣기
- 가능하면 related video를 같이 연결하기

## Paperclip secret 저장 방식

DB 접속정보는 repo에 적지 않는다.

`Shortform Factory` company secret로 저장한다.

권장 secret key:

- `MALMOELAB_DATABASE_URL`
- `MALMOELAB_BASE_URL`

권장값 예:

- `MALMOELAB_BASE_URL=https://malmoelab.com`

민감한 실제 접속 문자열은 `Channel Publisher & Analyst`가 아니라, 데이터 소싱 전담 role에만 준다.

## 권장 agent 구성

현재 구성에 아래 역할을 추가하는 것이 가장 좋다.

### `Sentence Source Operator`

이 role만 말모이랩 DB secret을 가진다.

책임:

- 예문 후보 조회
- focus word 선택
- 영어 gloss/예문 번역 확보
- 중복 회피 ledger 갱신
- source packet 생성

다른 agent는 DB 비밀번호를 몰라도 된다.

## 현재 agent 운영 권장

- `CEO`
  - 시리즈 승인
  - 포맷 변경 승인
- `Head of Content`
  - 기본 assignee
  - 새 episode 제작과 수정 총괄
- `Sentence Source Operator`
  - 예문 source packet 생성
- `Content Strategist`
  - 15초 퀴즈 브리프 설계
- `Script Writer`
  - 영어 질문 문구, reveal 문구, CTA 문구 작성
- `Video Editor`
  - 칠판 레이아웃, 팔 모션, Gemini 패널 자산 생성, 음악, 최종 합성
- `Quality & Fact Checker`
  - 한글, 로마자, 정답, 출처, 권리 검수
- `Channel Publisher & Analyst`
  - 설명란 출처 조립, 업로드, 관련 링크 정리

## Paperclip 업무 지시 규칙

- 새 영상 제작:
  - `new_episode`
  - assignee: `Head of Content`
  - project: `Weekly Production Engine`
- 기존 미발행 영상 수정:
  - 기존 issue comment
  - `작업 유형: revise_episode`
- 업로드만:
  - `publish_only`
  - assignee: `Channel Publisher & Analyst`
- 메타데이터 수정:
  - `metadata_update`
  - assignee: `Channel Publisher & Analyst`
- 포맷/시리즈 변경:
  - assignee: `CEO`
  - project: `Channel Launch Engine`

## 이번 포맷 전용 완료 조건

한 episode가 완료되려면 아래가 있어야 한다.

- source packet
- episode packet
- final mp4
- publish packet
- rights / music attribution data
- YouTube upload URL
