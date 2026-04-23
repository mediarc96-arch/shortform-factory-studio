#!/usr/bin/env python3
"""Paperclip cost-event helpers for external media APIs.

These helpers are intentionally best-effort. When Paperclip auth env vars are
missing, or the control plane is unavailable, the caller should continue its
main work without failing media generation.
"""

from __future__ import annotations

import atexit
import json
import math
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


XAI_USD_TICK_SCALE = 10_000_000_000
DEFAULT_SUPERTONE_ESTIMATED_USD_PER_MINUTE = 0.10


def _log(message: str) -> None:
    print(f"[paperclip-costs] {message}", file=sys.stderr)


def _read_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        return ""
    return value.strip()


def _resolve_linked_issue_id() -> str:
    explicit = _read_env("PAPERCLIP_TASK_ID")
    if explicit:
        return explicit
    linked = _read_env("PAPERCLIP_LINKED_ISSUE_IDS")
    if not linked:
        return ""
    for raw in linked.split(","):
        candidate = raw.strip()
        if candidate:
            return candidate
    return ""


def cost_reporting_enabled() -> bool:
    return bool(
        _read_env("PAPERCLIP_API_URL")
        and _read_env("PAPERCLIP_API_KEY")
        and _read_env("PAPERCLIP_COMPANY_ID")
        and _read_env("PAPERCLIP_AGENT_ID")
    )


def _coerce_float(value: Any) -> float | None:
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return float(value)
    if isinstance(value, str) and value.strip():
        try:
            parsed = float(value.strip())
        except ValueError:
            return None
        if math.isfinite(parsed):
            return parsed
    return None


def xai_cost_usd_from_payload(payload: dict[str, Any] | None) -> float:
    if not isinstance(payload, dict):
        return 0.0
    usage = payload.get("usage")
    if not isinstance(usage, dict):
        return 0.0
    ticks = _coerce_float(usage.get("cost_in_usd_ticks"))
    if ticks is None or ticks <= 0:
        return 0.0
    # xAI reports usage in 1e-10 USD ticks.
    return ticks / XAI_USD_TICK_SCALE


def resolve_supertone_estimated_usd_per_minute() -> float:
    override = _coerce_float(_read_env("SUPERTONE_ESTIMATED_USD_PER_MINUTE"))
    if override is not None and override > 0:
        return override
    return DEFAULT_SUPERTONE_ESTIMATED_USD_PER_MINUTE


def supertone_cost_usd_from_duration(duration_seconds: float) -> float:
    if not math.isfinite(duration_seconds) or duration_seconds <= 0:
        return 0.0
    return (duration_seconds / 60.0) * resolve_supertone_estimated_usd_per_minute()


def _usd_to_cents(cost_usd: float) -> int:
    if not math.isfinite(cost_usd) or cost_usd <= 0:
        return 0
    rounded = int(round(cost_usd * 100))
    return rounded if rounded > 0 else 1


@dataclass
class PendingCostEvent:
    provider: str
    biller: str
    billing_type: str
    model: str
    cost_usd: float = 0.0
    input_tokens: int = 0
    cached_input_tokens: int = 0
    output_tokens: int = 0


_pending_cost_events: dict[tuple[str, str, str, str], PendingCostEvent] = {}
_flush_registered = False


def _register_flush_hook() -> None:
    global _flush_registered
    if _flush_registered:
        return
    atexit.register(flush_pending_cost_events)
    _flush_registered = True


def accumulate_cost_event(
    *,
    provider: str,
    model: str,
    cost_usd: float,
    biller: str | None = None,
    billing_type: str = "metered_api",
    input_tokens: int = 0,
    cached_input_tokens: int = 0,
    output_tokens: int = 0,
) -> bool:
    if (
        (not math.isfinite(cost_usd) or cost_usd <= 0)
        and input_tokens <= 0
        and cached_input_tokens <= 0
        and output_tokens <= 0
    ):
        return False
    if not cost_reporting_enabled():
        return False

    normalized_provider = provider.strip() or "unknown"
    normalized_model = model.strip() or "unknown"
    normalized_biller = (biller or normalized_provider).strip() or normalized_provider
    normalized_billing_type = billing_type.strip() or "unknown"
    key = (normalized_provider, normalized_biller, normalized_billing_type, normalized_model)

    current = _pending_cost_events.get(key)
    if current is None:
        current = PendingCostEvent(
            provider=normalized_provider,
            biller=normalized_biller,
            billing_type=normalized_billing_type,
            model=normalized_model,
        )
        _pending_cost_events[key] = current

    if math.isfinite(cost_usd) and cost_usd > 0:
        current.cost_usd += cost_usd
    current.input_tokens += max(0, int(input_tokens))
    current.cached_input_tokens += max(0, int(cached_input_tokens))
    current.output_tokens += max(0, int(output_tokens))
    _register_flush_hook()
    return True


def record_xai_cost_from_payload(
    *,
    model: str,
    payload: dict[str, Any] | None,
    provider: str = "xai_grok",
    biller: str = "xai",
) -> bool:
    return accumulate_cost_event(
        provider=provider,
        biller=biller,
        billing_type="metered_api",
        model=model,
        cost_usd=xai_cost_usd_from_payload(payload),
    )


def record_supertone_cost_from_duration(
    *,
    model: str,
    duration_seconds: float,
    provider: str = "supertone",
    biller: str = "supertone",
) -> bool:
    return accumulate_cost_event(
        provider=provider,
        biller=biller,
        billing_type="credits",
        model=model,
        cost_usd=supertone_cost_usd_from_duration(duration_seconds),
    )


def _post_cost_event(payload: dict[str, Any]) -> None:
    api_url = _read_env("PAPERCLIP_API_URL")
    api_key = _read_env("PAPERCLIP_API_KEY")
    company_id = _read_env("PAPERCLIP_COMPANY_ID")
    request = urllib.request.Request(
        url=f"{api_url.rstrip('/')}/api/companies/{company_id}/cost-events",
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        data=json.dumps(payload).encode("utf-8"),
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        response.read()


def flush_pending_cost_events() -> None:
    if not _pending_cost_events:
        return
    if not cost_reporting_enabled():
        _pending_cost_events.clear()
        return

    agent_id = _read_env("PAPERCLIP_AGENT_ID")
    run_id = _read_env("PAPERCLIP_RUN_ID")
    issue_id = _resolve_linked_issue_id()
    occurred_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    pending = list(_pending_cost_events.values())
    _pending_cost_events.clear()

    for event in pending:
        cost_cents = _usd_to_cents(event.cost_usd)
        if cost_cents <= 0 and event.input_tokens <= 0 and event.cached_input_tokens <= 0 and event.output_tokens <= 0:
            continue
        body: dict[str, Any] = {
            "agentId": agent_id,
            "provider": event.provider,
            "biller": event.biller,
            "billingType": event.billing_type,
            "model": event.model,
            "inputTokens": event.input_tokens,
            "cachedInputTokens": event.cached_input_tokens,
            "outputTokens": event.output_tokens,
            "costCents": cost_cents,
            "occurredAt": occurred_at,
        }
        if run_id:
            body["heartbeatRunId"] = run_id
        if issue_id:
            body["issueId"] = issue_id
        try:
            _post_cost_event(body)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            _log(f"cost event POST failed {exc.code}: {detail[:400]}")
        except Exception as exc:  # pragma: no cover
            _log(f"cost event POST failed: {exc}")
