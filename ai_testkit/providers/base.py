"""Provider interface."""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(slots=True)
class ProviderResult:
    """Structured response from a provider call."""

    text: str
    tokens_in: int
    tokens_out: int
    cost: float
    latency_ms: float
    raw: Dict[str, Any]


class BaseProvider:
    """Base class for provider adapters."""

    model: str | None

    def __init__(self, model: Optional[str] = None) -> None:
        self.model = model

    def complete(self, prompt: str, params: Optional[Dict[str, Any]] = None) -> ProviderResult:
        raise NotImplementedError

    @classmethod
    def from_config(
        cls, config: Optional["ProviderConfig"], model_override: Optional[str] = None
    ) -> "BaseProvider":
        from ..config import ProviderConfig

        model = model_override or (config.model if config else None)
        instance = cls(model=model)
        if config:
            instance.default_params = dict(config.params)
        else:
            instance.default_params = {}
        return instance

    def with_params(self, params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        merged: Dict[str, Any] = getattr(self, "default_params", {}).copy()
        if params:
            merged.update(params)
        return merged

    def _timed_completion(self, func, *args, **kwargs) -> ProviderResult:
        start = time.perf_counter()
        result: ProviderResult = func(*args, **kwargs)
        latency = (time.perf_counter() - start) * 1000
        result.latency_ms = latency
        return result


__all__ = ["BaseProvider", "ProviderResult"]
