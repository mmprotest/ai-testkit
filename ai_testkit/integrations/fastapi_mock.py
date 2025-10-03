"""FastAPI mock server stub."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(slots=True)
class MockRequest:
    prompt: str


@dataclass(slots=True)
class MockResponse:
    text: str


class FastAPIMockServer:
    def __init__(self) -> None:
        self.storage: Dict[str, str] = {}

    def record(self, request: MockRequest, response: MockResponse) -> None:
        self.storage[request.prompt] = response.text

    def replay(self, prompt: str) -> MockResponse:
        return MockResponse(text=self.storage.get(prompt, ""))

