from __future__ import annotations

from pydantic import BaseModel


class UserSchema(BaseModel):
    """Base schema for user-facing responses."""

    class Config:
        from_attributes = True

