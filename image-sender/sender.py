from queue import Queue
from threading import Thread
import zmq
import logging

logger = logging.getLogger(__name__)

class ZMQSender:
    def __init__(self, frame_queue: Queue[bytes]):
        self.frame_queue = frame_queue
        self.context = zmq.Context()
        self.sock = self.context.socket(zmq.PUB)
        self.sock.bind("tcp://*:5555")
        logger.info("Created ZMQSender")

    def sender(self):
        while(True):
            logger.debug("Getting frame from queue")
            frame = self.frame_queue.get()
            if frame is None:
                break
            try:
                topic = '/frames'
                logger.debug("Sending frame over ZMQ")
                self.sock.send(topic.encode('ascii') + frame)
            except zmq.ZMQError as e:
                logger.error(f"Failed to send frame: {e}")
            self.frame_queue.task_done()

    def start(self):        
        self.sender_thread = Thread(target=self.sender)
        self.sender_thread.start()            
        logger.info("Started ZMQSender")

    def stop(self):
        # Signal the sender thread to stop.
        self.frame_queue.put(None)
        # Wait for the sender thread to finish.
        self.sender_thread.join()
        # Clean up the ZeroMQ socket and context.
        self.sock.close()
        self.context.term()
        logger.info("ZMQSender Stopped")
        logger.debug("ZeroMQ context terminated and socket closed")