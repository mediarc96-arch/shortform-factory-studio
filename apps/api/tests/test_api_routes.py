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

            readiness = client.get("/episodes/jjiroo-pilot-001/delivery-readiness")
            self.assertEqual(readiness.status_code, 200)
            self.assertEqual(readiness.json()["status"], "ready")

    def _write(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
