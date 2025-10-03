from __future__ import annotations

from ai_testkit.metrics.classic import exact_match, f1_score, rouge_l_score


def test_exact_match() -> None:
    result = exact_match("Paris", ["Paris"])
    assert result.passed and result.score == 1.0


def test_f1_score_partial() -> None:
    result = f1_score("blue car", ["blue truck"])
    assert 0.0 < result.score < 1.0


def test_rouge_l() -> None:
    result = rouge_l_score("the quick brown fox", ["quick brown fox jumps"])
    assert result.score > 0.5
