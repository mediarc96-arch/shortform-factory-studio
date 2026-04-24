from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from sfs_console.domain import DeliveryReadiness, EpisodeSummary, WorkspaceSnapshot


def _relative(path: Path | None) -> str | None:
    return str(path) if path else None


class HealthResponse(BaseModel):
    status: str
    service: str


class GateResponse(BaseModel):
    key: str
    label: str
    status: str
    detail: str


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
    episodes: list[EpisodeResponse]

    @classmethod
    def from_domain(cls, snapshot: WorkspaceSnapshot) -> "WorkspaceSnapshotResponse":
        return cls(
            character_count=len(snapshot.characters),
            episode_count=len(snapshot.episodes),
            format_count=len(snapshot.formats),
            ready_episode_count=snapshot.ready_episode_count,
            blocked_episode_count=snapshot.blocked_episode_count,
            episodes=[EpisodeResponse.from_domain(episode) for episode in snapshot.episodes],
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
