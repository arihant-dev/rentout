import os
import asyncio
import logging
from typing import Any, Dict, List, Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


async def _post_to_airbnb(listing: Dict[str, Any]) -> Dict[str, Any]:
    """Mock adapter for Airbnb. Replace with real API integration."""
    api_key = os.getenv("AIRBNB_API_KEY")
    if not api_key:
        logger.debug("Airbnb API key missing; skipping")
        return {"platform": "airbnb", "status": "skipped", "reason": "no_api_key"}

    # Example: do a POST to Airbnb's hypothetical create endpoint.
    # Real implementation requires OAuth and specific payloads.
    await asyncio.sleep(0.1)
    return {"platform": "airbnb", "status": "created", "remote_id": f"airbnb-{listing.get('id')}"}


async def _post_to_booking(listing: Dict[str, Any]) -> Dict[str, Any]:
    """Mock adapter for Booking.com."""
    api_key = os.getenv("BOOKING_API_KEY")
    if not api_key:
        logger.debug("Booking API key missing; skipping")
        return {"platform": "booking", "status": "skipped", "reason": "no_api_key"}

    await asyncio.sleep(0.1)
    return {"platform": "booking", "status": "created", "remote_id": f"booking-{listing.get('id')}"}


async def _post_to_vrbo(listing: Dict[str, Any]) -> Dict[str, Any]:
    """Mock adapter for Vrbo."""
    api_key = os.getenv("VRBO_API_KEY")
    if not api_key:
        logger.debug("Vrbo API key missing; skipping")
        return {"platform": "vrbo", "status": "skipped", "reason": "no_api_key"}

    await asyncio.sleep(0.1)
    return {"platform": "vrbo", "status": "created", "remote_id": f"vrbo-{listing.get('id')}"}


_ADAPTERS = {
    "airbnb": _post_to_airbnb,
    "booking": _post_to_booking,
    "vrbo": _post_to_vrbo,
}


async def publish_listing_cross_platform(listing: Dict[str, Any], platforms: Optional[List[str]] = None, timeout: int = 30) -> List[Dict[str, Any]]:
    """Publish a `listing` to multiple third-party platforms concurrently.

    - `listing`: dict containing listing data (id, title, price, etc.)
    - `platforms`: list of platform keys (e.g., ["airbnb","booking"]). If None, publishes to all adapters.
    - Returns a list of results per platform.

    NOTE: These are mocked adapters. Replace adapter implementations with real HTTP/API logic.
    """
    platforms = platforms or list(_ADAPTERS.keys())

    async def _wrap_call(fn, payload):
        try:
            return await asyncio.wait_for(fn(payload), timeout=timeout)
        except asyncio.TimeoutError:
            logger.exception("Timeout while contacting platform")
            return {"platform": getattr(fn, "__name__", "unknown"), "status": "error", "reason": "timeout"}
        except Exception as e:
            logger.exception("Error while contacting platform: %s", e)
            return {"platform": getattr(fn, "__name__", "unknown"), "status": "error", "reason": str(e)}

    tasks = []
    for p in platforms:
        adapter = _ADAPTERS.get(p)
        if not adapter:
            results = {"platform": p, "status": "unknown_platform"}
            tasks.append(asyncio.sleep(0, results))
        else:
            tasks.append(_wrap_call(adapter, listing))

    results = await asyncio.gather(*tasks)
    return results


async def remove_listing_cross_platform(remote_ids: Dict[str, str], platforms: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Remove listings on third-party platforms.

    - `remote_ids`: mapping platform -> remote_id returned at publish time.
    - `platforms`: optional list to restrict removals.
    """
    platforms = platforms or list(remote_ids.keys())

    async def _mock_delete(platform: str, remote_id: str):
        await asyncio.sleep(0.05)
        return {"platform": platform, "status": "deleted", "remote_id": remote_id}

    tasks = []
    for p in platforms:
        rid = remote_ids.get(p)
        if not rid:
            tasks.append(asyncio.sleep(0, {"platform": p, "status": "not_found"}))
        else:
            tasks.append(_mock_delete(p, rid))

    return await asyncio.gather(*tasks)


async def fetch_remote_availability(platform: str, remote_id: str) -> Dict[str, Any]:
    """Fetch availability/pricing from a remote platform for a given remote_id.

    This is a convenience function for cross-checking competitor data.
    """
    # Placeholder implementation — real code will call platform APIs
    await asyncio.sleep(0.05)
    return {"platform": platform, "remote_id": remote_id, "available": True, "price": 100}
