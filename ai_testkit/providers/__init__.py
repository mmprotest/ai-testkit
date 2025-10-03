"""Provider registry."""
from __future__ import annotations

from typing import Dict, Optional

from ..config import Config, ProviderConfig
from .base import BaseProvider
from .local_openai_compat import LocalOpenAICompatProvider

_PROVIDER_REGISTRY: Dict[str, type[BaseProvider]] = {
    "local": LocalOpenAICompatProvider,
}


def get_provider(name: str, config: Optional[Config] = None, model_override: Optional[str] = None) -> BaseProvider:
    if name not in _PROVIDER_REGISTRY:
        raise KeyError(f"Unknown provider '{name}'")
    provider_cls = _PROVIDER_REGISTRY[name]
    provider_config: Optional[ProviderConfig] = None
    if config is not None and name in config.providers:
        provider_config = config.providers[name]
    return provider_cls.from_config(provider_config, model_override=model_override)


__all__ = ["get_provider", "BaseProvider", "LocalOpenAICompatProvider"]
