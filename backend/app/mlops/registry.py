"""In-process model registry with explicit, guarded lifecycle promotion."""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class ModelLifecycle(StrEnum):
    DEVELOPMENT = "development"
    CANDIDATE = "candidate"
    APPROVED = "approved"
    ACTIVE = "active"
    RETIRED = "retired"


class ModelRecord(BaseModel):
    model_name: str
    version: str
    training_date: datetime
    training_window: str
    features: tuple[str, ...] = ()
    hyperparameters: dict[str, Any] = Field(default_factory=dict)
    metrics: dict[str, float] = Field(default_factory=dict)
    status: ModelLifecycle = ModelLifecycle.DEVELOPMENT
    artifact_location: str
    approval_status: str = "pending"
    degraded: bool = False


class ModelRegistry:
    def __init__(self) -> None:
        self._models: dict[tuple[str, str], ModelRecord] = {}

    def register(self, model: ModelRecord) -> ModelRecord:
        key = (model.model_name, model.version)
        if key in self._models:
            raise ValueError("model version already exists")
        self._models[key] = model
        return model

    def list(self, model_name: str | None = None) -> tuple[ModelRecord, ...]:
        return tuple(model for model in self._models.values() if model_name is None or model.model_name == model_name)

    def get(self, model_name: str, version: str) -> ModelRecord:
        try:
            return self._models[(model_name, version)]
        except KeyError as exc:
            raise KeyError("model version not found") from exc

    def promote(self, model_name: str, version: str, target: ModelLifecycle) -> ModelRecord:
        model = self.get(model_name, version)
        allowed = {
            ModelLifecycle.DEVELOPMENT: {ModelLifecycle.CANDIDATE},
            ModelLifecycle.CANDIDATE: {ModelLifecycle.APPROVED},
            ModelLifecycle.APPROVED: {ModelLifecycle.ACTIVE},
            ModelLifecycle.ACTIVE: {ModelLifecycle.RETIRED},
            ModelLifecycle.RETIRED: set(),
        }
        if target not in allowed[model.status]:
            raise ValueError(f"invalid lifecycle transition: {model.status} -> {target}")
        if target is ModelLifecycle.APPROVED and model.approval_status != "approved":
            raise PermissionError("model approval is required before promotion")
        if target is ModelLifecycle.ACTIVE and model.degraded:
            raise ValueError("degraded models cannot become active")
        if target is ModelLifecycle.ACTIVE:
            for other in self._models.values():
                if other.model_name == model_name and other.status is ModelLifecycle.ACTIVE:
                    other.status = ModelLifecycle.RETIRED
        model.status = target
        return model


model_registry = ModelRegistry()
