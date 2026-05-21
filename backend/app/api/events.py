import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.models.event import Event
from app.schemas.event import EventRead, EventsResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/events", response_model=EventsResponse, summary="Paginated event history")
async def get_events(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(20, ge=1, le=100, description="Events per page"),
    event_type: Optional[str] = Query(
        None, description="Filter by type: 'motion' or 'person'"
    ),
    db: AsyncSession = Depends(get_db_session),
) -> EventsResponse:
    """
    Return a paginated, time-descending list of stored detection events.
    Optionally filter by ``event_type``.
    """
    # Efficient count using func.count
    count_stmt = select(func.count()).select_from(Event)
    if event_type:
        count_stmt = count_stmt.where(Event.event_type == event_type)
    total: int = (await db.execute(count_stmt)).scalar_one()

    # Paginated result
    stmt = select(Event).order_by(desc(Event.timestamp))
    if event_type:
        stmt = stmt.where(Event.event_type == event_type)
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    rows = (await db.execute(stmt)).scalars().all()
    return EventsResponse(
        events=[EventRead.model_validate(row) for row in rows],
        total=total,
    )
