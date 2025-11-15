import logging
from typing import Dict, Any, List, Optional

from app.services.n8n_service import send_webhook
from app.services.listing_service import get_listing

logger = logging.getLogger(__name__)


async def schedule_cleaning(listing_id: str, when: str, cleaner_id: Optional[str] = None) -> Dict[str, Any]:
    """Schedule a cleaning task via n8n webhook.

    - `when` is an ISO timestamp or simple description.
    - Returns webhook result.
    """
    l = await get_listing(listing_id)
    payload = {"listing": l, "when": when, "cleaner_id": cleaner_id}
    try:
        res = await send_webhook("cleaning-schedule", payload)
        return {"ok": True, "result": res}
    except Exception:
        logger.exception("Failed to schedule cleaning for %s", listing_id)
        return {"ok": False}


async def run_ops_checks() -> List[Dict[str, Any]]:
    """Run a quick ops pass — placeholder that could check overdue tasks, etc."""
    # In a full implementation, fetch tasks, check statuses, escalate if overdue
    logger.info("Running ops checks (placeholder)")
    return [{"status": "ok"}]
