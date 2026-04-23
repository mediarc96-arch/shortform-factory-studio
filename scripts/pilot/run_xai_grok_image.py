#!/usr/bin/env python3

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from paperclip_costs import record_xai_cost_from_payload  # noqa: E402


API_BASE = "https://api.x.ai/v1"


def load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def resolve_local_media(value: str, base_dir: Path) -> str:
    if value.startswith("http://") or value.startswith("https://") or value.startswith("data:"):
        return value
    media_path = (base_dir / value).resolve()
    if not media_path.exists():
        raise FileNotFoundError(f"Referenced media file does not exist: {media_path}")
    mime_type, _ = mimetypes.guess_type(media_path.name)
    if not mime_type:
        mime_type = "application/octet-stream"
    encoded = base64.b64encode(media_path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def normalize_request(job_request: dict[str, Any], job_dir: Path) -> dict[str, Any]:
    request_payload = json.loads(json.dumps(job_request))

    image_value = request_payload.get("image")
    if isinstance(image_value, str):
        request_payload["image"] = {"url": resolve_local_media(image_value, job_dir)}
    elif isinstance(image_value, dict) and "url" in image_value:
        request_payload["image"] = dict(image_value)
        request_payload["image"]["url"] = resolve_local_media(str(image_value["url"]), job_dir)

    reference_images = request_payload.get("reference_images")
    if isinstance(reference_images, list):
        normalized: list[dict[str, Any]] = []
        for image in reference_images:
            if isinstance(image, str):
                normalized.append({"url": resolve_local_media(image, job_dir)})
            elif isinstance(image, dict) and "url" in image:
                current = dict(image)
                current["url"] = resolve_local_media(str(image["url"]), job_dir)
                normalized.append(current)
            else:
                raise ValueError("reference_images entries must be strings or objects with a url field")
        request_payload["reference_images"] = normalized

    return request_payload


def choose_endpoint(job: dict[str, Any]) -> str:
    explicit = str(job.get("_endpoint") or "").strip()
    if explicit:
        return explicit.split()[-1]
    task_type = str(job.get("taskType") or "").strip()
    if task_type == "image_edit":
        return f"{API_BASE}/images/edits"
    return f"{API_BASE}/images/generations"


def download_image(url: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"}, method="GET")
    try:
        with urlopen(req, timeout=300) as response, output_path.open("wb") as handle:
            handle.write(response.read())
        return
    except HTTPError:
        pass

    subprocess.run(
        [
            "curl",
            "-fsSL",
            "-A",
            "Mozilla/5.0",
            url,
            "-o",
            str(output_path),
        ],
        check=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a single xAI Grok image generation or edit job.")
    parser.add_argument("--job", required=True, help="Path to the image job JSON file")
    parser.add_argument("--env-file", default=".env", help="Optional env file to load before reading keys")
    args = parser.parse_args()

    job_path = Path(args.job).resolve()
    if not job_path.exists():
        raise FileNotFoundError(f"Job file not found: {job_path}")

    load_env_file(Path(args.env_file).resolve())
    api_key = os.environ.get("XAI_API_KEY") or os.environ.get("GROK_API_KEY")
    if not api_key:
        raise RuntimeError("Missing XAI_API_KEY or GROK_API_KEY in environment")

    job = json.loads(job_path.read_text(encoding="utf-8"))
    job_dir = job_path.parent
    request_payload = normalize_request(job["request"], job_dir)
    endpoint = choose_endpoint(job)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    body = json.dumps(request_payload).encode("utf-8")
    req = Request(endpoint, data=body, headers=headers, method="POST")
    try:
        with urlopen(req, timeout=300) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"xAI image request failed: {exc.code} {error_body}") from exc
    except URLError as exc:
        raise RuntimeError(f"xAI image request failed: {exc}") from exc
    image_data = payload.get("data") or []
    if not image_data or not isinstance(image_data, list):
        raise RuntimeError(f"Image response missing data array: {json.dumps(payload, ensure_ascii=False)}")
    first = image_data[0]
    image_url = first.get("url")
    if not image_url:
        raise RuntimeError(f"Image response missing url: {json.dumps(payload, ensure_ascii=False)}")

    runner = job["runner"]
    output_file = (job_dir / runner["outputFile"]).resolve()
    manifest_file = (job_dir / runner["manifestFile"]).resolve()
    download_image(image_url, output_file)

    manifest = {
        "provider": job.get("provider", "xai_grok"),
        "status": "succeeded",
        "taskType": job.get("taskType", "image_generation"),
        "jobPath": str(job_path),
        "manifestFile": str(manifest_file),
        "outputFile": str(output_file),
        "outputUrls": [image_url],
        "errorMessage": None,
        "request": request_payload,
        "response": payload,
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "revisedPrompt": first.get("revised_prompt") or "",
        "mimeType": first.get("mime_type") or None
    }
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    record_xai_cost_from_payload(model=str(request_payload.get("model") or "unknown"), payload=payload)

    print(str(output_file))
    print(str(manifest_file))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover
        print(f"error: {exc}", file=sys.stderr)
        raise
