"""Compatibility import surface for source quality validation."""

from app.data.validation import ValidationIssue, validate_payload_model, validate_record

__all__ = ["ValidationIssue", "validate_payload_model", "validate_record"]
