# logconfig.py

import logging
from logging.handlers import MemoryHandler
import time
import atexit

start_time = time.time()

class ElapsedTimeFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        elapsed_seconds = record.created - start_time
        elapsed_time = time.strftime("%H:%M:%S", time.gmtime(elapsed_seconds)) + f".{int(record.msecs):03d}"
        return elapsed_time

def setup_logging(logfile='application.log', buffer_size=10000, flush_level=logging.ERROR):
    formatter = ElapsedTimeFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create a file handler that logs messages to a file
    file_handler = logging.FileHandler(logfile, mode='a', encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # Console handler for INFO level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Create a MemoryHandler with a buffer size and a flush level
    memory_handler = MemoryHandler(capacity=buffer_size, flushLevel=flush_level, target=file_handler)

    # Get the root logger
    root_logger = logging.getLogger()
    
    # If the root logger already has handlers, remove them
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
    
    # Add the MemoryHandler to the root logger
    root_logger.addHandler(memory_handler)

    # Add the console handler to the root logger
    root_logger.addHandler(console_handler)

    # Set the logging level to the lowest level required by handlers
    root_logger.setLevel(logging.DEBUG)

    # Register the flush method of memory_handler to be called at exit
    atexit.register(memory_handler.flush)