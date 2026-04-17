#!/usr/bin/env python3

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
import time
from pathlib import Path
from typing import Any

import requests


API_BASE = "https://api.x.ai/v1"
POLL_INTERVAL_SEC = 5
POLL_TIMEOUT_SEC = 60 * 20


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

    if isinstance(request_payload.get("image"), str):
        request_payload["image"] = {"url": resolve_local_media(request_payload["image"], job_dir)}
    elif isinstance(request_payload.get("image"), dict) and "url" in request_payload["image"]:
        request_payload["image"]["url"] = resolve_local_media(request_payload["image"]["url"], job_dir)

    if isinstance(request_payload.get("reference_images"), list):
        normalized_images: list[dict[str, Any]] = []
        for image in request_payload["reference_images"]:
            if isinstance(image, str):
                normalized_images.append({"url": resolve_local_media(image, job_dir)})
            elif isinstance(image, dict) and "url" in image:
                normalized = dict(image)
                normalized["url"] = resolve_local_media(str(image["url"]), job_dir)
                normalized_images.append(normalized)
            else:
                raise ValueError("reference_images entries must be strings or objects with a url field")
        request_payload["reference_images"] = normalized_images

    return request_payload


def poll_until_done(request_id: str, headers: dict[str, str]) -> dict[str, Any]:
    deadline = time.time() + POLL_TIMEOUT_SEC
    last_payload: dict[str, Any] | None = None

    while time.time() < deadline:
        response = requests.get(f"{API_BASE}/videos/{request_id}", headers=headers, timeout=60)
        response.raise_for_status()
        payload = response.json()
        last_payload = payload
        status = payload.get("status")
        if status == "done":
            return payload
        if status in {"failed", "expired"}:
            raise RuntimeError(f"Video generation failed with status={status}: {json.dumps(payload, ensure_ascii=False)}")
        time.sleep(POLL_INTERVAL_SEC)

    raise TimeoutError(f"Timed out waiting for video generation request_id={request_id}. Last payload={json.dumps(last_payload or {}, ensure_ascii=False)}")


def download_video(url: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=300) as response:
        response.raise_for_status()
        with output_path.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    handle.write(chunk)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a single xAI Grok image-to-video scene job.")
    parser.add_argument("--job", required=True, help="Path to the scene job JSON file")
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

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    start_response = requests.post(
        f"{API_BASE}/videos/generations",
        headers=headers,
        json=request_payload,
        timeout=120,
    )
    start_response.raise_for_status()
    start_payload = start_response.json()
    request_id = start_payload["request_id"]

    result_payload = poll_until_done(request_id, headers)
    video_url = result_payload["video"]["url"]

    runner = job["runner"]
    output_file = (job_dir / runner["outputFile"]).resolve()
    manifest_file = (job_dir / runner["manifestFile"]).resolve()

    download_video(video_url, output_file)

    manifest = {
        "provider": job.get("provider", "xai_grok"),
        "status": "succeeded",
        "taskType": job.get("taskType", "image_to_video"),
        "taskId": request_id,
        "taskStatus": result_payload.get("status", "").upper(),
        "jobPath": str(job_path),
        "manifestFile": str(manifest_file),
        "outputFile": str(output_file),
        "outputUrls": [video_url],
        "errorMessage": None,
        "request": request_payload,
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "task": result_payload,
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
