from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from sfs_console.domain import ClientRevisionRequestRecord


class WebhookRevisionNotifier:
    def __init__(self, webhook_url: str) -> None:
        self._webhook_url = webhook_url

    def notify_client_revision_created(self, record: ClientRevisionRequestRecord) -> None:
        issue_ref = record.paperclip_issue_ref or "not linked"
        text = (
            f"SFS client revision: {record.episode_slug} "
            f"({record.timestamp_note or 'no timestamp'}, Paperclip {issue_ref})"
        )
        payload = {
            "text": text,
            "content": text,
            "episode_slug": record.episode_slug,
            "revision_request_id": record.id,
            "paperclip_issue_ref": record.paperclip_issue_ref,
            "requester_name": record.requester_name,
            "timestamp": record.timestamp_note,
        }
        request = Request(
            self._webhook_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=5) as response:
                if response.status >= 400:
                    raise ValueError(f"webhook returned {response.status}")
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise ValueError(f"webhook returned {error.code}: {detail}") from error
        except URLError as error:
            raise ValueError(f"webhook request failed: {error.reason}") from error
