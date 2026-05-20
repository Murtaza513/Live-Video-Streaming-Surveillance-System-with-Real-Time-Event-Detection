import cv2
import numpy as np

from app.config import settings


class CameraService:
    def __init__(self) -> None:
        self.cap = cv2.VideoCapture(settings.webcam_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, settings.frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, settings.frame_height)

    def read(self) -> np.ndarray | None:
        if not self.cap.isOpened():
            return None
        ok, frame = self.cap.read()
        if not ok:
            return None
        return frame

    def close(self) -> None:
        if self.cap.isOpened():
            self.cap.release()
