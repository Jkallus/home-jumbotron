from io import BytesIO
from queue import Queue
import logging
from threading import Thread
import time
from PIL.Image import Image

from frame_sources.frame_source import FrameSource
from image_utils.text_display import write_debug_image

logger = logging.getLogger(__name__)

class FrameMaker:
    def __init__(self, frame_queue: Queue[bytes], frame_source: FrameSource):
        self.frame_queue = frame_queue
        self.frame_source = frame_source
        self.running = False
        logger.info("Initialized FrameMaker")

    def get_buffer_bytes_from_img(self, img: Image) -> bytes:
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        image_byte_buffer = buffer.getvalue()
        buffer.close()
        return image_byte_buffer

    def generator(self):
        frame_interval = 1.0 / 60  # Target frame interval for 60 FPS
        last_frame_start_time = 0
        current_frame_start_time = 0
        with self.frame_source:
            while self.running:
                last_frame_start_time = current_frame_start_time
                current_frame_start_time = time.time()
                
                #logger.debug("Getting frame")
                image = self.frame_source.get_frame()

                if image == None:
                    raise Exception("Failed to get frame")

                #write_debug_image(image)
                
                #logger.debug("Getting bytes")
                bytes = self.get_buffer_bytes_from_img(image)
                
                self.frame_queue.put(bytes)
                #logger.debug("Frame put in queue")
                
                frame_time = 1000 * (current_frame_start_time - last_frame_start_time)
                logger.debug(f"Frame to frame time: {frame_time:.3f} ms")
                
                end_time = time.time()  # Record the end time
                processing_time = end_time - current_frame_start_time  # Calculate processing time
                
                # Calculate remaining time to wait, if processing_time < frame_interval
                time_to_wait = frame_interval - processing_time
                if time_to_wait > 0:
                    time.sleep(time_to_wait)                    
            logger.info("Generator thread stopping")

    def start(self):
        self.generator_thread = Thread(target=self.generator)
        self.running = True
        logger.info("Starting FrameMaker")
        self.generator_thread.start()
        logger.info("FrameMaker Started")

    def set_frame_source(self, source: FrameSource):
        self.stop()
        logger.info(f"Changing frame source to {source.name}")
        self.frame_source = source
        self.start()
        
    def stop(self):
        self.running = False
        self.generator_thread.join()
        logger.info("Stopped FrameMaker")