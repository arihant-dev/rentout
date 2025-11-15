from fastapi import FastAPI # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from app.api.v1 import listing, webhook, ai_proxy
from app.routes.predict import router as predict_router

app = FastAPI(title="Unicorn AI Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:3000",
        "http://127.0.0.1",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(predict_router)


app.include_router(listing.router, prefix="/api/v1/listings")
app.include_router(webhook.router, prefix="/api/v1/webhooks")
app.include_router(ai_proxy.router, prefix="/api/v1/ai")

@app.get("/health")
def health():
    return {"status": "ok"}
