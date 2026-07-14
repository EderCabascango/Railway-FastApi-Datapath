from pydantic import BaseModel

class PredictionRequest(BaseModel):
    inversion: float

class PredictionResponse(BaseModel):
    input: dict
    prediction: float