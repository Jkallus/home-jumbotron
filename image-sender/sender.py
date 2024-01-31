import cv2
import zmq
import numpy as np
from PIL import Image
from io import BytesIO
import time
import logging

# Initialize logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# ZeroMQ Context
logger.debug("Initializing ZeroMQ Context")
context = zmq.Context()

# Define the socket using the "Context"
logger.debug("Setting up the publisher socket on TCP port 5555")
sock = context.socket(zmq.PUB)
sock.bind("tcp://*:5555")

# Initialize USB webcam feed
logger.debug("Accessing the webcam")
cap = cv2.VideoCapture(0)  # Ensure the webcam index is correct (0 is typically the default)

try:
    while True:
        logger.debug("Capturing frame")
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            logger.error("Failed to grab frame")
            break

        logger.debug("Captured frame")

        # Convert the captured frame from BGR to RGB color space
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        logger.debug("Converted frame to RGB")

        # Calculate new width to maintain aspect ratio
        height, width = rgb_frame.shape[:2]
        new_height = 64
        aspect_ratio = width / height
        new_width = int(aspect_ratio * new_height)

        # Resize the frame
        resized_frame = cv2.resize(rgb_frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
        logger.debug(f"Resized frame to {new_width}x{new_height}")

        # Convert the NumPy array to a PIL Image
        img = Image.fromarray(resized_frame)
        logger.debug("Converted NumPy array to PIL Image")

        # Create a bytes buffer for the image and save as PNG
        buf = BytesIO()
        img.save(buf, format='PNG')

        # Byte data
        img_data = buf.getvalue()
        logger.debug("Saved image as byte buffer")

        # Prepare and send the images over ZeroMQ
        topic = '/frames'
        sock.send(topic.encode('ascii') + img_data)  
        logger.debug("Sent image data over ZeroMQ")

        # Frame sending interval
        #time.sleep(0.1)
        # Here you could add a display the image if desired.
        # cv2.imshow('Frame', rgb_frame)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

except KeyboardInterrupt:
    # Handle manual interrupt, clean up camera and close sockets
    logger.info("Interrupt received, stopping...")

finally:
    # When everything done, release the capture and close resources
    cap.release()
    sock.close()
    context.term()
    cv2.destroyAllWindows()
    logger.debug("Released all resources")