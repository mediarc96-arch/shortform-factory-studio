from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from sfs_console.application import CharacterTemplateDraft, ProductionRequestDraft
from sfs_console.domain import (
    AuditLogEntry,
    CharacterSummary,
    CharacterTemplateResult,
    DeliveryAsset,
    DeliveryPackage,
    DeliveryReadiness,
    DeliveryTokenRecord,
    EpisodeSummary,
    FormatProfileSummary,
    ProductionRequestRecord,
    WorkspaceSnapshot,
)


def _relative(path: Path | None) -> str | None:
    return str(path) if path else None


class HealthResponse(BaseModel):
    status: str
    service: str
    persistence: str = "memory"


class ProductionRequestPreviewRequest(BaseModel):
    request_type: Literal["new_episode", "revise_episode", "publish_only", "metadata_update"]
    episode_slug: str
    character_slug: str
    format_profile_slug: str
    output_target: str
    reference_path: str
    completion_criteria: str
    creative_brief: str

    def to_draft(self) -> ProductionRequestDraft:
        return ProductionRequestDraft(
            request_type=self.request_type,
            episode_slug=self.episode_slug,
            character_slug=self.character_slug,
            format_profile_slug=self.format_profile_slug,
            output_target=self.output_target,
            reference_path=self.reference_path,
            completion_criteria=self.completion_criteria,
            creative_brief=self.creative_brief,
        )


class ProductionRequestPreviewResponse(BaseModel):
    request_type: str
    episode_slug: str
    markdown: str


class ProductionRequestResponse(BaseModel):
    id: str
    request_type: str
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
    created_at: str
    updated_at: str

    @classmethod
    def from_domain(cls, record: ProductionRequestRecord) -> "ProductionRequestResponse":
        return cls(
            id=record.id,
            request_type=record.request_type,
            episode_slug=record.episode_slug,
            character_slug=record.character_slug,
            format_profile_slug=record.format_profile_slug,
            output_target=record.output_target,
            reference_path=record.reference_path,
            completion_criteria=record.completion_criteria,
            creative_brief=record.creative_brief,
            markdown=record.markdown,
            status=record.status,
            paperclip_issue_ref=record.paperclip_issue_ref,
            created_at=record.created_at.isoformat(),
            updated_at=record.updated_at.isoformat(),
        )


class GateResponse(BaseModel):
    key: str
    label: str
    status: str
    detail: str


class CharacterResponse(BaseModel):
    slug: str
    display_name: str
    root_path: str
    has_bible: bool
    has_prompts: bool
    has_rights: bool
    has_voice: bool
    rights_status: str

    @classmethod
    def from_domain(cls, character: CharacterSummary) -> "CharacterResponse":
        return cls(
            slug=character.slug,
            display_name=character.display_name,
            root_path=_relative(character.root_path) or "",
            has_bible=character.has_bible,
            has_prompts=character.has_prompts,
            has_rights=character.has_rights,
            has_voice=character.has_voice,
            rights_status=character.rights_status,
        )


class FormatProfileResponse(BaseModel):
    slug: str
    profile_path: str

    @classmethod
    def from_domain(cls, profile: FormatProfileSummary) -> "FormatProfileResponse":
        return cls(slug=profile.slug, profile_path=_relative(profile.profile_path) or "")


class EpisodeResponse(BaseModel):
    slug: str
    character_slug: str | None
    status: str
    final_output_path: str | None
    thumbnail_path: str | None
    review_report_path: str | None
    publish_packet_path: str | None

    @classmethod
    def from_domain(cls, episode: EpisodeSummary) -> "EpisodeResponse":
        return cls(
            slug=episode.slug,
            character_slug=episode.character_slug,
            status=episode.status,
            final_output_path=_relative(episode.final_output_path),
            thumbnail_path=_relative(episode.thumbnail_path),
            review_report_path=_relative(episode.review_report_path),
            publish_packet_path=_relative(episode.publish_packet_path),
        )


class WorkspaceSnapshotResponse(BaseModel):
    character_count: int
    episode_count: int
    format_count: int
    ready_episode_count: int
    blocked_episode_count: int
    characters: list[CharacterResponse]
    episodes: list[EpisodeResponse]
    formats: list[FormatProfileResponse]

    @classmethod
    def from_domain(cls, snapshot: WorkspaceSnapshot) -> "WorkspaceSnapshotResponse":
        return cls(
            character_count=len(snapshot.characters),
            episode_count=len(snapshot.episodes),
            format_count=len(snapshot.formats),
            ready_episode_count=snapshot.ready_episode_count,
            blocked_episode_count=snapshot.blocked_episode_count,
            characters=[CharacterResponse.from_domain(character) for character in snapshot.characters],
            episodes=[EpisodeResponse.from_domain(episode) for episode in snapshot.episodes],
            formats=[FormatProfileResponse.from_domain(profile) for profile in snapshot.formats],
        )


class DeliveryReadinessResponse(BaseModel):
    episode_slug: str
    status: str
    gates: list[GateResponse]

    @classmethod
    def from_domain(cls, readiness: DeliveryReadiness) -> "DeliveryReadinessResponse":
        return cls(
            episode_slug=readiness.episode_slug,
            status=readiness.status,
            gates=[GateResponse(**gate.__dict__) for gate in readiness.gates],
        )


class CharacterCreateRequest(BaseModel):
    slug: str
    display_name: str
    series: str
    voice_default: str
    rights_status: Literal["needs_review", "production_safe", "internal_only"]
    negative_prompt: str

    def to_draft(self) -> CharacterTemplateDraft:
        return CharacterTemplateDraft(
            slug=self.slug,
            display_name=self.display_name,
            series=self.series,
            voice_default=self.voice_default,
            rights_status=self.rights_status,
            negative_prompt=self.negative_prompt,
        )


class CharacterTemplateResponse(BaseModel):
    slug: str
    display_name: str
    root_path: str
    created_files: list[str]

    @classmethod
    def from_domain(cls, result: CharacterTemplateResult) -> "CharacterTemplateResponse":
        return cls(
            slug=result.slug,
            display_name=result.display_name,
            root_path=str(result.root_path),
            created_files=[str(path) for path in result.created_files],
        )


class DeliveryTokenCreateRequest(BaseModel):
    episode_slug: str
    expires_in_hours: int = 168
    max_accesses: int = 5


class DeliveryTokenResponse(BaseModel):
    id: str
    episode_slug: str
    status: str
    max_accesses: int
    access_count: int
    expires_at: str
    created_at: str
    revoked_at: str | None
    last_accessed_at: str | None
    token: str | None = None

    @classmethod
    def from_domain(
        cls,
        record: DeliveryTokenRecord,
        *,
        token: str | None = None,
    ) -> "DeliveryTokenResponse":
        return cls(
            id=record.id,
            episode_slug=record.episode_slug,
            status=record.status,
            max_accesses=record.max_accesses,
            access_count=record.access_count,
            expires_at=record.expires_at.isoformat(),
            created_at=record.created_at.isoformat(),
            revoked_at=record.revoked_at.isoformat() if record.revoked_at else None,
            last_accessed_at=record.last_accessed_at.isoformat() if record.last_accessed_at else None,
            token=token,
        )


class DeliveryAssetResponse(BaseModel):
    key: str
    label: str
    filename: str
    content_type: str
    size_bytes: int
    download_path: str

    @classmethod
    def from_domain(cls, asset: DeliveryAsset, *, token: str) -> "DeliveryAssetResponse":
        return cls(
            key=asset.key,
            label=asset.label,
            filename=asset.path.name,
            content_type=asset.content_type,
            size_bytes=asset.path.stat().st_size,
            download_path=f"/delivery/{token}/files/{asset.key}",
        )


class DeliveryPackageResponse(BaseModel):
    episode_slug: str
    token_id: str
    max_accesses: int
    access_count: int
    expires_at: str
    assets: list[DeliveryAssetResponse]

    @classmethod
    def from_domain(cls, package: DeliveryPackage, *, token: str) -> "DeliveryPackageResponse":
        return cls(
            episode_slug=package.episode_slug,
            token_id=package.token_id,
            max_accesses=package.max_accesses,
            access_count=package.access_count,
            expires_at=package.expires_at.isoformat(),
            assets=[DeliveryAssetResponse.from_domain(asset, token=token) for asset in package.assets],
        )


class AuditLogResponse(BaseModel):
    id: str
    action: str
    entity_type: str
    entity_id: str
    payload: dict[str, object]
    actor: str
    created_at: str

    @classmethod
    def from_domain(cls, entry: AuditLogEntry) -> "AuditLogResponse":
        return cls(
            id=entry.id,
            action=entry.action,
            entity_type=entry.entity_type,
            entity_id=entry.entity_id,
            payload=entry.payload,
            actor=entry.actor,
            created_at=entry.created_at.isoformat(),
        )


class OpsComponentResponse(BaseModel):
    key: str
    status: str
    detail: str


class OpsHealthResponse(BaseModel):
    status: str
    components: list[OpsComponentResponse]
