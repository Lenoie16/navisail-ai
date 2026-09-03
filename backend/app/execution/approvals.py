"""Human approval state machine."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class ApprovalStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    RETURNED = "returned_for_revision"
    EXPIRED = "expired"


class ApprovalDecision(BaseModel):
    model_config = ConfigDict(frozen=True)

    decision_id: UUID = Field(default_factory=uuid4)
    recommendation_id: str = Field(min_length=1)
    recommendation_version: str = Field(min_length=1)
    status: ApprovalStatus = ApprovalStatus.PENDING
    user: str = Field(min_length=1)
    role: str = Field(min_length=1)
    comment: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    decided_at: datetime | None = None
    expires_at: datetime | None = None


class ApprovalService:
    def __init__(self) -> None:
        self._decisions: dict[UUID, ApprovalDecision] = {}

    def create(
        self,
        recommendation_id: str,
        recommendation_version: str,
        user: str,
        role: str,
        *,
        expires_in: timedelta | None = None,
    ) -> ApprovalDecision:
        if role not in {"approver", "procurement_manager", "admin"}:
            raise PermissionError("role cannot create approvals")
        now = datetime.now(UTC)
        decision = ApprovalDecision(
            recommendation_id=recommendation_id,
            recommendation_version=recommendation_version,
            user=user,
            role=role,
            created_at=now,
            expires_at=now + expires_in if expires_in else None,
        )
        self._decisions[decision.decision_id] = decision
        return decision

    def decide(
        self,
        decision_id: UUID,
        *,
        user: str,
        role: str,
        status: ApprovalStatus,
        comment: str = "",
        now: datetime | None = None,
    ) -> ApprovalDecision:
        if role not in {"approver", "procurement_manager", "admin"}:
            raise PermissionError("role cannot decide approvals")
        current = self._decisions[decision_id]
        if current.status is not ApprovalStatus.PENDING:
            raise ValueError(f"approval is already {current.status.value}")
        moment = (now or datetime.now(UTC)).astimezone(UTC)
        if current.expires_at and moment >= current.expires_at:
            updated = current.model_copy(update={"status": ApprovalStatus.EXPIRED})
            self._decisions[decision_id] = updated
            raise ValueError("approval has expired")
        if status not in {
            ApprovalStatus.APPROVED,
            ApprovalStatus.REJECTED,
            ApprovalStatus.RETURNED,
        }:
            raise ValueError("decision must approve, reject, or return for revision")
        updated = current.model_copy(
            update={
                "status": status,
                "user": user,
                "role": role,
                "comment": comment,
                "decided_at": moment,
            }
        )
        self._decisions[decision_id] = updated
        return updated

    def get(self, decision_id: UUID) -> ApprovalDecision:
        return self._decisions[decision_id]


approval_service = ApprovalService()
