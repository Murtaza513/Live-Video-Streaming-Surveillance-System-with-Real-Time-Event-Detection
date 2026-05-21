import asyncio
import json
import logging
import time
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.config import settings
from app.core.database import AsyncSessionLocal

logger = logging.getLogger(__name__)
router = APIRouter()


class ConnectionManager:
    """Tracks active WebSocket clients and handles clean broadcast/disconnect."""

    def __init__(self) -> None:
        self._active: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._active.append(ws)
        logger.info("WS client connected. Total active: %d", len(self._active))

    def disconnect(self, ws: WebSocket) -> None:
        self._active = [c for c in self._active if c is not ws]
        logger.info("WS client disconnected. Total active: %d", len(self._active))

    async def broadcast(self, message: str) -> None:
        """Send a text message to every connected client; prune stale connections."""
        stale: list[WebSocket] = []
        for conn in self._active:
            try:
                await conn.send_text(message)
            except Exception:
                stale.append(conn)
        for conn in stale:
            self.disconnect(conn)


manager = ConnectionManager()


@router.websocket("/stream")
async def websocket_stream(websocket: WebSocket) -> None:
    """
    Async WebSocket endpoint: streams annotated JPEG frames to connected clients.

    Each message is a JSON object containing:
        frame           – base64-encoded JPEG
        timestamp       – ISO-8601 UTC string
        motion_detected – bool
        person_detected – bool
        motion_ratio    – float [0, 1]
        jpeg_quality    – int (actual quality used)
        scale           – float (actual resolution scale used)
        alert           – str | null (human-readable message when an event fires)

    On camera unavailability a reduced error payload is sent instead.
    """
    await manager.connect(websocket)

    # Retrieve shared services injected via app.state during lifespan startup
    state = websocket.app.state
    video_svc = state.video_service
    motion_det = state.motion_detector
    yolo_det = state.yolo_detector
    compressor = state.compressor
    snapshot_svc = state.snapshot_service
    event_orch = state.event_orchestrator

    frame_interval = 1.0 / max(settings.target_fps, 1)

    try:
        while True:
            tick = time.monotonic()

            frame = video_svc.read_frame()

            if frame is None:
                # Camera temporarily unavailable — notify client and wait
                error_payload = json.dumps(
                    {
                        "error": "camera_unavailable",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )
                await websocket.send_text(error_payload)
                await asyncio.sleep(frame_interval)
                continue

            # --- Detection pipeline ---
            motion = motion_det.detect(frame)
            yolo = yolo_det.detect(frame)

            # --- Adaptive compression ---
            comp = compressor.compress(frame, motion.motion_ratio)

            # --- Event orchestration (DB write only when detection fires) ---
            alert: str | None = None
            if motion.detected or yolo.person_detected:
                async with AsyncSessionLocal() as db:
                    alert = await event_orch.process(
                        frame=frame,
                        motion=motion,
                        yolo=yolo,
                        db=db,
                        snapshot_svc=snapshot_svc,
                    )

            # --- Build and stream payload ---
            payload = json.dumps(
                {
                    "frame": comp.frame_b64,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "motion_detected": motion.detected,
                    "person_detected": yolo.person_detected,
                    "motion_ratio": motion.motion_ratio,
                    "jpeg_quality": comp.jpeg_quality,
                    "scale": comp.scale,
                    "alert": alert,
                }
            )
            await websocket.send_text(payload)

            # Throttle to target FPS
            elapsed = time.monotonic() - tick
            sleep_for = max(0.0, frame_interval - elapsed)
            if sleep_for:
                await asyncio.sleep(sleep_for)

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected cleanly")
    except Exception as exc:
        logger.error("WebSocket stream error: %s", exc, exc_info=True)
    finally:
        manager.disconnect(websocket)
