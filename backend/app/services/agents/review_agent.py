import logging
from typing import Dict, Any

from app.services.llm_service import run_llm
from app.services.n8n_service import send_webhook

logger = logging.getLogger(__name__)


async def send_review_request(listing_id: str, guest: Dict[str, Any]) -> Dict[str, Any]:
    """Generate and send a review-request message for a guest.

    - Uses LLM to craft the message and sends it via n8n webhook for delivery.
    - Returns the webhook result (or error summary).
    """
    prompt = (
        "Write a short, friendly message asking the guest to leave a review for their recent stay. "
        "Keep it under 40 words and include a thank you."
    )
    try:
        message = await run_llm(prompt)
    except Exception:
        logger.exception("LLM failure generating review message")
        message = "Thanks for staying with us — we hope you enjoyed it! If you have a moment, please leave a review."

    payload = {"listing_id": listing_id, "guest": guest, "message": message}
    try:
        res = await send_webhook("send-review-message", payload)
        return {"ok": True, "result": res}
    except Exception:
        logger.exception("Failed to send review message via n8n")
        return {"ok": False}
