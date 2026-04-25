from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


API_SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(API_SRC))

try:
    from fastapi.testclient import TestClient

    from sfs_console.application import (
        ProductionRequestDraft,
        SaveProductionRequest,
        SendProductionRequestToPaperclip,
    )
    from sfs_console.config import Settings
    from sfs_console.infrastructure import InMemorySfsStore
    from sfs_console.presentation import create_app
except Exception:  # pragma: no cover - dependency guard for bare Python environments
    TestClient = None  # type: ignore[assignment]
    ProductionRequestDraft = None  # type: ignore[assignment]
    SaveProductionRequest = None  # type: ignore[assignment]
    SendProductionRequestToPaperclip = None  # type: ignore[assignment]
    Settings = None  # type: ignore[assignment]
    InMemorySfsStore = None  # type: ignore[assignment]
    create_app = None  # type: ignore[assignment]


@unittest.skipUnless(TestClient and Settings and create_app, "FastAPI test dependencies unavailable")
class ApiRoutesTest(unittest.TestCase):
    def test_health_and_workspace_snapshot_routes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root / "characters/jjiroo/bible.md", "# Jjiroo")
            self._write(root / "characters/jjiroo/prompts.md", "# Prompts")
            self._write(root / "characters/jjiroo/rights.md", "# Rights")
            self._write(root / "formats/pet-toon-image-only-v1/profile.json", "{}")
            self._write(root / "episodes/jjiroo-pilot-001/renders/final/final.mp4", "")
            self._write(root / "episodes/jjiroo-pilot-001/renders/final/final-thumb.jpg", "")
            self._write(root / "episodes/jjiroo-pilot-001/review/review-report.md", "# Review")
            self._write(root / "episodes/jjiroo-pilot-001/publish-packet.json", "{}")

            client = TestClient(create_app(Settings(workspace_root=root)))

            health = client.get("/health")
            self.assertEqual(health.status_code, 200)
            self.assertEqual(health.json()["status"], "ok")

            workspace = client.get("/workspace")
            self.assertEqual(workspace.status_code, 200)
            self.assertEqual(workspace.json()["episode_count"], 1)
            self.assertEqual(workspace.json()["ready_episode_count"], 1)
            self.assertEqual(workspace.json()["characters"][0]["slug"], "jjiroo")
            self.assertEqual(workspace.json()["formats"][0]["slug"], "pet-toon-image-only-v1")

            characters = client.get("/characters")
            self.assertEqual(characters.status_code, 200)
            self.assertEqual(characters.json()[0]["rights_status"], "present")

            formats = client.get("/formats")
            self.assertEqual(formats.status_code, 200)
            self.assertEqual(formats.json()[0]["slug"], "pet-toon-image-only-v1")

            readiness = client.get("/episodes/jjiroo-pilot-001/delivery-readiness")
            self.assertEqual(readiness.status_code, 200)
            self.assertEqual(readiness.json()["status"], "ready")

    def test_production_request_preview_route(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            client = TestClient(create_app(Settings(workspace_root=Path(tmp))))
            payload = {
                "request_type": "new_episode",
                "episode_slug": "jjiroo-pilot-002",
                "character_slug": "jjiroo",
                "format_profile_slug": "pet-toon-image-only-v1",
                "output_target": "vertical 1080x1920 mp4",
                "reference_path": "characters/jjiroo/refs",
                "completion_criteria": "final mp4, thumbnail, review report",
                "creative_brief": "Keep the character on model.",
            }

            response = client.post("/requests/production/preview", json=payload)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["request_type"], "new_episode")
            self.assertIn("# new_episode: jjiroo-pilot-002", response.json()["markdown"])
            self.assertIn("- character: jjiroo", response.json()["markdown"])

            created = client.post("/requests/production", json=payload)
            self.assertEqual(created.status_code, 200)
            self.assertEqual(created.json()["status"], "draft")
            self.assertIn("# new_episode: jjiroo-pilot-002", created.json()["markdown"])

            requests = client.get("/requests/production")
            self.assertEqual(requests.status_code, 200)
            self.assertEqual(requests.json()[0]["id"], created.json()["id"])

            audit = client.get("/audit-logs")
            self.assertEqual(audit.status_code, 200)
            self.assertEqual(audit.json()[0]["action"], "production_request.created")

    def test_paperclip_handoff_marks_issue_origin(self) -> None:
        class FakePaperclip:
            def __init__(self) -> None:
                self.calls: list[dict[str, str | None]] = []

            def create_issue(
                self,
                *,
                title: str,
                description: str,
                origin_kind: str | None = None,
                origin_id: str | None = None,
            ) -> str:
                self.calls.append(
                    {
                        "title": title,
                        "description": description,
                        "origin_kind": origin_kind,
                        "origin_id": origin_id,
                    }
                )
                return "SHO-123"

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
        paperclip = FakePaperclip()

        updated = SendProductionRequestToPaperclip(store, store, paperclip).execute(record.id)

        self.assertEqual(updated.paperclip_issue_ref, "SHO-123")
        self.assertEqual(paperclip.calls[0]["origin_kind"], "sfs_console.production_request")
        self.assertEqual(paperclip.calls[0]["origin_id"], record.id)

    def test_production_request_preview_rejects_missing_required_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            client = TestClient(create_app(Settings(workspace_root=Path(tmp))))
            payload = {
                "request_type": "revise_episode",
                "episode_slug": "jjiroo-pilot-001",
                "character_slug": "jjiroo",
                "format_profile_slug": "pet-toon-image-only-v1",
                "output_target": "vertical 1080x1920 mp4",
                "reference_path": "",
                "completion_criteria": "updated final mp4",
                "creative_brief": "Fix the drift in scene 04.",
            }

            response = client.post("/requests/production/preview", json=payload)

            self.assertEqual(response.status_code, 422)
            self.assertIn("reference_path", response.json()["detail"])

    def test_character_create_route_writes_template_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            client = TestClient(create_app(Settings(workspace_root=root)))

            response = client.post(
                "/characters",
                json={
                    "slug": "new-character",
                    "display_name": "New Character",
                    "series": "Pet Toon",
                    "voice_default": "warm Korean narrator",
                    "rights_status": "needs_review",
                    "negative_prompt": "Do not drift from canonical refs.",
                },
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["slug"], "new-character")
            self.assertTrue((root / "characters/new-character/bible.md").exists())
            self.assertTrue((root / "characters/new-character/prompts.md").exists())
            self.assertTrue((root / "characters/new-character/rights.md").exists())
            self.assertTrue((root / "characters/new-character/voice.json").exists())

            duplicate = client.post(
                "/characters",
                json={
                    "slug": "new-character",
                    "display_name": "New Character",
                    "series": "Pet Toon",
                    "voice_default": "warm Korean narrator",
                    "rights_status": "needs_review",
                    "negative_prompt": "Do not drift from canonical refs.",
                },
            )
            self.assertEqual(duplicate.status_code, 422)

    def test_delivery_token_route_requires_ready_episode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root / "characters/jjiroo/bible.md", "# Jjiroo")
            self._write(root / "characters/jjiroo/prompts.md", "# Prompts")
            self._write(root / "characters/jjiroo/rights.md", "# Rights")
            self._write(root / "episodes/jjiroo-pilot-001/renders/final/final.mp4", "")
            self._write(root / "episodes/jjiroo-pilot-001/renders/final/final-thumb.jpg", "")
            self._write(root / "episodes/jjiroo-pilot-001/review/review-report.md", "# Review")
            self._write(root / "episodes/jjiroo-pilot-001/publish-packet.json", "{}")
            client = TestClient(create_app(Settings(workspace_root=root)))

            response = client.post(
                "/deliveries/tokens",
                json={"episode_slug": "jjiroo-pilot-001", "expires_in_hours": 24},
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], "active")
            self.assertIsInstance(response.json()["token"], str)

            package = client.get(f"/public/deliveries/{response.json()['token']}")
            self.assertEqual(package.status_code, 200)
            self.assertEqual(package.json()["episode_slug"], "jjiroo-pilot-001")
            self.assertEqual(
                {asset["key"] for asset in package.json()["assets"]},
                {"final_video", "thumbnail", "review_report", "publish_packet"},
            )

            asset = client.get(f"/public/deliveries/{response.json()['token']}/files/final_video")
            self.assertEqual(asset.status_code, 200)

            tokens = client.get("/deliveries/tokens")
            self.assertEqual(tokens.status_code, 200)
            self.assertIsNone(tokens.json()[0]["token"])

            revoked = client.post(f"/deliveries/tokens/{response.json()['id']}/revoke")
            self.assertEqual(revoked.status_code, 200)
            self.assertEqual(revoked.json()["status"], "revoked")

            revoked_package = client.get(f"/public/deliveries/{response.json()['token']}")
            self.assertEqual(revoked_package.status_code, 404)

    def test_ops_health_route_reports_components(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            client = TestClient(create_app(Settings(workspace_root=Path(tmp))))

            response = client.get("/ops/health")

            self.assertEqual(response.status_code, 200)
            keys = {item["key"] for item in response.json()["components"]}
            self.assertIn("workspace", keys)
            self.assertIn("database", keys)

    def _write(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
