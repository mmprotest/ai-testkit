from __future__ import annotations

from pathlib import Path

from ai_testkit.runners.redteam_runner import RedteamRunner


PACK = Path("ai_testkit/redteam/packs/owaps_llm_top10.yaml")


def test_redteam_runner_flags_failures() -> None:
    runner = RedteamRunner()
    result = runner.run_pack(PACK)
    assert result.failures >= 1
