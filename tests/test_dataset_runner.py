from __future__ import annotations

from pathlib import Path

from ai_testkit.cache import DiskCache
from ai_testkit.datasets.loader import DatasetLoader
from ai_testkit.providers import get_provider
from ai_testkit.runners.dataset_runner import DatasetRunner, DatasetRunnerConfig


DATASET = Path("tests/data/sample_suite.ait.yaml")


def test_dataset_runner_executes_suite(tmp_path) -> None:
    DiskCache().clear()
    loader = DatasetLoader()
    suite = loader.load_from_path(DATASET)
    provider = get_provider("local")
    runner = DatasetRunner(provider=provider, config=DatasetRunnerConfig(use_cache=False))
    report = runner.run_suite(suite)
    assert report.pass_rate == 1.0
    assert len(report.cases) == 2
    assert all(case.passed for case in report.cases)


def test_dataset_runner_cache(tmp_path) -> None:
    DiskCache().clear()
    loader = DatasetLoader()
    suite = loader.load_from_path(DATASET)
    provider = get_provider("local")
    runner = DatasetRunner(provider=provider, config=DatasetRunnerConfig(use_cache=True))
    report_first = runner.run_suite(suite)
    assert report_first.cases[0].latency_ms > 0
    report_second = runner.run_suite(suite)
    assert report_second.cases[0].latency_ms == 0.0
