"""
In-memory car repository with seeded data.

This module intentionally avoids database connections and external services.

Repository capabilities:
- list_cars(): filtering (q, make, model, year range, price range), sorting, pagination
- get_car_by_id(): fetch one car or return None

Notes:
- This file now provides a class-based repository (InMemoryCarRepository) to support
  pluggable persistence layers (e.g., Supabase) without changing routes.
- Backwards-compatible module-level functions (list_cars/get_car_by_id) are preserved.
"""

from __future__ import annotations

import math
from dataclasses import asdict
from typing import Any, Dict, List, Optional, Tuple

from app.domain.car import Car
from app.repositories.car_repository import CarRepository


def _seed_cars() -> List[Car]:
    """Create a deterministic set of realistic sample cars for demos/dev use."""
    # Note: Image URLs are placeholders and can be replaced by real assets later.
    return [
        Car(
            id="b5d2d5d6-9d20-4c7f-8ac3-0f10dfb533a1",
            make="Toyota",
            model="Camry SE",
            year=2021,
            price=25990.0,
            mileage=32450.0,
            fuel="Gasoline",
            transmission="Automatic",
            images=[
                "https://images.unsplash.com/photo-1542362567-b07e54358753?w=1200&auto=format&fit=crop",
                "https://images.unsplash.com/photo-1550355291-bbee04a92027?w=1200&auto=format&fit=crop",
            ],
            description="Comfortable midsize sedan with a sporty SE trim and strong reliability.",
            features=["Apple CarPlay", "Adaptive Cruise Control", "Lane Keep Assist", "Backup Camera"],
        ),
        Car(
            id="2a1cc4f3-2d8f-4c6b-bb8d-bbd0a0bb4c19",
            make="Honda",
            model="Civic EX",
            year=2020,
            price=21950.0,
            mileage=28700.0,
            fuel="Gasoline",
            transmission="Automatic",
            images=[
                "https://images.unsplash.com/photo-1583267746897-2cf415887172?w=1200&auto=format&fit=crop",
            ],
            description="Efficient compact sedan with modern tech and a refined cabin.",
            features=["Heated Seats", "Sunroof", "Bluetooth", "LED Headlights"],
        ),
        Car(
            id="fdc6a5fd-5f3e-42df-9be6-2c6a4b4df5a4",
            make="Tesla",
            model="Model 3 Long Range",
            year=2022,
            price=37990.0,
            mileage=19800.0,
            fuel="Electric",
            transmission="Automatic",
            images=[
                "https://images.unsplash.com/photo-1619767886558-efdc259cde1b?w=1200&auto=format&fit=crop",
                "https://images.unsplash.com/photo-1611859266238-4b98091d9d9b?w=1200&auto=format&fit=crop",
            ],
            description="Long-range EV with quick acceleration, minimalist interior, and advanced driver assists.",
            features=["Autopilot", "Glass Roof", "Fast Charging", "Heated Front & Rear Seats"],
        ),
        Car(
            id="0f45c5df-6a7c-4510-a1e9-3b25bbef10d7",
            make="Ford",
            model="F-150 XLT",
            year=2019,
            price=32900.0,
            mileage=51200.0,
            fuel="Gasoline",
            transmission="Automatic",
            images=[
                "https://images.unsplash.com/photo-1502877338535-766e1452684a?w=1200&auto=format&fit=crop",
            ],
            description="Best-selling full-size truck with strong towing capability and roomy cabin.",
            features=["Tow Package", "4x4", "Remote Start", "Apple CarPlay"],
        ),
        Car(
            id="d2389b4f-5b4a-4a63-a3a1-8cc9969fbc42",
            make="Subaru",
            model="Outback Premium",
            year=2021,
            price=28995.0,
            mileage=40110.0,
            fuel="Gasoline",
            transmission="CVT",
            images=[
                "https://images.unsplash.com/photo-1549921296-3a6b4b9f9d67?w=1200&auto=format&fit=crop",
            ],
            description="Versatile wagon/SUV with standard AWD—ideal for road trips and all-weather driving.",
            features=["All-Wheel Drive", "Roof Rails", "Heated Seats", "Blind Spot Monitor"],
        ),
        Car(
            id="a84b0ef3-10b0-43d8-8cf5-4eb707bb0436",
            make="BMW",
            model="330i",
            year=2018,
            price=24950.0,
            mileage=62200.0,
            fuel="Gasoline",
            transmission="Automatic",
            images=[
                "https://images.unsplash.com/photo-1549924231-f129b911e442?w=1200&auto=format&fit=crop",
            ],
            description="Sporty luxury sedan with sharp handling and a premium interior.",
            features=["Leather Seats", "Navigation", "Sport Mode", "Parking Sensors"],
        ),
        Car(
            id="a2d04f0b-4b7c-42ea-80ee-004e0d97bf9b",
            make="Hyundai",
            model="Elantra SEL",
            year=2023,
            price=23490.0,
            mileage=9800.0,
            fuel="Gasoline",
            transmission="Automatic",
            images=[
                "https://images.unsplash.com/photo-1603386329225-868f9b1d5433?w=1200&auto=format&fit=crop",
            ],
            description="Modern compact with excellent value, safety tech, and a comfortable ride.",
            features=["Wireless Apple CarPlay", "Lane Following Assist", "Forward Collision Avoidance"],
        ),
        Car(
            id="2e3e81a7-b9f7-4f6d-8b7d-3fdd9c4e2c5c",
            make="Volkswagen",
            model="Golf GTI",
            year=2017,
            price=18990.0,
            mileage=71300.0,
            fuel="Gasoline",
            transmission="Manual",
            images=[
                "https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=1200&auto=format&fit=crop",
            ],
            description="Iconic hot hatch with engaging manual transmission and practical hatchback space.",
            features=["Manual Transmission", "Sport Suspension", "Android Auto", "Heated Seats"],
        ),
        Car(
            id="4a9efaa0-bc65-4d4a-8c8a-0f0df9e8cd3d",
            make="Kia",
            model="Telluride SX",
            year=2022,
            price=39950.0,
            mileage=24600.0,
            fuel="Gasoline",
            transmission="Automatic",
            images=[
                "https://images.unsplash.com/photo-1617093727343-374698b1b08d?w=1200&auto=format&fit=crop",
            ],
            description="Three-row SUV with upscale interior, strong features, and excellent family usability.",
            features=["Captain's Chairs", "360 Camera", "Harman Kardon Audio", "Adaptive Cruise Control"],
        ),
        Car(
            id="7c9f6d1c-0c5d-4e75-bb06-1c6b7f61f3db",
            make="Chevrolet",
            model="Bolt EV",
            year=2020,
            price=16995.0,
            mileage=36500.0,
            fuel="Electric",
            transmission="Automatic",
            images=[
                "https://images.unsplash.com/photo-1612810806563-4cb826a5e5f8?w=1200&auto=format&fit=crop",
            ],
            description="Compact EV with impressive practicality and low running costs.",
            features=["DC Fast Charging", "Heated Seats", "Backup Camera", "Bluetooth"],
        ),
        Car(
            id="e1a0a2e6-8a6f-4a8b-9c2c-92d5c3f3c2f2",
            make="Mercedes-Benz",
            model="GLC 300",
            year=2019,
            price=31950.0,
            mileage=44800.0,
            fuel="Gasoline",
            transmission="Automatic",
            images=[
                "https://images.unsplash.com/photo-1523987355523-c7b5b0dd90a7?w=1200&auto=format&fit=crop",
            ],
            description="Luxury compact SUV with a refined ride and premium cabin materials.",
            features=["Panoramic Sunroof", "Power Liftgate", "Blind Spot Assist", "Navigation"],
        ),
        Car(
            id="cce5a2f3-62c2-4d48-8f9b-8c4c7c4f7a99",
            make="Mazda",
            model="CX-5 Touring",
            year=2021,
            price=27450.0,
            mileage=30300.0,
            fuel="Gasoline",
            transmission="Automatic",
            images=[
                "https://images.unsplash.com/photo-1542281286-9e0a16bb7366?w=1200&auto=format&fit=crop",
            ],
            description="Driver-focused compact SUV with upscale feel and confident handling.",
            features=["Blind Spot Monitor", "Apple CarPlay", "Heated Seats", "Adaptive Cruise Control"],
        ),
    ]


_SEEDED_CARS: List[Car] = _seed_cars()
_MAX_PAGE_SIZE = 50


def _normalize_text(value: Optional[str]) -> str:
    return (value or "").strip().lower()


def _matches_search(car: Car, q: Optional[str]) -> bool:
    """
    Apply a case-insensitive substring search.

    The API requirement mentions searching over make/model/name; this dataset doesn't
    have a separate "name" field, so we treat the model as the human-facing name.
    """
    query = _normalize_text(q)
    if not query:
        return True
    haystack = f"{car.make} {car.model}".lower()
    return query in haystack


def _matches_exact_text(value: str, expected: Optional[str]) -> bool:
    """Case-insensitive exact match. When expected is empty/None, it matches everything."""
    exp = _normalize_text(expected)
    if not exp:
        return True
    return _normalize_text(value) == exp


def _in_int_range(value: int, min_value: Optional[int], max_value: Optional[int]) -> bool:
    if min_value is not None and value < min_value:
        return False
    if max_value is not None and value > max_value:
        return False
    return True


def _in_float_range(value: float, min_value: Optional[float], max_value: Optional[float]) -> bool:
    if min_value is not None and value < min_value:
        return False
    if max_value is not None and value > max_value:
        return False
    return True


def _sort_key(car: Car, sort_by: str) -> Any:
    # Stable, predictable sorting fields
    if sort_by == "year":
        return car.year
    if sort_by == "price":
        return car.price
    if sort_by == "mileage":
        return car.mileage
    if sort_by == "make":
        return car.make.lower()
    if sort_by == "model":
        return car.model.lower()
    # Fallback
    return car.year


def _paginate(items: List[Car], page: int, page_size: int) -> Tuple[List[Car], int, int]:
    total = len(items)
    total_pages = max(1, math.ceil(total / page_size)) if page_size > 0 else 1

    # Clamp page into valid range to avoid empty surprises.
    page = max(1, min(page, total_pages))

    start = (page - 1) * page_size
    end = start + page_size
    return items[start:end], total, total_pages


def _parse_sort(sort: Optional[str]) -> Tuple[str, str]:
    """
    Parse sort string like '-price' or 'year' into (sort_by, sort_dir).
    """
    raw = (sort or "").strip()
    if not raw:
        return "year", "desc"
    if raw.startswith("-"):
        return raw[1:], "desc"
    return raw, "asc"


class InMemoryCarRepository(CarRepository):
    """Car repository backed by a fixed in-memory list (seeded demo data)."""

    def __init__(self, cars: Optional[List[Car]] = None):
        self._cars: List[Car] = list(cars) if cars is not None else list(_SEEDED_CARS)

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
        """
        List cars with optional filtering, sorting, and pagination.

        Returns the same envelope shape used by the API:
          { "items": [...], "total": int, "page": int, "page_size": int }
        """
        # Defensive clamping even though request args schema validates this.
        page = max(1, int(page or 1))
        page_size = max(1, min(int(page_size or 12), _MAX_PAGE_SIZE))

        sort_by, sort_dir = _parse_sort(sort)

        filtered: List[Car] = []
        for car in self._cars:
            if not _matches_search(car, q):
                continue
            if not _matches_exact_text(car.make, make):
                continue
            if not _matches_exact_text(car.model, model):
                continue
            if not _in_int_range(car.year, year_min, year_max):
                continue
            if not _in_float_range(car.price, price_min, price_max):
                continue
            filtered.append(car)

        reverse = (sort_dir or "desc").lower() != "asc"
        filtered.sort(key=lambda c: _sort_key(c, sort_by), reverse=reverse)

        page_items, total, total_pages = _paginate(filtered, page=page, page_size=page_size)

        # Ensure returned page reflects clamping to last page.
        clamped_page = max(1, min(page, total_pages))

        return {
            "items": [asdict(c) for c in page_items],
            "total": total,
            "page": clamped_page,
            "page_size": page_size,
        }

    # PUBLIC_INTERFACE
    def get_car_by_id(self, car_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a car by id; returns dict or None."""
        for car in self._cars:
            if car.id == car_id:
                return asdict(car)
        return None


# A module-level default repository keeps previous import/usage patterns working.
_DEFAULT_REPO = InMemoryCarRepository()


# PUBLIC_INTERFACE
def list_cars(
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
    """
    Backwards-compatible function wrapper around the default InMemoryCarRepository.
    """
    return _DEFAULT_REPO.list_cars(
        q=q,
        make=make,
        model=model,
        year_min=year_min,
        year_max=year_max,
        price_min=price_min,
        price_max=price_max,
        sort=sort,
        page=page,
        page_size=page_size,
    )


# PUBLIC_INTERFACE
def get_car_by_id(car_id: str) -> Optional[Dict[str, Any]]:
    """
    Backwards-compatible function wrapper around the default InMemoryCarRepository.
    """
    return _DEFAULT_REPO.get_car_by_id(car_id)
