from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from sfs_console.domain import PaperclipIssueComment, PaperclipIssueSummary


def _optional_string(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return str(value)


def _string_or_default(value: object, default: str) -> str:
    return _optional_string(value) or default


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

    def create_issue(
        self,
        *,
        title: str,
        description: str,
        origin_kind: str | None = None,
        origin_id: str | None = None,
    ) -> str:
        payload: dict[str, object] = {
            "title": title,
            "description": description,
            "status": "todo",
            "priority": "medium",
        }
        if origin_kind:
            payload["originKind"] = origin_kind
        if origin_id:
            payload["originId"] = origin_id
        if self._project_id:
            payload["projectId"] = self._project_id

        body = self._request_json(
            "POST",
            f"/api/companies/{quote(self._company_id, safe='')}/issues",
            payload=payload,
            failure_label="Paperclip issue creation failed",
        )
        if not isinstance(body, dict):
            raise ValueError("Paperclip issue creation returned invalid payload")

        identifier = body.get("identifier") or body.get("id")
        if not isinstance(identifier, str) or not identifier:
            raise ValueError("Paperclip issue creation returned no issue reference")
        return identifier

    def get_issue(self, issue_ref: str) -> PaperclipIssueSummary | None:
        body = self._request_json(
            "GET",
            f"/api/issues/{quote(issue_ref, safe='')}",
            not_found_ok=True,
        )
        if body is None:
            return None
        if not isinstance(body, dict):
            raise ValueError("Paperclip issue lookup returned invalid payload")

        return PaperclipIssueSummary(
            ref=issue_ref,
            id=_string_or_default(body.get("id"), issue_ref),
            identifier=_optional_string(body.get("identifier")),
            title=_string_or_default(body.get("title"), issue_ref),
            status=_string_or_default(body.get("status"), "unknown"),
            priority=_optional_string(body.get("priority")),
            updated_at=_optional_string(body.get("updatedAt") or body.get("updated_at")),
        )

    def list_issue_comments(
        self,
        issue_ref: str,
        *,
        limit: int = 5,
    ) -> tuple[PaperclipIssueComment, ...]:
        safe_limit = max(1, min(limit, 20))
        query = urlencode({"limit": safe_limit, "order": "desc"})
        body = self._request_json(
            "GET",
            f"/api/issues/{quote(issue_ref, safe='')}/comments?{query}",
            not_found_ok=True,
        )
        if body is None:
            return ()
        if not isinstance(body, list):
            raise ValueError("Paperclip issue comments returned invalid payload")

        comments: list[PaperclipIssueComment] = []
        for item in body:
            if not isinstance(item, dict):
                continue
            comments.append(
                PaperclipIssueComment(
                    id=_string_or_default(item.get("id"), ""),
                    body=_string_or_default(item.get("body"), ""),
                    author=(
                        _optional_string(item.get("authorUserId"))
                        or _optional_string(item.get("authorAgentId"))
                        or "paperclip"
                    ),
                    created_at=_string_or_default(
                        item.get("createdAt") or item.get("created_at"),
                        "",
                    ),
                )
            )
        return tuple(comment for comment in comments if comment.id and comment.body)

    def _request_json(
        self,
        method: str,
        path: str,
        *,
        payload: dict[str, object] | None = None,
        not_found_ok: bool = False,
        failure_label: str = "Paperclip request failed",
    ) -> object:
        headers = {
            "Authorization": f"Bearer {self._api_token}",
            "Accept": "application/json",
        }
        data = None
        if payload is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(payload).encode("utf-8")

        request = Request(
            f"{self._base_url}{path}",
            data=data,
            headers=headers,
            method=method,
        )
        try:
            with urlopen(request, timeout=10) as response:
                raw_body = response.read().decode("utf-8")
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            if error.code == 404 and not_found_ok:
                return None
            raise ValueError(f"{failure_label}: {error.code} {detail}") from error
        except URLError as error:
            raise ValueError(f"{failure_label}: {error.reason}") from error

        return json.loads(raw_body) if raw_body else None
