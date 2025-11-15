from fastapi import APIRouter, UploadFile, File # type: ignore
from app.models.schemas import PredictRequest
from app.services.pipeline import run_pipeline

router = APIRouter(prefix="/api")

@router.post("/predict")
async def predict(req: PredictRequest):
    result = await run_pipeline(req)
    return {"result": result}

@router.post("/image")
async def predict_image(file: UploadFile = File(...)):
    content = await file.read()
    res = await run_pipeline({"image_bytes": content})
    return {"result": res}
