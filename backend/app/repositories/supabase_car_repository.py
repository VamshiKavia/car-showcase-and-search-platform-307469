"""
Supabase-backed car repository.

This repository reads from the Supabase table: `cars`.

Environment configuration (optional):
- Preferred (backend-appropriate) variables:
    - SUPABASE_URL
    - SUPABASE_ANON_KEY
- Also supported (when reusing frontend-prefixed vars in this template):
    - REACT_APP_SUPABASE_URL
    - REACT_APP_SUPABASE_KEY

If not configured, the app will fall back to in-memory repository (see repository_factory.py).
"""

from __future__ import annotations

import json
import math
from typing import Any, Dict, List, Optional, Tuple

from app.repositories.car_repository import CarRepository


def _normalize_text(value: Optional[str]) -> str:
    return (value or "").strip().lower()


def _parse_sort(sort: Optional[str]) -> Tuple[str, str]:
    """Parse sort string like '-price' or 'year' into (sort_by, sort_dir)."""
    raw = (sort or "").strip()
    if not raw:
        return "year", "desc"
    if raw.startswith("-"):
        return raw[1:], "desc"
    return raw, "asc"


def _safe_parse_json_list(value: Any) -> List[str]:
    """
    Supabase may return JSON arrays as real lists, or as JSON strings depending on column types.
    This helper normalizes to a list of strings.
    """
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value]
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return []
        # Try JSON array in string form
        try:
            parsed = json.loads(s)
            if isinstance(parsed, list):
                return [str(v) for v in parsed]
        except Exception:
            pass
        # Fallback: comma-separated
        return [part.strip() for part in s.split(",") if part.strip()]
    # Fallback: wrap scalar
    return [str(value)]


def _coerce_car_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Coerce a Supabase row into the API car dict shape expected by Marshmallow schemas.
    """
    images = _safe_parse_json_list(row.get("images"))
    features = _safe_parse_json_list(row.get("features"))

    # Ensure required fields exist with sane defaults (schema requires them).
    return {
        "id": str(row.get("id") or ""),
        "make": row.get("make") or "",
        "model": row.get("model") or "",
        "year": int(row.get("year") or 0),
        "price": float(row.get("price") or 0.0),
        "mileage": float(row.get("mileage") or 0.0),
        "fuel": row.get("fuel") or "",
        "transmission": row.get("transmission") or "",
        "images": images,
        "description": row.get("description") or "",
        "features": features,
    }


class SupabaseCarRepository(CarRepository):
    """CarRepository implementation backed by Supabase/PostgREST."""

    def __init__(self, *, supabase_url: str, supabase_key: str, table: str = "cars"):
        # Import lazily so that the project can run without supabase installed when unused.
        from supabase import create_client  # type: ignore

        self._client = create_client(supabase_url, supabase_key)
        self._table = table

    def _apply_filters(
        self,
        query,
        *,
        q: Optional[str],
        make: Optional[str],
        model: Optional[str],
        year_min: Optional[int],
        year_max: Optional[int],
        price_min: Optional[float],
        price_max: Optional[float],
    ):
        """
        Apply filters to a PostgREST query.

        Notes:
        - For `q`, we use ilike over make/model.
        - For make/model exact matching, we use `ilike` against lowercased input, which is
          case-insensitive but otherwise exact. (This matches in-memory behavior.)
        """
        if q:
            qn = _normalize_text(q)
            if qn:
                # OR over make and model
                query = query.or_(f"make.ilike.*{qn}*,model.ilike.*{qn}*")

        if make:
            mn = _normalize_text(make)
            if mn:
                query = query.ilike("make", mn)

        if model:
            modn = _normalize_text(model)
            if modn:
                query = query.ilike("model", modn)

        if year_min is not None:
            query = query.gte("year", int(year_min))
        if year_max is not None:
            query = query.lte("year", int(year_max))

        if price_min is not None:
            query = query.gte("price", float(price_min))
        if price_max is not None:
            query = query.lte("price", float(price_max))

        return query

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
        List cars using Supabase as the data source.

        Returns the same envelope shape as the in-memory repository:
          { "items": [...], "total": int, "page": int, "page_size": int }
        """
        # Mirror the in-memory hard limits to avoid breaking expectations.
        max_page_size = 50
        page = max(1, int(page or 1))
        page_size = max(1, min(int(page_size or 12), max_page_size))

        sort_by, sort_dir = _parse_sort(sort)
        reverse = (sort_dir or "desc").lower() != "asc"

        # 1) Count (for "total")
        count_query = self._client.table(self._table).select("id", count="exact")
        count_query = self._apply_filters(
            count_query,
            q=q,
            make=make,
            model=model,
            year_min=year_min,
            year_max=year_max,
            price_min=price_min,
            price_max=price_max,
        )
        count_res = count_query.execute()
        total = int(getattr(count_res, "count", 0) or 0)

        total_pages = max(1, math.ceil(total / page_size)) if page_size > 0 else 1
        clamped_page = max(1, min(page, total_pages))

        start = (clamped_page - 1) * page_size
        end = start + page_size - 1  # Supabase range is inclusive

        # 2) Fetch page data
        data_query = self._client.table(self._table).select("*")
        data_query = self._apply_filters(
            data_query,
            q=q,
            make=make,
            model=model,
            year_min=year_min,
            year_max=year_max,
            price_min=price_min,
            price_max=price_max,
        )

        # Supabase Python: order(column, desc=bool)
        data_query = data_query.order(sort_by, desc=reverse).range(start, end)
        data_res = data_query.execute()

        rows: List[Dict[str, Any]] = list(getattr(data_res, "data", None) or [])
        items = [_coerce_car_row(r) for r in rows]

        return {"items": items, "total": total, "page": clamped_page, "page_size": page_size}

    # PUBLIC_INTERFACE
    def get_car_by_id(self, car_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a car by id from Supabase; returns dict or None."""
        res = self._client.table(self._table).select("*").eq("id", car_id).limit(1).execute()
        rows: List[Dict[str, Any]] = list(getattr(res, "data", None) or [])
        if not rows:
            return None
        return _coerce_car_row(rows[0])
