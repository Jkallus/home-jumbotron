import logging
from PIL import Image
import cv2
from frame_sources.frame_source import FrameSource

logger = logging.getLogger(__name__)

class USBCameraFrameSource(FrameSource):
    def __init__(self):
        super().__init__()
        
    def get_frame(self) -> Image:
        logger.debug("Capturing frame")
        if not self.cap.isOpened():
            raise Exception("Camera is not initialized or opened")
        
        ret, frame = self.cap.read()
        if not ret:
            logger.error("Failed to grab frame")
            raise Exception(f"Failed to grab frame")
        
        logger.debug("Grabbed frame")

        # Convert the captured frame from BGR to RGB color space
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        logger.debug("Converted frame to RGB")

        # Calculate new width to maintain aspect ratio
        height, width = rgb_frame.shape[:2]
        new_height = self.image_size[1]
        aspect_ratio = width / height
        new_width = int(aspect_ratio * new_height)

        # Resize the frame
        resized_frame = cv2.resize(rgb_frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
        logger.debug(f"Resized frame to {new_width}x{new_height}")

        # Convert the NumPy array to a PIL Image
        img = Image.fromarray(resized_frame)
        logger.debug("Converted NumPy array to PIL Image")

        return img

    def __enter__(self):
        logger.info("Initializing Webcam")
        self.cap = cv2.VideoCapture(0)  # Ensure the webcam index is correct (0 is typically the default)

    def __exit__(self, exc_type, exc_value, traceback):
        logger.info("Releasing Webcam")
        if self.cap.isOpened():
            self.cap.release()