from __future__ import annotations

from ai_testkit.metrics import rag


def test_rag_metrics() -> None:
    answer = "Paris is the capital"
    contexts = [
        "Paris is the capital city of France.",
        "Berlin is the capital of Germany.",
    ]
    faithfulness = rag.rag_faithfulness(answer, contexts)
    precision = rag.rag_context_precision(answer, contexts)
    recall = rag.rag_context_recall("What is the capital of France?", contexts)
    utilization = rag.rag_context_utilization(answer, contexts)
    assert 0.0 <= faithfulness <= 1.0
    assert precision >= faithfulness
    assert 0.0 <= recall <= 1.0
    assert 0.0 <= utilization <= 1.0
