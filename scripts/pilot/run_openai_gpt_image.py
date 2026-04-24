#!/usr/bin/env python3

from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


API_BASE = "https://api.openai.com/v1"


def load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def resolve_path(value: str, base_dir: Path) -> Path:
    media_path = Path(value)
    if not media_path.is_absolute():
        media_path = base_dir / media_path
    media_path = media_path.resolve()
    if not media_path.exists():
        raise FileNotFoundError(f"Referenced image file does not exist: {media_path}")
    return media_path


def choose_endpoint(job: dict[str, Any]) -> str:
    explicit = str(job.get("_endpoint") or "").strip()
    if explicit:
        return explicit.split()[-1]
    task_type = str(job.get("taskType") or "").strip()
    if task_type == "image_edit":
        return f"{API_BASE}/images/edits"
    return f"{API_BASE}/images/generations"


def download_url(url: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"}, method="GET")
    try:
        with urlopen(req, timeout=300) as response, output_path.open("wb") as handle:
            handle.write(response.read())
        return
    except HTTPError:
        pass

    subprocess.run(
        ["curl", "-fsSL", "-A", "Mozilla/5.0", url, "-o", str(output_path)],
        check=True,
    )


def write_image_from_response(payload: dict[str, Any], output_path: Path) -> dict[str, Any]:
    image_data = payload.get("data") or []
    if not image_data or not isinstance(image_data, list):
        raise RuntimeError(f"Image response missing data array: {json.dumps(payload, ensure_ascii=False)}")
    first = image_data[0]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if first.get("b64_json"):
        output_path.write_bytes(base64.b64decode(first["b64_json"]))
    elif first.get("url"):
        download_url(str(first["url"]), output_path)
    else:
        raise RuntimeError(f"Image response missing b64_json/url: {json.dumps(payload, ensure_ascii=False)}")
    return first


def post_generation(api_key: str, endpoint: str, request_payload: dict[str, Any]) -> dict[str, Any]:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    body = json.dumps(request_payload).encode("utf-8")
    req = Request(endpoint, data=body, headers=headers, method="POST")
    try:
        with urlopen(req, timeout=300) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI image request failed: {exc.code} {error_body}") from exc
    except URLError as exc:
        raise RuntimeError(f"OpenAI image request failed: {exc}") from exc


def post_edit(api_key: str, endpoint: str, request_payload: dict[str, Any], job_dir: Path) -> dict[str, Any]:
    image_values = request_payload.get("image") or request_payload.get("reference_images") or []
    if isinstance(image_values, str):
        image_values = [image_values]
    if not isinstance(image_values, list) or not image_values:
        raise ValueError("image_edit jobs require request.image or request.reference_images")

    fields: list[str] = []
    for key, value in request_payload.items():
        if key in {"image", "reference_images"}:
            continue
        if value is None:
            continue
        if isinstance(value, (dict, list)):
            fields.extend(["-F", f"{key}={json.dumps(value, ensure_ascii=False)}"])
        else:
            fields.extend(["-F", f"{key}={value}"])

    for image in image_values:
        image_path = resolve_path(str(image), job_dir)
        fields.extend(["-F", f"image[]=@{image_path}"])

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as payload_file:
        payload_path = Path(payload_file.name)

    cmd = [
        "curl",
        "-fsS",
        "-X",
        "POST",
        endpoint,
        "-H",
        f"Authorization: Bearer {api_key}",
        *fields,
        "-o",
        str(payload_path),
    ]
    try:
        subprocess.run(cmd, check=True)
        return json.loads(payload_path.read_text(encoding="utf-8"))
    except subprocess.CalledProcessError as exc:
        error_body = payload_path.read_text(encoding="utf-8", errors="replace") if payload_path.exists() else ""
        raise RuntimeError(f"OpenAI image edit request failed: {error_body}") from exc
    finally:
        payload_path.unlink(missing_ok=True)


def public_request_payload(request_payload: dict[str, Any]) -> dict[str, Any]:
    payload = json.loads(json.dumps(request_payload, ensure_ascii=False))
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a single OpenAI GPT Image generation or edit job.")
    parser.add_argument("--job", required=True, help="Path to the image job JSON file")
    parser.add_argument("--env-file", default=".env", help="Optional env file to load before reading keys")
    args = parser.parse_args()

    job_path = Path(args.job).resolve()
    if not job_path.exists():
        raise FileNotFoundError(f"Job file not found: {job_path}")

    load_env_file(Path(args.env_file).resolve())
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY in environment")

    job = json.loads(job_path.read_text(encoding="utf-8"))
    job_dir = job_path.parent
    request_payload = dict(job["request"])
    request_payload.setdefault("model", os.environ.get("OPENAI_IMAGE_MODEL") or "gpt-image-2")
    endpoint = choose_endpoint(job)

    if str(job.get("taskType") or "").strip() == "image_edit":
        payload = post_edit(api_key, endpoint, request_payload, job_dir)
    else:
        payload = post_generation(api_key, endpoint, request_payload)

    runner = job["runner"]
    output_file = (job_dir / runner["outputFile"]).resolve()
    manifest_file = (job_dir / runner["manifestFile"]).resolve()
    first = write_image_from_response(payload, output_file)

    manifest = {
        "provider": job.get("provider", "openai"),
        "status": "succeeded",
        "taskType": job.get("taskType", "image_generation"),
        "model": request_payload.get("model"),
        "jobPath": str(job_path),
        "manifestFile": str(manifest_file),
        "outputFile": str(output_file),
        "endpoint": endpoint,
        "errorMessage": None,
        "request": public_request_payload(request_payload),
        "response": payload,
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "revisedPrompt": first.get("revised_prompt") or "",
        "mimeType": first.get("mime_type") or None
    }
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(str(output_file))
    print(str(manifest_file))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover
        print(f"error: {exc}", file=sys.stderr)
        raise
