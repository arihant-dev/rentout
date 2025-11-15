"""n8n integration helpers.

This module provides small, safe helpers to trigger n8n webhooks and call
the n8n REST API. The implementations are intentionally lightweight — they
use `httpx` with timeouts and return structured results. Replace or extend
these adapters with auth flows and payload mappings as needed.
"""
from typing import Any, Dict, Optional
import logging
import os
import httpx

from app.config import settings

logger = logging.getLogger(__name__)


async def send_webhook(event: str, payload: Dict[str, Any], *, timeout: float = 10.0) -> Dict[str, Any]:
    """Send a payload to the configured n8n webhook URL.

    The `settings.N8N_WEBHOOK_URL` is treated as a base URL and `event` is
    appended as path component. Example: base `http://n8n:5678/webhook` +
    event `listing-created` -> `http://n8n:5678/webhook/listing-created`.

    Returns a dict with `status_code` and either `json` or `text` and
    `ok` boolean.
    """
    base = settings.N8N_WEBHOOK_URL.rstrip("/")
    url = f"{base}/{event}"
    headers = {"Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(url, json=payload, headers=headers)
            try:
                data = r.json()
            except Exception:
                data = r.text
            return {"ok": r.is_success, "status_code": r.status_code, "result": data}
    except Exception as e:
        logger.exception("Failed to send n8n webhook to %s: %s", url, e)
        return {"ok": False, "status_code": None, "error": str(e)}


async def trigger_workflow_via_api(workflow_id: str, payload: Optional[Dict[str, Any]] = None, *, timeout: float = 15.0) -> Dict[str, Any]:
    """Trigger a workflow via n8n REST API.

    Behavior depends on n8n configuration. This function attempts to use a
    common n8n endpoint pattern. If your n8n instance exposes a different
    API, update the endpoint accordingly.

    - If `settings.N8N_API_KEY` is set, it will be sent as a Bearer token in
      the `Authorization` header.
    - The default endpoint used is: `{N8N_API_URL}/workflows/{workflow_id}/executions`

    Returns a dict summarizing the API call result.
    """
    api_base = settings.N8N_API_URL.rstrip("/")
    endpoint = f"{api_base}/workflows/{workflow_id}/executions"
    headers = {"Content-Type": "application/json"}
    if settings.N8N_API_KEY:
        headers["Authorization"] = f"Bearer {settings.N8N_API_KEY}"

    body = payload or {}

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(endpoint, json={"nodes": [], "workflowData": body}, headers=headers)
            try:
                data = r.json()
            except Exception:
                data = r.text
            return {"ok": r.is_success, "status_code": r.status_code, "result": data}
    except Exception as e:
        logger.exception("Failed to trigger n8n workflow %s: %s", workflow_id, e)
        return {"ok": False, "status_code": None, "error": str(e)}


async def list_workflows_via_api(*, timeout: float = 10.0) -> Dict[str, Any]:
    """List workflows from n8n REST API (if available).

    Returns a dict with `ok`, `status_code` and `result`.
    """
    api_base = settings.N8N_API_URL.rstrip("/")
    endpoint = f"{api_base}/workflows"
    headers = {}
    if settings.N8N_API_KEY:
        headers["Authorization"] = f"Bearer {settings.N8N_API_KEY}"

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.get(endpoint, headers=headers)
            try:
                data = r.json()
            except Exception:
                data = r.text
            return {"ok": r.is_success, "status_code": r.status_code, "result": data}
    except Exception as e:
        logger.exception("Failed to list n8n workflows: %s", e)
        return {"ok": False, "status_code": None, "error": str(e)}
