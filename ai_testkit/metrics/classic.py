"""Classic metrics implementations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from ..utils.text import normalize_whitespace, word_tokens


@dataclass(slots=True)
class MetricResult:
    name: str
    score: float
    passed: bool
    details: dict[str, float | str]


def _normalize_answers(references: Iterable[str]) -> list[str]:
    return [normalize_whitespace(ref) for ref in references]


def exact_match(prediction: str, references: Sequence[str]) -> MetricResult:
    norm_pred = normalize_whitespace(prediction)
    norm_refs = _normalize_answers(references)
    score = 1.0 if norm_pred in norm_refs else 0.0
    return MetricResult("exact_match", score, score == 1.0, {"prediction": norm_pred})


def f1_score(prediction: str, references: Sequence[str]) -> MetricResult:
    pred_tokens = word_tokens(prediction.lower())
    best = 0.0
    for ref in references:
        ref_tokens = word_tokens(ref.lower())
        common = set(pred_tokens) & set(ref_tokens)
        if not pred_tokens or not ref_tokens:
            continue
        precision = len(common) / len(pred_tokens)
        recall = len(common) / len(ref_tokens)
        if precision + recall == 0:
            continue
        score = 2 * precision * recall / (precision + recall)
        best = max(best, score)
    return MetricResult("f1", best, best == 1.0, {"f1": best})


def rouge_l_score(prediction: str, references: Sequence[str]) -> MetricResult:
    def lcs(a: list[str], b: list[str]) -> int:
        dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
        for i in range(len(a)):
            for j in range(len(b)):
                if a[i] == b[j]:
                    dp[i + 1][j + 1] = dp[i][j] + 1
                else:
                    dp[i + 1][j + 1] = max(dp[i][j + 1], dp[i + 1][j])
        return dp[-1][-1]

    pred_tokens = word_tokens(prediction.lower())
    scores = []
    for ref in references:
        ref_tokens = word_tokens(ref.lower())
        if not pred_tokens or not ref_tokens:
            continue
        lcs_len = lcs(pred_tokens, ref_tokens)
        precision = lcs_len / len(pred_tokens)
        recall = lcs_len / len(ref_tokens)
        if precision + recall == 0:
            continue
        beta = 1.0
        score = ((1 + beta**2) * precision * recall) / ((beta**2 * precision) + recall)
        scores.append(score)
    best = max(scores) if scores else 0.0
    return MetricResult("rouge_l", best, best == 1.0, {"rouge_l": best})


__all__ = ["MetricResult", "exact_match", "f1_score", "rouge_l_score"]
