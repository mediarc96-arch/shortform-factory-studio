# SFS Console Implementation Plan v2

날짜: 2026-04-24
기준 와이어프레임: `docs/wireframes/2026-04-24-sfs-console-wireframes-v2.html`
상태: 구현 전 실행 계획

## 1. 결론

`SFS Console` 구현은 v2 와이어프레임을 기준으로 진행한다.

제품 방향은 단순 관리자 페이지가 아니라 영상 제작 관제실이다. 첫 화면은 KPI 카드가 아니라 리뷰 가능한 영상 오브젝트, 컷 증거, 승인 게이트, 전달 리스크를 먼저 보여준다.

기술 방향은 `Next.js + FastAPI + Postgres` 모노레포다. 백엔드는 Python 클린 아키텍처와 TDD를 기준으로 하고, 프론트엔드는 Next.js App Router와 i18n dictionary 기반 UI를 기준으로 한다.

기본 언어는 한국어다.

지원 로케일:

| 사용자 표기 | 내부 코드 | 언어 |
| --- | --- | --- |
| KO | `ko-KR` | 한국어 |
| US | `en-US` | 미국 영어 |
| JP | `ja-JP` | 일본어 |
| CN | `zh-CN` | 중국어 간체 |
| SP | `es-ES` | 스페인어 |

`SP`는 사용자가 부르는 표기만 유지하고, 내부 구현은 표준 BCP 47 코드인 `es-ES`를 쓴다. 추후 남미권 Spanish가 필요하면 `es-419`를 추가한다.

## 2. 이전 PLAN 상태

이미 있는 문서:

- `docs/plans/2026-04-24-sfs-console-product-plan.md`
- `docs/plans/2026-04-24-sfs-console-storyboard.md`
- `docs/wireframes/2026-04-24-sfs-console-wireframes.html`
- `docs/wireframes/2026-04-24-sfs-console-wireframes-v2.html`

부족했던 문서:

- v2 와이어프레임을 기준으로 한 실제 구현 PLAN
- i18n 범위와 로케일 코드 결정
- 상업 사용 가능한 폰트 정책
- 모노레포 경계
- TDD 수용 기준
- 클린 아키텍처 레이어와 테스트 전략

이 문서가 해당 공백을 채운다.

## 3. i18n 정책

### 3.1 원칙

- 기본 로케일은 `ko-KR`이다.
- 루트 `/`는 `/ko`로 리다이렉트한다.
- 내부 운영 콘솔 URL은 locale prefix를 가진다.
- 외부 전달 링크는 token URL에 locale을 붙일 수 있다.
- UI 문자열은 번역한다.
- 에피소드 slug, 파일명, 경로, Paperclip issue id, 원본 제작 메타데이터는 번역하지 않는다.
- 자동 번역이 필요한 제목/설명/게시 메타데이터는 UI i18n과 분리해서 별도 content localization job으로 다룬다.

권장 라우팅:

```text
/ko/production
/ko/review
/ko/request
/ko/characters
/ko/delivery
/ko/ops

/en/production
/ja/production
/zh/production
/es/production
```

외부 전달 링크:

```text
/d/:token?lang=ko
/d/:token?lang=en
/d/:token?lang=ja
/d/:token?lang=zh
/d/:token?lang=es
```

### 3.2 Dictionary 구조

프론트엔드 dictionary는 기능 단위로 쪼갠다.

```text
apps/web/src/i18n/
  locales.ts
  routing.ts
  messages/
    ko-KR/
      common.json
      production.json
      review.json
      request.json
      characters.json
      delivery.json
      ops.json
    en-US/
    ja-JP/
    zh-CN/
    es-ES/
```

dictionary key는 화면 문구가 아니라 의미 기준으로 둔다.

좋은 예:

```json
{
  "production.openReview": "리뷰 열기",
  "delivery.generateToken": "토큰 생성"
}
```

나쁜 예:

```json
{
  "open_review_button_text": "리뷰 열기"
}
```

### 3.3 Locale 저장

우선순위:

1. URL prefix 또는 query
2. 사용자 프로필 locale
3. cookie
4. `Accept-Language`
5. 기본값 `ko-KR`

운영자 콘솔은 URL prefix를 우선한다. 외부 전달 페이지는 token 링크 공유가 중요하므로 query와 cookie를 우선 허용한다.

### 3.4 i18n 테스트

프론트엔드:

- 모든 지원 로케일의 dictionary key parity 테스트
- 누락 key가 있으면 CI 실패
- `ko-KR` smoke test는 전체 화면 대상
- `en-US`, `ja-JP`, `zh-CN`, `es-ES`는 주요 happy path 대상
- Playwright에서 locale switcher 클릭 후 `html[lang]` 변경 검증
- 가장 긴 문자열 기준 버튼/배지 overflow 검증

백엔드:

- API 응답은 locale-independent canonical code를 반환
- 사용자 표시용 label은 frontend dictionary에서 처리
- validation error code는 번역 가능한 code와 params로 반환

예:

```json
{
  "code": "delivery.rights_note_missing",
  "params": {
    "episodeSlug": "jjiroo-pilot-001"
  }
}
```

## 4. 폰트 정책

### 4.1 결정

기본 폰트는 Noto 계열로 간다.

권장 stack:

```css
font-family:
  "Noto Sans KR",
  "Noto Sans",
  "Noto Sans JP",
  "Noto Sans SC",
  ui-sans-serif,
  system-ui,
  sans-serif;
```

monospace:

```css
font-family:
  "Noto Sans Mono",
  "SFMono-Regular",
  Consolas,
  "Liberation Mono",
  monospace;
```

이유:

- 한국어, 영어, 일본어, 중국어 간체를 한 제품 안에서 안정적으로 다룰 수 있다.
- Noto 공식 문서 기준 OFL 라이선스이며 상업/디지털 제품 사용이 가능하다.
- CJK glyph coverage가 넓다.
- 운영 콘솔에는 화려한 display font보다 읽기 안정성이 중요하다.

### 4.2 Pretendard 사용 여부

Pretendard는 한국어/라틴 UI에 좋은 선택이고 OFL 라이선스다. 다만 JP/CN까지 같은 제품 안에서 일관되게 운영하려면 Noto를 기본으로 두고, 한국어 브랜드 감도가 더 필요할 때 `Pretendard`를 KO/Latin override로 추가한다.

권장 MVP:

- Noto Sans KR
- Noto Sans
- Noto Sans JP
- Noto Sans SC
- Noto Sans Mono

권장 V1:

- KO/Latin에 Pretendard optional 추가
- font subset 자동화
- locale별 lazy font loading

### 4.3 배포 방식

외부 CDN 의존을 줄이기 위해 production에서는 self-host를 우선한다.

```text
apps/web/public/fonts/
  noto-sans-kr/
  noto-sans/
  noto-sans-jp/
  noto-sans-sc/
  noto-sans-mono/
  LICENSES/
```

Next.js에서는 `next/font/local`을 기본으로 쓴다. `next/font/google`은 개발 초기에만 허용하고, 배포 전에는 font asset과 license 파일을 저장소에 명시한다.

## 5. 모노레포 구조

권장 구조:

```text
apps/
  web/
    src/
      app/
      components/
      features/
      i18n/
      lib/
      test/
  api/
    src/
      sfs_console/
        domain/
        application/
        infrastructure/
        presentation/
        config/
    tests/
  worker/
    src/
    tests/
packages/
  contracts/
    openapi/
    generated/
  config/
    eslint/
    typescript/
  design-tokens/
docs/
  plans/
  wireframes/
```

패키지 매니저는 `pnpm`을 권장한다. Python은 `uv` 또는 Poetry 중 서버 표준에 맞춘다. 현재 repo에 확정된 앱 skeleton이 없으므로 최초 구현 전에 서버의 기존 프로젝트 관례를 확인한다.

## 6. 백엔드 클린 아키텍처

### 6.1 레이어

```text
domain
  entities
  value objects
  domain errors

application
  use cases
  ports
  DTOs

infrastructure
  filesystem scanner
  postgres repositories
  paperclip adapter
  media storage adapter

presentation
  FastAPI routers
  request/response schemas
  auth dependencies
```

### 6.2 초기 use cases

MVP use case:

- `ScanWorkspace`
- `ListEpisodes`
- `GetEpisodeReview`
- `ListCharacters`
- `BuildProductionRequest`
- `CreateDeliveryPackage`
- `ValidateDeliveryReadiness`
- `GetOpsHealth`

V1 use case:

- `CreatePaperclipIssue`
- `AttachReviewComment`
- `RunExportJob`
- `RevokeDeliveryPackage`
- `RecordClientRevision`

### 6.3 DB 원칙

Postgres에는 metadata만 저장한다.

저장하는 것:

- episode index
- character registry
- asset metadata
- approval state
- delivery token hash
- audit log
- job log pointer

저장하지 않는 것:

- mp4 blob
- image blob
- 대용량 contact sheet 원본
- YouTube secret 원문

## 7. TDD 전략

### 7.1 백엔드

테스트 순서:

1. domain unit test
2. application use case test with fake ports
3. infrastructure contract test with fixture workspace
4. FastAPI route test
5. docker compose smoke test

초기 필수 테스트:

- scanner가 `episodes/`, `characters/`, `formats/`를 읽는다.
- 누락 파일은 exception이 아니라 status로 표현된다.
- public delivery는 rights gate가 열려야 생성된다.
- delivery token은 원문 저장 없이 hash로만 검증된다.
- Paperclip markdown 생성은 request type별 필수 항목 누락 시 실패한다.

### 7.2 프론트엔드

테스트 순서:

1. dictionary key parity test
2. component unit test
3. feature screen test
4. Playwright flow test

초기 필수 테스트:

- 기본 접속이 `ko-KR`로 열린다.
- locale switcher가 KO/US/JP/CN/SP를 노출한다.
- Production Desk에서 review 화면으로 이동한다.
- Review Studio에서 delivery 화면으로 이동한다.
- Delivery Room에서 권리 게이트 미통과 시 token 생성 버튼이 disabled 된다.
- 긴 JP/CN/SP 문구가 버튼이나 badge 밖으로 깨지지 않는다.

## 8. v2 화면 구현 순서

1. 공통 shell
   - sidebar
   - top search
   - locale switcher
   - user chip
   - responsive layout

2. Production Desk
   - active review preview
   - filmstrip
   - queue table
   - gate stack

3. Review Studio
   - player frame
   - timeline
   - contact sheet
   - review notes
   - audio meters

4. Request Builder
   - typed request form
   - validation state
   - generated markdown preview

5. Character Lab
   - reference wall
   - dossier fields
   - generated file status

6. Delivery Room
   - client preview
   - included files
   - token policy
   - audit log

7. Ops
   - nginx/api/web/db/paperclip runtime map
   - health checks
   - scanner state

## 9. 구현 단계

### Phase 0. Bootstrap

- monorepo scaffold
- `apps/web`
- `apps/api`
- shared lint/test commands
- `.env.example`
- local docker compose for dev only

완료 기준:

- `pnpm test`
- backend test command
- `/health` test

### Phase 1. i18n + Design Foundation

- locale routing
- KO default redirect
- dictionary structure
- locale switcher
- Noto font setup
- design tokens
- v2 shell implementation

완료 기준:

- 5개 locale dictionary parity 통과
- Playwright locale switcher smoke 통과
- font license 파일 포함

### Phase 2. Read-Only Scanner MVP

- fixture workspace 기반 scanner
- episode/character/format indexing
- API read endpoints
- Production Desk 데이터 연결

완료 기준:

- 실제 workspace를 read-only로 스캔한다.
- 누락 산출물이 status로 노출된다.
- shell 접속 없이 episode 상태를 확인할 수 있다.

### Phase 3. Request / Character Authoring

- production request draft
- Paperclip markdown generator
- character creation draft
- explicit write action만 파일 생성

완료 기준:

- request type별 markdown 생성 테스트 통과
- character template 생성 테스트 통과
- 쓰기 작업은 audit log에 남는다.

### Phase 4. Delivery Package

- tokenized delivery package
- expiry/revoke
- safe media serving
- revision request form
- audit logging

완료 기준:

- 승인된 파일만 외부 페이지에 노출된다.
- token hash만 DB에 저장된다.
- 만료/폐기 상태가 즉시 반영된다.

### Phase 5. Paperclip Integration

- issue/comment adapter
- handoff status sync
- failure retry policy

완료 기준:

- MVP copy markdown flow와 V1 API integration flow가 같은 use case를 공유한다.
- Paperclip 장애 시 콘솔 데이터가 손상되지 않는다.

## 10. 배포 원칙

서비스명:

```text
sfs-web
sfs-api
sfs-worker
```

nginx:

```text
sfs.devscent.com -> sfs-web:3000
/api/* -> sfs-api:8000
/health -> sfs-api:8000/health
/media/* -> sfs-api:8000/media/*
```

네트워크:

```text
edge
```

호스트 공개 포트:

```text
none
```

DB:

```text
postgres14 / shortform_factory
```

파일 마운트:

```text
/home/kindsr/projects/shortform-factory-studio:/workspace/shortform-factory-studio
```

기본은 read-only mount다. 파일 생성은 request/character/delivery처럼 명시적 action만 별도 write scope를 준다.

## 11. 오픈 결정

- SP 표기를 UI에 그대로 둘지, 표준 `ES`로 바꿀지
- Spanish 기본을 `es-ES`로 둘지 `es-419`로 둘지
- KO/Latin에서 Pretendard를 브랜드 폰트로 추가할지
- 초기 인증을 기존 서버 auth와 붙일지, SFS 자체 role table로 시작할지
- delivery link의 public page를 같은 Next.js app에서 serving할지 별도 lightweight route로 둘지

현재 권장:

- UI 표기는 요청대로 `SP`, 내부 코드는 `es-ES`
- MVP는 Noto only
- 인증은 최소 role table로 시작하되, 이후 서버 공통 auth가 있으면 adapter로 교체
- delivery page는 같은 Next.js app에서 시작

## 12. 참고 소스

- Noto 공식 문서: https://notofonts.github.io/noto-docs/website/use/
- SIL Open Font License 공식 문서: https://openfontlicense.org/open-font-license-official-text/
- Pretendard license: https://github.com/orioncactus/pretendard/blob/main/LICENSE
