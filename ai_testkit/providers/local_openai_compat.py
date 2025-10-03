"""Local mock provider used for tests and offline evaluation."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from .base import BaseProvider, ProviderResult


@dataclass(slots=True)
class LocalProviderSettings:
    """Settings for the local provider."""

    response_map: Dict[str, str]

    @classmethod
    def from_env(cls) -> "LocalProviderSettings":
        mapping_env = Path.home() / ".ait" / "local_responses.json"
        if mapping_env.exists():
            return cls(response_map=json.loads(mapping_env.read_text()))
        return cls(response_map={})


class LocalOpenAICompatProvider(BaseProvider):
    """A deterministic provider that serves canned responses.

    The provider looks for a Jinja rendered prompt in a local mapping file.
    When no mapping exists it returns the prompt itself which makes the
    system deterministic for tests.
    """

    def __init__(self, model: Optional[str] = None) -> None:
        super().__init__(model=model)
        self.settings = LocalProviderSettings.from_env()

    def complete(self, prompt: str, params: Optional[Dict[str, Any]] = None) -> ProviderResult:
        merged = self.with_params(params)
        response = self.settings.response_map.get(prompt, prompt)
        tokens_in = len(prompt.split())
        tokens_out = len(response.split())
        cost = 0.0
        latency_ms = 0.1
        raw = {"params": merged}
        return ProviderResult(
            text=response,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost=cost,
            latency_ms=latency_ms,
            raw=raw,
        )

