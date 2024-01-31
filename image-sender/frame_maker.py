from queue import Queue
import logging
from threading import Thread
import time

from frame_source import FrameSource
from image_generator import get_buffer_bytes_from_img

logger = logging.getLogger(__name__)

class FrameMaker():
    def __init__(self, command_queue: Queue[dict], frame_queue: Queue[bytes]):
        self.command_queue = command_queue
        self.frame_queue = frame_queue
        self.frame_source: FrameSource = FrameSource()
        self.running = False
        logger.info("Initialized FrameMaker")

    def generator(self):
        frame_interval = 1.0 / 30  # Target frame interval for 30 FPS
        while self.running:
            start_time = time.time()  # Record the start time
            
            logger.debug("Getting frame")
            image = self.frame_source.get_frame()
            
            logger.debug("Getting bytes")
            bytes = get_buffer_bytes_from_img(image)
            
            self.frame_queue.put(bytes)
            logger.debug("Frame put in queue")
            
            end_time = time.time()  # Record the end time
            processing_time = end_time - start_time  # Calculate processing time
            
            # Calculate remaining time to wait, if processing_time < frame_interval
            time_to_wait = frame_interval - processing_time
            if time_to_wait > 0:
                time.sleep(time_to_wait)
                
        logger.info("Generator thread stopping")

    def start(self):
        self.generator_thread = Thread(target=self.generator)
        self.running = True
        self.generator_thread.start()
        logger.info("Started FrameMaker")

    def stop(self):
        self.running = False
        self.generator_thread.join()
        logger.info("Stopped FrameMaker")