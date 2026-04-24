from __future__ import annotations

from pathlib import Path

from sfs_console.domain import CharacterSummary, EpisodeSummary, FormatProfileSummary, WorkspaceSnapshot


class FileSystemWorkspaceScanner:
    """Read-only scanner for the Shortform Factory Studio workspace."""

    def __init__(self, workspace_root: Path | str) -> None:
        self._root = Path(workspace_root).resolve()

    def scan(self) -> WorkspaceSnapshot:
        characters = self._scan_characters()
        character_slugs = tuple(character.slug for character in characters)
        return WorkspaceSnapshot(
            characters=characters,
            episodes=self._scan_episodes(character_slugs),
            formats=self._scan_formats(),
        )

    def _scan_characters(self) -> tuple[CharacterSummary, ...]:
        character_root = self._root / "characters"
        if not character_root.exists():
            return ()

        characters: list[CharacterSummary] = []
        for path in sorted(character_root.iterdir(), key=lambda item: item.name):
            if not path.is_dir() or path.name.startswith("_"):
                continue
            characters.append(
                CharacterSummary(
                    slug=path.name,
                    display_name=self._display_name(path.name),
                    root_path=path,
                    has_bible=(path / "bible.md").exists(),
                    has_prompts=(path / "prompts.md").exists(),
                    has_rights=(path / "rights.md").exists(),
                    has_voice=(path / "voice.json").exists(),
                )
            )
        return tuple(characters)

    def _scan_formats(self) -> tuple[FormatProfileSummary, ...]:
        format_root = self._root / "formats"
        if not format_root.exists():
            return ()

        profiles: list[FormatProfileSummary] = []
        for profile in sorted(format_root.glob("*/profile.json"), key=lambda item: item.parent.name):
            if profile.parent.name.startswith("_"):
                continue
            profiles.append(FormatProfileSummary(slug=profile.parent.name, profile_path=profile))
        return tuple(profiles)

    def _scan_episodes(self, character_slugs: tuple[str, ...]) -> tuple[EpisodeSummary, ...]:
        episode_root = self._root / "episodes"
        if not episode_root.exists():
            return ()

        episodes: list[EpisodeSummary] = []
        for path in sorted(episode_root.iterdir(), key=lambda item: item.name):
            if not path.is_dir() or path.name.startswith("_"):
                continue
            episodes.append(
                EpisodeSummary(
                    slug=path.name,
                    root_path=path,
                    character_slug=self._infer_character_slug(path.name, character_slugs),
                    final_output_path=self._first_existing(
                        path,
                        (
                            "renders/final/*final*.mp4",
                            "renders/final/*.mp4",
                            "renders/picture-lock/*.mp4",
                        ),
                    ),
                    thumbnail_path=self._first_existing(
                        path,
                        (
                            "renders/final/*thumb*.jpg",
                            "renders/final/*thumb*.png",
                            "thumbnail.jpg",
                            "thumbnail.png",
                        ),
                    ),
                    review_report_path=self._first_existing(
                        path,
                        (
                            "review/final-review-report.md",
                            "review/review-report.md",
                            "review/picture-preview/README.md",
                        ),
                    ),
                    publish_packet_path=self._first_existing(path, ("publish-packet.json",)),
                )
            )
        return tuple(episodes)

    def _first_existing(self, base: Path, patterns: tuple[str, ...]) -> Path | None:
        for pattern in patterns:
            matches = sorted(base.glob(pattern))
            if matches:
                return matches[0]
        return None

    def _infer_character_slug(self, episode_slug: str, character_slugs: tuple[str, ...]) -> str | None:
        for slug in sorted(character_slugs, key=len, reverse=True):
            if slug in episode_slug:
                return slug
        return None

    def _display_name(self, slug: str) -> str:
        return " ".join(part.capitalize() for part in slug.replace("_", "-").split("-"))
