"""Shared FastAPI dependencies."""
from app.db.session import get_session  # re-exported for route modules

__all__ = ["get_session"]
