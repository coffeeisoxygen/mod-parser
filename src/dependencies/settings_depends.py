"""dependencies jika butuh settings."""

from fastapi import Request
from src.settings.base import BussinessConfig


def get_settings(request: Request) -> BussinessConfig:
    """Dependency untuk inject settings global ke endpoint/service."""
    return request.app.state.settings
