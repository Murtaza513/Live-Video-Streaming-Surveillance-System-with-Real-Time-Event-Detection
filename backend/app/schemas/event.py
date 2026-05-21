from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EventRead(BaseModel):
    """Schema returned by the REST event-history endpoint."""

    id: int
    event_type: str
    confidence: float
    motion_ratio: float
    timestamp: datetime
    message: str
    snapshot_path: Optional[str] = None

    model_config = {"from_attributes": True}


class EventsResponse(BaseModel):
    """Paginated wrapper for event list responses."""

    events: list[EventRead]
    total: int


class StreamFramePayload(BaseModel):
    """Shape of each JSON message sent over the WebSocket stream."""

    frame: str                   # base64-encoded JPEG
    timestamp: str               # ISO-8601 UTC
    motion_detected: bool
    person_detected: bool
    motion_ratio: float
    jpeg_quality: int
    scale: float
    alert: Optional[str] = None  # human-readable message when an event fires
