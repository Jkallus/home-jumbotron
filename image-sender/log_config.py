# logconfig.py

import logging
from logging.handlers import MemoryHandler
import queue
import threading
import time
import atexit

log_config_logger = logging.getLogger('log_config')

start_time = time.time()

class ElapsedTimeFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        elapsed_seconds = record.created - start_time
        elapsed_time = time.strftime("%H:%M:%S", time.gmtime(elapsed_seconds)) + f".{int(record.msecs):03d}"
        return elapsed_time

class ThreadedMemoryHandler(MemoryHandler):
    def __init__(self, capacity, flushLevel=logging.ERROR, target=None):
        super().__init__(capacity, flushLevel, target)
        self.flush_queue = queue.Queue()
        self.flush_thread = threading.Thread(target=self.flusher)
        self.flush_thread.daemon = True
        self.flush_thread.start()
        self._flush_event = threading.Event()  # Create an event to signal when flushing is done

    def flusher(self):
        while True:
            to_flush = self.flush_queue.get()
            for record in to_flush:
                self.target.handle(record)
            self.flush_queue.task_done()
            self._flush_event.set()  # Signal that flushing is done

    def flush(self):
        self.acquire()
        try:
            if len(self.buffer) > 0:
                self._flush_event.clear()  # Clear the event before putting items in the queue
                self.flush_queue.put(self.buffer)
                self.buffer = []
                self.release()  # Release the lock before waiting for the event
                self._flush_event.wait()  # Wait for the flusher to signal that it's done
            else:
                self.release()
        except Exception as e:
            # Log exception if something goes wrong during flush
            log_config_logger.exception("Exception occurred during flush: %s", e)
            self.release()


def setup_logging(logfile='application.log', buffer_size=1000, flush_level=logging.ERROR):
    formatter = ElapsedTimeFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create a file handler that logs messages to a file
    file_handler = logging.FileHandler(logfile, mode='w', encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # Console handler for INFO level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Create a ThreadedMemoryHandler with a buffer size and a flush level
    memory_handler = ThreadedMemoryHandler(capacity=buffer_size, flushLevel=flush_level, target=file_handler)

    # Get the root logger
    root_logger = logging.getLogger()
    
    # If the root logger already has handlers, remove them
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
    
    # Add the ThreadedMemoryHandler to the root logger
    root_logger.addHandler(memory_handler)

    # Add the console handler to the root logger
    root_logger.addHandler(console_handler)

    # Set the logging level to the lowest level required by handlers
    root_logger.setLevel(logging.DEBUG)

    # Register the flush method of memory_handler to be called at exit
    atexit.register(memory_handler.flush)

    log_config_logger.debug("Logging is set up with file: %s", logfile)

    return memory_handler