import logging
import time

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class VideoCaptureService:
    """
    Wraps cv2.VideoCapture for a local webcam with automatic reconnect on failure.

    Usage:
        svc = VideoCaptureService(camera_index=0)
        frame = svc.read_frame()   # returns np.ndarray or None
        svc.close()
    """

    _MAX_RECONNECT_ATTEMPTS = 5
    _RECONNECT_DELAY_SECS = 2.0

    def __init__(self, camera_index: int) -> None:
        self.camera_index = camera_index
        self._cap: cv2.VideoCapture | None = None
        self._connect()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _connect(self) -> None:
        for attempt in range(1, self._MAX_RECONNECT_ATTEMPTS + 1):
            cap = cv2.VideoCapture(self.camera_index)
            if cap.isOpened():
                self._cap = cap
                logger.info("Camera index %d opened successfully", self.camera_index)
                return
            cap.release()
            logger.warning(
                "Camera %d not available (attempt %d/%d) — retrying in %.1fs",
                self.camera_index,
                attempt,
                self._MAX_RECONNECT_ATTEMPTS,
                self._RECONNECT_DELAY_SECS,
            )
            time.sleep(self._RECONNECT_DELAY_SECS)

        raise RuntimeError(
            f"Unable to open camera index {self.camera_index} after "
            f"{self._MAX_RECONNECT_ATTEMPTS} attempts"
        )

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def read_frame(self) -> np.ndarray | None:
        """Read one frame from the camera. Returns None on transient failure."""
        if self._cap is None or not self._cap.isOpened():
            logger.error("Camera not open — attempting reconnect")
            try:
                self._connect()
            except RuntimeError:
                return None

        ok, frame = self._cap.read()
        if not ok or frame is None:
            logger.warning("Failed to read frame from camera %d", self.camera_index)
            return None

        return frame

    def close(self) -> None:
        """Release the underlying VideoCapture resource."""
        if self._cap and self._cap.isOpened():
            self._cap.release()
            logger.info("Camera %d released", self.camera_index)
