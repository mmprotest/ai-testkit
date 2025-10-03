"""Dataset loader utilities."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

import json

from .schema import DatasetSuite, TestCase


class DatasetLoader:
    """Load dataset suites from YAML documents."""

    def load_from_path(self, path: Path) -> DatasetSuite:
        data = json.loads(path.read_text())
        suite = DatasetSuite.from_dict(data)
        return suite

    def expand_cases(self, suite: DatasetSuite) -> Iterable[TestCase]:
        for test in suite.tests:
            if not test.vars:
                yield test
                continue
            for idx, variables in enumerate(test.vars):
                cloned = test.copy(deep=True)
                cloned.name = f"{test.name}[{idx}]"
                cloned.vars = [variables]
                yield cloned

    def render_golden(self, suite: DatasetSuite, run) -> str:
        data = suite.dict()
        for case, result in zip(data["tests"], run.cases):
            case.setdefault("references", [])
            if isinstance(case["references"], list):
                if not case["references"]:
                    case["references"].append(result.output)
                else:
                    case["references"][0] = result.output
        return json.dumps(data, indent=2)

    def to_json(self, suite: DatasetSuite) -> str:
        return json.dumps(suite.dict())

    def load_cases(self, suite: DatasetSuite) -> List[TestCase]:
        return list(self.expand_cases(suite))


__all__ = ["DatasetLoader"]
