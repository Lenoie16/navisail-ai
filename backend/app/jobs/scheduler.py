"""Compatibility facade for scheduling orchestration jobs."""

from app.jobs.tasks import orchestration_service

__all__ = ["orchestration_service"]
