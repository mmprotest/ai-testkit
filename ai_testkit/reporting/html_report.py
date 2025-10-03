"""HTML report generation without external dependencies."""
from __future__ import annotations

from html import escape
from typing import Dict

from ..runners.dataset_runner import RunReport


class HTMLReport:
    def __init__(self, html: str) -> None:
        self.html = html

    @classmethod
    def from_run(cls, report: RunReport, timestamp: str) -> "HTMLReport":
        rows = []
        for case in report.cases:
            rows.append(
                "<tr><td>{}</td><td>{}</td><td>{:.2f}</td></tr>".format(
                    escape(case.name), "PASS" if case.passed else "FAIL", case.score
                )
            )
        table = "".join(rows)
        html = (
            "<html><head><title>ai-testkit report - {name}</title></head><body>"
            "<h1>Suite: {name}</h1>"
            "<p>Pass rate: {pass_rate:.2%}, Total cost: ${total_cost:.2f}, Avg latency: {avg_latency:.2f}ms</p>"
            "<p>Generated at {timestamp}</p>"
            "<table><tr><th>Test</th><th>Status</th><th>Score</th></tr>{rows}</table>"
            "</body></html>"
        ).format(
            name=escape(report.suite.name),
            pass_rate=report.pass_rate,
            total_cost=report.total_cost,
            avg_latency=report.avg_latency,
            timestamp=escape(timestamp),
            rows=table,
        )
        return cls(html)

    def to_html(self) -> str:
        return self.html

    @classmethod
    def from_json(cls, data: Dict[str, object]) -> "HTMLReport":
        cases = data.get("cases", [])
        rows = []
        for case in cases:  # type: ignore[assignment]
            name = escape(str(case.get("name", "")))
            score = float(case.get("score", 0.0))
            status = "PASS" if case.get("passed") else "FAIL"
            rows.append(f"<tr><td>{name}</td><td>{status}</td><td>{score:.2f}</td></tr>")
        suite_name = escape(str(data.get("suite", {}).get("name", "unknown")))
        html = (
            f"<html><body><h1>Suite: {suite_name}</h1><table><tr><th>Test</th><th>Status</th><th>Score</th></tr>{''.join(rows)}</table></body></html>"
        )
        return cls(html)

