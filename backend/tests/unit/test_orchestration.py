import asyncio

from app.jobs.tasks import JobStatus, StageStatus, OrchestrationService


def _complete_inputs(service: OrchestrationService) -> dict[str, dict[str, object]]:
    return {name: {"source": name} for name in service.stage_names}


def test_orchestration_completes_and_is_idempotent() -> None:
    async def run() -> None:
        service = OrchestrationService()
        stages = _complete_inputs(service)
        first = service.create(decision_session_id="session-1", idempotency_key="key-1", stages=stages)
        second = service.create(decision_session_id="session-1", idempotency_key="key-1", stages={})
        assert second.job_id == first.job_id
        result = await service.wait(first.job_id)
        assert result.status is JobStatus.COMPLETED
        assert all(stage.status is StageStatus.COMPLETED for stage in result.stages)

    asyncio.run(run())


def test_critical_failure_stops_recommendation_finalization() -> None:
    async def run() -> None:
        service = OrchestrationService()
        stages = _complete_inputs(service)
        stages["forecast"] = {"error": "forecast service unavailable"}
        job = service.create(decision_session_id="session-1", idempotency_key="key-2", stages=stages)
        result = await service.wait(job.job_id)
        assert result.status is JobStatus.FAILED
        assert result.recommendation is None
        assert result.stages[-1].status is StageStatus.SKIPPED

    asyncio.run(run())


def test_noncritical_failure_produces_explicit_partial_state() -> None:
    async def run() -> None:
        service = OrchestrationService()
        stages = _complete_inputs(service)
        stages["copilot"] = None
        job = service.create(decision_session_id="session-1", idempotency_key="key-3", stages=stages)
        result = await service.wait(job.job_id)
        assert result.status is JobStatus.PARTIAL
        assert next(stage for stage in result.stages if stage.name == "copilot").status is StageStatus.UNAVAILABLE

    asyncio.run(run())


def test_transient_unavailable_stage_retries_with_bounded_attempts() -> None:
    async def run() -> None:
        service = OrchestrationService(max_attempts=3)
        stages = _complete_inputs(service)
        stages["copilot"] = None
        job = service.create(decision_session_id="session-1", idempotency_key="key-4", stages=stages)
        result = await service.wait(job.job_id)
        copilot = next(stage for stage in result.stages if stage.name == "copilot")
        assert result.status is JobStatus.PARTIAL
        assert copilot.attempts == 3
        assert copilot.status is StageStatus.UNAVAILABLE

    asyncio.run(run())


def test_stage_timeout_is_explicit_and_does_not_orphan_task() -> None:
    async def run() -> None:
        service = OrchestrationService(stage_timeout_seconds=0.001, max_attempts=1)
        stages = _complete_inputs(service)
        stages["copilot"] = {"delay_seconds": 0.01}
        job = service.create(decision_session_id="session-1", idempotency_key="key-5", stages=stages)
        result = await service.wait(job.job_id)
        copilot = next(stage for stage in result.stages if stage.name == "copilot")
        assert result.status is JobStatus.PARTIAL
        assert copilot.error == "stage timed out"
        assert job.job_id not in service._tasks

    asyncio.run(run())
