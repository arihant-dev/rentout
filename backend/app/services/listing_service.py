import os
import json
import uuid
import threading
import asyncio
from typing import Any, Dict, List, Optional
import logging

from app.services.n8n_service import send_webhook

logger = logging.getLogger(__name__)

# File-backed listings storage (no DB). Uses atomic replace and a module-level lock
DATA_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "listings.json")
)

_lock = threading.Lock()


def _read_file_sync() -> List[Dict[str, Any]]:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return []


def _write_file_sync(data: List[Dict[str, Any]]) -> None:
    dirpath = os.path.dirname(DATA_FILE)
    os.makedirs(dirpath, exist_ok=True)
    tmp = DATA_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_FILE)


async def _read_listings() -> List[Dict[str, Any]]:
    return await asyncio.to_thread(_read_file_sync)


async def _write_listings(data: List[Dict[str, Any]]) -> None:
    await asyncio.to_thread(_write_file_sync, data)


def _find_index(listings: List[Dict[str, Any]], listing_id: str) -> int:
    for i, l in enumerate(listings):
        if str(l.get("id")) == str(listing_id):
            return i
    return -1


async def create_listing(payload: Dict[str, Any]) -> Dict[str, Any]:
    with _lock:
        listings = await _read_listings()
        new = {"id": str(uuid.uuid4()), "available": True, **payload}
        # Ensure price is numeric if present
        if "price" in new:
            try:
                new["price"] = float(new["price"])
            except Exception:
                new["price"] = 0.0
        listings.append(new)
        await _write_listings(listings)
        # Fire-and-forget an n8n webhook for new listings. We schedule this
        # after the file write so the listing exists even if the webhook fails.
        async def _fire_webhook(l):
            try:
                res = await send_webhook("listing-created", l)
                logger.info("n8n webhook result: %s", res)
            except Exception:
                logger.exception("n8n webhook failed for listing %s", l.get("id"))

        try:
            asyncio.create_task(_fire_webhook(new))
        except Exception:
            logger.exception("Failed to schedule n8n webhook task for listing %s", new.get("id"))

        return new


async def get_listing(listing_id: str) -> Optional[Dict[str, Any]]:
    listings = await _read_listings()
    idx = _find_index(listings, listing_id)
    return listings[idx] if idx >= 0 else None


async def list_listings(available_only: bool = False) -> List[Dict[str, Any]]:
    listings = await _read_listings()
    if available_only:
        return [l for l in listings if l.get("available", True)]
    return listings


async def update_listing(listing_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    with _lock:
        listings = await _read_listings()
        idx = _find_index(listings, listing_id)
        if idx < 0:
            return None
        listings[idx].update(updates)
        # normalize price if updated
        if "price" in updates:
            try:
                listings[idx]["price"] = float(listings[idx]["price"])
            except Exception:
                listings[idx]["price"] = 0.0
        await _write_listings(listings)
        return listings[idx]


async def delete_listing(listing_id: str) -> bool:
    with _lock:
        listings = await _read_listings()
        idx = _find_index(listings, listing_id)
        if idx < 0:
            return False
        listings.pop(idx)
        await _write_listings(listings)
        return True


async def set_availability(listing_id: str, available: bool) -> Optional[Dict[str, Any]]:
    return await update_listing(listing_id, {"available": bool(available)})


async def adjust_price(listing_id: str, *, multiplier: Optional[float] = None, delta: Optional[float] = None, set_price: Optional[float] = None) -> Optional[Dict[str, Any]]:
    """Adjust price for a single listing. Provide one of multiplier, delta or set_price.

    - multiplier: multiply current price by value (e.g., 1.05 for +5%)
    - delta: add (or subtract) value to current price
    - set_price: set absolute price
    """
    listings = await _read_listings()
    idx = _find_index(listings, listing_id)
    if idx < 0:
        return None
    current = float(listings[idx].get("price", 0.0))
    new_price = current
    if set_price is not None:
        new_price = float(set_price)
    elif multiplier is not None:
        new_price = current * float(multiplier)
    elif delta is not None:
        new_price = current + float(delta)
    listings[idx]["price"] = round(new_price, 2)
    await _write_listings(listings)
    return listings[idx]


async def adjust_all_dynamic(rate: float = 1.0) -> List[Dict[str, Any]]:
    """Apply a simple multiplier to all available listings' prices.

    This is a placeholder for more sophisticated dynamic pricing logic.
    """
    with _lock:
        listings = await _read_listings()
        for l in listings:
            if l.get("available", True):
                try:
                    l["price"] = round(float(l.get("price", 0.0)) * rate, 2)
                except Exception:
                    l["price"] = 0.0
        await _write_listings(listings)
        return listings


async def get_competitor_prices(address: str) -> Dict[str, Any]:
    # mock competitor scraping; in prod you'd call APIs or scrape
    return {
        "address": address,
        "competitors": [
            {"platform": "Airbnb", "price": 120},
            {"platform": "Booking.com", "price": 110},
            {"platform": "Vrbo", "price": 125},
        ],
    }
