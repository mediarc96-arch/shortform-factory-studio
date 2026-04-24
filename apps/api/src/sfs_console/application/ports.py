from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Protocol

from sfs_console.domain import AuditLogEntry, DeliveryTokenRecord, ProductionRequestRecord, WorkspaceSnapshot
from sfs_console.domain.models import ProductionRequestType


class WorkspaceScanner(Protocol):
    def scan(self) -> WorkspaceSnapshot:
        """Return a read-only snapshot of the production workspace."""


class ProductionRequestStore(Protocol):
    def initialize(self) -> None:
        """Prepare persistence for use."""

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
        """Persist a generated production request draft."""

    def list_production_requests(self, *, limit: int = 20) -> tuple[ProductionRequestRecord, ...]:
        """Return recent production requests."""

    def get_production_request(self, request_id: str) -> ProductionRequestRecord | None:
        """Return one production request."""

    def set_paperclip_issue_ref(
        self,
        *,
        request_id: str,
        issue_ref: str,
    ) -> ProductionRequestRecord:
        """Attach a Paperclip issue reference to a request."""


class DeliveryTokenStore(Protocol):
    def create_delivery_token(
        self,
        *,
        episode_slug: str,
        token_hash: str,
        expires_at: datetime,
    ) -> DeliveryTokenRecord:
        """Persist a delivery token hash."""

    def revoke_delivery_token(self, token_id: str) -> DeliveryTokenRecord | None:
        """Revoke a token by id."""

    def list_delivery_tokens(self, *, limit: int = 20) -> tuple[DeliveryTokenRecord, ...]:
        """Return recent delivery tokens."""


class AuditLogStore(Protocol):
    def append_audit_log(
        self,
        *,
        action: str,
        entity_type: str,
        entity_id: str,
        payload: dict[str, object] | None = None,
        actor: str = "operator",
    ) -> AuditLogEntry:
        """Persist an audit event."""

    def list_audit_logs(self, *, limit: int = 30) -> tuple[AuditLogEntry, ...]:
        """Return recent audit events."""


class CharacterWriter(Protocol):
    def create_template(
        self,
        *,
        slug: str,
        display_name: str,
        series: str,
        voice_default: str,
        rights_status: str,
        negative_prompt: str,
    ) -> tuple[Path, tuple[Path, ...]]:
        """Create a character template and return root plus created file paths."""


class PaperclipIssueClient(Protocol):
    def create_issue(
        self,
        *,
        title: str,
        description: str,
    ) -> str:
        """Create a Paperclip issue and return its external reference."""
