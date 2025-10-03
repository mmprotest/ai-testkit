"""Minimal LlamaIndex integration."""
from __future__ import annotations

from typing import Iterable, List

from ..metrics.rag import rag_faithfulness


def evaluate_responses(responses: Iterable[str], contexts: Iterable[list[str]]) -> List[float]:
    scores: List[float] = []
    for response, ctx in zip(responses, contexts):
        scores.append(rag_faithfulness(response, ctx))
    return scores

