"""Observed outcomes used for future model evaluation."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class OutcomeFeedback(BaseModel):
    feedback_id: UUID = Field(default_factory=uuid4)
    model_name: str
    model_version: str
    prediction_id: str
    predicted_value: float
    actual_value: float
    observed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    context: dict[str, Any] = Field(default_factory=dict)


class FeedbackService:
    def __init__(self) -> None:
        self._items: list[OutcomeFeedback] = []

    def record(self, item: OutcomeFeedback) -> OutcomeFeedback:
        self._items.append(item)
        return item

    def list(self, model_name: str | None = None) -> tuple[OutcomeFeedback, ...]:
        return tuple(item for item in self._items if model_name is None or item.model_name == model_name)


feedback_service = FeedbackService()
