# YouTube 채널 설정

이 문서는 실제 YouTube 채널을 `Shortform Factory`에 연결할 때 권장되는 순서를 정리한 가이드입니다.

YouTube 자격증명은 `Channel Publisher & Analyst`만 가져야 합니다.

## 필요한 값

아래 4개 값이 필요합니다.

- `YOUTUBE_CHANNEL_ID`
- `YOUTUBE_OAUTH_CLIENT_ID`
- `YOUTUBE_OAUTH_CLIENT_SECRET`
- `YOUTUBE_OAUTH_REFRESH_TOKEN`

권장 추가 값:

- `YOUTUBE_DEFAULT_PRIVACY_STATUS=private`
- `YOUTUBE_DEFAULT_CATEGORY_ID=22`
- `YOUTUBE_DISCLOSURE_TEXT=AI로 만들어진 영상입니다.`
- `YOUTUBE_NOTIFY_SUBSCRIBERS=false`

## 1. Google Cloud 준비

Google Cloud Console에서:

1. 대상 프로젝트를 엽니다.
2. `YouTube Data API v3`를 활성화합니다.
3. OAuth client를 생성합니다.
4. client 타입은 `Desktop app`으로 설정합니다.
5. client ID와 client secret을 복사합니다.

OAuth 앱이 아직 `Testing` 상태라면:

1. Google Auth/OAuth audience 설정을 엽니다.
2. 실제로 로그인할 Google 계정을 `Test user`로 추가합니다.

## 2. 채널 ID 확인

YouTube에서:

1. 실제 채널 소유자 계정으로 로그인합니다.
2. `Settings`를 엽니다.
3. `Advanced settings`를 엽니다.
4. 채널 ID를 복사합니다.

이 값을 `YOUTUBE_CHANNEL_ID`로 저장합니다.

## 3. Refresh Token 받기

Paperclip 서버에서 OAuth helper를 실행합니다.

```bash
cd /home/kindsr/paperclip
node scripts/youtube-oauth-bootstrap.mjs \
  --client-id "<YOUR_CLIENT_ID>" \
  --client-secret "<YOUR_CLIENT_SECRET>"
```

브라우저가 로컬 PC에 있다면 먼저 SSH 포트 포워딩을 사용합니다.

```bash
ssh -L 8789:127.0.0.1:8789 kindsr@<paperclip-server>
```

그 다음:

1. helper가 출력한 URL을 브라우저에서 엽니다.
2. 실제 YouTube 채널 소유자 Google 계정으로 로그인합니다.
3. 접근 권한을 승인합니다.
4. helper가 아래 값을 출력할 때까지 기다립니다.
   - `refreshToken`
   - `channelId`
   - `channelTitle`

사용 방법:

- `refreshToken` -> `YOUTUBE_OAUTH_REFRESH_TOKEN`
- `channelId` -> `null`이 아닐 때만 `YOUTUBE_CHANNEL_ID`

`channelId`가 `null`이면 YouTube 설정 화면에서 직접 복사한 채널 ID를 사용합니다.

## 4. Paperclip에 secret 등록

회사:

- `Shortform Factory`

에이전트:

- `Channel Publisher & Analyst`

UI 경로:

1. `Shortform Factory`를 엽니다.
2. `Agents`를 엽니다.
3. `Channel Publisher & Analyst`를 엽니다.
4. `Configuration`을 엽니다.
5. `Permissions & Configuration`을 엽니다.
6. `Environment variables`를 찾습니다.

아래 키로 row를 만듭니다.

- `YOUTUBE_CHANNEL_ID`
- `YOUTUBE_OAUTH_CLIENT_ID`
- `YOUTUBE_OAUTH_CLIENT_SECRET`
- `YOUTUBE_OAUTH_REFRESH_TOKEN`

그 다음 아래 값도 추가합니다.

- `YOUTUBE_DEFAULT_PRIVACY_STATUS`
- `YOUTUBE_DEFAULT_CATEGORY_ID`
- `YOUTUBE_DISCLOSURE_TEXT`
- `YOUTUBE_NOTIFY_SUBSCRIBERS`

민감한 값마다:

1. 우선 `Plain`으로 입력합니다.
2. `Seal`을 클릭합니다.
3. 회사 secret으로 저장합니다.
4. agent 설정 전체를 저장합니다.

## 5. 수동 Dry Run 실행

agent가 실제로 업로드하기 전에 직접 검증합니다.

```bash
cd /home/kindsr/paperclip
YOUTUBE_CHANNEL_ID="<channel-id>" \
YOUTUBE_OAUTH_CLIENT_ID="<client-id>" \
YOUTUBE_OAUTH_CLIENT_SECRET="<client-secret>" \
YOUTUBE_OAUTH_REFRESH_TOKEN="<refresh-token>" \
node scripts/youtube-upload.mjs \
  --title "Shortform Factory private test" \
  --description "Private test upload

AI로 만들어진 영상입니다." \
  --video-file "/absolute/path/to/test.mp4"
```

이 단계는 실제 게시 없이 자격증명과 요청 형식을 검증합니다.

## 6. Private 테스트 업로드 실행

dry run이 정상이라면:

```bash
cd /home/kindsr/paperclip
YOUTUBE_CHANNEL_ID="<channel-id>" \
YOUTUBE_OAUTH_CLIENT_ID="<client-id>" \
YOUTUBE_OAUTH_CLIENT_SECRET="<client-secret>" \
YOUTUBE_OAUTH_REFRESH_TOKEN="<refresh-token>" \
node scripts/youtube-upload.mjs \
  --title "Shortform Factory private test" \
  --description "Private test upload

AI로 만들어진 영상입니다." \
  --video-file "/absolute/path/to/test.mp4" \
  --publish
```

첫 업로드 테스트는 `private`로 유지합니다.

## 7. Agent 기반 업로드

자격증명을 설정한 뒤에는 `Channel Publisher & Analyst`가 publish packet 이슈 코멘트에서 바로 업로드할 수 있습니다.

코멘트는 아래 heading으로 시작해야 합니다.

```md
## YouTube Publish Packet Ready
```

그 아래에 publish payload를 담은 JSON 코드 블록을 넣습니다.

## 현재 작업 디렉터리

현재 `Shortform Factory` agent들의 작업 루트는 아래로 설정되어 있습니다.

- `/home/kindsr/projects/shortform-factory-studio`

이 경로를 아래 산출물의 canonical 작업 위치로 사용합니다.

- 에피소드 패킷
- 렌더 결과물
- 썸네일
- 최종 영상 파일

## 운영 가드레일

- YouTube secret을 `CEO`, `Head of Content`, `Script Writer`나 다른 제작 agent에게 주지 않습니다.
- 첫 테스트 업로드는 `private`로 유지합니다.
- YouTube 설명란에는 `AI로 만들어진 영상입니다.`를 포함합니다.
- OAuth 앱이 아직 testing 상태라면 tester 제한과 토큰 불안정성이 있을 수 있습니다.
