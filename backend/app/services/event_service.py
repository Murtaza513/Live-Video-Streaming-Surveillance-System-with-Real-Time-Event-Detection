import logging
from datetime import datetime
from typing import Optional

import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event
from app.services.detection import MotionResult
from app.services.snapshot import SnapshotService
from app.services.yolo_detector import YoloResult

logger = logging.getLogger(__name__)


class EventOrchestrator:
    """
    Combines motion and YOLO detection outcomes into a single alert decision.

    Features:
        - Priority ordering: person detection takes precedence over motion.
        - Per-type cooldown to prevent duplicate events flooding the log.
        - Persists each fired event to the database with a snapshot path.
    """

    def __init__(self, cooldown_seconds: int = 2) -> None:
        self.cooldown_seconds = cooldown_seconds
        self._last_fired: dict[str, datetime] = {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _on_cooldown(self, event_type: str) -> bool:
        last = self._last_fired.get(event_type)
        if last is None:
            return False
        return (datetime.utcnow() - last).total_seconds() < self.cooldown_seconds

    def _mark(self, event_type: str) -> None:
        self._last_fired[event_type] = datetime.utcnow()

    async def _fire(
        self,
        *,
        frame: np.ndarray,
        event_type: str,
        confidence: float,
        motion_ratio: float,
        message: str,
        db: AsyncSession,
        snapshot_svc: SnapshotService,
    ) -> str:
        """Persist the event, save snapshot, and return the alert message."""
        self._mark(event_type)
        snapshot_path = snapshot_svc.save(frame, event_type)

        event = Event(
            event_type=event_type,
            confidence=confidence,
            motion_ratio=motion_ratio,
            timestamp=datetime.utcnow(),
            message=message,
            snapshot_path=snapshot_path,
        )
        db.add(event)
        await db.commit()
        logger.info("Event persisted: [%s] %s", event_type, message)
        return message

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    async def process(
        self,
        frame: np.ndarray,
        motion: MotionResult,
        yolo: YoloResult,
        db: AsyncSession,
        snapshot_svc: SnapshotService,
    ) -> Optional[str]:
        """
        Evaluate detections and fire an alert if warranted.

        Returns the alert message string if an event was persisted, else None.
        """
        # Person detection takes priority
        if yolo.person_detected and not self._on_cooldown("person"):
            return await self._fire(
                frame=frame,
                event_type="person",
                confidence=yolo.confidence,
                motion_ratio=motion.motion_ratio,
                message=f"Person detected (confidence {yolo.confidence:.0%})",
                db=db,
                snapshot_svc=snapshot_svc,
            )

        if motion.detected and not self._on_cooldown("motion"):
            return await self._fire(
                frame=frame,
                event_type="motion",
                confidence=round(motion.motion_ratio, 3),
                motion_ratio=motion.motion_ratio,
                message=f"Motion detected ({motion.motion_ratio * 100:.1f}% of frame changed)",
                db=db,
                snapshot_svc=snapshot_svc,
            )

        return None
