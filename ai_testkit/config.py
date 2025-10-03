"""Configuration helpers for ai-testkit."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import tomllib


@dataclass(slots=True)
class ProviderConfig:
    """Configuration for a provider entry."""

    name: str
    model: str | None = None
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Config:
    """Runtime configuration loaded from TOML files or environment."""

    providers: Dict[str, ProviderConfig] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "Config":
        """Load configuration from a TOML file.

        When *path* is ``None`` the loader searches ``~/.ait/config.toml``.
        Missing files are tolerated and return an empty configuration.
        """

        config_path = path or Path.home() / ".ait" / "config.toml"
        if not config_path.exists():
            return cls()
        data = tomllib.loads(config_path.read_text())
        providers: Dict[str, ProviderConfig] = {}
        for name, entry in data.get("providers", {}).items():
            providers[name] = ProviderConfig(
                name=name,
                model=entry.get("model"),
                params=dict(entry.get("params", {})),
            )
        return cls(providers=providers)

    def get_provider(self, name: str) -> ProviderConfig:
        if name not in self.providers:
            raise KeyError(f"Provider '{name}' is not configured")
        return self.providers[name]
