# AGENTS.md — Production Service Guide

이 프로젝트는 운영 서버에서 Docker Compose로 실행되는 서비스입니다.

## Production Restart

- Service root: `/home/kindsr/projects/shortform-factory-studio`
- Compose file: `docker-compose.yml`
- Backend/frontend 재기동은 프로젝트 루트에서 실행합니다:

```bash
cd /home/kindsr/projects/shortform-factory-studio
docker compose up -d --build
```

- 상태 확인:

```bash
docker compose ps
docker compose logs --tail=100
```

## Do Not Start Dev Servers

- 운영 서버에서 `npm run dev`, `pnpm dev`, `yarn dev`, `next dev`, `vite --host`, `uvicorn --reload`, `fastapi dev`, `flask run`, `python manage.py runserver` 같은 개발 서버를 띄우지 않습니다.
- 새 포트를 열거나 `0.0.0.0` 바인딩을 만들지 않습니다.
- 서비스 재기동이 필요하면 위 Compose 명령을 사용합니다.
- `docker compose down`, 볼륨 삭제, DB 초기화는 사용자가 명시적으로 요청한 경우에만 실행합니다.

## If The Root Command Does Not Apply

- 먼저 Compose 위치를 확인합니다:

```bash
find . -maxdepth 3 \( -name 'docker-compose.yml' -o -name 'compose.yml' -o -name 'docker-compose.yaml' -o -name 'compose.yaml' \) -print
docker compose config
```

- 루트 Compose가 없거나 실패할 때만 `backend/`, `frontend/`, `deploy/`, `docker/` 아래 Compose 파일을 확인합니다.

## Karpathy Guidelines

- 구현 전 가정과 성공 기준을 짧게 명시합니다. 모호하면 추측하지 말고 묻습니다.
- 요청 범위와 직접 연결된 파일만 수정합니다. 주변 코드 정리나 임의 리팩터링은 하지 않습니다.
- 한 번만 쓰는 추상화, 추측성 옵션, 과한 일반화는 만들지 않습니다.
- 기존 코드 스타일과 프로젝트 구조를 우선합니다.
- 변경 후 가장 작은 관련 검증부터 실행합니다. 예: `docker compose config`, 관련 테스트, 타입 체크, 빌드.
- 검증을 실행하지 못하면 실행하지 못한 명령과 이유를 남깁니다.
