"""Repository layer package (in-memory, database-backed, etc.)."""

from .car_repository import CarRepository
from .in_memory_car_repository import InMemoryCarRepository
from .repository_factory import get_car_repository

__all__ = ["CarRepository", "InMemoryCarRepository", "get_car_repository"]
