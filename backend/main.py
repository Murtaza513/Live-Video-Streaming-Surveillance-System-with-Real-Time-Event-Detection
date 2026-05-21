import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.events import router as events_router
from app.api.stream import router as stream_router
from app.core.config import settings
from app.core.database import Base, engine
from app.core.logging import configure_logging

# Import model so SQLAlchemy registers it with Base.metadata before create_all
from app.models.event import Event  # noqa: F401
from app.services.compression import AdaptiveCompressor
from app.services.detection import MotionDetector
from app.services.event_service import EventOrchestrator
from app.services.snapshot import SnapshotService
from app.services.video_capture import VideoCaptureService
from app.services.yolo_detector import YoloDetector

configure_logging()
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Application lifespan — startup and shutdown hooks
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Create database tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema verified / created")

    # 2. Initialise all services and attach to app.state
    app.state.video_service = VideoCaptureService(settings.camera_index)

    app.state.motion_detector = MotionDetector(
        threshold=settings.motion_threshold,
        blur_kernel=settings.motion_blur_kernel,
    )
    app.state.yolo_detector = YoloDetector(
        model_path=settings.yolo_model,
        enabled=settings.enable_yolo,
        confidence=settings.person_confidence,
    )
    app.state.compressor = AdaptiveCompressor(
        base_quality=settings.base_jpeg_quality,
        min_quality=settings.min_jpeg_quality,
        max_quality=settings.max_jpeg_quality,
    )
    app.state.snapshot_service = SnapshotService(snapshot_dir=settings.snapshot_dir)
    app.state.event_orchestrator = EventOrchestrator(
        cooldown_seconds=settings.event_cooldown_seconds,
    )
    logger.info("All services started — streaming on camera index %d", settings.camera_index)

    yield  # Application runs here

    # 3. Graceful shutdown
    app.state.video_service.close()
    logger.info("Services shut down cleanly")


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Real-time video surveillance platform with adaptive streaming and event detection.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST event history
app.include_router(events_router, prefix="/api/v1", tags=["events"])

# WebSocket video stream
app.include_router(stream_router, prefix="/ws", tags=["stream"])

# Serve saved event snapshots as static files
_snapshots_path = Path(settings.snapshot_dir)
_snapshots_path.mkdir(parents=True, exist_ok=True)
app.mount("/snapshots", StaticFiles(directory=str(_snapshots_path)), name="snapshots")


@app.get("/health", tags=["health"])
async def health_check():
    """Quick liveness check."""
    return {"status": "ok", "app": settings.app_name, "env": settings.app_env}
