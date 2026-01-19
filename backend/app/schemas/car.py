"""
Marshmallow schemas for the Car domain.

These schemas are designed for Flask-Smorest integration (request args parsing and
response serialization).
"""

from __future__ import annotations

from marshmallow import Schema, fields, validate


class CarSchema(Schema):
    """Serialization/deserialization schema for a car."""

    id = fields.Str(required=True, metadata={"description": "Car identifier (uuid/string)."})
    make = fields.Str(required=True, metadata={"description": "Manufacturer / make (e.g., Toyota)."})
    model = fields.Str(required=True, metadata={"description": "Model name (e.g., Camry)."})
    year = fields.Int(
        required=True,
        metadata={"description": "Model year."},
        validate=validate.Range(min=1886, max=2100),
    )
    price = fields.Float(required=True, metadata={"description": "Price in USD (or chosen currency)."})
    mileage = fields.Float(required=True, metadata={"description": "Mileage in miles (or chosen unit)."})
    fuel = fields.Str(required=True, metadata={"description": "Fuel type (e.g., Gasoline, Hybrid, Electric)."})
    transmission = fields.Str(required=True, metadata={"description": "Transmission type (e.g., Automatic, Manual)."})
    images = fields.List(
        fields.Str(),
        required=True,
        metadata={"description": "List of image URLs."},
    )
    description = fields.Str(required=True, metadata={"description": "Human-readable description of the car."})
    features = fields.List(
        fields.Str(),
        required=True,
        metadata={"description": "List of notable features."},
    )


class CarListQueryArgsSchema(Schema):
    """
    Query args for listing cars.

    Designed to support basic search/filter/sort/pagination over the in-memory dataset.
    """

    q = fields.Str(
        required=False,
        allow_none=True,
        metadata={"description": "Search text applied across make/model (case-insensitive)."},
    )

    year_min = fields.Int(
        required=False,
        allow_none=True,
        metadata={"description": "Minimum model year (inclusive)."},
    )
    year_max = fields.Int(
        required=False,
        allow_none=True,
        metadata={"description": "Maximum model year (inclusive)."},
    )

    price_min = fields.Float(
        required=False,
        allow_none=True,
        metadata={"description": "Minimum price (inclusive)."},
    )
    price_max = fields.Float(
        required=False,
        allow_none=True,
        metadata={"description": "Maximum price (inclusive)."},
    )

    sort_by = fields.Str(
        required=False,
        load_default="year",
        metadata={
            "description": (
                "Field to sort by. Supported: year, price, mileage, make, model. Default: year."
            )
        },
        validate=validate.OneOf(["year", "price", "mileage", "make", "model"]),
    )
    sort_dir = fields.Str(
        required=False,
        load_default="desc",
        metadata={"description": "Sort direction. Default: desc."},
        validate=validate.OneOf(["asc", "desc"]),
    )

    page = fields.Int(
        required=False,
        load_default=1,
        metadata={"description": "1-based page index. Default: 1."},
        validate=validate.Range(min=1),
    )
    page_size = fields.Int(
        required=False,
        load_default=12,
        metadata={"description": "Page size. Default: 12. Max: 100."},
        validate=validate.Range(min=1, max=100),
    )


class PaginatedCarsSchema(Schema):
    """Envelope schema for paginated car list responses."""

    items = fields.List(fields.Nested(CarSchema), required=True, metadata={"description": "Cars in this page."})
    total = fields.Int(required=True, metadata={"description": "Total cars matching the filter (before pagination)."})
    page = fields.Int(required=True, metadata={"description": "Current 1-based page index."})
    page_size = fields.Int(required=True, metadata={"description": "Current page size."})
    total_pages = fields.Int(required=True, metadata={"description": "Total number of pages."})
