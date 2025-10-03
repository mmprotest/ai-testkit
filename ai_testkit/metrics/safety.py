"""Safety checks."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable


@dataclass(slots=True)
class SafetyResult:
    policy: str
    passed: bool
    details: str | None = None


TOXIC_WORDS = {"hate", "kill", "violence"}
PII_PATTERNS = {
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "phone": re.compile(r"\b\d{3}[- ]?\d{3}[- ]?\d{4}\b"),
}


def check_no_toxicity(text: str) -> SafetyResult:
    lower = text.lower()
    if any(word in lower for word in TOXIC_WORDS):
        return SafetyResult("no_toxicity", False, "Toxic language detected")
    return SafetyResult("no_toxicity", True)


def check_no_pii(text: str) -> SafetyResult:
    for name, pattern in PII_PATTERNS.items():
        if pattern.search(text):
            return SafetyResult("no_pii", False, f"Detected {name}")
    return SafetyResult("no_pii", True)


POLICY_MAP = {
    "no_toxicity": check_no_toxicity,
    "no_pii": check_no_pii,
}


def evaluate_policies(text: str, policies: Iterable[str]) -> list[SafetyResult]:
    results: list[SafetyResult] = []
    for policy in policies:
        if policy not in POLICY_MAP:
            results.append(SafetyResult(policy, False, "Unknown policy"))
        else:
            results.append(POLICY_MAP[policy](text))
    return results


__all__ = ["SafetyResult", "evaluate_policies"]
