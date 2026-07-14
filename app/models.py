from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from .database import Base

class InputData(Base):
    __tablename__ = "inputs"

    id = Column(Integer, primary_key=True, index=True)
    inversion = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class PredictionOutput(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    input_id = Column(Integer, ForeignKey("inputs.id"), nullable=False)
    ventas_estimadas = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())