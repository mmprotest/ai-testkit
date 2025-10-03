"""Minimal LangChain integration."""
from __future__ import annotations

from typing import Callable, Iterable, List

from ..metrics.classic import exact_match


def evaluate_chain(chain: Callable[[str], str], prompts: Iterable[str], references: Iterable[str]) -> List[float]:
    results: List[float] = []
    refs = list(references)
    for prompt, reference in zip(prompts, refs):
        output = chain(prompt)
        metric = exact_match(output, [reference])
        results.append(metric.score)
    return results

