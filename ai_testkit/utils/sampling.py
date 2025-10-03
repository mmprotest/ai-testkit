"""Sampling helpers for deterministic shuffles."""
from __future__ import annotations

import random
from typing import Iterable, List, Sequence, TypeVar

T = TypeVar("T")


def shuffled(items: Sequence[T], seed: int | None = None) -> List[T]:
    rng = random.Random(seed)
    copy = list(items)
    rng.shuffle(copy)
    return copy
