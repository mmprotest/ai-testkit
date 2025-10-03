"""JSON report serialization."""
from __future__ import annotations

import json

from ..runners.dataset_runner import RunReport


class JSONReport:
    def __init__(self, payload: dict[str, object]) -> None:
        self.payload = payload

    @classmethod
    def from_run(cls, report: RunReport, timestamp: str) -> "JSONReport":
        payload = {
            "suite": report.suite.dict(),
            "cases": [
                {
                    "name": case.name,
                    "score": case.score,
                    "passed": case.passed,
                    "metrics": case.metrics,
                    "validations": [vars(v) for v in case.validations],
                    "safety": [vars(s) for s in case.safety],
                    "judge": vars(case.judge) if case.judge else None,
                    "output": case.output,
                }
                for case in report.cases
            ],
            "summary": {
                "pass_rate": report.pass_rate,
                "total_cost": report.total_cost,
                "avg_latency": report.avg_latency,
                "timestamp": timestamp,
            },
        }
        return cls(payload)

    def to_json(self) -> str:
        return json.dumps(self.payload, indent=2)

    @classmethod
    def from_json(cls, data: dict[str, object]) -> "JSONReport":
        return cls(payload=data)

