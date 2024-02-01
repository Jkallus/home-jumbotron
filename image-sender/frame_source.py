from datetime import datetime
import logging
import os
from PIL import Image, ImageDraw, ImageFont
import pytz

logger = logging.getLogger(__name__)

class FrameSource():
    def __init__(self):
        # Load the font once during initialization
        font_path = os.path.join(os.getcwd(), "image-sender", "fonts", "10x20.pil")
        self.font = ImageFont.load(font_path)

        # Store the timezone once during initialization
        self.timezone = pytz.timezone('America/New_York')

        # Specify the size of the image (Width, Height)
        self.image_size = (128, 64)
        # Specify the background color (black) and text color (green)
        self.background_color = (0, 0, 0)  # Black
        self.text_color = (0, 255, 0)  # Green
        # Specify the position to render the text
        self.text_position = (0, 0)  # Top left corner of the image

        self.image = Image.new("RGB", self.image_size, self.background_color)
        self.draw = ImageDraw.Draw(self.image)

        logger.info("Initialized FrameSource")

        self.i = 0

    def get_frame(self) -> Image:
        # Create a new image with the specified size and color
        
        
        self.draw.rectangle([(self.text_position[0], self.text_position[1]), (self.image_size[0], self.image_size[1])], fill=self.background_color)

        # Get the current time and adjust for the timezone
        #current_time = datetime.now(pytz.utc)
        #adjusted_time = current_time.astimezone(self.timezone)
        #text = adjusted_time.strftime("%I:%M:%S.%f")[:-3]
        text = f"i: {self.i}"
        self.i = self.i + 1
        # Render the text on the image
        self.draw.text(self.text_position, text, font=self.font, fill=self.text_color)
        return self.image