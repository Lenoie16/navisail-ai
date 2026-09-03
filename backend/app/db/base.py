"""ORM metadata registry."""

from app.models.all import ModelBase

Base = ModelBase

# Importing models here ensures Alembic and create_all see every entity.
from app.models.all import (  # noqa: E402,F401
    Approval,
    AuditRecord,
    Berth,
    Commodity,
    Contract,
    DecisionSession,
    Execution,
    Inventory,
    MaritimeStateSnapshot,
    Origin,
    Plant,
    Port,
    Recommendation,
    Route,
    Shipment,
    Vessel,
    VesselPosition,
    Voyage,
)
