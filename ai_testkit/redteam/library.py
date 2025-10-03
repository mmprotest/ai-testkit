"""Red-team pack loader."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import json


@dataclass(slots=True)
class RedteamCase:
    name: str
    prompt: str
    expected_policy: str


@dataclass(slots=True)
class RedteamPack:
    name: str
    cases: List[RedteamCase]


class RedteamLibrary:
    def load(self, path: Path) -> RedteamPack:
        data = json.loads(path.read_text())
        name = data.get("name", path.stem)
        cases = [
            RedteamCase(case["name"], case["prompt"], case["expected_policy"])
            for case in data.get("cases", [])
        ]
        return RedteamPack(name=name, cases=cases)

