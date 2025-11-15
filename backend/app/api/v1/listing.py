from typing import Optional

from fastapi import APIRouter, HTTPException, status # type: ignore
from pydantic import BaseModel # type: ignore

from app.services.listing_service import (
    create_listing,
    get_competitor_prices,
    list_listings,
    get_listing,
    update_listing,
    delete_listing,
    set_availability,
    adjust_price,
    adjust_all_dynamic,
)

router = APIRouter()

class ListingCreate(BaseModel):
    title: str
    description: str
    address: str
    price: float


class ListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    price: Optional[float] = None
    available: Optional[bool] = None
    metadata: Optional[dict] = None


class Availability(BaseModel):
    available: bool


class PriceAdjust(BaseModel):
    multiplier: Optional[float] = None
    delta: Optional[float] = None
    set_price: Optional[float] = None


class DynamicAdjust(BaseModel):
    rate: float = 1.0

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create(l: ListingCreate):
    try:
        new = await create_listing(l.dict())
        return {"id": new["id"], "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compare")
async def compare(address: str):
    return await get_competitor_prices(address)


@router.get("/")
async def list_all(available_only: bool = False):
    return await list_listings(available_only=available_only)


@router.get("/{listing_id}")
async def read(listing_id: str):
    item = await get_listing(listing_id)
    if not item:
        raise HTTPException(status_code=404, detail="Listing not found")
    return item


@router.put("/{listing_id}")
async def update(listing_id: str, upd: ListingUpdate):
    updated = await update_listing(listing_id, {k: v for k, v in upd.dict().items() if v is not None})
    if not updated:
        raise HTTPException(status_code=404, detail="Listing not found")
    return updated


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove(listing_id: str):
    ok = await delete_listing(listing_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Listing not found")
    return None


@router.post("/{listing_id}/availability")
async def availability(listing_id: str, body: Availability):
    updated = await set_availability(listing_id, body.available)
    if not updated:
        raise HTTPException(status_code=404, detail="Listing not found")
    return updated


@router.post("/{listing_id}/price")
async def price_adjust(listing_id: str, body: PriceAdjust):
    updated = await adjust_price(listing_id, multiplier=body.multiplier, delta=body.delta, set_price=body.set_price)
    if not updated:
        raise HTTPException(status_code=404, detail="Listing not found")
    return updated


@router.post("/dynamic")
async def dynamic_adjust(body: DynamicAdjust):
    updated = await adjust_all_dynamic(rate=body.rate)
    return {"updated": len(updated)}