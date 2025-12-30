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
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 

class URLRedirectResponse(BaseModel):
    """Minimal response for redirect endpoint"""

    short_code: str
    original_url: HttpUrl


class URLFilterParams(BaseModel):
    id: Optional[int] = Field(default=None, ge=0, description="Database primary key of the URL")
    short_code: Optional[str] = Field(default=None, max_length=10, description="Short code of the URL")
    is_active: Optional[bool] = Field(default=None, description="Whether the URL is active")