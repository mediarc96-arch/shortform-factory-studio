#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from http.cookiejar import CookieJar
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import HTTPCookieProcessor, HTTPRedirectHandler, Request, build_opener


BASE_URL = os.environ.get("SFS_SMOKE_BASE_URL", "https://sfs.devscent.com").rstrip("/")
API_URL = os.environ.get("SFS_SMOKE_API_URL", "https://api.devscent.com/openapi.json")
SECRET_FILE = Path(
    os.environ.get("SFS_SMOKE_PASSWORD_FILE", "/home/kindsr/.config/sfs-console/basic-auth.txt")
)
USERNAME = os.environ.get("SFS_OPERATOR_USERNAME", os.environ.get("SFS_CONSOLE_BASIC_USER", "sfs-admin"))


class NoRedirect(HTTPRedirectHandler):
    def http_error_302(self, request, fp, code, msg, headers):  # type: ignore[no-untyped-def]
        raise HTTPError(request.full_url, code, msg, headers, fp)

    http_error_301 = http_error_302
    http_error_303 = http_error_302
    http_error_307 = http_error_302
    http_error_308 = http_error_302


def main() -> None:
    username, password = read_credentials()
    cookies = CookieJar()
    opener = build_opener(HTTPCookieProcessor(cookies), NoRedirect())

    no_auth_status, no_auth_headers = request(opener, "GET", f"{BASE_URL}/ko/delivery", allow_error=True)
    assert_equal(no_auth_status, 307, "console redirects unauthenticated users to app login")
    if "/login" not in no_auth_headers.get("location", ""):
        raise AssertionError(f"unexpected unauthenticated redirect: {no_auth_headers.get('location', '')}")

    login_body = urlencode(
        {"username": username, "password": password, "next": "/ko/delivery"}
    ).encode("utf-8")
    login_status, login_headers = request(
        opener,
        "POST",
        f"{BASE_URL}/api/auth/login",
        headers={
            "content-type": "application/x-www-form-urlencoded",
        },
        body=login_body,
        allow_error=True,
    )
    assert_equal(login_status, 303, "app login returns redirect")
    location = login_headers.get("location", "")
    if location != f"{BASE_URL}/ko/delivery":
        raise AssertionError(f"unexpected login redirect: {location}")

    page_status, page_body = request(
        opener,
        "GET",
        f"{BASE_URL}/ko/delivery",
    )
    assert_equal(page_status, 200, "authenticated delivery page loads")
    if "SFS Console" not in page_body and "딜리버리" not in page_body:
        raise AssertionError("authenticated delivery page did not contain expected console text")

    api_no_auth_status, _ = request(
        build_opener(),
        "GET",
        f"{BASE_URL}/api/sfs/ops/health",
        allow_error=True,
    )
    assert_equal(api_no_auth_status, 401, "app API requires operator session")

    api_status, api_body = request(build_opener(), "GET", API_URL)
    assert_equal(api_status, 200, "api.devscent.com openapi loads")
    api_title = json.loads(api_body).get("info", {}).get("title")
    if api_title != "Fusion Sensor Monitoring":
        raise AssertionError(f"api.devscent.com appears changed: {api_title}")

    print("SFS console smoke passed")


def read_credentials() -> tuple[str, str]:
    raw = os.environ.get("SFS_OPERATOR_PASSWORD", os.environ.get("SFS_CONSOLE_BASIC_PASSWORD"))
    username = USERNAME
    if raw is None and SECRET_FILE.exists():
        raw = SECRET_FILE.read_text(encoding="utf-8").strip()
    if not raw:
        raise RuntimeError("SFS_CONSOLE_BASIC_PASSWORD or SFS_SMOKE_PASSWORD_FILE is required")
    if ":" in raw:
        file_user, file_password = raw.split(":", 1)
        username = os.environ.get("SFS_CONSOLE_BASIC_USER", file_user.strip() or USERNAME)
        raw = file_password
    if "\n" in raw or raw.startswith("username=") or raw.startswith("password="):
        values = {}
        for line in raw.splitlines():
            key, separator, value = line.partition("=")
            if separator:
                values[key.strip()] = value.strip()
        username = os.environ.get("SFS_CONSOLE_BASIC_USER", values.get("username", USERNAME))
        raw = values.get("password", "")
        if not raw:
            raise RuntimeError("password key is missing from SFS smoke password file")
    return username, raw.strip()


def request(
    opener,
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    body: bytes | None = None,
    allow_error: bool = False,
) -> tuple[int, str]:
    req = Request(url, data=body, method=method, headers=headers or {})
    try:
        with opener.open(req, timeout=20) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except HTTPError as error:
        if not allow_error:
            raise
        return error.code, error.headers


def assert_equal(actual: object, expected: object, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected}, got {actual}")


if __name__ == "__main__":
    main()
