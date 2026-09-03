"""Freight forecast and evaluation endpoints."""

from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.forecasting.inference.service import (
    EvaluationMetrics,
    ForecastModel,
    ForecastResult,
    FreightObservation,
    forecast_engine,
)

router = APIRouter(prefix="/forecasts", tags=["forecasts"])


class ForecastRequest(BaseModel):
    observations: list[FreightObservation]
    route: str = Field(min_length=1)
    vessel_class: str = Field(min_length=1)
    horizon_days: int
    model: ForecastModel = "auto"
    as_of: datetime | None = None


@router.post("", response_model=ForecastResult)
async def create_forecast(request: ForecastRequest) -> ForecastResult:
    return forecast_engine.forecast(
        request.observations,
        route=request.route,
        vessel_class=request.vessel_class,
        horizon_days=request.horizon_days,
        model=request.model,
        as_of=request.as_of,
    )


class BacktestRequest(BaseModel):
    observations: list[FreightObservation]
    horizon_days: int


class CalibrationRequest(BacktestRequest):
    model: ForecastModel = "naive"


@router.post("/backtest", response_model=dict[str, EvaluationMetrics])
async def backtest_forecast(request: BacktestRequest) -> dict[str, EvaluationMetrics]:
    return forecast_engine.backtest(
        request.observations, horizon_days=request.horizon_days
    )


@router.post("/calibration", response_model=dict[str, float | int | str | None])
async def calibrate_forecast(
    request: CalibrationRequest,
) -> dict[str, float | int | str | None]:
    return forecast_engine.calibration(
        request.observations,
        horizon_days=request.horizon_days,
        model=request.model,
    )
