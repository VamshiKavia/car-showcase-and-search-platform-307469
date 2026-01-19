"""
Repository factory and environment-based selection.

Selection rules:
- If Supabase credentials are present (SUPABASE_URL + SUPABASE_ANON_KEY), use Supabase.
- Else, if frontend-prefixed credentials are present (REACT_APP_SUPABASE_URL + REACT_APP_SUPABASE_KEY),
  use Supabase.
- Otherwise, fall back to in-memory repository.

This keeps endpoints and response shapes unchanged while enabling optional persistence.
"""

from __future__ import annotations

import os
from typing import Optional

from app.repositories.car_repository import CarRepository
from app.repositories.in_memory_car_repository import InMemoryCarRepository


def _get_env(name: str) -> Optional[str]:
    value = os.getenv(name)
    if value is None:
        return None
    value = value.strip()
    return value or None


# PUBLIC_INTERFACE
def get_car_repository() -> CarRepository:
    """
    Create and return the active CarRepository based on environment configuration.

    Returns:
        CarRepository: SupabaseCarRepository if configured, else InMemoryCarRepository.

    Env vars:
        - SUPABASE_URL + SUPABASE_ANON_KEY (preferred for backend)
        - OR REACT_APP_SUPABASE_URL + REACT_APP_SUPABASE_KEY (supported for convenience)
    """
    supabase_url = _get_env("SUPABASE_URL") or _get_env("REACT_APP_SUPABASE_URL")
    supabase_key = _get_env("SUPABASE_ANON_KEY") or _get_env("REACT_APP_SUPABASE_KEY")

    if supabase_url and supabase_key:
        # Import inside branch to keep in-memory path working without supabase installed.
        from app.repositories.supabase_car_repository import SupabaseCarRepository

        return SupabaseCarRepository(supabase_url=supabase_url, supabase_key=supabase_key, table="cars")

    return InMemoryCarRepository()
