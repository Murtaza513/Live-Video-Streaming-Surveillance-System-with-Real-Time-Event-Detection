import base64
import logging
from dataclasses import dataclass

import cv2
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class CompressionResult:
    frame_b64: str      # base64-encoded JPEG string ready for JSON transport
    jpeg_quality: int   # quality value actually used
    scale: float        # resolution scale factor actually used (1.0 = original)


class AdaptiveCompressor:
    """
    Dynamically adjusts JPEG quality and frame resolution based on motion intensity.

    Strategy:
        - Low motion  → high quality + full resolution  (preserves detail in calm scenes)
        - High motion → low quality  + reduced resolution (reduces bandwidth during busy periods)

    Both quality and scale are linearly interpolated from motion_ratio ∈ [0, 1].
    """

    def __init__(
        self,
        base_quality: int = 75,
        min_quality: int = 40,
        max_quality: int = 90,
    ) -> None:
        self.min_quality = min_quality
        self.max_quality = max_quality

    def _quality_for(self, motion_ratio: float) -> int:
        """Inversely map motion_ratio → JPEG quality."""
        clamped = min(max(motion_ratio, 0.0), 1.0)
        quality = int(self.max_quality - clamped * (self.max_quality - self.min_quality))
        return max(self.min_quality, min(self.max_quality, quality))

    def _scale_for(self, motion_ratio: float) -> float:
        """Inversely map motion_ratio → resolution scale [0.5, 1.0]."""
        clamped = min(max(motion_ratio, 0.0), 1.0)
        return round(1.0 - clamped * 0.5, 2)

    def compress(self, frame: np.ndarray, motion_ratio: float) -> CompressionResult:
        """Encode a frame to a base64 JPEG string with adaptive quality and scale."""
        quality = self._quality_for(motion_ratio)
        scale = self._scale_for(motion_ratio)

        # Resize when scale is less than 1.0 to reduce payload size
        if scale < 1.0:
            h, w = frame.shape[:2]
            new_w = max(1, int(w * scale))
            new_h = max(1, int(h * scale))
            display_frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
        else:
            display_frame = frame

        ok, buffer = cv2.imencode(".jpg", display_frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
        if not ok:
            logger.error("Failed to JPEG-encode frame; returning empty payload")
            return CompressionResult(frame_b64="", jpeg_quality=quality, scale=scale)

        frame_b64 = base64.b64encode(buffer.tobytes()).decode("utf-8")
        return CompressionResult(frame_b64=frame_b64, jpeg_quality=quality, scale=scale)
