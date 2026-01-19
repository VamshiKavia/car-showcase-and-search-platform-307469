"""
Repository interface for Car data access.

Routes depend on this interface, allowing the data source to be swapped (e.g., in-memory
for dev/demo, Supabase for persistence) without changing endpoints or response shapes.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Protocol


class CarRepository(Protocol):
    """Protocol for car repositories."""

    # PUBLIC_INTERFACE
    def list_cars(
        self,
        *,
        q: Optional[str] = None,
        make: Optional[str] = None,
        model: Optional[str] = None,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        sort: Optional[str] = "-year",
        page: int = 1,
        page_size: int = 12,
    ) -> Dict[str, Any]:
        """List cars with filtering/sorting/pagination; returns the standard envelope."""
        raise NotImplementedError

    # PUBLIC_INTERFACE
    def get_car_by_id(self, car_id: str) -> Optional[Dict[str, Any]]:
        """Return a single car dict by id, or None if not found."""
        raise NotImplementedError
