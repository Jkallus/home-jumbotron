from datetime import datetime
import logging
import os
from PIL import Image
from PIL.Image import Image as PILImage
logger = logging.getLogger(__name__)

class FrameSource():
    def __init__(self, name: str):
        # Specify the size of the image (Width, Height)
        self.image_size = (128, 128)
        self.send_black_frame_1 = False
        self.send_black_frame_2 = False
        self.name = name

    def get_frame(self) -> PILImage:
        if self.send_black_frame_1:
            self.send_black_frame_1 = False
            return Image.new('RGB', self.image_size, color=(0 ,0 ,0))
        elif self.send_black_frame_2:
            self.send_black_frame_2 = False
            return Image.new('RGB', self.image_size, color=(0 ,0 ,0))
        else:
            return self.create_frame()

    def create_frame(self) -> PILImage:
        raise NotImplementedError("Subclasses must override create_frame method")
    
    def __enter__(self):
        self.send_black_frame_1 = True
        self.send_black_frame_2 = True
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        pass