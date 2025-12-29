# app/schemas.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class URLBase(BaseModel):
    short_code: Optional[str] = Field(None, max_length=10)
    original_url: HttpUrl  # Validates URL format
    expires_at: Optional[datetime] = None
    is_active: bool = True


class URLCreate(URLBase):
    """Input for creating new short URL"""

    pass  # Inherits all from URLBase


class URLUpdate(BaseModel):
    """Input for updating URL"""

    original_url: Optional[HttpUrl] = None
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class URLResponse(URLBase):
    """Full response with ID"""

    id: int
    short_code: str  # Generated, required in response

    class Config:
        from_attributes = True  # SQLAlchemy compatibility


class URLRedirectResponse(BaseModel):
    """Minimal response for redirect endpoint"""

    short_code: str
    original_url: HttpUrl
