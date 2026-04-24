from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from sfs_console.application import ProductionRequestDraft
from sfs_console.domain import (
    CharacterSummary,
    DeliveryReadiness,
    EpisodeSummary,
    FormatProfileSummary,
    WorkspaceSnapshot,
)


def _relative(path: Path | None) -> str | None:
    return str(path) if path else None


class HealthResponse(BaseModel):
    status: str
    service: str


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
