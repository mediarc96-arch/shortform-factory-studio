# SFS 클라이언트 수정 요청 운영 흐름

이 문서는 SFS Console에서 클라이언트 전달 링크로 들어온 수정 요청을 접수하고,
Paperclip 작업 흐름으로 넘긴 뒤 다시 SFS에서 상태를 확인하는 운영 규칙이다.

## 기본 흐름

1. `sfs.devscent.com/ko/delivery`에서 전달 가능한 에피소드를 선택한다.
2. Delivery token을 발급한다.
3. `/delivery/<token>` 링크를 클라이언트 승인 채널에 전달한다.
4. 클라이언트가 공개 revision form에서 타임스탬프와 수정 내용을 제출한다.
5. SFS가 요청을 `client_revision_requests`에 저장하고 Paperclip issue를 생성한다.
6. 운영자는 Paperclip issue에서 실제 수정 작업을 진행한다.
7. Delivery Room에서 `Paperclip sync`를 눌러 상태와 최신 코멘트를 갱신한다.

자동 동기화는 아직 켜지지 않았다. 현재 운영 기준은 필요한 시점에 수동 sync를 실행하는 방식이다.

## 상태 매핑

| Paperclip status | SFS revision status |
| --- | --- |
| `backlog`, `todo` | `sent_to_paperclip` |
| `in_progress`, `in_review` | `in_progress` |
| `blocked` | `blocked` |
| `done`, `cancelled` | `resolved` |

SFS는 Paperclip status, priority, title, latest comment, sync time, sync error를
Postgres에 캐시한다. API에서 `include_paperclip=true`를 주면 가능한 경우 Paperclip
상세 정보도 함께 반환한다.

## Delivery Room

Revision queue 패널은 기본적으로 아직 끝나지 않은 요청만 보여준다. 필터는 아래처럼 쓴다.

- `open`: `resolved`가 아닌 모든 요청
- `blocked`: Paperclip에서 막힌 요청
- `resolved`: 완료되거나 취소 처리된 요청
- `all`: 전체 요청

각 row에는 SFS 상태, Paperclip issue reference, Paperclip 상태, 최신 Paperclip 코멘트,
마지막 sync 시간이 표시된다. Audit 패널은 delivery token 발급/회수 같은 감사 이벤트만
담당한다.

## 공개 Form 보호

공개 revision form은 브라우저와 서버 양쪽에서 입력을 제한한다.

- name: 120자
- email: 254자, 값이 있으면 email 형식 필요
- timestamp: 120자
- message: 필수, 3000자
- hidden spam trap field
- Next.js route in-memory rate limit: token/IP 기준 10분 4회

FastAPI가 최종 validation 기준이다. 내부 API로 직접 잘못된 payload를 보내면 `422`로 실패한다.
Next.js rate limit은 단일 프로세스 메모리 기준이므로, 장기적으로 트래픽이 늘면 Redis 기반
rate limit으로 옮기는 것이 좋다.

## 알림 Webhook

새 client revision이 들어왔을 때 운영 알림을 보내려면 project `.env`에
`SFS_REVISION_NOTIFY_WEBHOOK_URL`을 설정한다. webhook payload에는 아래 값이 들어간다.

- `episode_slug`
- `revision_request_id`
- `paperclip_issue_ref`
- `requester_name`
- `timestamp`

Webhook URL은 secret으로 취급하고 git에 커밋하지 않는다. 설정 후 컨테이너를 재빌드한다.

```bash
docker compose up -d --build
```

secret 값을 출력하지 않고 설정 여부만 확인한다.

```bash
docker compose exec -T sfs-console-api sh -lc 'test -n "$SFS_REVISION_NOTIFY_WEBHOOK_URL" && echo configured || echo missing'
```

실제 발송 테스트가 필요하면 새 revision request를 하나 생성해야 한다. 이 경우 Paperclip issue와
운영 알림이 실제로 생성되므로 테스트 요청임을 본문에 명시한다.

## 점검 명령

```bash
python3 -m unittest discover -s apps/api/tests
pnpm test:web
pnpm typecheck:web
pnpm build:web
pnpm smoke:sfs
```
