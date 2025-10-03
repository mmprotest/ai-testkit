"""Cost helpers."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CostSummary:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_cost: float = 0.0

    def add(self, prompt: int, completion: int, cost: float) -> None:
        self.prompt_tokens += prompt
        self.completion_tokens += completion
        self.total_cost += cost

