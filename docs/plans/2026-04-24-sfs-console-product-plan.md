# SFS Console Product Plan

날짜: 2026-04-24
대상 경로: `/home/kindsr/projects/shortform-factory-studio`
대상 도메인: `sfs.devscent.com`
상태: 기획안

## 1. 결론

`sfs.devscent.com`에는 Paperclip을 대체하는 새 오케스트레이터가 아니라, `shortform-factory-studio` 폴더를 사람이 안전하게 다루는 운영 웹앱을 둔다.

권장 제품명은 `SFS Console`이다.

역할은 네 가지다.

1. 사용자나 내부 운영자가 최종 결과물을 서버 접속 없이 받는다.
2. 새 에피소드 제작 요청을 Paperclip 이슈 규칙에 맞는 구조화 요청으로 만든다.
3. 캐릭터, 권리, 프롬프트, voice 설정, reference asset을 관리한다.
4. episode folder의 산출물 상태를 읽어 후반작업, QA, publish handoff를 추적한다.

## 2. 현재 구조에서 확인한 사실

- 현재 workspace는 `characters/`, `episodes/`, `formats/`, `shared/`, `scripts/`, `docs/`를 가진 파일시스템 기반 제작 루트다.
- 현재 캐릭터 폴더는 10개, 에피소드 폴더는 40개다.
- 대표 제작 표준은 `malmoelab-keyframe-dub-after-picture-v1`, `pet-story-short-vertical-v1`, `pet-toon-image-only-v1` 등 `formats/*/profile.json`에 있다.
- `docs/PAPERCLIP_ISSUE_OPERATIONS.md`는 Paperclip 이슈의 `new_episode`, `revise_episode`, `publish_only`, `metadata_update` 규칙을 이미 정의한다.
- `episodes/malmoelab-template/README.md`는 `source -> brief -> script -> keyframe review -> picture -> dub -> typography -> QA -> publish` 체인을 정식 표준으로 둔다.
- 기존 계획 문서 `2026-04-17-dubbing-workbench-lite-ia.md`는 후반 제작 콘솔이 필요하다고 결론내렸다.
- `pc.devscent.com`은 `/opt/infra/nginx/conf/services-enabled/96-harness.conf`에서 `paperclip:3100`으로 연결되어 있다.
- `sfs.devscent.com`은 현재 nginx 설정에 없다.
- 서버 런북 기준 신규 서비스는 `80/443` nginx 경유, Docker `edge` 네트워크, 호스트 포트 미공개를 기본으로 해야 한다.
- Postgres는 `/opt/infra/postgres14`의 shared `postgres14`를 쓰며 호스트에서는 `127.0.0.1:5432`로만 바인딩되어 있다.

## 3. 사용자와 작업

### 3.1 외부 사용자 또는 클라이언트

목표:

- 승인된 결과물 링크를 받는다.
- final mp4, thumbnail, review report, publish metadata를 내려받는다.
- 수정 요청을 폼으로 남긴다.

권장 화면:

- `Delivery Package`
- `Revision Request`

### 3.2 Producer

목표:

- 새 에피소드 요청을 만든다.
- 캐릭터와 포맷을 선택한다.
- 필요한 reference, rights, output 조건 누락을 확인한다.
- Paperclip 이슈 본문을 자동 생성하거나 API로 이슈를 만든다.

권장 화면:

- `New Request`
- `Episode Pipeline`

### 3.3 Content Operator

목표:

- episode folder를 열지 않고 상태를 본다.
- picture lock, dub lock, type lock, final export, QA 상태를 확인한다.
- preview, contact sheet, frame map, review report를 한 화면에서 본다.

권장 화면:

- `Episodes`
- `Episode Workspace`
- `Review`

### 3.4 Character Manager

목표:

- 새 캐릭터를 추가한다.
- `bible.md`, `prompts.md`, `rights.md`, `voice.json`, reference image/video를 template 기준으로 채운다.
- public production에 사용할 수 있는 rights 상태인지 확인한다.

권장 화면:

- `Characters`
- `Character Editor`

### 3.5 Publisher

목표:

- final output과 publish packet을 확인한다.
- YouTube secret 값은 보지 않고 secret 존재 여부만 확인한다.
- `publish_only` 또는 `metadata_update` 요청을 Paperclip의 `Channel Publisher & Analyst`에게 넘긴다.

권장 화면:

- `Publish Handoff`

## 4. 제품 범위

### 4.1 MVP

MVP는 읽기 중심이어야 한다.

- file-system scanner
- episode index
- character registry
- final output delivery package
- structured request builder
- character creation wizard
- review report viewer
- Paperclip issue body generator
- auth + role
- `/health` endpoint

MVP에서 하지 않을 것:

- 브라우저 기반 풀 타임라인 편집기
- 영상 생성 모델 직접 호출
- YouTube secret 직접 보관
- 대용량 영상 파일 DB 저장
- Paperclip job scheduler 재구현

### 4.2 V1

- Paperclip API 연동으로 issue/comment 생성
- voice slot 업로드와 승인 take 관리
- typography slot 편집
- final export script 실행 job
- delivery link 만료/재발급
- audit log

### 4.3 V2

- Dubbing Workbench Lite 기능 확장
- browser recorder
- contact sheet annotation
- shot/keyframe approval gate
- format profile editor
- client-facing revision loop

## 5. 정보 구조

전역 네비게이션:

1. `Dashboard`
2. `Requests`
3. `Episodes`
4. `Characters`
5. `Deliveries`
6. `Docs`
7. `Settings`

핵심 객체:

- `ProductionRequest`: 사람이 만든 요청
- `Episode`: `episodes/<slug>`와 매핑되는 제작 단위
- `Character`: `characters/<slug>`와 매핑되는 반복 캐릭터
- `FormatProfile`: `formats/<id>/profile.json`
- `DeliveryPackage`: 승인된 외부 전달 묶음
- `PaperclipLink`: Paperclip issue/comment/task 연결
- `Job`: scanner/export/postprocess 실행 기록

## 6. 권장 아키텍처

권장 기본 방향은 `Next.js + FastAPI + Postgres`다.

이유:

- 서버 내 다른 서비스가 이미 Next.js/FastAPI 패턴을 많이 쓴다.
- Python backend가 기존 `scripts/`와 ffmpeg 중심 후반작업을 직접 다루기 쉽다.
- Next.js는 internal dashboard와 delivery page를 같은 앱에서 제공하기 좋다.
- Postgres는 metadata, audit, delivery token, approval state만 저장하고 대용량 media는 파일 경로로 참조한다.

컨테이너:

```text
sfs-web       Next.js standalone, internal Docker network only
sfs-api       FastAPI, SQLAlchemy/Alembic, workspace scanner
sfs-worker    optional Python worker for long scripts and exports
postgres14    shared DB in /opt/infra/postgres14
nginx         public ingress
```

Docker network:

```text
edge
```

호스트 포트:

```text
none
```

Nginx:

```text
/opt/infra/nginx/conf/services-enabled/97-sfs.conf

server_name sfs.devscent.com;
/api/*   -> http://sfs-api:8000
/health  -> http://sfs-api:8000/health
/media/* -> http://sfs-api:8000/media/*
/        -> http://sfs-web:3000
```

DB:

```text
postgres14 database: shortform_factory
```

파일 마운트:

```text
/home/kindsr/projects/shortform-factory-studio:/workspace/shortform-factory-studio
```

권장 기본값은 backend read-only scanner에서 시작하고, character/request 생성 등 명시적 action만 쓰기 권한을 부여하는 것이다.

## 7. 데이터 모델 초안

```text
users
  id, email, name, role, created_at

characters
  id, slug, display_name, status, rights_status, root_path, created_at, updated_at

character_assets
  id, character_id, kind, relative_path, media_type, sha256, is_canonical, created_at

episodes
  id, slug, series_slug, character_id, format_profile_id, status,
  root_path, source_issue_ref, final_output_path, thumbnail_path,
  picture_lock_path, review_report_path, publish_packet_path,
  discovered_at, updated_at

episode_assets
  id, episode_id, kind, stage, relative_path, media_type, sha256, mtime, created_at

production_requests
  id, request_type, title, body, episode_slug, character_slug,
  format_profile_id, status, paperclip_issue_ref, created_by, created_at

delivery_packages
  id, episode_id, title, token_hash, expires_at, status, created_by, created_at

reviews
  id, episode_id, gate, status, reviewer_id, notes, report_path, created_at

jobs
  id, kind, target_type, target_id, status, command_name, started_at, finished_at, log_path

audit_logs
  id, actor_id, action, target_type, target_id, payload_json, created_at
```

경로 저장 규칙:

- DB에는 absolute path를 저장하지 않는다.
- `shortform-factory-studio` 기준 relative path만 저장한다.
- API는 path traversal을 막기 위해 allowlist root를 강제한다.

## 8. 파일시스템 스캐너 규칙

스캐너는 아래 순서로 episode 상태를 추론한다.

1. `packet.md`, `source-packet.json`, `episode.schema.json` 존재 여부
2. `video-generation-job.json`, `keyframe-plan.json`, `storyboard/*` 존재 여부
3. `renders/picture-lock/*` 또는 `renders/final/*` 존재 여부
4. `audio/*`, `voice-slots.json`, `typography-slots.json` 존재 여부
5. `review/*review-report*.md`, `review/contact-sheets/*` 존재 여부
6. `final/*`, `publish-packet.json` 존재 여부

상태 매핑:

```text
request-draft
packet-ready
storyboard-ready
keyframe-review
picture-ready
picture-lock
dub-ready
dub-lock
type-ready
type-lock
final-export
qa-ready
qa-pass
delivery-ready
published
blocked
```

## 9. Paperclip 관계

Paperclip은 계속 agent execution layer로 둔다.

`SFS Console`은 다음만 담당한다.

- 요청을 구조화한다.
- Paperclip 이슈 템플릿을 생성한다.
- Paperclip issue/comment/task link를 저장한다.
- 실행 결과가 workspace에 남으면 scanner로 읽는다.
- 사용자가 서버 shell 없이 결과를 확인한다.

초기에는 Paperclip API를 직접 쓰지 않아도 된다. 폼에서 생성한 Markdown을 사람이 복사해도 MVP는 성립한다.

V1에서 Paperclip API를 붙인다.

## 10. 보안과 운영 가드레일

- `sfs.devscent.com`은 app-level auth가 필요하다.
- delivery link는 token 기반, 만료일 필수, 다운로드 audit log 필수.
- YouTube OAuth secret은 SFS Console에 저장하지 않는다.
- secret 값은 보여주지 않고 존재 여부와 마지막 검증 시각만 보여준다.
- media API는 workspace allowlist 밖 파일을 절대 서빙하지 않는다.
- nginx는 `80/443`만 public ingress로 사용한다.
- compose에는 host `ports`를 두지 않는다.
- `/health`는 인증 없이 열어 모니터링 가능하게 한다.
- 신규 서비스 등록 시 `/home/kindsr/server-runbook/02_SERVICE_INVENTORY.md`, `03_OPS_CHANGELOG.md`, `09_MONITORING_LOGGING.md`를 갱신한다.

## 11. 배포 초안

추천 파일:

```text
/home/kindsr/projects/shortform-factory-studio/apps/sfs-console/
  docker-compose.yml
  backend/
  frontend/
```

또는 운영 경계가 더 명확해야 하면 별도 repo:

```text
/home/kindsr/projects/devscent-sfs-console
```

처음에는 현재 repo 안에 두는 것이 낫다. 이유는 앱이 이 repo의 파일 구조를 product contract로 삼기 때문이다.

배포 절차:

1. DB `shortform_factory` 생성
2. Alembic migration 실행
3. `sfs-api`, `sfs-web`를 `edge` network에 붙여 기동
4. `97-sfs.conf` 추가
5. certbot으로 `sfs.devscent.com` 인증서 발급
6. `docker exec nginx nginx -t`
7. `docker exec nginx nginx -s reload`
8. `https://sfs.devscent.com/health` smoke test

## 12. 첫 구현 순서

1. FastAPI backend skeleton과 `/health`
2. Postgres schema와 Alembic
3. workspace scanner read-only API
4. Next.js dashboard, episodes, characters, deliveries 화면
5. delivery package token download
6. request builder와 Paperclip issue Markdown generator
7. character creation wizard
8. Paperclip API integration
9. export/postprocess job runner

## 13. 주요 결정

지금 결정해야 하는 것은 앱의 본질이다.

권장 결정:

- `SFS Console`은 제작 실행 엔진이 아니라 제작 운영 콘솔이다.
- Paperclip은 agent 실행 엔진으로 유지한다.
- 대용량 파일은 DB로 옮기지 않는다.
- 먼저 read-only scanner와 delivery flow를 만든다.
- write action은 요청 생성, 캐릭터 생성, delivery package 생성부터 제한적으로 연다.
