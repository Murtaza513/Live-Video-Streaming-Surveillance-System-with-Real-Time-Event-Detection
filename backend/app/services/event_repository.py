from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event


class EventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_event(self, event_type: str, confidence: float, message: str) -> Event:
        event = Event(event_type=event_type, confidence=confidence, message=message)
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        return event

    async def get_recent(self, limit: int = 50) -> list[Event]:
        stmt = select(Event).order_by(desc(Event.created_at)).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
