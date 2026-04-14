# 에피소드 패킷: 나비의 한국 여행

## 메타데이터

- 에피소드 슬러그: `nabi-korea-trip-001`
- 소스 이슈: [SHO-8](/SHO/issues/SHO-8)
- 제작 모드: `reference-only`
- 주인공: `나비`
- 캐릭터 바이블: `/home/kindsr/projects/shortform-factory-studio/characters/nabi/bible.md`
- 레퍼런스 패킷 경로: `/home/kindsr/projects/shortform-factory-studio/characters/nabi`
- 최종 렌더 기준 레퍼런스 이미지: `/home/kindsr/projects/shortform-factory-studio/characters/nabi/나비_IMG_1286.png`
- 출력 대상: YouTube Shorts
- 목표 길이: 15초
- 화면비: `9:16`
- 고지 문구: `AI로 만들어진 영상입니다.`
- 고지 위치: 전 장면 우하단 번인 + `publish-packet.json` 설명란 본문

## 패키징 약속

- 주제: 한국을 여행하는 나비
- 시청자에게 주는 약속: 서울, 부산, 제주를 15초 안에 빠르게 훑으며 다음 여행 상상을 자극한다.
- 첫 1초 패키징 약속: `나비랑 15초 만에 한국 한 바퀴 돌아볼래?`
- 유지해야 할 핵심: 장소 전환이 빨라야 하고, 나비의 얼굴/귀 포인트/꼬리 붕대가 장면마다 유지되어야 한다.

## 스타일 타깃

- 밝고 귀여운 여행 브이로그 톤을 유지하되, 화면 전환은 장난스럽기보다 빠르고 또렷해야 한다.
- 서울, 부산, 제주 각 구간은 색감과 실루엣이 즉시 달라 보여야 하며, 장소 변경 자체가 리텐션 장치로 작동해야 한다.
- 자막과 장소 라벨은 배경 설명용이 아니라 시청자가 1초 안에 맥락을 잡게 만드는 정보 레이어로만 사용한다.

## 내레이션 및 화면 텍스트

- 내레이션:
  - `서울의 밤부터`
  - `부산의 바다를 지나`
  - `제주의 바람까지`
  - `나비랑 한국 한 바퀴`
- 화면 자막:
  - `서울의 밤`
  - `부산의 바다`
  - `제주의 바람`
  - `다음 여행도 같이 갈래?`
- CTA:
  - `다음 여행 편도 보고 싶다면 구독해줘`

## 페이싱 및 쇼트 구조

1. `0.0s-5.0s` 서울
   - 목적: 첫 장면에서 캐릭터와 여행 콘셉트를 동시에 잠근다.
   - 화면: 서울 야경 톤, 남산타워 느낌 실루엣, 정면을 보는 나비
   - 보이스/텍스트: `서울의 밤부터` / `서울의 밤`
   - 전환: 오프닝 타이틀 뒤 즉시 진입, 5초 지점에서 하드 컷
   - 리텐션 체크: 1초 안에 `한국 여행`과 `나비`를 둘 다 읽을 수 있어야 함
2. `5.0s-10.0s` 부산
   - 목적: 중간 5초에서 색감과 위치를 바꿔 스와이프 이탈을 줄인다.
   - 화면: 해변과 다리 실루엣, 더 밝은 블루 계열, 좌측 배치 나비
   - 보이스/텍스트: `부산의 바다를 지나` / `부산의 바다`
   - 전환: 서울에서 부산으로 하드 컷, 텍스트와 위치 반전으로 리듬 확보
   - 리텐션 체크: 서울과 다른 장소감이 즉시 보이는지 확인
3. `10.0s-15.0s` 제주
   - 목적: 마무리 풍경과 CTA를 함께 남기며 루프 가능성을 만든다.
   - 화면: 녹색 풍경, 산 실루엣, 돌하르방 요소, 우측 배치 나비
   - 보이스/텍스트: `제주의 바람까지` / `다음 여행도 같이 갈래?`
   - 전환: 부산에서 제주로 하드 컷, 마지막 2초는 CTA와 여운 유지
   - 리텐션 체크: CTA가 과하게 늦지 않고 풍경 마감과 동시에 읽히는지 확인

## 쇼트 실행 플랜

1. `Shot 01 / 서울 / 0.0s-5.0s`
   - 주인공: `나비`
   - 레퍼런스: `/home/kindsr/projects/shortform-factory-studio/characters/nabi/나비_IMG_1286.png`
   - 배경 소스: `render_prototype.py`의 `seoul` fallback scene
   - 프레임 기준: `/home/kindsr/projects/shortform-factory-studio/episodes/nabi-korea-trip-001/renders/frames`
   - 연속성 메모: 정면 시선, 파란 귀 안쪽, 꼬리 끝 하늘색, 꼬리 붕대 유지
2. `Shot 02 / 부산 / 5.0s-10.0s`
   - 주인공: `나비`
   - 레퍼런스: `/home/kindsr/projects/shortform-factory-studio/characters/nabi/나비_IMG_1286.png`
   - 배경 소스: `render_prototype.py`의 `busan` fallback scene
   - 프레임 기준: `/home/kindsr/projects/shortform-factory-studio/episodes/nabi-korea-trip-001/renders/frames`
   - 연속성 메모: 캐릭터 크기만 소폭 조정 가능, 얼굴 구조와 검은 눈 라인은 유지
3. `Shot 03 / 제주 / 10.0s-15.0s`
   - 주인공: `나비`
   - 레퍼런스: `/home/kindsr/projects/shortform-factory-studio/characters/nabi/나비_IMG_1286.png`
   - 배경 소스: `render_prototype.py`의 `jeju` fallback scene
   - 프레임 기준: `/home/kindsr/projects/shortform-factory-studio/episodes/nabi-korea-trip-001/renders/frames`
   - 연속성 메모: CTA를 띄우더라도 귀/꼬리 포인트를 가리지 말 것

## 연속성 및 비주얼 가드레일

- 나비는 모든 장면에서 동일한 원본 레퍼런스 이미지 기반으로 처리한다.
- 귀 안쪽 하늘색, 꼬리 끝 하늘색, 꼬리 붕대, 검은 눈 라인은 절대 드리프트시키지 않는다.
- 장소가 바뀌어도 의상 추가나 체형 변화는 넣지 않는다.
- 오버레이는 장소 라벨과 AI 고지 외에는 최소화해 화면 혼잡을 막는다.

## 자산 및 출처 메모

- 실제 캐릭터 입력:
  - `/home/kindsr/projects/shortform-factory-studio/characters/nabi/나비_IMG_1286.png`
- 실제 배경 입력:
  - 없음. `/home/kindsr/projects/shortform-factory-studio/episodes/nabi-korea-trip-001/assets/backgrounds/images`에는 현재 `.gitkeep`만 존재한다.
- 최종 MP4와 썸네일의 배경:
  - `render_prototype.py` 내부 fallback scene generation으로 생성됨
  - 서울: 야경/타워 형태를 코드로 합성
  - 부산: 바다/다리 실루엣을 코드로 합성
  - 제주: 산/돌하르방 형태를 코드로 합성
- 음악: 없음
- 효과음: 없음
- 오버레이:
  - 장소 라벨
  - 전 장면 우하단 AI 고지
  - 영상 내 번인 자막

## 산출물 및 추적 경로

- 렌더 스크립트: `/home/kindsr/projects/shortform-factory-studio/episodes/nabi-korea-trip-001/render_prototype.py`
- 렌더 프레임 폴더: `/home/kindsr/projects/shortform-factory-studio/episodes/nabi-korea-trip-001/renders/frames`
- 최종 영상: `/home/kindsr/projects/shortform-factory-studio/episodes/nabi-korea-trip-001/final/nabi-korea-trip-001-v1.mp4`
- 최종 썸네일: `/home/kindsr/projects/shortform-factory-studio/episodes/nabi-korea-trip-001/final/nabi-korea-trip-001-thumb.png`
- 게시 패킷: `/home/kindsr/projects/shortform-factory-studio/episodes/nabi-korea-trip-001/publish-packet.json`
- 렌더 무결성 노트: `/home/kindsr/projects/shortform-factory-studio/episodes/nabi-korea-trip-001/render-notes.md`

## QA 전달 메모

- 현재 패킷은 publish-ready 선언이 아니다.
- QA는 아래 항목을 별도로 확인해야 한다.
  - 실제 MP4에서 `AI로 만들어진 영상입니다.` 문구가 전 구간 읽히는지
  - 캐릭터 핵심 포인트가 장면별로 흔들리지 않는지
  - 설명란 고지가 `publish-packet.json`과 최종 업로드 화면에서 일치하는지
  - 코드 fallback 배경을 사용한 점이 패킷/README/render note와 일치하는지

## 쇼츠 출력 체크리스트

- 소스 이슈, 주인공, 레퍼런스 경로, 제작 모드가 패킷에 명시되어 있음
- 15초 러닝타임, `9:16`, 한국어 자막 기준이 패킷과 최종 MP4에 맞춰져 있음
- 첫 1초 훅과 장소 전환 구조가 패키징 약속과 일치함
- 장소 라벨, 내레이션, CTA가 과장된 사실 주장 없이 구성됨
- AI 고지 문구가 패킷과 게시 설명에 모두 기록되어 있음
- 실제 배경 입력 부재와 fallback scene 사용 사실이 패킷, README, render note에 반영되어 있음
- 최종 산출물 경로(MP4, 썸네일, publish packet, render notes)가 모두 추적 가능함
- 게시 보류 항목: `/home/kindsr/projects/shortform-factory-studio/characters/nabi/rights.md` 권리 정보 미기재로 QA 재승인 전까지 업로드 불가
