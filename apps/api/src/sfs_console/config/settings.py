from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote


@dataclass(frozen=True)
class Settings:
    workspace_root: Path
    service_name: str = "sfs-console-api"
    database_url: str | None = None
    paperclip_base_url: str | None = None
    paperclip_api_token: str | None = None
    paperclip_company_id: str | None = None
    paperclip_project_id: str | None = None
    revision_notify_webhook_url: str | None = None

    @classmethod
    def from_env(cls) -> "Settings":
        workspace_root = os.environ.get(
            "SFS_WORKSPACE_ROOT",
            "/workspace/shortform-factory-studio",
        )
        return cls(
            workspace_root=Path(workspace_root),
            database_url=_database_url_from_env(),
            paperclip_base_url=os.environ.get("PAPERCLIP_BASE_URL"),
            paperclip_api_token=os.environ.get("PAPERCLIP_API_TOKEN"),
            paperclip_company_id=os.environ.get("PAPERCLIP_COMPANY_ID"),
            paperclip_project_id=os.environ.get("PAPERCLIP_PROJECT_ID"),
            revision_notify_webhook_url=os.environ.get("SFS_REVISION_NOTIFY_WEBHOOK_URL"),
        )


def _database_url_from_env() -> str | None:
    explicit = os.environ.get("SFS_DATABASE_URL")
    if explicit:
        return explicit

    host = os.environ.get("SFS_DB_HOST")
    name = os.environ.get("SFS_DB_NAME")
    user = os.environ.get("SFS_DB_USER") or os.environ.get("POSTGRES_USER")
    password = os.environ.get("SFS_DB_PASSWORD") or os.environ.get("POSTGRES_PASSWORD")
    port = os.environ.get("SFS_DB_PORT", "5432")

    if not all((host, name, user, password)):
        return None

    return (
        f"postgresql://{quote(user or '')}:{quote(password or '')}"
        f"@{host}:{port}/{quote(name or '')}"
    )
