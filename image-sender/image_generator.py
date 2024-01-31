from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime
import pytz

def get_buffer_bytes_from_img(img: Image) -> bytes:
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    image_byte_buffer = buffer.getvalue()
    buffer.close()
    return image_byte_buffer

def get_test_image() -> Image:
    font_path = os.getcwd() + "/image-sender/fonts/10x20.pil"
    font_size = 24
    font = ImageFont.load(font_path)



    # Specify the size of the image
    image_size = (128, 64)
    # Specify the background color (black) and text color (green)
    background_color = (0, 0, 0)  # Black
    text_color = (0, 255, 0)  # Green

    # Create a new image with the specified size and color
    #image = Image._new("RGB", image_size, background_color)
    image = Image.new("RGB", image_size, background_color)
    draw = ImageDraw.Draw(image)

    # Specify the position and text to render
    text_position = (0, 0)  # Top left corner of the image

    
    timezone = pytz.timezone('America/New_York')
    current_time = datetime.now(pytz.utc)
    adjusted_time = current_time.astimezone(timezone)
    

    text = adjusted_time.strftime("%I:%M:%S.%f")[:-3]

    # Render the text on the image
    draw.text(text_position, text, font=font, fill=text_color)

    return image

def generate_moving_square_image(square_y_position) -> Image:
    global square_x_position, movement_direction
    
    # Set square properties and image size
    square_size = 4
    img_size = 64
    square_color = (0, 255, 0)  # Green color in RGB
    background_color = (0, 0, 0)  # Black color in RGB
    
    # Create new image with black background
    img = Image.new("RGB", (img_size, img_size), background_color)
    draw = ImageDraw.Draw(img)
    
    # Calculate the square's corner positions
    square_left = square_x_position
    square_right = square_left + square_size
    square_top = square_y_position
    square_bottom = square_top + square_size
    
    # Draw the green square
    draw.rectangle([(square_left, square_top), (square_right - 1, square_bottom - 1)], fill=square_color)
    
    # Update square_x_position for next call
    square_x_position += movement_direction
    
    # Check for horizontal bounds and change direction if necessary. 
    if square_right >= (img_size - 1) and movement_direction > 0:
        movement_direction *= -1  # Reverse direction to left
    elif square_left <= 0 and movement_direction < 0:
        movement_direction *= -1  # Reverse direction to right

    return img