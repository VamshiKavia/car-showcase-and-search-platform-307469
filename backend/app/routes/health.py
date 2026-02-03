"""
Health check routes (Flask-Smorest).

Provides:
- GET / : basic health check used for uptime verification and local smoke tests.

This blueprint is registered in app/__init__.py and intentionally kept minimal.
"""

from flask.views import MethodView
from flask_smorest import Blueprint

blp = Blueprint(
    "Health Check",
    __name__,
    url_prefix="/",
    description="Health check route",
)


@blp.route("/")
class HealthCheck(MethodView):
    """Simple health check endpoint."""

    # PUBLIC_INTERFACE
    def get(self):
        """Return a basic health status payload."""
        return {"message": "Healthy"}
