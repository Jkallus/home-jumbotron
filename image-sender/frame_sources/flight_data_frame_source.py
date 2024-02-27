import logging
import os
from threading import Lock, Thread
import time
from PIL import ImageFont, Image, ImageDraw
from PIL.Image import Image as PILImage
from dotenv import load_dotenv
from flight_radar_utils.flight_data_source import Box, FlightDataSource, Location
from frame_sources.frame_source import FrameSource

load_dotenv()

logger = logging.getLogger(__name__)

class FlightDataFrameSource(FrameSource):
    def __init__(self):
        super().__init__()

        font_path = os.path.join(os.getcwd(), "image-sender", "fonts", "5x8.pil")
        self.font = ImageFont.load(font_path)
        self.background_color = (0, 0, 0)  # Black
        self.text_color = (0, 255, 0)  # Green
        self.image = Image.new("RGB", self.image_size, self.background_color)
        self.draw = ImageDraw.Draw(self.image)

        # Box
        x1 = os.getenv("X1")
        y1 = os.getenv("Y1")
        x2 = os.getenv("X2")
        y2 = os.getenv("Y2")

        if x1 is not None and y1 is not None and x2 is not None and y2 is not None:
            box = Box(float(x1), float(y1), float(x2), float(y2))
        else:
            raise Exception("Failed to load environment variables for FlightRadar24 bounding box")

        # Home
        x = os.getenv("X")
        y = os.getenv("Y")

        if x is not None and y is not None:
            home = Location(float(x), float(y))
        else:
            raise Exception("Failed to load environment variables for FlightRadar24 home location")
        
        # Login
        email = os.getenv("FR24_EMAIL")
        password = os.getenv("FR24_PASSWORD")

        self.data_source = FlightDataSource(box, home, email, password)

        self.flight_data = self.data_source.get_flight_data()
        self.flight_data_lock = Lock()

        def updater():
            while(True):
                with self.flight_data_lock:
                    self.flight_data = self.data_source.get_flight_data()
                time.sleep(3)

        self.update_thread = Thread(target=updater, name="FlightRadar24 Updater")
        self.update_thread.start()

        

    def create_frame(self) -> PILImage:
        with self.flight_data_lock:
            self.draw.rectangle(((0, 0), self.image_size), fill=self.background_color) # Empty the image
            cursor_y = 0
            sorted_flights = sorted(self.flight_data, key=lambda flight: flight['Distance'])

            for flight in sorted_flights:
                if flight['Distance'] < 10:
                    distance_format = "0.2f"
                elif flight['Distance'] < 100:
                    distance_format = "0.1f"
                elif flight['Distance'] < 1000:
                    distance_format = "0.0f"
                else:
                    distance_format = "0.0f"
                text = f"{flight['Aircraft']} {flight['Speed']:3d} {flight['Distance']:{distance_format}} {flight['FlightNumber'][:6]} {flight['Direction']}"
                self.draw.text((0, cursor_y), text, font=self.font, fill=self.text_color)
                cursor_y += 8

        return self.image