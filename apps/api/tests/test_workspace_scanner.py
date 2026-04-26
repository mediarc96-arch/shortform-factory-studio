from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


API_SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(API_SRC))

from sfs_console.application.use_cases import (  # noqa: E402
    BuildProductionRequestMarkdown,
    CharacterTemplateDraft,
    CreateCharacterTemplate,
    IssueDeliveryToken,
    ProductionRequestDraft,
    SaveProductionRequest,
    ValidateDeliveryReadiness,
)
from sfs_console.infrastructure import (  # noqa: E402
    FileSystemCharacterWriter,
    FileSystemWorkspaceScanner,
    InMemorySfsStore,
)


class WorkspaceScannerTest(unittest.TestCase):
    def test_scanner_indexes_workspace_without_requiring_all_assets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root / "characters/jjiroo/bible.md", "# Jjiroo")
            self._write(root / "characters/jjiroo/prompts.md", "# Prompts")
            self._write(root / "characters/jjiroo/refs/canonical-wall/01-front-neutral.jpg", "")
            self._write(root / "characters/jjiroo/refs/canonical-wall/_overview.jpg", "")
            self._write(root / "formats/pet-toon-image-only-v1/profile.json", "{}")
            self._write(root / "episodes/jjiroo-pilot-001/renders/final/final.mp4", "")
            self._write(root / "episodes/jjiroo-pilot-001/review/review-report.md", "# Review")

            snapshot = FileSystemWorkspaceScanner(root).scan()

            self.assertEqual(len(snapshot.characters), 1)
            self.assertEqual(len(snapshot.characters[0].reference_images), 1)
            self.assertEqual(snapshot.characters[0].reference_images[0].slot, "front-neutral")
            self.assertEqual(snapshot.characters[0].reference_images[0].filename, "01-front-neutral.jpg")
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

    def test_save_production_request_records_audit_event(self) -> None:
        store = InMemorySfsStore()
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

        record = SaveProductionRequest(store, store).execute(draft)

        self.assertEqual(record.status, "draft")
        self.assertEqual(store.list_production_requests()[0].id, record.id)
        self.assertEqual(store.list_audit_logs()[0].action, "production_request.created")

    def test_character_template_writer_creates_canonical_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            writer = FileSystemCharacterWriter(root)
            store = InMemorySfsStore()

            result = CreateCharacterTemplate(writer, store).execute(
                CharacterTemplateDraft(
                    slug="jjiroo-friend",
                    display_name="Jjiroo Friend",
                    series="Pet Toon",
                    voice_default="warm narrator",
                    rights_status="needs_review",
                    negative_prompt="Do not change face shape.",
                )
            )

            self.assertEqual(result.slug, "jjiroo-friend")
            self.assertTrue((root / "characters/jjiroo-friend/bible.md").exists())
            self.assertEqual(store.list_audit_logs()[0].action, "character_template.created")

    def test_delivery_token_hash_is_stored_without_plain_token(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root / "characters/jjiroo/bible.md", "# Jjiroo")
            self._write(root / "characters/jjiroo/rights.md", "# Rights")
            self._write(root / "episodes/jjiroo-pilot-001/renders/final/final.mp4", "")
            self._write(root / "episodes/jjiroo-pilot-001/renders/final/final-thumb.jpg", "")
            self._write(root / "episodes/jjiroo-pilot-001/review/review-report.md", "# Review")
            self._write(root / "episodes/jjiroo-pilot-001/publish-packet.json", "{}")
            scanner = FileSystemWorkspaceScanner(root)
            store = InMemorySfsStore()

            issued = IssueDeliveryToken(scanner, store, store).execute(
                episode_slug="jjiroo-pilot-001",
                expires_in_hours=24,
            )

            self.assertNotEqual(issued.record.token_hash, issued.token)
            self.assertEqual(len(issued.record.token_hash), 64)
            self.assertEqual(store.list_delivery_tokens()[0].id, issued.record.id)

    def _write(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
