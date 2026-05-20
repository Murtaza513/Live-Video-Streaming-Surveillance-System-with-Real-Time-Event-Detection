from dataclasses import dataclass
import logging

import cv2
import numpy as np

from app.config import settings


@dataclass
class DetectionResult:
    event_type: str | None
    confidence: float
    motion_intensity: float


class MotionAndPersonDetector:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.previous_gray: np.ndarray | None = None
        self.yolo_model = None

        if settings.enable_yolo:
            try:
                from ultralytics import YOLO

                self.yolo_model = YOLO(settings.yolo_model)
            except Exception as exc:
                self.logger.warning('YOLO initialization failed, falling back to motion detection: %s', exc)
                self.yolo_model = None

    def _motion_score(self, frame: np.ndarray) -> float:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if self.previous_gray is None:
            self.previous_gray = gray
            return 0.0

        delta = cv2.absdiff(self.previous_gray, gray)
        thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
        motion_pixels = float(np.count_nonzero(thresh))
        total_pixels = float(thresh.size)
        self.previous_gray = gray
        return (motion_pixels / max(total_pixels, 1.0)) * 100.0

    def _person_detected(self, frame: np.ndarray) -> float:
        if self.yolo_model is None:
            return 0.0

        results = self.yolo_model(frame, verbose=False)
        max_conf = 0.0
        for result in results:
            for box in result.boxes:
                cls = int(box.cls[0].item())
                conf = float(box.conf[0].item())
                if cls == 0 and conf > max_conf:
                    max_conf = conf
        return max_conf

    def analyze(self, frame: np.ndarray) -> DetectionResult:
        motion_intensity = self._motion_score(frame)
        person_conf = self._person_detected(frame)

        if person_conf > 0.5:
            return DetectionResult(event_type='person', confidence=person_conf, motion_intensity=motion_intensity)
        if motion_intensity >= settings.motion_threshold:
            normalized = min(1.0, motion_intensity / 100.0)
            return DetectionResult(event_type='motion', confidence=normalized, motion_intensity=motion_intensity)
        return DetectionResult(event_type=None, confidence=0.0, motion_intensity=motion_intensity)
