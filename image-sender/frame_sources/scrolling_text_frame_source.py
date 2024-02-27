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
        super().__init__()
        font_path = os.path.join(os.getcwd(), "image-sender", "fonts", "clR6x12.pil")
        self.font = ImageFont.load(font_path)

        self.text_source = NBACommentsTextSource()

        # Specify the background color (black) and text color (green)
        self.text_color = (0, 255, 0)  # Green
        self.background_color = (0, 0, 0)  # Black

        logger.info("Initialized Scrolling Text FrameSource")

        self.image = PILImage.new("RGB", self.image_size, self.background_color)
        self.draw = ImageDraw.Draw(self.image)

        self.messages = self.text_source.get_new_messages()

        self.subframes: list[Image] = [generate_subframe(message, self.font, (6, 12), self.image_size, self.text_color) for message in self.messages]
        self.appended: Image = append_subframes(self.subframes)
        self.vertical_pixels_per_second = 15
        self.window_offset = 0

        def text_swapper():
            while(True):
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
        
        self.appended_lock = threading.Lock()
        self.update_thread = threading.Thread(target=text_swapper)
        self.update_thread.start()
        
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