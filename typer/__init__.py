"""Minimal Typer stub for offline environments."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Optional


def Option(default: Any = None, *args: Any, **kwargs: Any) -> Any:  # noqa: D401
    """Return the provided default; placeholder for Typer Option."""

    return default


def Argument(default: Any = None, *args: Any, **kwargs: Any) -> Any:
    return default


@dataclass
class CommandInfo:
    name: str
    callback: Callable[..., Any]
    help_text: str


class Typer:
    def __init__(self, help: str | None = None) -> None:
        self.help = help or ""
        self._commands: Dict[str, CommandInfo] = {}

    def command(self, name: Optional[str] = None, *_, **__) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            cmd_name = name or func.__name__.replace("_", "-")
            self._commands[cmd_name] = CommandInfo(cmd_name, func, func.__doc__ or "")
            return func

        return decorator

    def _generate_help(self) -> str:
        lines = ["Usage: ait [COMMAND]", "", "Commands:"]
        for cmd in sorted(self._commands):
            info = self._commands[cmd]
            lines.append(f"  {info.name}\t{info.help_text.strip()}")
        return "\n".join(lines)

    def invoke(self, argv: Iterable[str]) -> tuple[int, str]:
        args = list(argv)
        if not args or args[0] in {"--help", "-h"}:
            return 0, self._generate_help()
        cmd_name = args[0]
        info = self._commands.get(cmd_name)
        if info is None:
            return 1, f"Unknown command: {cmd_name}"
        info.callback(*args[1:])
        return 0, ""


__all__ = ["Typer", "Option", "Argument"]
