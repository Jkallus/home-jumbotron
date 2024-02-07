import logging
from queue import Queue
from threading import Thread
import time
from frame_sources.clock_frame_source import ClockFrameSource
from frame_sources.count_frame_source import CountFrameSource
from frame_sources.frame_source import FrameSource
from frame_sources.usb_cam_frame_source import USBCameraFrameSource
from input_controller import InputController
from sender import ZMQSender
from frame_maker import FrameMaker
import log_config

memory_handler = log_config.setup_logging()

logger = logging.getLogger(__name__)
logger.info("Image-Sender Started")

controller = InputController()
try:
    controller.start()
    while(True):
        controller.set_source("Square")
        time.sleep(10)
        controller.set_source("Count")
        time.sleep(10)
        # controller.set_source("Clock")
        # time.sleep(3)
        # controller.set_source("Camera")
        # time.sleep(3)
except KeyboardInterrupt:
    # Handle manual interrupt, clean up camera and close sockets
    logger.info("Interrupt received, stopping...")
except Exception as e:
    logger.exception("Caught an exception")
finally:
    # When everything done, release the capture and close resources
    controller.stop()
    logger.debug("Released all resources")
    logger.info("Image-Sender exiting")
    memory_handler.flush()