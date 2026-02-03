"""
Car domain model.

This module defines the core Car entity used across the backend. It is intentionally
framework-agnostic and does not depend on Flask or database libraries.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class Car:
    """
    Immutable Car entity.

    Fields match the API contract and the in-memory repository structure.
    """

    id: str
    make: str
    model: str
    year: int
    price: float
    mileage: float
    fuel: str
    transmission: str
    images: List[str] = field(default_factory=list)
    description: str = ""
    features: List[str] = field(default_factory=list)
