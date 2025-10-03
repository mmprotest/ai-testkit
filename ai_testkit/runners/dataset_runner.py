"""Dataset runner implementation."""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

from ..cache.disk_cache import DiskCache
from ..datasets.schema import DatasetSuite, TestCase
from ..metrics.classic import exact_match, f1_score, rouge_l_score
from ..metrics.rag import (
    rag_answer_relevancy,
    rag_context_precision,
    rag_context_recall,
    rag_context_utilization,
    rag_faithfulness,
)
from ..metrics.validators import ValidationResult, json_equals, validate_json_schema
from ..metrics.safety import SafetyResult, evaluate_policies
from ..providers.base import BaseProvider
from ..judge.llm_judge import LocalJudge
from ..judge.base import JudgeResult
from ..utils.text import render_template


@dataclass(slots=True)
class RunCaseResult:
    name: str
    output: str
    passed: bool
    score: float
    metrics: Dict[str, float]
    validations: List[ValidationResult]
    safety: List[SafetyResult]
    judge: Optional[JudgeResult]
    cost: float
    latency_ms: float


@dataclass(slots=True)
class RunReport:
    suite: DatasetSuite
    cases: List[RunCaseResult]

    @property
    def pass_rate(self) -> float:
        if not self.cases:
            return 0.0
        return sum(1 for case in self.cases if case.passed) / len(self.cases)

    @property
    def total_cost(self) -> float:
        return sum(case.cost for case in self.cases)

    @property
    def avg_latency(self) -> float:
        if not self.cases:
            return 0.0
        return sum(case.latency_ms for case in self.cases) / len(self.cases)


@dataclass(slots=True)
class DatasetRunnerConfig:
    use_cache: bool = True
    enable_judge: bool = False
    store_judge_rationales: bool = False


class DatasetRunner:
    """Execute dataset suites using a provider."""

    def __init__(self, provider: BaseProvider, config: Optional[DatasetRunnerConfig] = None) -> None:
        self.provider = provider
        self.config = config or DatasetRunnerConfig()
        self.cache = DiskCache()
        self.judge = LocalJudge() if self.config.enable_judge else None

    def run_suite(self, suite: DatasetSuite) -> RunReport:
        cases: List[RunCaseResult] = []
        for test in suite.tests:
            rendered_prompts = self._render_prompts(test)
            for idx, prompt in enumerate(rendered_prompts):
                result = self._execute_case(suite, test, prompt, idx)
                cases.append(result)
        return RunReport(suite=suite, cases=cases)

    def _render_prompts(self, test: TestCase) -> List[str]:
        if not test.vars:
            return [render_template(test.input, {})]
        return [render_template(test.input, vars_) for vars_ in test.vars]

    def _execute_case(
        self, suite: DatasetSuite, test: TestCase, prompt: str, idx: int
    ) -> RunCaseResult:
        params = suite.defaults.params
        cache_key = None
        if self.config.use_cache:
            cache_key = self._cache_key(prompt, params)
            cached = self.cache.get(cache_key)
        else:
            cached = None
        if cached is None:
            provider_result = self.provider.complete(prompt, params)
            if cache_key is not None:
                self.cache.set(cache_key, provider_result.text)
            output_text = provider_result.text
            cost = provider_result.cost
            latency = provider_result.latency_ms
        else:
            output_text = cached
            cost = 0.0
            latency = 0.0
        metrics, validations, safety_results, score, passed = self._evaluate(test, output_text)
        judge_result = None
        if self.judge is not None:
            judge_result = self.judge.evaluate(prompt, [output_text])
            if not self.config.store_judge_rationales:
                judge_result = JudgeResult(judge_result.verdict, judge_result.score, [])
        rendered_prompts = self._render_prompts(test)
        name = test.name if len(rendered_prompts) == 1 else f"{test.name}[{idx}]"
        return RunCaseResult(
            name=name,
            output=output_text,
            passed=passed,
            score=score,
            metrics=metrics,
            validations=validations,
            safety=safety_results,
            judge=judge_result,
            cost=cost,
            latency_ms=latency,
        )

    def _evaluate(
        self, test: TestCase, output_text: str
    ) -> tuple[Dict[str, float], List[ValidationResult], List[SafetyResult], float, bool]:
        metrics: Dict[str, float] = {}
        validations: List[ValidationResult] = []
        safety_results: List[SafetyResult] = []
        score = 0.0
        passed = True
        references = test.references if isinstance(test.references, list) else []
        if test.expect and test.expect.metric:
            metric_name = test.expect.metric
            if metric_name == "f1":
                result = f1_score(output_text, references)
            elif metric_name == "rouge":
                result = rouge_l_score(output_text, references)
            elif metric_name == "em":
                result = exact_match(output_text, references)
            else:
                result = exact_match(output_text, references)
            metrics[result.name] = result.score
            score = result.score
            if test.expect.min is not None:
                passed = result.score >= test.expect.min
            else:
                passed = result.passed
        else:
            if references:
                result = exact_match(output_text, references)
                metrics[result.name] = result.score
                score = result.score
                passed = result.passed
            else:
                score = 1.0
                passed = True
        if test.kind == "rag" and test.contexts:
            metrics.update(
                {
                    "rag_faithfulness": rag_faithfulness(output_text, test.contexts),
                    "rag_answer_relevancy": rag_answer_relevancy(test.input, output_text),
                    "rag_context_precision": rag_context_precision(output_text, test.contexts),
                    "rag_context_recall": rag_context_recall(test.input, test.contexts),
                    "rag_context_utilization": rag_context_utilization(output_text, test.contexts),
                }
            )
        if test.expect:
            if test.expect.json_equals is not None:
                validations.append(json_equals(output_text, test.expect.json_equals))
                passed = passed and validations[-1].passed
            if test.expect.json_schema is not None:
                instance = json.loads(output_text)
                validations.append(validate_json_schema(instance, test.expect.json_schema))
                passed = passed and validations[-1].passed
            if test.expect.regex is not None:
                pattern = re.compile(test.expect.regex)
                matches = bool(pattern.search(output_text))
                metrics["regex"] = 1.0 if matches else 0.0
                passed = passed and matches
                score = metrics.get("regex", score)
            if test.expect.contains is not None:
                contains = test.expect.contains in output_text
                metrics["contains"] = 1.0 if contains else 0.0
                passed = passed and contains
                score = metrics.get("contains", score)
        if test.safety_expect:
            policies = [expectation.policy for expectation in test.safety_expect]
            safety_results = evaluate_policies(output_text, policies)
            passed = passed and all(item.passed for item in safety_results)
        return metrics, validations, safety_results, score, passed

    def _cache_key(self, prompt: str, params: Dict[str, object]) -> str:
        payload = json.dumps({"prompt": prompt, "params": params}, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()


__all__ = ["DatasetRunner", "RunReport", "RunCaseResult", "DatasetRunnerConfig"]
