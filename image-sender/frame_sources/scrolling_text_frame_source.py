from collections import deque
import logging
import os
import threading
from math import ceil, floor
import time
import PIL.Image as PILImage
from PIL.Image import Image
from PIL import ImageDraw, ImageFont
from frame_sources.frame_source import FrameSource
from image_utils.text_display import append_subframes, generate_subframe
from reddit_utils.nba_comments_text_source import NBACommentsTextSource
from reddit_utils.test_text_source import TestTextSource
from reddit_utils.text_source import TextSource

logger = logging.getLogger(__name__)

class ScrollingTextFrameSource(FrameSource):
    def __init__(self):
        super().__init__("Scrolling Text")
        font_path = os.path.join(os.getcwd(), "image-sender", "fonts", "clR6x12.pil")
        self.font = ImageFont.load(font_path)

        # Specify the background color (black) and text color (green)
        self.text_color = (0, 255, 0)  # Green
        self.background_color = (0, 0, 0)  # Black
        self.image = PILImage.new("RGB", self.image_size, self.background_color)
        self.draw = ImageDraw.Draw(self.image)

        self.run_swapper = False

        logger.info("Constructed Scrolling Text FrameSource")
        
        
        
    def create_frame(self) -> Image:
        self.draw.rectangle(((0, 0), self.image_size), fill=self.background_color) # Empty the image

        left = 0
        upper = 0 + floor(self.window_offset)
        right = self.image_size[0]
        lower = self.image_size[1] + floor(self.window_offset)
        box = (left, upper, right, lower)
        with self.appended_lock:
            window = self.appended.crop(box)
        
        frame_time = 1 / 60
        self.window_offset += self.vertical_pixels_per_second * frame_time

        return window
    
    def text_swapper(self):
            while(self.run_swapper):
                crop_lower_edge = self.window_offset + self.image_size[1]
                total_height = self.appended.size[1]
                remaining_scroll = total_height - floor(crop_lower_edge)
                if remaining_scroll < 30:
                    logger.info(f"Remaining scroll is {remaining_scroll}")
                    self.messages = self.text_source.get_new_messages()
                    logger.info(f"Got new messages")
                    new_subframes = [generate_subframe(message, self.font, (6, 12), self.image_size, self.text_color) for message in self.messages]
                    with self.appended_lock:
                        old_frame_rollover_height = self.image_size[1] + remaining_scroll
                        left = 0
                        top = total_height - old_frame_rollover_height
                        right = self.appended.size[0]
                        bottom = total_height
                        old_frame_rollover = self.appended.crop((left, top, right, bottom))
                        self.subframes = [old_frame_rollover]
                        self.subframes.extend(new_subframes)
                        self.appended = append_subframes(self.subframes)
                        logger.info(f"Swapping buffer, new total length is {self.appended.size[1]}")
                        self.window_offset = 0
                time.sleep(0.5)
                pass
    
    def __enter__(self):
        if not hasattr(self, 'text_source') or self.text_source is None:
            try:
                self.text_source = NBACommentsTextSource()
            except Exception as ex:
                logger.error("Exception occurred initializing NBACommentsTextSource", exc_info=True)
                raise  # Re-raise the exception to handle it outside
        
        self.messages = self.text_source.get_new_messages()

        self.subframes: list[Image] = [generate_subframe(message, self.font, (6, 12), self.image_size, self.text_color) for message in self.messages]
        self.appended: Image = append_subframes(self.subframes)
        self.vertical_pixels_per_second = 15
        self.window_offset = 0

        if not hasattr(self, 'appended_lock'):
            self.appended_lock = threading.Lock()
        if not hasattr(self, 'update_thread') or not self.update_thread.is_alive():
            self.run_swapper = True
            self.update_thread = threading.Thread(target=self.text_swapper)
            self.update_thread.start()

        logger.info("Initialized Scrolling Text FrameSource")

    def __exit__(self, exc_type, exc_value, traceback):
        self.run_swapper = False
        self.update_thread.join()