"""Controlled execution workflow state machine."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from app.execution.approvals import ApprovalStatus
from pydantic import BaseModel, ConfigDict, Field


class ExecutionStatus(StrEnum):
    DRAFT = "draft"
    APPROVED = "approved"
    BOOKING_REQUESTED = "booking_requested"
    BOOKING_IN_PROGRESS = "booking_in_progress"
    BOOKED = "booked"
    VOYAGE_ACTIVE = "voyage_active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ExecutionRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    execution_id: UUID = Field(default_factory=uuid4)
    recommendation_id: str = Field(min_length=1)
    status: ExecutionStatus = ExecutionStatus.DRAFT
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_by: str = Field(min_length=1)
    approval_id: UUID | None = None


_TRANSITIONS = {
    ExecutionStatus.DRAFT: {ExecutionStatus.APPROVED, ExecutionStatus.CANCELLED},
    ExecutionStatus.APPROVED: {ExecutionStatus.BOOKING_REQUESTED, ExecutionStatus.CANCELLED},
    ExecutionStatus.BOOKING_REQUESTED: {
        ExecutionStatus.BOOKING_IN_PROGRESS,
        ExecutionStatus.CANCELLED,
    },
    ExecutionStatus.BOOKING_IN_PROGRESS: {ExecutionStatus.BOOKED, ExecutionStatus.CANCELLED},
    ExecutionStatus.BOOKED: {ExecutionStatus.VOYAGE_ACTIVE, ExecutionStatus.CANCELLED},
    ExecutionStatus.VOYAGE_ACTIVE: {ExecutionStatus.COMPLETED, ExecutionStatus.CANCELLED},
    ExecutionStatus.COMPLETED: set(),
    ExecutionStatus.CANCELLED: set(),
}


class ExecutionService:
    def __init__(self) -> None:
        self._records: dict[UUID, ExecutionRecord] = {}

    def create(self, recommendation_id: str, user: str) -> ExecutionRecord:
        record = ExecutionRecord(recommendation_id=recommendation_id, updated_by=user)
        self._records[record.execution_id] = record
        return record

    def transition(
        self,
        execution_id: UUID,
        target: ExecutionStatus,
        *,
        user: str,
        approval_status: ApprovalStatus | None = None,
        approval_id: UUID | None = None,
    ) -> ExecutionRecord:
        current = self._records[execution_id]
        if target is ExecutionStatus.APPROVED and approval_status is not ApprovalStatus.APPROVED:
            raise PermissionError("execution requires an approved recommendation")
        if target not in _TRANSITIONS[current.status]:
            raise ValueError(f"invalid transition from {current.status.value} to {target.value}")
        updated = current.model_copy(
            update={
                "status": target,
                "updated_by": user,
                "updated_at": datetime.now(UTC),
                "approval_id": approval_id or current.approval_id,
            }
        )
        self._records[execution_id] = updated
        return updated

    def get(self, execution_id: UUID) -> ExecutionRecord:
        return self._records[execution_id]


execution_service = ExecutionService()
