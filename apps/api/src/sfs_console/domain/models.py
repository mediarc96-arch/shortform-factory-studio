from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal


AssetStatus = Literal["present", "missing"]
EpisodeStatus = Literal["ready", "review", "blocked"]
ProductionRequestType = Literal["new_episode", "revise_episode", "publish_only", "metadata_update"]


def utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True)
class GateStatus:
    key: str
    label: str
    status: AssetStatus
    detail: str


@dataclass(frozen=True)
class CharacterSummary:
    slug: str
    display_name: str
    root_path: Path
    has_bible: bool
    has_prompts: bool
    has_rights: bool
    has_voice: bool

    @property
    def rights_status(self) -> AssetStatus:
        return "present" if self.has_rights else "missing"


@dataclass(frozen=True)
class FormatProfileSummary:
    slug: str
    profile_path: Path


@dataclass(frozen=True)
class EpisodeSummary:
    slug: str
    root_path: Path
    character_slug: str | None
    final_output_path: Path | None
    thumbnail_path: Path | None
    review_report_path: Path | None
    publish_packet_path: Path | None

    @property
    def status(self) -> EpisodeStatus:
        if self.final_output_path is None:
            return "blocked"
        if self.review_report_path is None or self.publish_packet_path is None:
            return "review"
        return "ready"


@dataclass(frozen=True)
class DeliveryReadiness:
    episode_slug: str
    status: Literal["ready", "blocked"]
    gates: tuple[GateStatus, ...]

    @property
    def is_ready(self) -> bool:
        return self.status == "ready"


@dataclass(frozen=True)
class DeliveryAsset:
    key: Literal["final_video", "thumbnail", "review_report", "publish_packet"]
    label: str
    path: Path
    content_type: str


@dataclass(frozen=True)
class DeliveryPackage:
    episode_slug: str
    token_id: str
    max_accesses: int
    access_count: int
    expires_at: datetime
    assets: tuple[DeliveryAsset, ...]


@dataclass(frozen=True)
class WorkspaceSnapshot:
    characters: tuple[CharacterSummary, ...]
    episodes: tuple[EpisodeSummary, ...]
    formats: tuple[FormatProfileSummary, ...]

    @property
    def ready_episode_count(self) -> int:
        return sum(1 for episode in self.episodes if episode.status == "ready")

    @property
    def blocked_episode_count(self) -> int:
        return sum(1 for episode in self.episodes if episode.status == "blocked")


@dataclass(frozen=True)
class ProductionRequestRecord:
    id: str
    request_type: ProductionRequestType
    episode_slug: str
    character_slug: str
    format_profile_slug: str
    output_target: str
    reference_path: str
    completion_criteria: str
    creative_brief: str
    markdown: str
    status: str
    paperclip_issue_ref: str | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class CharacterTemplateResult:
    slug: str
    display_name: str
    root_path: Path
    created_files: tuple[Path, ...]


@dataclass(frozen=True)
class DeliveryTokenRecord:
    id: str
    episode_slug: str
    token_hash: str
    status: Literal["active", "revoked"]
    max_accesses: int
    access_count: int
    expires_at: datetime
    created_at: datetime
    revoked_at: datetime | None = None
    last_accessed_at: datetime | None = None


@dataclass(frozen=True)
class ClientRevisionRequestRecord:
    id: str
    token_id: str
    episode_slug: str
    requester_name: str
    requester_email: str
    timestamp_note: str
    message: str
    status: str
    paperclip_issue_ref: str | None
    created_at: datetime
    updated_at: datetime
    paperclip_status: str | None = None
    paperclip_priority: str | None = None
    paperclip_title: str | None = None
    paperclip_updated_at: str | None = None
    paperclip_latest_comment: str | None = None
    paperclip_latest_comment_at: str | None = None
    paperclip_synced_at: datetime | None = None
    paperclip_sync_error: str | None = None


@dataclass(frozen=True)
class PaperclipIssueSummary:
    ref: str
    id: str
    identifier: str | None
    title: str
    status: str
    priority: str | None
    updated_at: str | None


@dataclass(frozen=True)
class PaperclipIssueComment:
    id: str
    body: str
    author: str
    created_at: str


@dataclass(frozen=True)
class AuditLogEntry:
    id: str
    action: str
    entity_type: str
    entity_id: str
    payload: dict[str, object]
    actor: str
    created_at: datetime
