from datetime import datetime
import logging
import os
from PIL import Image, ImageDraw, ImageFont
logger = logging.getLogger(__name__)

class FrameSource():
    def __init__(self):
        # Specify the size of the image (Width, Height)
        self.image_size = (128, 64)

    def get_frame(self) -> Image:
        raise Exception("Get frame called on base framesource, need to override")