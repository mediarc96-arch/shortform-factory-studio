from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import hashlib
import mimetypes
from pathlib import Path
import re
import secrets
from typing import Literal

from sfs_console.application.ports import (
    AuditLogStore,
    CharacterWriter,
    ClientRevisionRequestStore,
    DeliveryTokenStore,
    PaperclipIssueClient,
    ProductionRequestStore,
    WorkspaceScanner,
)
from sfs_console.domain import (
    CharacterTemplateResult,
    ClientRevisionRequestRecord,
    DeliveryAsset,
    DeliveryPackage,
    DeliveryReadiness,
    DeliveryTokenRecord,
    EpisodeSummary,
    GateStatus,
    PaperclipIssueComment,
    PaperclipIssueSummary,
    ProductionRequestRecord,
    WorkspaceSnapshot,
)
from sfs_console.domain.models import ProductionRequestType, utc_now


SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{1,62}[a-z0-9]$")
MEDIA_ACCESS_GRACE = timedelta(minutes=30)


@dataclass(frozen=True)
class ProductionRequestDraft:
    request_type: ProductionRequestType
    episode_slug: str
    character_slug: str
    format_profile_slug: str
    output_target: str
    reference_path: str
    completion_criteria: str
    creative_brief: str


@dataclass(frozen=True)
class CharacterTemplateDraft:
    slug: str
    display_name: str
    series: str
    voice_default: str
    rights_status: Literal["needs_review", "production_safe", "internal_only"]
    negative_prompt: str


@dataclass(frozen=True)
class DeliveryTokenIssue:
    record: DeliveryTokenRecord
    token: str


@dataclass(frozen=True)
class ClientRevisionRequestDraft:
    requester_name: str
    requester_email: str
    timestamp_note: str
    message: str


@dataclass(frozen=True)
class PaperclipIssueSync:
    ref: str
    issue: PaperclipIssueSummary | None
    comments: tuple[PaperclipIssueComment, ...]
    error: str | None = None


class ListWorkspaceSnapshot:
    def __init__(self, scanner: WorkspaceScanner) -> None:
        self._scanner = scanner

    def execute(self) -> WorkspaceSnapshot:
        return self._scanner.scan()


class ValidateDeliveryReadiness:
    def execute(self, episode: EpisodeSummary, *, character_has_rights: bool) -> DeliveryReadiness:
        gates = (
            self._gate(
                "final_output",
                "Final mp4",
                episode.final_output_path is not None,
                "final output exists" if episode.final_output_path else "final output is missing",
            ),
            self._gate(
                "thumbnail",
                "Thumbnail",
                episode.thumbnail_path is not None,
                "thumbnail exists" if episode.thumbnail_path else "thumbnail is missing",
            ),
            self._gate(
                "review_report",
                "Review report",
                episode.review_report_path is not None,
                "review report exists" if episode.review_report_path else "review report is missing",
            ),
            self._gate(
                "publish_packet",
                "Publish packet",
                episode.publish_packet_path is not None,
                "publish packet exists" if episode.publish_packet_path else "publish packet is missing",
            ),
            self._gate(
                "rights",
                "Rights note",
                character_has_rights,
                "rights note exists" if character_has_rights else "rights note is missing",
            ),
        )
        status = "ready" if all(gate.status == "present" for gate in gates) else "blocked"
        return DeliveryReadiness(episode_slug=episode.slug, status=status, gates=gates)

    def _gate(self, key: str, label: str, condition: bool, detail: str) -> GateStatus:
        return GateStatus(
            key=key,
            label=label,
            status="present" if condition else "missing",
            detail=detail,
        )


class BuildProductionRequestMarkdown:
    def execute(self, draft: ProductionRequestDraft) -> str:
        missing = self._missing_fields(draft)
        if missing:
            fields = ", ".join(missing)
            raise ValueError(f"Missing required production request fields: {fields}")

        return "\n".join(
            [
                f"# {draft.request_type}: {draft.episode_slug}",
                "",
                "## Workspace",
                "- root: /workspace/shortform-factory-studio",
                f"- format: {draft.format_profile_slug}",
                f"- character: {draft.character_slug}",
                "",
                "## Required output",
                f"- {draft.output_target}",
                f"- completion: {draft.completion_criteria}",
                "",
                "## Source assets",
                f"- reference: {draft.reference_path}",
                "",
                "## Creative brief",
                draft.creative_brief,
                "",
                "## Acceptance",
                "- Do not publish externally until rights.md is confirmed.",
                "- Keep generated character output aligned to the canonical reference pack.",
            ]
        )

    def _missing_fields(self, draft: ProductionRequestDraft) -> list[str]:
        fields = {
            "episode_slug": draft.episode_slug,
            "character_slug": draft.character_slug,
            "format_profile_slug": draft.format_profile_slug,
            "output_target": draft.output_target,
            "reference_path": draft.reference_path,
            "completion_criteria": draft.completion_criteria,
            "creative_brief": draft.creative_brief,
        }
        return [key for key, value in fields.items() if not value.strip()]


class SaveProductionRequest:
    def __init__(
        self,
        request_store: ProductionRequestStore,
        audit_log: AuditLogStore,
    ) -> None:
        self._request_store = request_store
        self._audit_log = audit_log

    def execute(self, draft: ProductionRequestDraft) -> ProductionRequestRecord:
        markdown = BuildProductionRequestMarkdown().execute(draft)
        record = self._request_store.create_production_request(
            request_type=draft.request_type,
            episode_slug=draft.episode_slug,
            character_slug=draft.character_slug,
            format_profile_slug=draft.format_profile_slug,
            output_target=draft.output_target,
            reference_path=draft.reference_path,
            completion_criteria=draft.completion_criteria,
            creative_brief=draft.creative_brief,
            markdown=markdown,
        )
        self._audit_log.append_audit_log(
            action="production_request.created",
            entity_type="production_request",
            entity_id=record.id,
            payload={
                "episode_slug": record.episode_slug,
                "character_slug": record.character_slug,
                "request_type": record.request_type,
            },
        )
        return record


class SendProductionRequestToPaperclip:
    def __init__(
        self,
        request_store: ProductionRequestStore,
        audit_log: AuditLogStore,
        paperclip: PaperclipIssueClient,
    ) -> None:
        self._request_store = request_store
        self._audit_log = audit_log
        self._paperclip = paperclip

    def execute(self, request_id: str) -> ProductionRequestRecord:
        record = self._request_store.get_production_request(request_id)
        if not record:
            raise ValueError("production request not found")
        if record.paperclip_issue_ref:
            return record

        issue_ref = self._paperclip.create_issue(
            title=f"SFS {record.request_type}: {record.episode_slug}",
            description=record.markdown,
            origin_kind="sfs_console.production_request",
            origin_id=record.id,
        )
        updated = self._request_store.set_paperclip_issue_ref(
            request_id=record.id,
            issue_ref=issue_ref,
        )
        self._audit_log.append_audit_log(
            action="production_request.paperclip_handoff",
            entity_type="production_request",
            entity_id=updated.id,
            payload={"paperclip_issue_ref": issue_ref},
        )
        return updated


class CreateCharacterTemplate:
    def __init__(self, writer: CharacterWriter, audit_log: AuditLogStore) -> None:
        self._writer = writer
        self._audit_log = audit_log

    def execute(self, draft: CharacterTemplateDraft) -> CharacterTemplateResult:
        missing = self._missing_fields(draft)
        if missing:
            raise ValueError(f"Missing required character fields: {', '.join(missing)}")
        if not SLUG_PATTERN.match(draft.slug):
            raise ValueError("Character slug must be lowercase kebab-case")

        root, created_files = self._writer.create_template(
            slug=draft.slug,
            display_name=draft.display_name,
            series=draft.series,
            voice_default=draft.voice_default,
            rights_status=draft.rights_status,
            negative_prompt=draft.negative_prompt,
        )
        result = CharacterTemplateResult(
            slug=draft.slug,
            display_name=draft.display_name,
            root_path=root,
            created_files=created_files,
        )
        self._audit_log.append_audit_log(
            action="character_template.created",
            entity_type="character",
            entity_id=draft.slug,
            payload={
                "display_name": draft.display_name,
                "series": draft.series,
                "file_count": len(created_files),
            },
        )
        return result

    def _missing_fields(self, draft: CharacterTemplateDraft) -> list[str]:
        fields = {
            "slug": draft.slug,
            "display_name": draft.display_name,
            "series": draft.series,
            "voice_default": draft.voice_default,
            "negative_prompt": draft.negative_prompt,
        }
        return [key for key, value in fields.items() if not value.strip()]


class IssueDeliveryToken:
    def __init__(
        self,
        scanner: WorkspaceScanner,
        token_store: DeliveryTokenStore,
        audit_log: AuditLogStore,
    ) -> None:
        self._scanner = scanner
        self._token_store = token_store
        self._audit_log = audit_log

    def execute(
        self,
        *,
        episode_slug: str,
        expires_in_hours: int = 168,
        max_accesses: int = 5,
    ) -> DeliveryTokenIssue:
        if not episode_slug.strip():
            raise ValueError("episode_slug is required")
        if expires_in_hours < 1 or expires_in_hours > 24 * 60:
            raise ValueError("expires_in_hours must be between 1 and 1440")
        if max_accesses < 1 or max_accesses > 100:
            raise ValueError("max_accesses must be between 1 and 100")

        snapshot = self._scanner.scan()
        episode = next((item for item in snapshot.episodes if item.slug == episode_slug), None)
        if not episode:
            raise ValueError("episode not found")
        character = next(
            (item for item in snapshot.characters if item.slug == episode.character_slug),
            None,
        )
        readiness = ValidateDeliveryReadiness().execute(
            episode,
            character_has_rights=bool(character and character.has_rights),
        )
        if not readiness.is_ready:
            missing = ", ".join(gate.key for gate in readiness.gates if gate.status == "missing")
            raise ValueError(f"delivery is blocked: {missing}")

        token = secrets.token_urlsafe(32)
        record = self._token_store.create_delivery_token(
            episode_slug=episode_slug,
            token_hash=hashlib.sha256(token.encode("utf-8")).hexdigest(),
            expires_at=utc_now() + timedelta(hours=expires_in_hours),
            max_accesses=max_accesses,
        )
        self._audit_log.append_audit_log(
            action="delivery_token.created",
            entity_type="delivery_token",
            entity_id=record.id,
            payload={
                "episode_slug": episode_slug,
                "expires_at": record.expires_at.isoformat(),
                "max_accesses": max_accesses,
            },
        )
        return DeliveryTokenIssue(record=record, token=token)


class RevokeDeliveryToken:
    def __init__(self, token_store: DeliveryTokenStore, audit_log: AuditLogStore) -> None:
        self._token_store = token_store
        self._audit_log = audit_log

    def execute(self, token_id: str) -> DeliveryTokenRecord:
        record = self._token_store.revoke_delivery_token(token_id)
        if not record:
            raise ValueError("delivery token not found")
        self._audit_log.append_audit_log(
            action="delivery_token.revoked",
            entity_type="delivery_token",
            entity_id=record.id,
            payload={"episode_slug": record.episode_slug},
        )
        return record


class CreateClientRevisionRequest:
    def __init__(
        self,
        token_store: DeliveryTokenStore,
        revision_store: ClientRevisionRequestStore,
        audit_log: AuditLogStore,
        paperclip: PaperclipIssueClient | None = None,
    ) -> None:
        self._token_store = token_store
        self._revision_store = revision_store
        self._audit_log = audit_log
        self._paperclip = paperclip

    def execute(self, *, token: str, draft: ClientRevisionRequestDraft) -> ClientRevisionRequestRecord:
        if not token.strip():
            raise ValueError("delivery token not found")
        if not draft.message.strip():
            raise ValueError("message is required")

        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        delivery_token = self._token_store.get_delivery_token_by_hash(token_hash)
        if (
            not delivery_token
            or delivery_token.status != "active"
            or delivery_token.expires_at <= utc_now()
        ):
            raise ValueError("delivery token not found")

        record = self._revision_store.create_client_revision_request(
            token_id=delivery_token.id,
            episode_slug=delivery_token.episode_slug,
            requester_name=draft.requester_name.strip() or "Client",
            requester_email=draft.requester_email.strip(),
            timestamp_note=draft.timestamp_note.strip(),
            message=draft.message.strip(),
        )
        self._audit_log.append_audit_log(
            action="client_revision.created",
            entity_type="client_revision_request",
            entity_id=record.id,
            payload={
                "episode_slug": record.episode_slug,
                "token_id": record.token_id,
                "has_requester_email": bool(record.requester_email),
            },
            actor="client",
        )
        return self._send_to_paperclip(record)

    def _send_to_paperclip(
        self,
        record: ClientRevisionRequestRecord,
    ) -> ClientRevisionRequestRecord:
        if not self._paperclip:
            return record
        try:
            issue_ref = self._paperclip.create_issue(
                title=f"SFS client revision: {record.episode_slug}",
                description="\n".join(
                    [
                        f"# Client revision request: {record.episode_slug}",
                        "",
                        "## Requester",
                        f"- name: {record.requester_name}",
                        f"- email: {record.requester_email or 'not provided'}",
                        f"- timestamp: {record.timestamp_note or 'not provided'}",
                        f"- delivery token id: {record.token_id}",
                        "",
                        "## Requested change",
                        record.message,
                    ]
                ),
                origin_kind="sfs_console.client_revision_request",
                origin_id=record.id,
            )
        except ValueError as error:
            self._audit_log.append_audit_log(
                action="client_revision.paperclip_handoff_failed",
                entity_type="client_revision_request",
                entity_id=record.id,
                payload={"episode_slug": record.episode_slug, "error": str(error)},
            )
            return record

        updated = self._revision_store.set_client_revision_paperclip_issue_ref(
            request_id=record.id,
            issue_ref=issue_ref,
        )
        self._audit_log.append_audit_log(
            action="client_revision.paperclip_handoff",
            entity_type="client_revision_request",
            entity_id=updated.id,
            payload={
                "episode_slug": updated.episode_slug,
                "paperclip_issue_ref": issue_ref,
            },
        )
        return updated


class SyncClientRevisionRequestPaperclip:
    def __init__(self, paperclip: PaperclipIssueClient) -> None:
        self._paperclip = paperclip

    def execute(self, record: ClientRevisionRequestRecord) -> PaperclipIssueSync | None:
        if not record.paperclip_issue_ref:
            return None
        try:
            issue = self._paperclip.get_issue(record.paperclip_issue_ref)
            if not issue:
                return PaperclipIssueSync(
                    ref=record.paperclip_issue_ref,
                    issue=None,
                    comments=(),
                    error="Paperclip issue not found",
                )
            comments = self._paperclip.list_issue_comments(record.paperclip_issue_ref, limit=5)
            return PaperclipIssueSync(ref=record.paperclip_issue_ref, issue=issue, comments=comments)
        except ValueError as error:
            return PaperclipIssueSync(
                ref=record.paperclip_issue_ref,
                issue=None,
                comments=(),
                error=str(error),
            )


class ResolveDeliveryPackage:
    def __init__(
        self,
        scanner: WorkspaceScanner,
        token_store: DeliveryTokenStore,
        audit_log: AuditLogStore | None = None,
    ) -> None:
        self._scanner = scanner
        self._token_store = token_store
        self._audit_log = audit_log

    def execute(
        self,
        token: str,
        *,
        record_access: bool = False,
        allow_recent_media_access: bool = False,
    ) -> DeliveryPackage:
        if not token.strip():
            raise ValueError("delivery token not found")

        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        record = self._token_store.get_delivery_token_by_hash(token_hash)
        if not record or record.status != "active" or record.expires_at <= utc_now():
            raise ValueError("delivery token not found")
        access_limit_reached = record.access_count >= record.max_accesses
        if access_limit_reached and not (
            allow_recent_media_access and self._has_recent_media_access(record)
        ):
            raise ValueError("delivery token access limit reached")
        if record_access:
            if not access_limit_reached:
                accessed = self._token_store.mark_delivery_token_accessed(record.id)
                if not accessed:
                    raise ValueError("delivery token not found")
                record = accessed
                self._append_audit(
                    action="delivery_token.accessed",
                    entity_id=record.id,
                    payload={
                        "episode_slug": record.episode_slug,
                        "access_count": record.access_count,
                        "max_accesses": record.max_accesses,
                    },
                )

        snapshot = self._scanner.scan()
        episode = next((item for item in snapshot.episodes if item.slug == record.episode_slug), None)
        if not episode:
            raise ValueError("episode not found")

        assets = tuple(
            asset
            for asset in (
                self._asset("final_video", "Final video", episode.final_output_path, "video/mp4"),
                self._asset("thumbnail", "Thumbnail", episode.thumbnail_path, "image/jpeg"),
                self._asset("review_report", "Review report", episode.review_report_path, "text/markdown"),
                self._asset("publish_packet", "Publish packet", episode.publish_packet_path, "application/json"),
            )
            if asset is not None
        )
        if len(assets) < 4:
            raise ValueError("delivery package is incomplete")

        return DeliveryPackage(
            episode_slug=record.episode_slug,
            token_id=record.id,
            max_accesses=record.max_accesses,
            access_count=record.access_count,
            expires_at=record.expires_at,
            assets=assets,
        )

    def get_asset(
        self,
        token: str,
        asset_key: str,
        *,
        record_access: bool = False,
        allow_recent_media_access: bool = False,
    ) -> DeliveryAsset:
        package = self.execute(
            token,
            record_access=record_access,
            allow_recent_media_access=allow_recent_media_access,
        )
        asset = next((item for item in package.assets if item.key == asset_key), None)
        if not asset:
            raise ValueError("delivery asset not found")
        self._append_audit(
            action="delivery_asset.requested",
            entity_id=package.token_id,
            payload={
                "episode_slug": package.episode_slug,
                "asset_key": asset.key,
                "filename": asset.path.name,
                "access_count": package.access_count,
                "max_accesses": package.max_accesses,
            },
        )
        return asset

    def _has_recent_media_access(self, record: DeliveryTokenRecord) -> bool:
        if not record.last_accessed_at:
            return False
        return utc_now() - record.last_accessed_at <= MEDIA_ACCESS_GRACE

    def _append_audit(
        self,
        *,
        action: str,
        entity_id: str,
        payload: dict[str, object],
    ) -> None:
        if not self._audit_log:
            return
        self._audit_log.append_audit_log(
            action=action,
            entity_type="delivery_token",
            entity_id=entity_id,
            payload=payload,
        )

    def _asset(
        self,
        key: Literal["final_video", "thumbnail", "review_report", "publish_packet"],
        label: str,
        path: Path | None,
        content_type: str,
    ) -> DeliveryAsset | None:
        if path is None:
            return None
        guessed_content_type = mimetypes.guess_type(path.name)[0] or content_type
        return DeliveryAsset(key=key, label=label, path=path, content_type=guessed_content_type)
