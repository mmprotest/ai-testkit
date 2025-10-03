# ai-testkit

ai-testkit is a lightweight yet batteries-included evaluation harness for large language model (LLM)
applications. It helps teams keep quality high while controlling safety, latency, and cost as prompts
and models evolve.

## Why ai-testkit?

Modern LLM applications change rapidly. Prompts, model versions, and retrieval corpora drift, which
can silently degrade quality or safety. Industry teams need:

* **Beyond accuracy** – Regression suites must cover exactness, semantic similarity, JSON validity,
and retrieval-grounded faithfulness. ai-testkit bundles classic metrics, semantic matching, and RAG
coverage checks out of the box.
* **Safety first** – Offensive jailbreaks, OWASP LLM Top-10 attacks, and PII leaks demand continuous
hardening. The built-in red-team packs and safety policies provide guardrails to stop toxic or private
data responses before they ship.
* **Cost & latency visibility** – Deployments must balance response quality against token spend and
latency budgets. Run reports track cost, latency, and variability to guide trade-offs.
* **Judge bias controls** – LLM-as-judge pipelines are vulnerable to ordering bias and stochastic
variance. ai-testkit applies deterministic shuffling and multi-trial majority voting to keep verdicts
stable.

These capabilities are available through a single CLI and Python API that works with any
OpenAI-compatible provider or local mock, making it easy to integrate into existing workflows.

## Quickstart (5 minutes)

### 1. Install

```bash
pip install -e .
```

### 2. Scaffold a suite and run it

```bash
ait init sample.ait.yaml
ait run sample.ait.yaml --html report.html --json run.json --junit run.xml
```

### 3. Add to pytest

```python
from ai_testkit.runners.dataset_runner import DatasetRunner, DatasetRunnerConfig
from ai_testkit.datasets.loader import DatasetLoader
from ai_testkit.providers import get_provider

loader = DatasetLoader()
suite = loader.load_from_path("sample.ait.yaml")
provider = get_provider("local")
runner = DatasetRunner(provider, DatasetRunnerConfig())
report = runner.run_suite(suite)
assert report.pass_rate == 1.0
```

In CI, call `ait run` to emit JSON, JUnit, and HTML artifacts that integrate with dashboards and
code-review bots.

## Choosing metrics

* **Exactness (EM/F1/ROUGE/BLEU)** – Use for deterministic answers or structured extractions. ai-testkit
normalizes whitespace and tokenizes text for robust scoring.
* **Semantic similarity** – Cosine similarity and optional embedding-based metrics capture meaning when
the exact words differ.
* **RAG metrics** – Faithfulness, answer relevancy, and context precision/recall/utilization quantify
how well retrieved passages support responses, highlighting hallucinations.
* **Validators** – JSON equality, schema checks, and pydantic validation ensure structured output
contracts remain intact.
* **Safety policies** – Regex-based PII detection and toxicity heuristics catch obvious failures early;
plug in Detoxify or other models when available.

When combining metrics, set minimum thresholds (`min`) and use judges for nuanced calls such as
summaries or style adherence.

## Judge guidance

LLM-as-judge systems are powerful but imperfect. ai-testkit mitigates bias by shuffling candidate
order, running multiple trials, and majority voting on the verdict. Still, judges can inherit provider
biases or hallucinate, so reserve human review for critical launches or contentious failures.

## Security note

Evaluation datasets must never contain real secrets or production data. The bundled red-team packs use
synthetic prompts with obvious PII patterns purely for testing, ensuring that practicing against them
does not leak confidential information.

## Repository layout

```
ai_testkit/
  providers/       # Provider adapters and local mock
  runners/         # Dataset, red-team, and compare runners
  datasets/        # Suite schema and loader
  metrics/         # Classic, semantic, RAG, safety, validators
  judge/           # Deterministic judge with bias mitigations
  reporting/       # JSON, JUnit, HTML, and run database utilities
  cache/           # Disk cache for reproducible runs
  redteam/         # OWASP-inspired packs
  integrations/    # LangChain, LlamaIndex, FastAPI stubs
```

## Contributing

Run the test suite before submitting changes:

```bash
pytest
```

ai-testkit is MIT licensed. Pull requests and feedback are welcome.
