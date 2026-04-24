from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


API_SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(API_SRC))

try:
    from fastapi.testclient import TestClient

    from sfs_console.config import Settings
    from sfs_console.presentation import create_app
except Exception:  # pragma: no cover - dependency guard for bare Python environments
    TestClient = None  # type: ignore[assignment]
    Settings = None  # type: ignore[assignment]
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

    def _write(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
