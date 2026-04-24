from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal


AssetStatus = Literal["present", "missing"]
EpisodeStatus = Literal["ready", "review", "blocked"]


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
