import os
import joblib
import pandas as pd
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from .database import engine, Base, get_db
from .models import InputData, PredictionOutput
from .schemas import PredictionRequest, PredictionResponse

# Crear las tablas automáticamente si no existen en la BD
Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de Predicción de Ventas MLOps")

# Cargar el modelo entrenado
MODEL_PATH = "modelos/modelo_ventas.pkl"
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
else:
    raise FileNotFoundError(f"No se encontró el archivo de modelo en {MODEL_PATH}")

# 1. Endpoint de validación de conexión (Health Check)
@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Ejecuta consulta de prueba
        db.execute(text("SELECT 1"))
        return {
            "status": "success",
            "message": "Connected to the database successfully."
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Database connection failed: {str(e)}"
        )

# 2. Endpoint de predicción con guardado persistente
@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest, db: Session = Depends(get_db)):
    try:
        inversion_val = request.inversion
        
        # Guardar el Input en la base de datos
        db_input = InputData(inversion=inversion_val)
        db.add(db_input)
        db.commit()
        db.refresh(db_input)

        # Preparar datos para el modelo e inferir predicción
        input_df = pd.DataFrame([[inversion_val]], columns=['inversion_publicidad'])
        prediccion_val = float(model.predict(input_df)[0])

        # Guardar la Predicción relacionada en la base de datos
        db_prediction = PredictionOutput(input_id=db_input.id, ventas_estimadas=prediccion_val)
        db.add(db_prediction)
        db.commit()

        # Retornar respuesta bajo el formato solicitado
        return {
            "input": {
                "inversion": inversion_val
            },
            "prediction": round(prediccion_val, 2)
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Inference/Database Error: {str(e)}")