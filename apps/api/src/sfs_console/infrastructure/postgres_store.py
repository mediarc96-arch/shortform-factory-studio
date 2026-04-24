from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from sfs_console.domain import AuditLogEntry, DeliveryTokenRecord, ProductionRequestRecord
from sfs_console.domain.models import ProductionRequestType, utc_now


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS production_requests (
  id text PRIMARY KEY,
  request_type text NOT NULL CHECK (
    request_type IN ('new_episode', 'revise_episode', 'publish_only', 'metadata_update')
  ),
  episode_slug text NOT NULL,
  character_slug text NOT NULL,
  format_profile_slug text NOT NULL,
  output_target text NOT NULL,
  reference_path text NOT NULL,
  completion_criteria text NOT NULL,
  creative_brief text NOT NULL,
  markdown text NOT NULL,
  status text NOT NULL DEFAULT 'draft',
  paperclip_issue_ref text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_production_requests_created_at
  ON production_requests (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_production_requests_episode_slug
  ON production_requests (episode_slug);

CREATE TABLE IF NOT EXISTS delivery_tokens (
  id text PRIMARY KEY,
  episode_slug text NOT NULL,
  token_hash text NOT NULL UNIQUE,
  status text NOT NULL CHECK (status IN ('active', 'revoked')),
  expires_at timestamptz NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  revoked_at timestamptz
);

CREATE INDEX IF NOT EXISTS idx_delivery_tokens_episode_slug
  ON delivery_tokens (episode_slug);
CREATE INDEX IF NOT EXISTS idx_delivery_tokens_status_expires_at
  ON delivery_tokens (status, expires_at);

CREATE TABLE IF NOT EXISTS audit_logs (
  id text PRIMARY KEY,
  action text NOT NULL,
  entity_type text NOT NULL,
  entity_id text NOT NULL,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  actor text NOT NULL DEFAULT 'operator',
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at
  ON audit_logs (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_entity
  ON audit_logs (entity_type, entity_id);
"""


class PostgresSfsStore:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url

    def initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(SCHEMA_SQL)
            conn.commit()

    def create_production_request(
        self,
        *,
        request_type: ProductionRequestType,
        episode_slug: str,
        character_slug: str,
        format_profile_slug: str,
        output_target: str,
        reference_path: str,
        completion_criteria: str,
        creative_brief: str,
        markdown: str,
    ) -> ProductionRequestRecord:
        now = utc_now()
        row = self._fetchone(
            """
            INSERT INTO production_requests (
              id, request_type, episode_slug, character_slug, format_profile_slug,
              output_target, reference_path, completion_criteria, creative_brief,
              markdown, status, created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'draft', %s, %s)
            RETURNING *
            """,
            (
                str(uuid4()),
                request_type,
                episode_slug,
                character_slug,
                format_profile_slug,
                output_target,
                reference_path,
                completion_criteria,
                creative_brief,
                markdown,
                now,
                now,
            ),
        )
        return _production_request_from_row(row)

    def list_production_requests(self, *, limit: int = 20) -> tuple[ProductionRequestRecord, ...]:
        rows = self._fetchall(
            "SELECT * FROM production_requests ORDER BY created_at DESC LIMIT %s",
            (limit,),
        )
        return tuple(_production_request_from_row(row) for row in rows)

    def get_production_request(self, request_id: str) -> ProductionRequestRecord | None:
        row = self._fetchone_or_none("SELECT * FROM production_requests WHERE id = %s", (request_id,))
        return _production_request_from_row(row) if row else None

    def set_paperclip_issue_ref(
        self,
        *,
        request_id: str,
        issue_ref: str,
    ) -> ProductionRequestRecord:
        row = self._fetchone(
            """
            UPDATE production_requests
            SET status = 'sent_to_paperclip',
                paperclip_issue_ref = %s,
                updated_at = %s
            WHERE id = %s
            RETURNING *
            """,
            (issue_ref, utc_now(), request_id),
        )
        return _production_request_from_row(row)

    def create_delivery_token(
        self,
        *,
        episode_slug: str,
        token_hash: str,
        expires_at: datetime,
    ) -> DeliveryTokenRecord:
        row = self._fetchone(
            """
            INSERT INTO delivery_tokens (
              id, episode_slug, token_hash, status, expires_at, created_at
            )
            VALUES (%s, %s, %s, 'active', %s, %s)
            RETURNING *
            """,
            (str(uuid4()), episode_slug, token_hash, expires_at, utc_now()),
        )
        return _delivery_token_from_row(row)

    def revoke_delivery_token(self, token_id: str) -> DeliveryTokenRecord | None:
        row = self._fetchone_or_none(
            """
            UPDATE delivery_tokens
            SET status = 'revoked', revoked_at = %s
            WHERE id = %s
            RETURNING *
            """,
            (utc_now(), token_id),
        )
        return _delivery_token_from_row(row) if row else None

    def list_delivery_tokens(self, *, limit: int = 20) -> tuple[DeliveryTokenRecord, ...]:
        rows = self._fetchall(
            "SELECT * FROM delivery_tokens ORDER BY created_at DESC LIMIT %s",
            (limit,),
        )
        return tuple(_delivery_token_from_row(row) for row in rows)

    def append_audit_log(
        self,
        *,
        action: str,
        entity_type: str,
        entity_id: str,
        payload: dict[str, object] | None = None,
        actor: str = "operator",
    ) -> AuditLogEntry:
        from psycopg.types.json import Json

        row = self._fetchone(
            """
            INSERT INTO audit_logs (id, action, entity_type, entity_id, payload, actor, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (str(uuid4()), action, entity_type, entity_id, Json(payload or {}), actor, utc_now()),
        )
        return _audit_log_from_row(row)

    def list_audit_logs(self, *, limit: int = 30) -> tuple[AuditLogEntry, ...]:
        rows = self._fetchall("SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT %s", (limit,))
        return tuple(_audit_log_from_row(row) for row in rows)

    def _connect(self) -> Any:
        import psycopg
        from psycopg.rows import dict_row

        return psycopg.connect(self._database_url, row_factory=dict_row)

    def _fetchone(self, sql: str, params: tuple[object, ...] = ()) -> dict[str, Any]:
        with self._connect() as conn:
            row = conn.execute(sql, params).fetchone()
            conn.commit()
        if not row:
            raise ValueError("database operation returned no row")
        return dict(row)

    def _fetchone_or_none(
        self,
        sql: str,
        params: tuple[object, ...] = (),
    ) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(sql, params).fetchone()
            conn.commit()
        return dict(row) if row else None

    def _fetchall(self, sql: str, params: tuple[object, ...] = ()) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]


def _production_request_from_row(row: dict[str, Any]) -> ProductionRequestRecord:
    return ProductionRequestRecord(
        id=str(row["id"]),
        request_type=row["request_type"],
        episode_slug=str(row["episode_slug"]),
        character_slug=str(row["character_slug"]),
        format_profile_slug=str(row["format_profile_slug"]),
        output_target=str(row["output_target"]),
        reference_path=str(row["reference_path"]),
        completion_criteria=str(row["completion_criteria"]),
        creative_brief=str(row["creative_brief"]),
        markdown=str(row["markdown"]),
        status=str(row["status"]),
        paperclip_issue_ref=row["paperclip_issue_ref"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _delivery_token_from_row(row: dict[str, Any]) -> DeliveryTokenRecord:
    return DeliveryTokenRecord(
        id=str(row["id"]),
        episode_slug=str(row["episode_slug"]),
        token_hash=str(row["token_hash"]),
        status=row["status"],
        expires_at=row["expires_at"],
        created_at=row["created_at"],
        revoked_at=row["revoked_at"],
    )


def _audit_log_from_row(row: dict[str, Any]) -> AuditLogEntry:
    return AuditLogEntry(
        id=str(row["id"]),
        action=str(row["action"]),
        entity_type=str(row["entity_type"]),
        entity_id=str(row["entity_id"]),
        payload=dict(row["payload"]),
        actor=str(row["actor"]),
        created_at=row["created_at"],
    )
