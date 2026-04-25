# SFS Console 사용 매뉴얼

이 문서는 현재 배포된 `sfs.devscent.com` 기준 운영자용 사용 매뉴얼이다.

## 현재 구현 범위

SFS Console은 v2 와이어프레임 전체가 완성된 상태가 아니다. 현재 동작하는 범위는 아래와 같다.

- workspace episode/character/format 스캔
- 제작 요청 draft 생성
- 제작 요청 Paperclip issue handoff
- 캐릭터 템플릿 파일 생성
- delivery token 발급/폐기
- 공개 delivery page와 다운로드
- 공개 client revision request 접수
- client revision request Paperclip handoff/sync
- 운영 health check

아직 자동 sync, job log, reference upload, frame-level review action, 검색, 권한 역할 분리는 구현되지 않았다.

## 로그인

1. `https://sfs.devscent.com`에 접속한다.
2. nginx Basic Auth를 통과한다.
3. SFS Console 로그인 폼에서 operator 계정으로 로그인한다.

환경변수는 project `.env`의 `SFS_OPERATOR_USERNAME`, `SFS_OPERATOR_PASSWORD`,
`SFS_AUTH_SECRET`을 사용한다.

## 프로덕션 데스크

용도: 현재 workspace의 episode 상태를 빠르게 확인한다.

동작하는 기능:

- episode 목록 표시
- episode별 character/status/next gate 표시
- `Package` 클릭 시 Delivery Room 이동
- `Open` 클릭 시 Review Studio 이동

주의:

- 상단 preview는 실제 final mp4가 있는 episode만 재생 가능하다.
- final mp4가 없으면 재생 버튼을 보여주지 않고 `No playable final mp4` 상태로 표시한다.
- `Run scanner`는 아직 수동 재스캔 job이 아니라 잠긴 기능으로 다뤄야 한다.

## 리뷰 스튜디오

용도: final mp4가 있는 episode를 재생하고, 리뷰 상태를 한 화면에서 확인한다.

동작하는 기능:

- final mp4가 있으면 native video player로 재생
- thumbnail이 있으면 poster로 표시
- final mp4가 없으면 재생 불가 상태 표시
- `Approve delivery` 클릭 시 Delivery Room 이동

아직 미구현:

- frame note 편집
- contact sheet frame 선택
- audio meter 실제 분석
- `Request revision` 직접 생성

현재 revision request는 public delivery page에서 받거나 Paperclip에서 처리한다.

## 요청 빌더

용도: Paperclip issue로 넘길 제작 요청 draft를 만든다.

사용 순서:

1. 요청 유형을 선택한다.
2. episode slug를 입력한다.
3. character를 선택한다.
4. format profile을 선택한다.
5. reference path, output target, completion criteria, creative brief를 입력한다.
6. `Validate`를 눌러 Paperclip markdown을 생성한다.
7. 내용이 맞으면 `Save draft`를 누른다.
8. 저장된 draft row의 `Paperclip` 버튼을 눌러 Paperclip issue를 생성한다.

주의:

- 이제 샘플값이 자동으로 채워지지 않는다.
- `Save draft`는 필수 항목이 모두 입력되어야 열린다.
- `Validate`는 누락 항목을 확인하기 위해 비어 있는 상태에서도 누를 수 있다.

## 캐릭터 랩

용도: 기존 캐릭터 파일 상태를 확인하고, 새 캐릭터 템플릿을 생성한다.

기존 캐릭터 확인:

1. 오른쪽 `Generated files` 목록에서 캐릭터를 클릭한다.
2. 선택된 캐릭터의 slug, display name, rights 상태를 확인한다.
3. `bible`, `prompt`, `rights`, `voice` 파일 존재 여부를 확인한다.

새 캐릭터 생성:

1. `New character template`에서 slug를 입력한다.
2. display name, series, voice default, negative prompt를 입력한다.
3. rights status를 선택한다.
4. `Create character`를 누른다.

생성 조건:

- slug는 lowercase kebab-case여야 한다. 예: `jjiroo-friend`
- 기존 character slug와 중복되면 생성할 수 없다.
- 필수 항목이 비어 있으면 생성할 수 없다.

생성 파일:

- `characters/<slug>/bible.md`
- `characters/<slug>/prompts.md`
- `characters/<slug>/rights.md`
- `characters/<slug>/voice.json`
- `characters/<slug>/refs/README.md`

아직 미구현:

- reference image upload
- canonical image 지정
- unsafe variation 표시

reference 이미지는 현재 서버 파일 시스템에서 직접 넣어야 한다.

## 딜리버리 룸

용도: 클라이언트 전달 링크를 만들고, 수정 요청을 추적한다.

사용 순서:

1. episode를 선택한다.
2. readiness gate를 확인한다.
3. 모든 gate가 ready이면 `Generate token`을 누른다.
4. 생성된 `/delivery/<token>` 링크를 클라이언트에게 전달한다.
5. 클라이언트가 public page에서 파일을 확인하고 revision request를 남긴다.
6. Delivery Room의 revision queue에서 요청을 확인한다.
7. Paperclip 진행 상태를 갱신하려면 `Paperclip sync`를 누른다.

Revision queue 필터:

- `open`: 완료되지 않은 요청
- `blocked`: 막힌 요청
- `resolved`: 완료 또는 취소 처리된 요청
- `all`: 전체 요청

주의:

- 자동 Paperclip sync는 아직 켜지지 않았다.
- token은 access limit, expiry, revoke 상태를 가진다.
- 공개 form은 hidden spam trap과 token/IP rate limit을 적용한다.

## 운영 설정

용도: 서비스 연결 상태를 확인한다.

동작하는 기능:

- `Run health check`
- workspace 경로 확인
- Postgres 연결 확인
- Paperclip 설정 확인
- scanner episode index 개수 확인

아직 미구현:

- job log viewer
- runbook 직접 열기 버튼
- backup trigger

## 문제 해결

플레이어가 재생되지 않는 경우:

- 해당 episode에 `renders/final/*.mp4` 또는 `renders/picture-lock/*.mp4`가 있는지 확인한다.
- 파일이 없으면 정상적으로 재생 불가 상태가 표시된다.

캐릭터 생성 버튼이 비활성화된 경우:

- slug가 lowercase kebab-case인지 확인한다.
- 기존 slug와 중복되지 않는지 확인한다.
- display name, series, voice default, negative prompt가 모두 입력됐는지 확인한다.

Delivery token 생성이 실패하는 경우:

- final mp4, thumbnail, review report, publish packet이 모두 있는지 확인한다.
- character에 `rights.md`가 있는지 확인한다.

Revision sync가 기대대로 보이지 않는 경우:

- Paperclip issue ref가 있는 요청인지 확인한다.
- `Paperclip sync`를 수동으로 실행한다.
- Paperclip API 설정과 `/ops/health` 결과를 확인한다.
