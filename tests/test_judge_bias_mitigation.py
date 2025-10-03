from __future__ import annotations

from ai_testkit.judge.base import JudgeConfig
from ai_testkit.judge.llm_judge import LocalJudge


def test_local_judge_multi_trial() -> None:
    config = JudgeConfig(n_trials=5, seed=42)
    judge = LocalJudge(config)
    result = judge.evaluate("prompt", ["short", "a much longer answer"])
    assert len(result.reasoning) == 5
    assert 0.0 <= result.score <= 1.0
    assert result.verdict in {"accept", "reject"}
