"""Command line interface for ai-testkit."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from .config import Config
from .datasets.loader import DatasetLoader
from .providers import get_provider
from .reporting.html_report import HTMLReport
from .reporting.json_report import JSONReport
from .reporting.junit_report import JUnitReport
from .runners.compare_runner import CompareRunner
from .runners.dataset_runner import DatasetRunner, DatasetRunnerConfig
from .runners.redteam_runner import RedteamRunner
from .utils.time import utc_now_iso

app = typer.Typer(help="ai-testkit CLI")


def _write_if_requested(path: Optional[Path], data: str) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data)


@app.command()
def init(path: Path = typer.Argument(..., help="Target path for the scaffolded suite")) -> None:
    """Create a minimal dataset suite and configuration stub."""

    suite = Path(path)
    suite.write_text(
        """{\n  \"name\": \"example-suite\",\n  \"version\": \"0.1.0\",\n  \"description\": \"Example evaluation suite\",\n  \"tags\": [\"smoke\"],\n  \"defaults\": {\n    \"provider\": \"local\",\n    \"model\": \"mock\",\n    \"params\": {\n      \"temperature\": 0\n    }\n  },\n  \"tests\": [\n    {\n      \"name\": \"addition\",\n      \"kind\": \"qa\",\n      \"input\": \"What is {{a}} + {{b}}?\",\n      \"vars\": [\n        {\n          \"a\": 1,\n          \"b\": 1,\n          \"answer\": 2\n        }\n      ],\n      \"references\": [\"2\"],\n      \"expect\": {\n        \"exact\": true\n      }\n    }\n  ]\n}\n"""
    )
    config_dir = Path.home() / ".ait"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "config.toml"
    if not config_path.exists():
        config_path.write_text("[providers.local]\nmodel='mock'\n")
    print(f"Scaffolded suite at {suite}")
    print(f"Config located at {config_path}")


@app.command()
def run(
    suite: Path = typer.Argument(..., exists=True, dir_okay=False),
    model: Optional[str] = typer.Option(None, help="Override model name"),
    provider_name: str = typer.Option("local", "--provider", help="Provider to use"),
    json_out: Optional[Path] = typer.Option(None, "--json", help="Write JSON report"),
    junit_out: Optional[Path] = typer.Option(None, "--junit", help="Write JUnit report"),
    html_out: Optional[Path] = typer.Option(None, "--html", help="Write HTML report"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Bypass cache"),
    judge: bool = typer.Option(False, "--judge", help="Enable LLM judge"),
    store_judge_rationales: bool = typer.Option(False, help="Persist judge rationales"),
) -> None:
    """Run a dataset suite and emit reports."""

    config = Config.load()
    provider = get_provider(provider_name, config=config, model_override=model)
    loader = DatasetLoader()
    suite_data = loader.load_from_path(suite)
    runner = DatasetRunner(
        provider=provider,
        config=DatasetRunnerConfig(
            use_cache=not no_cache,
            enable_judge=judge,
            store_judge_rationales=store_judge_rationales,
        ),
    )
    report = runner.run_suite(suite_data)
    print(f"Suite: {suite_data.name}")
    print("Test | Status | Score")
    for case in report.cases:
        status = "PASS" if case.passed else "FAIL"
        print(f"{case.name} | {status} | {case.score:.2f}")
    timestamp = utc_now_iso()
    json_report = JSONReport.from_run(report, timestamp=timestamp)
    junit_report = JUnitReport.from_run(report, timestamp=timestamp)
    html_report = HTMLReport.from_run(report, timestamp=timestamp)
    _write_if_requested(json_out, json_report.to_json())
    _write_if_requested(junit_out, junit_report.to_xml())
    _write_if_requested(html_out, html_report.to_html())
    print(f"Completed run at {timestamp}")


@app.command()
def redteam(pack: Path = typer.Argument(..., exists=True, dir_okay=False)) -> None:
    """Execute a red-team pack."""

    runner = RedteamRunner()
    result = runner.run_pack(pack)
    print(f"Executed {len(result.cases)} red-team cases, {result.failures} failures")


@app.command()
def compare(base: Path, contender: Path) -> None:
    """Compare two run JSON files."""

    compare_runner = CompareRunner()
    output = compare_runner.compare(json.loads(base.read_text()), json.loads(contender.read_text()))
    print(output)


@app.command()
def list_providers() -> None:
    """List configured providers."""

    config = Config.load()
    if not config.providers:
        print("No providers configured")
        return
    print("Name | Model | Params")
    for provider in config.providers.values():
        params = json.dumps(provider.params)
        model = provider.model or "-"
        print(f"{provider.name} | {model} | {params}")


@app.command()
def cache(action: str = typer.Argument(..., help="Supported action: clear")) -> None:
    """Cache management commands."""

    if action != "clear":
        raise typer.BadParameter("Only 'clear' action is supported")
    from .cache.disk_cache import DiskCache

    DiskCache().clear()
    print("Cache cleared")


@app.command()
def report(run_json: Path = typer.Argument(..., exists=True), html: bool = typer.Option(False)) -> None:
    """Regenerate reports from JSON run output."""

    data = json.loads(run_json.read_text())
    if html:
        report_obj = HTMLReport.from_json(data)
        path = run_json.with_suffix(".html")
        path.write_text(report_obj.to_html())
        print(f"Wrote HTML report to {path}")
    else:
        print(json.dumps(data, indent=2))


@app.command()
def record(suite: Path = typer.Argument(..., exists=True, dir_okay=False)) -> None:
    """Record golden outputs for a suite using the current provider."""

    config = Config.load()
    provider = get_provider("local", config=config)
    loader = DatasetLoader()
    suite_data = loader.load_from_path(suite)
    runner = DatasetRunner(provider=provider, config=DatasetRunnerConfig(use_cache=False))
    run = runner.run_suite(suite_data)
    suite.write_text(loader.render_golden(suite_data, run))
    print("Recorded golden outputs")
