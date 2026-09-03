"""Async orchestration job state and execution."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from app.events.publisher import publish_event


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    PARTIAL = "partial"
    COMPLETED = "completed"
    FAILED = "failed"


class StageStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    UNAVAILABLE = "unavailable"
    FAILED = "failed"
    SKIPPED = "skipped"


class StageResult(BaseModel):
    name: str
    status: StageStatus = StageStatus.PENDING
    attempts: int = 0
    critical: bool = True
    result: dict[str, Any] | None = None
    error: str | None = None


class OrchestrationJob(BaseModel):
    job_id: UUID = Field(default_factory=uuid4)
    idempotency_key: str
    correlation_id: UUID = Field(default_factory=uuid4)
    decision_session_id: str
    status: JobStatus = JobStatus.QUEUED
    stages: tuple[StageResult, ...] = ()
    recommendation: dict[str, Any] | None = None
    error: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class OrchestrationService:
    stage_names = (
        "shipment", "decision_session", "maritime_state", "forecast",
        "vessel_intelligence", "port_compatibility", "congestion", "landed_cost",
        "timing", "contract", "risk", "optimization", "recommendation",
        "explanation", "copilot", "approval", "execution", "audit",
    )
    critical_stages = frozenset({"shipment", "decision_session", "maritime_state", "forecast", "optimization", "recommendation"})

    def __init__(self, *, stage_timeout_seconds: float = 30.0, max_attempts: int = 2) -> None:
        self._jobs: dict[str, OrchestrationJob] = {}
        self._tasks: dict[UUID, asyncio.Task[None]] = {}
        self.stage_timeout_seconds = stage_timeout_seconds
        self.max_attempts = max_attempts

    def create(self, *, decision_session_id: str, idempotency_key: str, correlation_id: UUID | None = None, stages: dict[str, dict[str, Any] | None] | None = None) -> OrchestrationJob:
        if idempotency_key in self._jobs:
            return self._jobs[idempotency_key]
        job = OrchestrationJob(
            idempotency_key=idempotency_key,
            correlation_id=correlation_id or uuid4(),
            decision_session_id=decision_session_id,
            stages=tuple(StageResult(name=name, critical=name in self.critical_stages) for name in self.stage_names),
        )
        self._jobs[idempotency_key] = job
        task = asyncio.create_task(self._run(job, stages or {}))
        self._tasks[job.job_id] = task
        task.add_done_callback(lambda _task: self._tasks.pop(job.job_id, None))
        return job

    def get(self, job_id: UUID) -> OrchestrationJob:
        for job in self._jobs.values():
            if job.job_id == job_id:
                return job
        raise KeyError("orchestration job not found")

    async def wait(self, job_id: UUID) -> OrchestrationJob:
        task = self._tasks.get(job_id)
        if task:
            await task
        return self.get(job_id)

    async def _run(self, job: OrchestrationJob, supplied: dict[str, dict[str, Any] | None]) -> None:
        job.status = JobStatus.RUNNING
        await publish_event(
            "orchestration.started",
            correlation_id=job.correlation_id,
            aggregate_id=str(job.job_id),
            payload={"decision_session_id": job.decision_session_id},
        )
        job.updated_at = datetime.now(UTC)
        stage_results = list(job.stages)
        for index, stage in enumerate(stage_results):
            value = supplied.get(stage.name)
            for attempt in range(1, self.max_attempts + 1):
                stage.status = StageStatus.RUNNING
                stage.attempts = attempt
                try:
                    await asyncio.wait_for(
                        self._execute_stage(value),
                        timeout=self.stage_timeout_seconds,
                    )
                except TimeoutError:
                    stage.status = StageStatus.FAILED
                    stage.error = "stage timed out"
                except ValueError as exc:
                    stage.status = StageStatus.FAILED
                    stage.error = str(exc)
                else:
                    if value is None:
                        stage.status = StageStatus.UNAVAILABLE
                        stage.error = "authoritative stage result unavailable"
                    elif value.get("error"):
                        stage.status = StageStatus.FAILED
                        stage.error = str(value["error"])
                    else:
                        stage.status = StageStatus.COMPLETED
                        stage.result = value
                if stage.status is StageStatus.COMPLETED:
                    break
                if not self._retryable(stage.error) or attempt == self.max_attempts:
                    break
            if stage.status in {StageStatus.UNAVAILABLE, StageStatus.FAILED} and stage.critical:
                job.status = JobStatus.FAILED
                job.error = f"critical stage {stage.status.value}: {stage.name}"
                for remaining in stage_results[index + 1:]:
                    remaining.status = StageStatus.SKIPPED
                job.stages = tuple(stage_results)
                break
            job.stages = tuple(stage_results)
            job.updated_at = datetime.now(UTC)
        else:
            job.status = (
                JobStatus.PARTIAL
                if any(s.status in {StageStatus.UNAVAILABLE, StageStatus.FAILED} for s in stage_results)
                else JobStatus.COMPLETED
            )
            recommendation = next((s.result for s in stage_results if s.name == "recommendation"), None)
            job.recommendation = recommendation
        job.updated_at = datetime.now(UTC)
        await publish_event(
            "orchestration.completed",
            correlation_id=job.correlation_id,
            aggregate_id=str(job.job_id),
            payload={"status": job.status.value, "error": job.error},
        )

    async def _execute_stage(self, value: dict[str, Any] | None) -> None:
        if value and value.get("delay_seconds"):
            await asyncio.sleep(float(value["delay_seconds"]))

    @staticmethod
    def _retryable(error: str | None) -> bool:
        return error is None or error == "authoritative stage result unavailable" or error.lower().startswith("transient")


orchestration_service = OrchestrationService()
