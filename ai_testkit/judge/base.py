"""Judge interfaces."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol


@dataclass(slots=True)
class JudgeConfig:
    rubric: str = "Quality"
    n_trials: int = 3
    seed: int = 0


@dataclass(slots=True)
class JudgeResult:
    verdict: str
    score: float
    reasoning: list[str]


class Judge(Protocol):
    def evaluate(self, prompt: str, outputs: Iterable[str]) -> JudgeResult:
        ...
