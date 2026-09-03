from datetime import timedelta
from uuid import uuid4

import pytest
from app.audit.service import AuditService
from app.audit.trail import record_transition
from app.execution.approvals import ApprovalService, ApprovalStatus
from app.execution.workflow import ExecutionService, ExecutionStatus


def test_unauthorized_and_valid_approval() -> None:
    approvals = ApprovalService()
    with pytest.raises(PermissionError):
        approvals.create("rec-1", "v1", "viewer", "viewer")

    pending = approvals.create("rec-1", "v1", "alice", "approver")
    approved = approvals.decide(
        pending.decision_id,
        user="alice",
        role="approver",
        status=ApprovalStatus.APPROVED,
        comment="Reviewed.",
    )
    assert approved.status is ApprovalStatus.APPROVED
    assert approved.comment == "Reviewed."


def test_return_reject_and_expiry_are_terminal() -> None:
    approvals = ApprovalService()
    returned = approvals.create("rec-1", "v1", "alice", "approver")
    result = approvals.decide(
        returned.decision_id,
        user="alice",
        role="approver",
        status=ApprovalStatus.RETURNED,
    )
    assert result.status is ApprovalStatus.RETURNED
    with pytest.raises(ValueError):
        approvals.decide(
            returned.decision_id,
            user="alice",
            role="approver",
            status=ApprovalStatus.APPROVED,
        )

    expired = approvals.create(
        "rec-2", "v1", "alice", "approver", expires_in=timedelta(hours=1)
    )
    with pytest.raises(ValueError, match="expired"):
        approvals.decide(
            expired.decision_id,
            user="alice",
            role="approver",
            status=ApprovalStatus.APPROVED,
            now=expired.expires_at + timedelta(seconds=1),
        )


def test_execution_requires_approval_and_records_transition_audit() -> None:
    executions = ExecutionService()
    record = executions.create("rec-1", "alice")
    with pytest.raises(PermissionError):
        executions.transition(
            record.execution_id,
            ExecutionStatus.APPROVED,
            user="alice",
        )
    approved = executions.transition(
        record.execution_id,
        ExecutionStatus.APPROVED,
        user="manager",
        approval_status=ApprovalStatus.APPROVED,
        approval_id=uuid4(),
    )
    assert approved.status is ExecutionStatus.APPROVED
    with pytest.raises(ValueError):
        executions.transition(
            record.execution_id,
            ExecutionStatus.COMPLETED,
            user="manager",
        )

    audit = AuditService()
    event = record_transition(
        actor="manager",
        entity_type="execution",
        entity_id=str(record.execution_id),
        action="transition",
        details=approved.model_dump(mode="json"),
    )
    audit.record(event)
    assert audit.for_entity("execution", str(record.execution_id)) == (event,)
