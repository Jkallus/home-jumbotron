
import logging
from queue import Queue
from frame_maker import FrameMaker
from frame_sources.clock_frame_source import ClockFrameSource
from frame_sources.count_frame_source import CountFrameSource
from frame_sources.flight_data_frame_source import FlightDataFrameSource
from frame_sources.frame_source import FrameSource
from frame_sources.moving_green_square_source import MovingSquareSource
from frame_sources.scrolling_text_frame_source import ScrollingTextFrameSource
from frame_sources.usb_cam_frame_source import USBCameraFrameSource

from sender import ZMQSender


logger = logging.getLogger(__name__)

class InputController:
    def __init__(self) -> None:
        logger.info("Initializing InputController")
        self.frames: Queue[bytes] = Queue()
        self.commands: Queue[bytes] = Queue()

        self.sender: ZMQSender = ZMQSender(self.frames)
        

        self.sources: dict[str, FrameSource] = {
            "Count": CountFrameSource(),
            "Clock": ClockFrameSource(),
            "Camera": USBCameraFrameSource(),
            "Square": MovingSquareSource(),
            "ScrollingText": ScrollingTextFrameSource(),
            "FlightRadar24": FlightDataFrameSource()
        }

        self.frame_maker: FrameMaker = FrameMaker(command_queue=self.commands, frame_queue=self.frames, frame_source=self.sources["Clock"])
        

    def start(self) -> None:
        self.sender.start()
        self.frame_maker.start()
        
    def stop(self) -> None:
        logging.info("Stopping InputController")
        self.frame_maker.stop()
        self.sender.stop()
        logging.info("InputController stopped")

    def set_source(self, source_name: str):
        self.frame_maker.set_frame_source(self.sources[source_name])