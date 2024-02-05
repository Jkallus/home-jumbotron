import logging
from queue import Queue
from threading import Thread
import time
from frame_sources.clock_frame_source import ClockFrameSource
from frame_sources.count_frame_source import CountFrameSource
from frame_sources.usb_cam_frame_source import USBCameraFrameSource
from sender import ZMQSender
from frame_maker import FrameMaker
import log_config

log_config.setup_logging()

logger = logging.getLogger(__name__)
logger.info("Image-Sender Started")

frames: Queue[bytes] = Queue()
commands: Queue[dict] = Queue()

sender: ZMQSender = ZMQSender(frames)
sender.start()

frame_maker: FrameMaker = FrameMaker(command_queue=commands, frame_queue=frames, frame_source=CountFrameSource())

try:        
    frame_maker.start()
    while True:
        pass
except KeyboardInterrupt:
    # Handle manual interrupt, clean up camera and close sockets
    logger.info("Interrupt received, stopping...")
finally:
    # When everything done, release the capture and close resources
    frame_maker.stop()
    sender.stop()
    logger.debug("Released all resources")