import logging
import re
from typing import Dict, Any

from app.services.llm_service import run_llm
from app.services.n8n_service import send_webhook

logger = logging.getLogger(__name__)


async def handle_incoming_message(listing_id: str, message: str, guest: Dict[str, Any]) -> Dict[str, Any]:
    """Basic guest communication agent.

    - Uses the configured LLM provider to generate a friendly reply.
    - If message contains urgent keywords, escalate via n8n webhook.
    """
    # Simple urgent keyword detection
    urgent = bool(re.search(r"(urgent|help|broken|asap|emergency)", message, re.I))
    if urgent:
        # fire an escalation webhook (non-blocking will be handled by caller)
        try:
            await send_webhook("ops-escalation", {"listing_id": listing_id, "message": message, "guest": guest})
        except Exception:
            logger.exception("Failed to send escalation webhook")

    # Use LLM to craft a human-friendly reply
    prompt = (
        "You are a friendly property manager assistant. Reply concisely to the guest: '"
        + message
        + "' Provide helpful next steps and ask clarifying questions if needed."
    )
    try:
        reply = await run_llm(prompt)
    except Exception:
        logger.exception("LLM failed; falling back to template reply")
        reply = "Thanks for your message — we've received it and will get back to you shortly."

    return {"reply": reply, "escalated": urgent}
