"""Simplified RAG metrics."""
from __future__ import annotations

from typing import Sequence

from ..utils.text import word_tokens


def _overlap(a: Sequence[str], b: Sequence[str]) -> float:
    a_set = set(a)
    b_set = set(b)
    if not a_set or not b_set:
        return 0.0
    return len(a_set & b_set) / len(a_set)


def rag_faithfulness(answer: str, contexts: Sequence[str]) -> float:
    answer_tokens = word_tokens(answer.lower())
    context_tokens = [token for ctx in contexts for token in word_tokens(ctx.lower())]
    precision = rag_context_precision(answer, contexts)
    return min(precision, _overlap(answer_tokens, context_tokens))


def rag_answer_relevancy(question: str, answer: str) -> float:
    return _overlap(word_tokens(answer.lower()), word_tokens(question.lower()))


def rag_context_precision(answer: str, contexts: Sequence[str]) -> float:
    if not contexts:
        return 0.0
    answer_tokens = word_tokens(answer.lower())
    per_context = [
        _overlap(answer_tokens, word_tokens(ctx.lower()))
        for ctx in contexts
    ]
    return sum(per_context) / len(per_context)


def rag_context_recall(question: str, contexts: Sequence[str]) -> float:
    if not contexts:
        return 0.0
    question_tokens = word_tokens(question.lower())
    context_tokens = [token for ctx in contexts for token in word_tokens(ctx.lower())]
    if not question_tokens:
        return 0.0
    return len(set(question_tokens) & set(context_tokens)) / len(set(question_tokens))


def rag_context_utilization(answer: str, contexts: Sequence[str]) -> float:
    if not contexts:
        return 0.0
    used = sum(1 for ctx in contexts if _overlap(word_tokens(answer.lower()), word_tokens(ctx.lower())) > 0)
    return used / len(contexts)

