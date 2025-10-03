"""Text utilities."""
from __future__ import annotations

import re

_WHITESPACE_RE = re.compile(r"\s+")


def normalize_whitespace(value: str) -> str:
    """Collapse whitespace for robust comparisons."""

    return _WHITESPACE_RE.sub(" ", value.strip())


def word_tokens(value: str) -> list[str]:
    return [token for token in re.split(r"\W+", value) if token]


_TEMPLATE_RE = re.compile(r'{{\s*(.*?)\s*}}')

def render_template(template: str, variables: dict[str, object] | None = None) -> str:
    if not variables:
        return template
    def repl(match: re.Match[str]) -> str:
        key = match.group(1)
        return str(variables.get(key, ''))
    return _TEMPLATE_RE.sub(repl, template)
