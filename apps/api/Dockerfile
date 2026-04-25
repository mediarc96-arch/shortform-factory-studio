FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/apps/api/src \
    SFS_WORKSPACE_ROOT=/workspace/shortform-factory-studio

WORKDIR /app

COPY apps/api/pyproject.toml apps/api/pyproject.toml
COPY apps/api/alembic.ini apps/api/alembic.ini
COPY apps/api/migrations apps/api/migrations

RUN python - <<'PY'
import pathlib
import subprocess
import sys
import tomllib

project = tomllib.loads(pathlib.Path("apps/api/pyproject.toml").read_text())
dependencies = project["project"]["dependencies"]
subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-cache-dir", *dependencies])
PY

COPY apps/api/src apps/api/src

EXPOSE 8000

CMD ["uvicorn", "sfs_console.presentation.api:app", "--host", "0.0.0.0", "--port", "8000"]
