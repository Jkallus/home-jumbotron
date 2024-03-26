from datetime import datetime
import logging
import os
from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Image as PILImage
import pytz

from .frame_source import FrameSource
from image_utils.analog_clock_util import get_clock_frame

logger = logging.getLogger(__name__)

class AnalogClockFrameSource(FrameSource):
    def __init__(self):
        super().__init__("AnalogClock")
        
        # Store the timezone once during initialization
        self.timezone = pytz.timezone('America/New_York')

        # Specify the background color (black) and text color (green)
        self.background_color = (0, 0, 0)  # Black
        
        self.image = Image.new("RGB", self.image_size, self.background_color)
        self.draw = ImageDraw.Draw(self.image)

        logger.info("Initialized Clock FrameSource")

    def create_frame(self) -> PILImage:
        return get_clock_frame()