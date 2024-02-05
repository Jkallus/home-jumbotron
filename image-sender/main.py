import logging
from queue import Queue
from threading import Thread
import time
from frame_sources.clock_frame_source import ClockFrameSource
from frame_sources.count_frame_source import CountFrameSource
from frame_sources.frame_source import FrameSource
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

sources: list[FrameSource] = [CountFrameSource(), ClockFrameSource(), USBCameraFrameSource()]

frame_maker: FrameMaker = FrameMaker(command_queue=commands, frame_queue=frames, frame_source=sources[0])
frame_maker.start()

try:
    current_source_idx = 0
    frame_maker.set_frame_source(sources[current_source_idx])
    start_time = time.time()
    
    while True:
        time.sleep(0.1)  # Sleep to prevent tight loop (optional, can be adjusted)
        elapsed_time = time.time() - start_time
        if elapsed_time >= 10:
            current_source_idx = (current_source_idx + 1) % len(sources)
            frame_maker.set_frame_source(sources[current_source_idx])
            start_time = time.time()  # Reset the timer    
except KeyboardInterrupt:
    # Handle manual interrupt, clean up camera and close sockets
    logger.info("Interrupt received, stopping...")
finally:
    # When everything done, release the capture and close resources
    frame_maker.stop()
    sender.stop()
    logger.debug("Released all resources")