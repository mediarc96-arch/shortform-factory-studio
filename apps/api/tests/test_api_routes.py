from __future__ import annotations

from datetime import timedelta
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path


API_SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(API_SRC))

try:
    from fastapi.testclient import TestClient

    from sfs_console.application import (
        ClientRevisionRequestDraft,
        CreateClientRevisionRequest,
        ProductionRequestDraft,
        SaveProductionRequest,
        SendProductionRequestToPaperclip,
    )
    from sfs_console.config import Settings
    from sfs_console.domain import PaperclipIssueComment, PaperclipIssueSummary
    from sfs_console.domain.models import utc_now
    from sfs_console.infrastructure import InMemorySfsStore
    from sfs_console.presentation import create_app
except Exception:  # pragma: no cover - dependency guard for bare Python environments
    TestClient = None  # type: ignore[assignment]
    ClientRevisionRequestDraft = None  # type: ignore[assignment]
    CreateClientRevisionRequest = None  # type: ignore[assignment]
    ProductionRequestDraft = None  # type: ignore[assignment]
    SaveProductionRequest = None  # type: ignore[assignment]
    SendProductionRequestToPaperclip = None  # type: ignore[assignment]
    Settings = None  # type: ignore[assignment]
    PaperclipIssueComment = None  # type: ignore[assignment]
    PaperclipIssueSummary = None  # type: ignore[assignment]
    utc_now = None  # type: ignore[assignment]
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

            video = client.get("/episodes/jjiroo-pilot-001/files/final_video")
            self.assertEqual(video.status_code, 200)
            self.assertEqual(video.headers["content-type"], "video/mp4")

            missing_asset = client.get("/episodes/jjiroo-pilot-001/files/unknown")
            self.assertEqual(missing_asset.status_code, 404)

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

        client_token = "client-token"
        store.create_delivery_token(
            episode_slug="jjiroo-pilot-002",
            token_hash=hashlib.sha256(client_token.encode("utf-8")).hexdigest(),
            expires_at=utc_now() + timedelta(hours=1),
            max_accesses=1,
        )

        revision = CreateClientRevisionRequest(store, store, store, paperclip).execute(
            token=client_token,
            draft=ClientRevisionRequestDraft(
                requester_name="Client",
                requester_email="client@example.com",
                timestamp_note="00:12",
                message="Please trim this beat.",
            ),
        )

        self.assertEqual(revision.paperclip_issue_ref, "SHO-123")
        self.assertEqual(paperclip.calls[1]["origin_kind"], "sfs_console.client_revision_request")
        self.assertEqual(paperclip.calls[1]["origin_id"], revision.id)

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
                json={"episode_slug": "jjiroo-pilot-001", "expires_in_hours": 24, "max_accesses": 2},
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], "active")
            self.assertEqual(response.json()["max_accesses"], 2)
            self.assertEqual(response.json()["access_count"], 0)
            self.assertIsInstance(response.json()["token"], str)

            package = client.get(f"/public/deliveries/{response.json()['token']}")
            self.assertEqual(package.status_code, 200)
            self.assertEqual(package.json()["episode_slug"], "jjiroo-pilot-001")
            self.assertEqual(package.json()["access_count"], 1)
            self.assertEqual(
                {asset["key"] for asset in package.json()["assets"]},
                {"final_video", "thumbnail", "review_report", "publish_packet"},
            )

            revision = client.post(
                f"/public/deliveries/{response.json()['token']}/revision-requests",
                json={
                    "requester_name": "Client",
                    "requester_email": "client@example.com",
                    "timestamp": "00:12",
                    "message": "Please shorten the opening pause.",
                },
            )
            self.assertEqual(revision.status_code, 200)
            self.assertEqual(revision.json()["episode_slug"], "jjiroo-pilot-001")
            self.assertEqual(revision.json()["status"], "received")

            revisions = client.get("/revision-requests?episode_slug=jjiroo-pilot-001")
            self.assertEqual(revisions.status_code, 200)
            self.assertEqual(revisions.json()[0]["id"], revision.json()["id"])

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

    def test_revision_request_route_can_include_paperclip_state(self) -> None:
        class FakePaperclip:
            def create_issue(
                self,
                *,
                title: str,
                description: str,
                origin_kind: str | None = None,
                origin_id: str | None = None,
            ) -> str:
                return "SHO-900"

            def get_issue(self, issue_ref: str):
                return PaperclipIssueSummary(
                    ref=issue_ref,
                    id="issue-900",
                    identifier=issue_ref,
                    title="SFS client revision: jjiroo-pilot-001",
                    status="in_progress",
                    priority="medium",
                    updated_at="2026-04-25T00:00:00.000Z",
                )

            def list_issue_comments(self, issue_ref: str, *, limit: int = 5):
                return (
                    PaperclipIssueComment(
                        id="comment-1",
                        body="Trim accepted; rendering a shorter pass.",
                        author="operator",
                        created_at="2026-04-25T00:05:00.000Z",
                    ),
                )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(root / "characters/jjiroo/bible.md", "# Jjiroo")
            self._write(root / "characters/jjiroo/prompts.md", "# Prompts")
            self._write(root / "characters/jjiroo/rights.md", "# Rights")
            self._write(root / "episodes/jjiroo-pilot-001/renders/final/final.mp4", "")
            self._write(root / "episodes/jjiroo-pilot-001/renders/final/final-thumb.jpg", "")
            self._write(root / "episodes/jjiroo-pilot-001/review/review-report.md", "# Review")
            self._write(root / "episodes/jjiroo-pilot-001/publish-packet.json", "{}")
            client = TestClient(
                create_app(
                    Settings(workspace_root=root),
                    paperclip_client=FakePaperclip(),
                )
            )

            token_response = client.post(
                "/deliveries/tokens",
                json={
                    "episode_slug": "jjiroo-pilot-001",
                    "expires_in_hours": 24,
                    "max_accesses": 2,
                },
            )
            revision = client.post(
                f"/public/deliveries/{token_response.json()['token']}/revision-requests",
                json={
                    "requester_name": "Client",
                    "requester_email": "client@example.com",
                    "timestamp": "00:12",
                    "message": "Please shorten the opening pause.",
                },
            )
            revisions = client.get(
                "/revision-requests?episode_slug=jjiroo-pilot-001&include_paperclip=true"
            )

            self.assertEqual(revision.status_code, 200)
            self.assertEqual(revisions.status_code, 200)
            paperclip_issue = revisions.json()[0]["paperclip_issue"]
            self.assertEqual(revisions.json()[0]["paperclip_issue_ref"], "SHO-900")
            self.assertEqual(revisions.json()[0]["status"], "in_progress")
            self.assertEqual(revisions.json()[0]["paperclip_status"], "in_progress")
            self.assertEqual(
                revisions.json()[0]["paperclip_latest_comment"],
                "Trim accepted; rendering a shorter pass.",
            )
            self.assertIsNotNone(revisions.json()[0]["paperclip_synced_at"])
            self.assertEqual(paperclip_issue["status"], "in_progress")
            self.assertEqual(
                paperclip_issue["comments"][0]["body"],
                "Trim accepted; rendering a shorter pass.",
            )

            synced = client.post("/revision-requests/paperclip-sync?episode_slug=jjiroo-pilot-001")
            self.assertEqual(synced.status_code, 200)
            self.assertEqual(synced.json()[0]["status"], "in_progress")

    def test_revision_request_rejects_invalid_public_payload(self) -> None:
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

            token_response = client.post(
                "/deliveries/tokens",
                json={
                    "episode_slug": "jjiroo-pilot-001",
                    "expires_in_hours": 24,
                    "max_accesses": 2,
                },
            )
            invalid_email = client.post(
                f"/public/deliveries/{token_response.json()['token']}/revision-requests",
                json={
                    "requester_name": "Client",
                    "requester_email": "not-an-email",
                    "timestamp": "00:12",
                    "message": "Please shorten the opening pause.",
                },
            )
            long_message = client.post(
                f"/public/deliveries/{token_response.json()['token']}/revision-requests",
                json={
                    "requester_name": "Client",
                    "requester_email": "client@example.com",
                    "timestamp": "00:12",
                    "message": "x" * 3001,
                },
            )

            self.assertEqual(invalid_email.status_code, 422)
            self.assertEqual(long_message.status_code, 422)

    def test_delivery_token_access_limit_blocks_package(self) -> None:
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
                json={"episode_slug": "jjiroo-pilot-001", "expires_in_hours": 24, "max_accesses": 1},
            )

            self.assertEqual(response.status_code, 200)
            first = client.get(f"/public/deliveries/{response.json()['token']}")
            asset = client.get(f"/public/deliveries/{response.json()['token']}/files/final_video")
            second = client.get(f"/public/deliveries/{response.json()['token']}")

            self.assertEqual(first.status_code, 200)
            self.assertEqual(first.json()["access_count"], 1)
            self.assertEqual(asset.status_code, 200)
            self.assertEqual(second.status_code, 404)
            audit = client.get("/audit-logs")
            self.assertIn(
                "delivery_asset.requested",
                {entry["action"] for entry in audit.json()},
            )

    def test_delivery_asset_direct_access_consumes_limit_and_blocks_new_package(self) -> None:
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
                json={"episode_slug": "jjiroo-pilot-001", "expires_in_hours": 24, "max_accesses": 1},
            )

            self.assertEqual(response.status_code, 200)
            asset = client.get(f"/public/deliveries/{response.json()['token']}/files/final_video")
            package = client.get(f"/public/deliveries/{response.json()['token']}")
            tokens = client.get("/deliveries/tokens")
            audit = client.get("/audit-logs")

            self.assertEqual(asset.status_code, 200)
            self.assertEqual(package.status_code, 404)
            self.assertEqual(tokens.json()[0]["access_count"], 1)
            self.assertIn(
                "delivery_token.accessed",
                {entry["action"] for entry in audit.json()},
            )
            self.assertIn(
                "delivery_asset.requested",
                {entry["action"] for entry in audit.json()},
            )

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
