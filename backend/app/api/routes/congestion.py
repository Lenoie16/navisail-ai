"""Congestion prediction endpoints."""

from fastapi import APIRouter

from app.congestion.service import (
	CongestionPrediction,
	PortCongestionInput,
	congestion_engine,
)

router = APIRouter(prefix="/congestion", tags=["congestion"])


@router.post("/predict", response_model=CongestionPrediction)
async def predict_congestion(request: PortCongestionInput) -> CongestionPrediction:
	return congestion_engine.predict(request)


@router.post("/predict-many", response_model=list[CongestionPrediction])
async def predict_congestion_many(
	request: list[PortCongestionInput],
) -> list[CongestionPrediction]:
	return congestion_engine.predict_many(request)
