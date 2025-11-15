from fastapi import APIRouter, Request # type: ignore
from app.services.sync_worker import handle_platform_webhook # type: ignore

router = APIRouter()

@router.post("/platform")
async def platform_webhook(req: Request):
    payload = await req.json()
    # push into worker/queue
    await handle_platform_webhook(payload)
    return {"received": True}