from pydantic import BaseModel # type: ignore

class PredictRequest(BaseModel):
    text: str | None = None
    context: str | None = None
