from config import logger
import numpy as np
from typing import Optional

import cv2
from utils.vision.describer import Describer
from utils.vision.webcam import Webcam


class Watcher:
    """
    A class that manages vision functions.

    Attributes:
        describer: The describer used to describe images.
        device: The device used to capture images.
        _previous_frame (np.ndarray): The previous frame captured by the camera.
        
    Methods:
        describe(image): Describes the image.
        _is_diff_frame(frame): Check if the current frame is different from the previous frame.
        glance(): Captures an image from the camera and describes it.
        deactivate(): Deactivates the watching device.
    """
    
    def __init__(self, model_name: str, base_url: str):
        self.describer = Describer(model_name, base_url)
        self.device = Webcam() # this could support multiple input devices, use an initialize function to select the device later
        self._previous_frame = None
        
    def _is_diff_frame(self, frame: np.ndarray) -> bool:
        
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        if self._previous_frame is None:
            self._previous_frame = frame
            return True
        
        frame_diff = cv2.absdiff(frame, self._previous_frame)
        changed_pixels = np.sum(frame_diff > 10)
        change_percentage = changed_pixels / frame.size
        self._previous_frame = frame
        
        # logger.info(f"Watcher: Frame change detected. Percentage: {change_percentage}") 
        # only  return a description if there is significant change.
        return change_percentage > 0.4
    
    def glance(self) -> Optional[str]:
        frame = self.device.capture()
        
        if self._is_diff_frame(frame):
            timecontent = self.describer.describe("vision", frame)
            return timecontent
        
        return None
    
    def deactivate(self) -> None:
        # Deactivate the watching device.
        if self.device is not None:
            self.device.stop_watch()
