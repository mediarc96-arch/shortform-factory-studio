from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


API_SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(API_SRC))

from sfs_console.application.use_cases import (  # noqa: E402
    BuildProductionRequestMarkdown,
    ProductionRequestDraft,
    ValidateDeliveryReadiness,
)
from sfs_console.infrastructure import FileSystemWorkspaceScanner  # noqa: E402


class WorkspaceScannerTest(unittest.TestCase):
    def test_scanner_indexes_workspace_without_requiring_all_assets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root / "characters/jjiroo/bible.md", "# Jjiroo")
            self._write(root / "characters/jjiroo/prompts.md", "# Prompts")
            self._write(root / "formats/pet-toon-image-only-v1/profile.json", "{}")
            self._write(root / "episodes/jjiroo-pilot-001/renders/final/final.mp4", "")
            self._write(root / "episodes/jjiroo-pilot-001/review/review-report.md", "# Review")

            snapshot = FileSystemWorkspaceScanner(root).scan()

            self.assertEqual(len(snapshot.characters), 1)
            self.assertEqual(len(snapshot.formats), 1)
            self.assertEqual(len(snapshot.episodes), 1)
            self.assertEqual(snapshot.episodes[0].slug, "jjiroo-pilot-001")
            self.assertEqual(snapshot.episodes[0].character_slug, "jjiroo")
            self.assertEqual(snapshot.episodes[0].status, "review")

    def test_delivery_readiness_blocks_missing_rights_and_publish_packet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root / "characters/jjiroo/bible.md", "# Jjiroo")
            self._write(root / "episodes/jjiroo-pilot-001/renders/final/final.mp4", "")
            self._write(root / "episodes/jjiroo-pilot-001/renders/final/final-thumb.jpg", "")
            self._write(root / "episodes/jjiroo-pilot-001/review/review-report.md", "# Review")

            episode = FileSystemWorkspaceScanner(root).scan().episodes[0]
            readiness = ValidateDeliveryReadiness().execute(episode, character_has_rights=False)

            self.assertFalse(readiness.is_ready)
            self.assertEqual(readiness.status, "blocked")
            self.assertIn("publish_packet", {gate.key for gate in readiness.gates if gate.status == "missing"})
            self.assertIn("rights", {gate.key for gate in readiness.gates if gate.status == "missing"})

    def test_production_request_markdown_validates_required_fields(self) -> None:
        draft = ProductionRequestDraft(
            request_type="new_episode",
            episode_slug="jjiroo-pilot-002",
            character_slug="jjiroo",
            format_profile_slug="pet-toon-image-only-v1",
            output_target="vertical 1080x1920 mp4",
            reference_path="characters/jjiroo/refs",
            completion_criteria="final mp4, thumbnail, review report",
            creative_brief="Keep the character on model.",
        )

        markdown = BuildProductionRequestMarkdown().execute(draft)

        self.assertIn("# new_episode: jjiroo-pilot-002", markdown)
        self.assertIn("- character: jjiroo", markdown)
        self.assertIn("Do not publish externally", markdown)

    def _write(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
