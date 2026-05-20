from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.event import EventResponse
from app.services.event_repository import EventRepository

router = APIRouter(prefix='/api/events', tags=['events'])


@router.get('', response_model=list[EventResponse])
async def get_events(
    limit: int = Query(default=50, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
) -> list[EventResponse]:
    repository = EventRepository(session)
    return await repository.get_recent(limit=limit)
