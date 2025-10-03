"""Simple deterministic judge implementation."""
from __future__ import annotations

import random
from typing import Iterable

from .base import Judge, JudgeConfig, JudgeResult
from ..utils.sampling import shuffled


class LocalJudge(Judge):
    """A lightweight judge that scores outputs by length heuristics.

    The implementation randomizes candidate order per trial and performs a
    majority vote to determine the verdict. The heuristic is intentionally
    simple but deterministic given the seed.
    """

    def __init__(self, config: JudgeConfig | None = None) -> None:
        self.config = config or JudgeConfig()

    def evaluate(self, prompt: str, outputs: Iterable[str]) -> JudgeResult:
        choices = list(outputs)
        if not choices:
            return JudgeResult("reject", 0.0, ["No outputs provided"])
        rng = random.Random(self.config.seed)
        votes: list[str] = []
        reasoning: list[str] = []
        for trial in range(self.config.n_trials):
            order = shuffled(choices, seed=rng.randint(0, 10_000))
            scored = sorted(order, key=len, reverse=True)
            winner = "accept" if len(scored[0]) >= len(prompt) / 2 else "reject"
            votes.append(winner)
            reasoning.append(f"Trial {trial+1}: {winner} (len={len(scored[0])})")
        verdict = "accept" if votes.count("accept") >= votes.count("reject") else "reject"
        score = votes.count("accept") / len(votes)
        return JudgeResult(verdict, score, reasoning)

