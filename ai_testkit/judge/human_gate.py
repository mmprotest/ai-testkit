"""Human approval stub."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class HumanDecision:
    approved: bool
    notes: str | None = None


def prompt_human(prompt: str, output: str) -> HumanDecision:
    """Placeholder for interactive review."""

    return HumanDecision(approved=len(output) > 0, notes="auto-approved")
