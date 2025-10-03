from __future__ import annotations

from pathlib import Path

from ai_testkit.datasets.loader import DatasetLoader
from ai_testkit.providers import get_provider
from ai_testkit.reporting.html_report import HTMLReport
from ai_testkit.reporting.json_report import JSONReport
from ai_testkit.reporting.junit_report import JUnitReport
from ai_testkit.runners.dataset_runner import DatasetRunner, DatasetRunnerConfig
from ai_testkit.utils.time import utc_now_iso

DATASET = Path("tests/data/sample_suite.ait.yaml")


def test_reporting_generates_artifacts(tmp_path) -> None:
    loader = DatasetLoader()
    suite = loader.load_from_path(DATASET)
    provider = get_provider("local")
    runner = DatasetRunner(provider=provider, config=DatasetRunnerConfig(use_cache=False))
    report = runner.run_suite(suite)
    timestamp = utc_now_iso()
    json_report = JSONReport.from_run(report, timestamp=timestamp)
    junit_report = JUnitReport.from_run(report, timestamp=timestamp)
    html_report = HTMLReport.from_run(report, timestamp=timestamp)

    json_path = tmp_path / "run.json"
    json_path.write_text(json_report.to_json())
    junit_path = tmp_path / "run.xml"
    junit_path.write_text(junit_report.to_xml())
    html_path = tmp_path / "run.html"
    html_path.write_text(html_report.to_html())

    assert json_path.exists()
    assert junit_path.exists()
    assert html_path.exists()
