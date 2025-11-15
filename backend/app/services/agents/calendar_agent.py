import asyncio
import logging
from typing import Optional, List, Dict, Any

from app.services.listing_service import list_listings, update_listing
from app.services.integrations_service import fetch_remote_availability

logger = logging.getLogger(__name__)


async def run_calendar_sync(listing_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Basic calendar sync agent.

    - If `listing_id` is provided, sync that listing only; otherwise sync all.
    - For each listing, this MVP fetches a mocked remote availability and
      updates the listing `available` flag accordingly.
    """
    results = []
    listings = []
    if listing_id:
        l = await update_listing(listing_id, {})  # read current state
        if l:
            listings = [l]
    else:
        listings = await list_listings()

    async def _sync_one(l: Dict[str, Any]):
        # In a real agent, fetch platform calendars or iCal feeds. Here we
        # simulate by asking integrations for a remote availability for any
        # recorded remote ids in metadata.
        meta = l.get("metadata", {})
        remote = meta.get("remote_ids", {})
        if not remote:
            return {"id": l["id"], "skipped": True}
        # pick first remote platform to check
        platform, remote_id = next(iter(remote.items()))
        remote_info = await fetch_remote_availability(platform, remote_id)
        # Update availability based on remote info
        updated = await update_listing(l["id"], {"available": bool(remote_info.get("available", True))})
        return {"id": l["id"], "platform": platform, "remote": remote_info, "updated": updated}

    tasks = [ _sync_one(l) for l in listings ]
    if tasks:
        results = await asyncio.gather(*tasks)
    return results
