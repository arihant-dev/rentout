import asyncio
import logging
from typing import Optional, Dict, Any, List

from app.services.listing_service import get_listing, list_listings, update_listing
from app.services.integrations_service import get_competitor_prices

logger = logging.getLogger(__name__)


def _compute_suggested_price(current_price: float, competitors: List[Dict[str, Any]], constraints: Dict[str, Any]) -> float:
    """Simple rule-based pricing:
    - If competitor data available, set price to min_competitor - 1
    - Enforce min_price/max_price constraints
    - Otherwise return current price
    """
    if competitors:
        prices = [c.get("price", current_price) for c in competitors]
        suggested = min(prices) - 1.0
    else:
        suggested = current_price

    # apply constraints
    min_p = constraints.get("min_price") if constraints else None
    max_p = constraints.get("max_price") if constraints else None
    if min_p is not None:
        suggested = max(suggested, float(min_p))
    if max_p is not None:
        suggested = min(suggested, float(max_p))

    # avoid negative
    return round(max(0.0, suggested), 2)


async def run_pricing_for_listing(listing_id: str) -> Optional[Dict[str, Any]]:
    """Run pricing logic for a single listing and persist suggestion.

    Returns the updated listing dict or None if listing not found.
    """
    l = await get_listing(listing_id)
    if not l:
        return None
    current = float(l.get("price", 0.0))
    # fetch competitor prices (mock)
    try:
        comp = await get_competitor_prices(l.get("address", ""))
        competitors = comp.get("competitors", [])
    except Exception:
        logger.exception("Failed to fetch competitor prices for %s", listing_id)
        competitors = []

    constraints = l.get("constraints", {})
    suggested = _compute_suggested_price(current, competitors, constraints)

    # persist suggestion in listing metadata and update price
    updates = {"price": suggested, "metadata": {**l.get("metadata", {}), "suggested_price": suggested}}
    updated = await update_listing(listing_id, updates)
    return updated


async def run_pricing_all() -> List[Dict[str, Any]]:
    listings = await list_listings(available_only=False)
    tasks = [ run_pricing_for_listing(l["id"]) for l in listings ]
    return await asyncio.gather(*tasks)
