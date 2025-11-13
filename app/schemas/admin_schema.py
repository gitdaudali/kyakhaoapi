from __future__ import annotations

from pydantic import BaseModel


class AdminSchema(BaseModel):
    """Base schema for admin-facing payloads."""

    class Config:
        from_attributes = True

