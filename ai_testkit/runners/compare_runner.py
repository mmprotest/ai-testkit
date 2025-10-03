"""Compare two run reports."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(slots=True)
class CompareResult:
    regressions: List[str]
    improvements: List[str]

    def render(self) -> str:
        lines = ["Regressions:"]
        lines.extend(f"- {item}" for item in self.regressions or ["None"])
        lines.append("Improvements:")
        lines.extend(f"- {item}" for item in self.improvements or ["None"])
        return "\n".join(lines)


class CompareRunner:
    def compare(self, base: Dict[str, object], contender: Dict[str, object]) -> str:
        base_cases = {case["name"]: case for case in base.get("cases", [])}
        cont_cases = {case["name"]: case for case in contender.get("cases", [])}
        regressions: List[str] = []
        improvements: List[str] = []
        for name, cont_case in cont_cases.items():
            base_case = base_cases.get(name)
            if not base_case:
                improvements.append(f"New case {name} with score {cont_case['score']:.2f}")
                continue
            delta = cont_case["score"] - base_case["score"]
            if delta < -0.05:
                regressions.append(f"{name}: -{abs(delta):.2f}")
            elif delta > 0.05:
                improvements.append(f"{name}: +{delta:.2f}")
        return CompareResult(regressions, improvements).render()

