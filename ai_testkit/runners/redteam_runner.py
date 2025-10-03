"""Red-team runner."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

from ..metrics.safety import evaluate_policies
from ..providers.local_openai_compat import LocalOpenAICompatProvider
from ..redteam.library import RedteamLibrary, RedteamPack


@dataclass(slots=True)
class RedteamResult:
    pack: RedteamPack
    cases: List[bool]

    @property
    def failures(self) -> int:
        return len([case for case in self.cases if not case])


class RedteamRunner:
    def __init__(self) -> None:
        self.library = RedteamLibrary()
        self.provider = LocalOpenAICompatProvider()

    def run_pack(self, path: Path) -> RedteamResult:
        pack = self.library.load(path)
        outcomes: List[bool] = []
        for case in pack.cases:
            result = self.provider.complete(case.prompt)
            policies = evaluate_policies(result.text, [case.expected_policy])
            outcomes.append(all(item.passed for item in policies))
        return RedteamResult(pack=pack, cases=outcomes)

