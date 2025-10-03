"""Schema validation helpers."""
from __future__ import annotations

from typing import Any

from jsonschema import Draft7Validator


def validate_json_schema(instance: Any, schema: dict[str, Any]) -> list[str]:
    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)
    return [error.message for error in errors]
