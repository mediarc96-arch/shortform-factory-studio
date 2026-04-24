from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from sfs_console.application.ports import WorkspaceScanner
from sfs_console.domain import DeliveryReadiness, EpisodeSummary, GateStatus, WorkspaceSnapshot


@dataclass(frozen=True)
class ProductionRequestDraft:
    request_type: Literal["new_episode", "revise_episode", "publish_only", "metadata_update"]
    episode_slug: str
    character_slug: str
    format_profile_slug: str
    output_target: str
    reference_path: str
    completion_criteria: str
    creative_brief: str


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
