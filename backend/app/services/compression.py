import cv2
import numpy as np

from app.config import settings


class AdaptiveCompressor:
    def __init__(self) -> None:
        self.min_quality = settings.min_jpeg_quality
        self.max_quality = settings.max_jpeg_quality
        self.base_width = settings.frame_width
        self.base_height = settings.frame_height

    def compress(self, frame: np.ndarray, motion_intensity: float) -> bytes:
        normalized = min(max(motion_intensity / 100.0, 0.0), 1.0)
        quality = int(self.max_quality - (self.max_quality - self.min_quality) * normalized)

        scale = 1.0 - (0.35 * normalized)
        width = max(320, int(self.base_width * scale))
        height = max(240, int(self.base_height * scale))

        resized = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
        encoded, buffer = cv2.imencode('.jpg', resized, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
        if not encoded:
            raise RuntimeError('Failed to encode frame')
        return buffer.tobytes()
