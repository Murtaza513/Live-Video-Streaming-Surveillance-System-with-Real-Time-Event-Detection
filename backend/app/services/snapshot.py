import logging
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class SnapshotService:
    """
    Saves event-trigger frames as JPEG files on disk.

    Files are stored as:
        <snapshot_dir>/<event_type>_<YYYYMMDD_HHMMSS_microseconds>.jpg

    The relative path is returned for persistence in the database.
    """

    def __init__(self, snapshot_dir: str = "snapshots") -> None:
        self.snapshot_dir = Path(snapshot_dir)
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Snapshot directory: %s", self.snapshot_dir.resolve())

    def save(self, frame: np.ndarray, event_type: str) -> str | None:
        """
        Encode and write a frame to disk.

        Returns the relative file path string on success, or None on failure.
        """
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{event_type}_{ts}.jpg"
        filepath = self.snapshot_dir / filename

        ok, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if not ok:
            logger.error("Failed to encode snapshot frame for event '%s'", event_type)
            return None

        try:
            filepath.write_bytes(buffer.tobytes())
            logger.debug("Snapshot saved: %s", filepath)
            return str(filepath)
        except OSError as exc:
            logger.error("Failed to write snapshot to %s: %s", filepath, exc)
            return None
