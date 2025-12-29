from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Text,
    Boolean,
    DateTime,
    Index,
)

from app.db import Base
from app.models.mixins import TimestampMixin, CRUDMixin


class URL(Base, TimestampMixin, CRUDMixin):
    __tablename__ = "urls"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    short_code = Column(String(10), unique=True, nullable=False, index=True)
    original_url = Column(Text, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Composite indexes
    __table_args__ = (Index("idx_active_urls", "is_active", "short_code"),)
