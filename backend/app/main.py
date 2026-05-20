import asyncio
import base64
import json
import logging
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.events import router as events_router
from app.config import settings
from app.db.base import Base
from app.db.session import engine, get_session
from app.logging_config import configure_logging
from app.services.compression import AdaptiveCompressor
from app.services.detection import MotionAndPersonDetector
from app.services.event_repository import EventRepository
from app.services.video_capture import CameraService

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.include_router(events_router)

camera_service = CameraService()
detector = MotionAndPersonDetector()
compressor = AdaptiveCompressor()


@app.on_event('startup')
async def startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event('shutdown')
def shutdown() -> None:
    camera_service.close()


@app.get('/health')
async def health() -> dict[str, str]:
    return {'status': 'ok'}


@app.websocket('/ws/stream')
async def stream_endpoint(websocket: WebSocket, session: AsyncSession = Depends(get_session)) -> None:
    await websocket.accept()
    repository = EventRepository(session)

    try:
        while True:
            frame = camera_service.read()
            if frame is None:
                await websocket.send_text(json.dumps({'type': 'error', 'message': 'Unable to read webcam frame'}))
                await asyncio.sleep(1.0)
                continue

            detection = detector.analyze(frame)
            encoded = compressor.compress(frame, detection.motion_intensity)
            frame_b64 = base64.b64encode(encoded).decode('utf-8')

            payload = {
                'type': 'frame',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'image': frame_b64,
                'event_type': detection.event_type,
                'confidence': detection.confidence,
                'motion_intensity': detection.motion_intensity,
            }

            if detection.event_type:
                message = (
                    f"{detection.event_type.title()} detected "
                    f"(confidence={detection.confidence:.2f}, motion={detection.motion_intensity:.2f}%)"
                )
                await repository.add_event(
                    event_type=detection.event_type,
                    confidence=detection.confidence,
                    message=message,
                )
                logger.info(message)

            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(1 / max(settings.websocket_fps, 1))

    except WebSocketDisconnect:
        logger.info('Client disconnected from stream')
    except Exception as exc:
        logger.exception('Streaming error: %s', exc)
        await websocket.close(code=1011)
