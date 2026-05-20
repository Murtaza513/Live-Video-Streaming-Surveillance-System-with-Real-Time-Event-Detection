from datetime import datetime

from pydantic import BaseModel


class EventResponse(BaseModel):
    id: int
    event_type: str
    confidence: float
    message: str
    created_at: datetime

    class Config:
        from_attributes = True
