"""Lightweight data structures for dataset suites."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Literal, Optional

TestKind = Literal["qa", "summarize", "extract", "classify", "function_call", "rag", "safety", "json"]


@dataclass(slots=True)
class Expectation:
    exact: Optional[bool] = None
    contains: Optional[str] = None
    regex: Optional[str] = None
    json_equals: Optional[Dict[str, object]] = None
    json_schema: Optional[Dict[str, object]] = None
    jmespath: Optional[str] = None
    metric: Optional[str] = None
    min: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Dict[str, object] | None) -> "Expectation | None":
        if data is None:
            return None
        return cls(**data)


@dataclass(slots=True)
class SafetyExpectation:
    policy: str

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "SafetyExpectation":
        return cls(policy=str(data.get("policy", "")))


@dataclass(slots=True)
class TestCase:
    name: str
    kind: TestKind
    input: str
    vars: List[Dict[str, object]] = field(default_factory=list)
    references: Optional[List[str] | Dict[str, object]] = None
    contexts: Optional[List[str]] = None
    expect: Optional[Expectation] = None
    safety_expect: Optional[List[SafetyExpectation]] = None
    filters: Optional[Dict[str, object]] = None
    timeout_s: Optional[int] = None
    redteam: Optional[Dict[str, object]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "TestCase":
        expectation = Expectation.from_dict(data.get("expect"))
        safety_raw = data.get("safety_expect") or data.get("safety_expectations") or []
        safety_expect = [SafetyExpectation.from_dict(item) for item in safety_raw] if safety_raw else None
        vars_data = data.get("vars")
        if isinstance(vars_data, dict):
            vars_list = [vars_data]
        elif isinstance(vars_data, list):
            vars_list = [dict(item) for item in vars_data]
        else:
            vars_list = []
        references = data.get("references")
        return cls(
            name=str(data["name"]),
            kind=str(data["kind"]),
            input=str(data.get("input", "")),
            vars=vars_list,
            references=references,
            contexts=data.get("contexts"),
            expect=expectation,
            safety_expect=safety_expect,
            filters=data.get("filters"),
            timeout_s=data.get("timeout_s"),
            redteam=data.get("redteam"),
        )


@dataclass(slots=True)
class SuiteDefaults:
    provider: Optional[str] = None
    model: Optional[str] = None
    params: Dict[str, object] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, object] | None) -> "SuiteDefaults":
        if data is None:
            return cls()
        return cls(
            provider=data.get("provider"),
            model=data.get("model"),
            params=dict(data.get("params", {})),
        )


@dataclass(slots=True)
class DatasetSuite:
    name: str
    version: str
    description: Optional[str]
    tags: List[str]
    defaults: SuiteDefaults
    tests: List[TestCase]

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "DatasetSuite":
        defaults = SuiteDefaults.from_dict(data.get("defaults"))
        tests = [TestCase.from_dict(item) for item in data.get("tests", [])]
        return cls(
            name=str(data["name"]),
            version=str(data.get("version", "0.0.0")),
            description=data.get("description"),
            tags=list(data.get("tags", [])),
            defaults=defaults,
            tests=tests,
        )

    def dict(self) -> Dict[str, object]:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "tags": self.tags,
            "defaults": {
                "provider": self.defaults.provider,
                "model": self.defaults.model,
                "params": self.defaults.params,
            },
            "tests": [self._test_to_dict(test) for test in self.tests],
        }

    @staticmethod
    def _test_to_dict(test: TestCase) -> Dict[str, object]:
        data: Dict[str, object] = {
            "name": test.name,
            "kind": test.kind,
            "input": test.input,
            "vars": test.vars,
        }
        if test.references is not None:
            data["references"] = test.references
        if test.contexts is not None:
            data["contexts"] = test.contexts
        if test.expect is not None:
            data["expect"] = {k: v for k, v in asdict(test.expect).items() if v is not None}
        if test.safety_expect is not None:
            data["safety_expect"] = [asdict(se) for se in test.safety_expect]
        if test.filters is not None:
            data["filters"] = test.filters
        if test.timeout_s is not None:
            data["timeout_s"] = test.timeout_s
        if test.redteam is not None:
            data["redteam"] = test.redteam
        return data


__all__ = [
    "DatasetSuite",
    "TestCase",
    "Expectation",
    "SafetyExpectation",
    "SuiteDefaults",
]
