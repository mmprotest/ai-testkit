"""Simple diff highlighter."""
from __future__ import annotations

import difflib


def inline_diff(a: str, b: str) -> str:
    diff = difflib.ndiff(a.split(), b.split())
    return " ".join(diff)
