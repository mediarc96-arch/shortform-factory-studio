from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class PaperclipIssueHttpClient:
    def __init__(
        self,
        *,
        base_url: str,
        api_token: str,
        company_id: str,
        project_id: str | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_token = api_token
        self._company_id = company_id
        self._project_id = project_id

    def create_issue(self, *, title: str, description: str) -> str:
        payload: dict[str, object] = {
            "title": title,
            "description": description,
            "status": "todo",
            "priority": "medium",
        }
        if self._project_id:
            payload["projectId"] = self._project_id

        url = f"{self._base_url}/api/companies/{self._company_id}/issues"
        request = Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._api_token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=10) as response:
                body = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise ValueError(f"Paperclip issue creation failed: {error.code} {detail}") from error
        except URLError as error:
            raise ValueError(f"Paperclip issue creation failed: {error.reason}") from error

        identifier = body.get("identifier") or body.get("id")
        if not isinstance(identifier, str) or not identifier:
            raise ValueError("Paperclip issue creation returned no issue reference")
        return identifier
