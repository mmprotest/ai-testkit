"""Testing utilities for the Typer stub."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from . import Typer


@dataclass
class Result:
    exit_code: int
    stdout: str


class CliRunner:
    def invoke(self, app: Typer, args: Iterable[str]):
        exit_code, stdout = app.invoke(args)
        return Result(exit_code=exit_code, stdout=stdout)
