import asyncio
async def handle_platform_webhook(payload: dict):
    # quick worker example: lock calendar, update DB, call n8n workflow via HTTP
    # For demo: just print
    print("webhook payload", payload)
    # TODO: push to Celery for heavy tasks
    await asyncio.sleep(0.01)
    return True