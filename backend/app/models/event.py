from datetime import datetime

from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Event(Base):
    """Persisted record for every motion or person-detection alert."""

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_type: Mapped[str] = mapped_column(String(32), index=True)       # "motion" | "person"
    confidence: Mapped[float] = mapped_column(Float)
    motion_ratio: Mapped[float] = mapped_column(Float)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=False), index=True)
    message: Mapped[str] = mapped_column(String(256))
    snapshot_path: Mapped[str | None] = mapped_column(Text, nullable=True)  # relative path to saved JPEG
