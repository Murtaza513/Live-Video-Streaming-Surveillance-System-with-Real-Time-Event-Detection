from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class MotionResult:
    detected: bool
    motion_ratio: float   # fraction of pixels that changed [0.0, 1.0]


class MotionDetector:
    """
    Frame-differencing motion detector.

    Pipeline per frame:
        BGR → Grayscale → Gaussian blur → absdiff with previous frame
        → binary threshold → morphological dilation → changed-pixel ratio

    Args:
        threshold:    Fraction of changed pixels required to declare motion.
        blur_kernel:  Size of the Gaussian blur kernel (must be odd).
    """

    def __init__(self, threshold: float = 0.03, blur_kernel: int = 21) -> None:
        self.threshold = threshold
        # Kernel must be odd and positive
        self.blur_kernel = blur_kernel if blur_kernel % 2 == 1 else blur_kernel + 1
        self._prev_gray: np.ndarray | None = None

    def detect(self, frame: np.ndarray) -> MotionResult:
        """Process one frame and return a MotionResult."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (self.blur_kernel, self.blur_kernel), 0)

        if self._prev_gray is None:
            # First frame — nothing to compare against
            self._prev_gray = gray
            return MotionResult(detected=False, motion_ratio=0.0)

        delta = cv2.absdiff(self._prev_gray, gray)
        _, thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)
        thresh = cv2.dilate(thresh, None, iterations=2)

        changed = float(np.count_nonzero(thresh))
        total = float(thresh.size)
        motion_ratio = changed / max(total, 1.0)

        self._prev_gray = gray
        return MotionResult(
            detected=motion_ratio >= self.threshold,
            motion_ratio=round(motion_ratio, 5),
        )
