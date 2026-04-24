from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from uuid import uuid4

from sfs_console.domain import AuditLogEntry, DeliveryTokenRecord, ProductionRequestRecord
from sfs_console.domain.models import ProductionRequestType, utc_now


class InMemorySfsStore:
    def __init__(self) -> None:
        self._production_requests: dict[str, ProductionRequestRecord] = {}
        self._delivery_tokens: dict[str, DeliveryTokenRecord] = {}
        self._audit_logs: dict[str, AuditLogEntry] = {}

    def initialize(self) -> None:
        return None

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
        record = ProductionRequestRecord(
            id=str(uuid4()),
            request_type=request_type,
            episode_slug=episode_slug,
            character_slug=character_slug,
            format_profile_slug=format_profile_slug,
            output_target=output_target,
            reference_path=reference_path,
            completion_criteria=completion_criteria,
            creative_brief=creative_brief,
            markdown=markdown,
            status="draft",
            paperclip_issue_ref=None,
            created_at=now,
            updated_at=now,
        )
        self._production_requests[record.id] = record
        return record

    def list_production_requests(self, *, limit: int = 20) -> tuple[ProductionRequestRecord, ...]:
        return tuple(
            sorted(
                self._production_requests.values(),
                key=lambda item: item.created_at,
                reverse=True,
            )[:limit]
        )

    def get_production_request(self, request_id: str) -> ProductionRequestRecord | None:
        return self._production_requests.get(request_id)

    def set_paperclip_issue_ref(
        self,
        *,
        request_id: str,
        issue_ref: str,
    ) -> ProductionRequestRecord:
        record = self._production_requests[request_id]
        updated = replace(
            record,
            status="sent_to_paperclip",
            paperclip_issue_ref=issue_ref,
            updated_at=utc_now(),
        )
        self._production_requests[request_id] = updated
        return updated

    def create_delivery_token(
        self,
        *,
        episode_slug: str,
        token_hash: str,
        expires_at: datetime,
    ) -> DeliveryTokenRecord:
        record = DeliveryTokenRecord(
            id=str(uuid4()),
            episode_slug=episode_slug,
            token_hash=token_hash,
            status="active",
            expires_at=expires_at,
            created_at=utc_now(),
        )
        self._delivery_tokens[record.id] = record
        return record

    def revoke_delivery_token(self, token_id: str) -> DeliveryTokenRecord | None:
        record = self._delivery_tokens.get(token_id)
        if not record:
            return None
        updated = replace(record, status="revoked", revoked_at=utc_now())
        self._delivery_tokens[token_id] = updated
        return updated

    def list_delivery_tokens(self, *, limit: int = 20) -> tuple[DeliveryTokenRecord, ...]:
        return tuple(
            sorted(self._delivery_tokens.values(), key=lambda item: item.created_at, reverse=True)[
                :limit
            ]
        )

    def append_audit_log(
        self,
        *,
        action: str,
        entity_type: str,
        entity_id: str,
        payload: dict[str, object] | None = None,
        actor: str = "operator",
    ) -> AuditLogEntry:
        entry = AuditLogEntry(
            id=str(uuid4()),
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            payload=payload or {},
            actor=actor,
            created_at=utc_now(),
        )
        self._audit_logs[entry.id] = entry
        return entry

    def list_audit_logs(self, *, limit: int = 30) -> tuple[AuditLogEntry, ...]:
        return tuple(
            sorted(self._audit_logs.values(), key=lambda item: item.created_at, reverse=True)[
                :limit
            ]
        )
