# SFS Console Storyboard

날짜: 2026-04-24
관련 기획서: `docs/plans/2026-04-24-sfs-console-product-plan.md`
관련 와이어프레임: `docs/wireframes/2026-04-24-sfs-console-wireframes.html`

## 1. 화면 목록

1. `Dashboard`
2. `New Request`
3. `Episode Workspace`
4. `Character Editor`
5. `Delivery Package`
6. `Settings / Ops`

## 2. 흐름 A: 최종 결과물 전달

### A1. Dashboard

사용자는 `Dashboard`에서 `Ready for delivery` 상태의 episode를 본다.

표시 정보:

- episode slug
- character
- final output 존재 여부
- thumbnail 존재 여부
- review status
- publish packet 존재 여부

행동:

- `Open workspace`
- `Create delivery`

성공 기준:

- shell 접속 없이 final mp4, thumbnail, review report, publish packet 위치를 확인한다.

### A2. Delivery Package

Producer는 전달할 파일을 선택하고 만료일을 정한다.

선택 가능한 항목:

- final mp4
- thumbnail
- review report
- publish packet
- rights note
- revision request form

행동:

- `Generate link`
- `Copy client link`
- `Revoke`

성공 기준:

- 외부 사용자는 서버 계정 없이 승인된 패키지만 볼 수 있다.
- 다운로드와 열람 기록이 audit log에 남는다.

## 3. 흐름 B: 새 에피소드 요청

### B1. New Request

Producer가 요청 유형을 고른다.

요청 유형:

- `new_episode`
- `revise_episode`
- `publish_only`
- `metadata_update`

필수 입력:

- episode slug
- character
- format profile
- output target
- reference path
- background asset path
- completion criteria

행동:

- `Validate`
- `Generate Paperclip Markdown`
- `Create draft`

성공 기준:

- `docs/PAPERCLIP_ISSUE_OPERATIONS.md`의 필수 항목이 빠지면 진행할 수 없다.

### B2. Paperclip Handoff

앱은 Paperclip issue body를 생성한다.

표시 정보:

- title
- assignee recommendation
- project recommendation
- issue body
- missing assets

행동:

- MVP: `Copy Markdown`
- V1: `Create Paperclip Issue`

성공 기준:

- Paperclip agent가 바로 작업할 수 있는 issue body가 생성된다.

## 4. 흐름 C: 에피소드 후반작업 확인

### C1. Episode Workspace

Operator가 episode를 연다.

상단 정보:

- current state
- source issue
- format profile
- character
- rights status
- final output

탭:

- `Overview`
- `Media`
- `Dubbing`
- `Typography`
- `Review`
- `Export`

성공 기준:

- episode folder를 직접 뒤지지 않아도 어디가 막혔는지 보인다.

### C2. Review

Reviewer는 contact sheet와 final review report를 함께 본다.

표시 정보:

- picture preview
- final output
- contact sheet
- frame map
- review report
- audio analysis

행동:

- `Approve`
- `Request revision`
- `Create delivery`

성공 기준:

- 승인/수정 요청이 episode와 Paperclip issue에 연결된다.

## 5. 흐름 D: 새 캐릭터 추가

### D1. Character Editor

Character Manager가 새 캐릭터 slug를 만든다.

필수 입력:

- display name
- series/world
- role
- rights status
- canonical image
- bible fields
- prompt defaults
- voice config

생성 파일:

- `characters/<slug>/bible.md`
- `characters/<slug>/prompts.md`
- `characters/<slug>/rights.md`
- `characters/<slug>/voice.json`
- `characters/<slug>/refs/*`

성공 기준:

- 캐릭터가 rights unknown 상태면 public publish flow에 들어갈 수 없다.

### D2. Reference Lock

사용자는 canonical reference를 지정한다.

행동:

- `Set canonical`
- `Add variation`
- `Mark unsafe for generation`

성공 기준:

- episode request에서 사용할 reference pack이 명확하다.

## 6. 흐름 E: 운영 설정

### E1. Settings / Ops

Admin은 서비스 상태를 본다.

표시 정보:

- backend health
- DB health
- scanner last run
- workspace path
- Paperclip API connectivity
- nginx route note
- backup/runbook links

행동:

- `Run scanner`
- `View job log`
- `Open runbook`

성공 기준:

- 신규 서비스가 기존 `pc.devscent.com`, `postgres14`, nginx route와 충돌하지 않는다.

## 7. 와이어프레임 메모

UI 방향:

- 내부 운영툴이므로 landing hero는 없다.
- 첫 화면은 곧바로 dashboard다.
- sidebar + table + detail panel 구조를 쓴다.
- status는 작은 label로만 표시한다.
- 큰 카드형 KPI grid를 첫 화면에 두지 않는다.
- final output, review, delivery 같은 실제 작업 물체가 우선이다.

## 8. MVP 수용 기준

- `/health`가 `ok`를 반환한다.
- scanner가 `characters/`, `episodes/`, `formats/`를 읽는다.
- `Episodes` 목록에서 final output과 review report를 찾는다.
- `Characters`에서 bible/prompts/rights/voice 상태를 본다.
- `New Request`가 Paperclip issue markdown을 만든다.
- `Delivery Package`가 token link를 만든다.
- 직접 서버 shell 접속 없이 approved output을 내려받을 수 있다.
