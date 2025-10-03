from __future__ import annotations

from ai_testkit.runners.compare_runner import CompareRunner


def test_compare_runner_reports_deltas() -> None:
    runner = CompareRunner()
    base = {"cases": [{"name": "qa_case", "score": 1.0}]}
    contender = {"cases": [{"name": "qa_case", "score": 0.8}, {"name": "new", "score": 1.0}]}
    output = runner.compare(base, contender)
    assert "Regressions" in output
    assert "Improvements" in output
