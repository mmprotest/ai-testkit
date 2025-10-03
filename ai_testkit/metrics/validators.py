"""Validation helpers without external dependencies."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict


@dataclass(slots=True)
class ValidationResult:
    name: str
    passed: bool
    details: str | None = None


def json_equals(candidate: str, expected: Dict[str, Any]) -> ValidationResult:
    try:
        data = json.loads(candidate)
    except json.JSONDecodeError as exc:
        return ValidationResult("json_equals", False, f"Invalid JSON: {exc}")
    passed = data == expected
    return ValidationResult("json_equals", passed, None if passed else "JSON mismatch")


def validate_json_schema(instance: Any, schema: Dict[str, Any]) -> ValidationResult:
    # Minimal schema validation: check required keys exist.
    required = schema.get("required", []) if isinstance(schema, dict) else []
    missing = [key for key in required if key not in instance]
    if missing:
        return ValidationResult("json_schema", False, f"Missing keys: {', '.join(missing)}")
    return ValidationResult("json_schema", True)


def validate_pydantic(instance: Any, model: Any) -> ValidationResult:
    # Placeholder implementation.
    return ValidationResult("pydantic", True)


def validate_function_call(instance: Dict[str, Any], schema: Dict[str, Any]) -> ValidationResult:
    return validate_json_schema(instance, schema)


__all__ = [
    "ValidationResult",
    "json_equals",
    "validate_json_schema",
    "validate_pydantic",
    "validate_function_call",
]
