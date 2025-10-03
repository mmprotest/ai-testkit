"""Semantic similarity metrics."""
from __future__ import annotations

import math
from typing import Sequence

from ..utils.text import word_tokens


def cosine_similarity(prediction: str, references: Sequence[str]) -> float:
    pred_tokens = word_tokens(prediction.lower())
    if not pred_tokens or not references:
        return 0.0
    vocab = sorted(set(pred_tokens + [token for ref in references for token in word_tokens(ref.lower())]))
    pred_vec = [pred_tokens.count(term) for term in vocab]
    ref_tokens = word_tokens(references[0].lower())
    ref_vec = [ref_tokens.count(term) for term in vocab]
    dot = sum(p * r for p, r in zip(pred_vec, ref_vec))
    pred_norm = math.sqrt(sum(p * p for p in pred_vec))
    ref_norm = math.sqrt(sum(r * r for r in ref_vec))
    if pred_norm == 0 or ref_norm == 0:
        return 0.0
    return dot / (pred_norm * ref_norm)

