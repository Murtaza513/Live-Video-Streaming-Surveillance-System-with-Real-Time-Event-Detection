import logging
from dataclasses import dataclass

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class YoloResult:
    person_detected: bool
    confidence: float   # highest confidence among detected persons
    count: int          # number of person detections above threshold


class YoloDetector:
    """
    Optional YOLOv8 person detector.

    Controlled by the ``enabled`` flag (maps to ENABLE_YOLO env var).
    If disabled, or if the model fails to load or infer, the detector
    degrades gracefully to a no-op that always returns no detection —
    the system falls back to motion-only mode transparently.
    """

    def __init__(self, model_path: str, enabled: bool, confidence: float = 0.4) -> None:
        self.confidence = confidence
        self._model = None

        if not enabled:
            logger.info("YOLOv8 detection disabled by configuration")
            return

        try:
            from ultralytics import YOLO  # lazy import to avoid load cost when disabled

            self._model = YOLO(model_path)
            logger.info("YOLOv8 model loaded: %s", model_path)
        except Exception as exc:
            logger.warning(
                "Failed to load YOLOv8 model (%s) — falling back to motion-only mode. "
                "Error: %s",
                model_path,
                exc,
            )
            self._model = None

    def detect(self, frame: np.ndarray) -> YoloResult:
        """
        Run person detection on a frame.
        Returns safe defaults (no detection) if the model is unavailable.
        """
        if self._model is None:
            return YoloResult(person_detected=False, confidence=0.0, count=0)

        try:
            # classes=[0] restricts inference to the COCO "person" class only
            results = self._model(frame, verbose=False, classes=[0])
            persons = [
                box
                for result in results
                for box in result.boxes
                if float(box.conf) >= self.confidence
            ]
            if persons:
                best_conf = max(float(b.conf) for b in persons)
                return YoloResult(
                    person_detected=True,
                    confidence=round(best_conf, 3),
                    count=len(persons),
                )
        except Exception as exc:
            logger.error("YOLO inference error: %s", exc)

        return YoloResult(person_detected=False, confidence=0.0, count=0)
