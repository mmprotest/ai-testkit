"""Simple disk cache."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass(slots=True)
class DiskCache:
    root: Path = Path(".ait_cache")

    def __post_init__(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)

    def path_for(self, key: str) -> Path:
        return self.root / f"{key}.json"

    def get(self, key: str) -> Optional[str]:
        path = self.path_for(key)
        if not path.exists():
            return None
        return json.loads(path.read_text())

    def set(self, key: str, value: str) -> None:
        path = self.path_for(key)
        path.write_text(json.dumps(value))

    def clear(self) -> None:
        for file in self.root.glob("*.json"):
            file.unlink()

