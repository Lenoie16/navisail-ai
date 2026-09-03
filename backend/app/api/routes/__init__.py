"""Route registry for the public API."""

from app.api.routes.berths import router as berths_router
from app.api.routes.charter import router as charter_router
from app.api.routes.compatibility import router as compatibility_router
from app.api.routes.congestion import router as congestion_router
from app.api.routes.copilot import router as copilot_router
from app.api.routes.data_health import router as data_health_router
from app.api.routes.datadocked import router as datadocked_router
from app.api.routes.digital_twin import router as digital_twin_router
from app.api.routes.execution import router as execution_router
from app.api.routes.events import router as events_router
from app.api.routes.explainability import router as explainability_router
from app.api.routes.forecasts import router as forecasts_router
from app.api.routes.health import router as health_router
from app.api.routes.landed_cost import router as landed_cost_router
from app.api.routes.maritime_state import router as maritime_state_router
from app.api.routes.mlops import router as mlops_router
from app.api.routes.optimization import router as optimization_router
from app.api.routes.orchestration import router as orchestration_router
from app.api.routes.performance import router as performance_router
from app.api.routes.plants import router as plants_router
from app.api.routes.ports import router as ports_router
from app.api.routes.recommendations import router as recommendations_router
from app.api.routes.risk import router as risk_router
from app.api.routes.shipments import router as shipments_router
from app.api.routes.supply import router as supply_router
from app.api.routes.vessels import router as vessels_router

routers = (
    health_router,
    landed_cost_router,
    data_health_router,
    datadocked_router,
    digital_twin_router,
    explainability_router,
    execution_router,
    events_router,
    forecasts_router,
    maritime_state_router,
    mlops_router,
    optimization_router,
    orchestration_router,
    performance_router,
    shipments_router,
    supply_router,
    vessels_router,
    ports_router,
    berths_router,
    charter_router,
    compatibility_router,
    copilot_router,
    congestion_router,
    plants_router,
    risk_router,
    recommendations_router,
)
