import logging
import os
from threading import Lock, Thread
import time
from PIL import ImageFont, Image, ImageDraw
from PIL.Image import Image as PILImage
from dotenv import load_dotenv
from geopy import distance
from flight_radar_utils.flight_data_source import Box, FlightDataSource, Location
from frame_sources.frame_source import FrameSource

load_dotenv()

logger = logging.getLogger(__name__)

class FlightDataFrameSource(FrameSource):
    def __init__(self):
        super().__init__("Flight Data")

        font_path = os.path.join(os.getcwd(), "image-sender", "fonts", "6x13.pil")
        self.font = ImageFont.load(font_path)
        self.background_color = (0, 0, 0)  # Black
        self.arriving_color = (0, 255, 0)  # Green
        self.departing_color = (255, 255, 0) # yellow
        self.over_color = (255, 255, 255) # White
        self.image = Image.new("RGB", self.image_size, self.background_color)
        self.draw = ImageDraw.Draw(self.image)

        # Box
        x1 = os.getenv("X1")
        y1 = os.getenv("Y1")
        x2 = os.getenv("X2")
        y2 = os.getenv("Y2")

        if x1 is not None and y1 is not None and x2 is not None and y2 is not None:
            self.box = Box(float(x1), float(y1), float(x2), float(y2))
        else:
            raise Exception("Failed to load environment variables for FlightRadar24 bounding box")

        # Home
        x = os.getenv("X")
        y = os.getenv("Y")

        if x is not None and y is not None:
            self.home = Location(float(x), float(y))
        else:
            raise Exception("Failed to load environment variables for FlightRadar24 home location")
        
        self.run_updater = False

        logger.info("Constructed Flight Data FrameSource")

    def updater(self):
            while(self.run_updater):
                with self.flight_data_lock:
                    self.flight_data = self.data_source.get_flight_data()
                time.sleep(3)

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

                top_line = f"{flight['Aircraft']}, {flight['Distance']:{distance_format}}"
                bottom_line = f"{flight['Origin']} {flight['FlightNumber']}"

                color = None
                if flight["Direction"] == "In":
                    color = self.arriving_color
                elif flight["Direction"] == "Out":
                    color = self.departing_color
                elif flight["Direction"] == "Over":
                    color = self.over_color

                #text = f"{flight['Aircraft']} {flight['Speed']:3d} {flight['Distance']:{distance_format}} {flight['FlightNumber'][:6]} {flight['Direction']}"
                self.draw.text((0, cursor_y), top_line, font=self.font, fill=color)
                cursor_y += 12
                self.draw.text((0, cursor_y), bottom_line, font=self.font, fill=color)
                cursor_y += 12
                self.draw.line([(0, cursor_y), (self.image_size[1], cursor_y)], fill=(0,0,255))

        return self.image
    
    def __enter__(self):
        # Login
        self.email = os.getenv("FR24_EMAIL")
        self.password = os.getenv("FR24_PASSWORD")

        self.data_source = FlightDataSource(self.box, self.home, self.email, self.password)
        self.flight_data = self.data_source.get_flight_data()
        self.flight_data_lock = Lock()

        self.run_updater = True
        self.update_thread = Thread(target=self.updater, name="FlightRadar24 Updater")
        self.update_thread.start()

        logger.info("Initialized Flight Data FrameSource")
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.run_updater = False
        self.update_thread.join()
        logger.info("Deinitialized Flight Data FrameSource")