from datetime import datetime
from math import ceil, floor
import os
from typing import Tuple
from PIL.Image import Image
import PIL.Image as PILImage
from PIL import ImageDraw
from PIL.ImageFont import ImageFont
from textwrap import wrap

def wrap_text(text: str, font: ImageFont, font_size: Tuple[int, int], canvas_width: int) -> list:
    words = text.split()
    lines = []
    current_line = ''
    max_chars = canvas_width // font_size[0]  # Calculate max number of characters per line

    for word in words:
        # Check if adding the word to the current line would exceed the max line length
        if len(current_line) + len(word) > max_chars:
            # If it would exceed, append the current line to lines and start a new one
            lines.append(current_line)
            current_line = word
        else:
            # If the current line is not empty, add a space before the word
            if current_line:
                current_line += ' '
            current_line += word
    # Append any remaining text as the last line
    if current_line:
        lines.append(current_line)

    return lines

def write_debug_image(image: Image):
        cwd = os.getcwd()
        # Create the 'debug_images' directory if it doesn't exist
        debug_images_dir = os.path.join(cwd, 'debug_images')
        os.makedirs(debug_images_dir, exist_ok=True)

        # Generate a timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Create the filename with the timestamp
        filename = f'debug_image_{timestamp}.png'

        # Construct the full file path
        file_path = os.path.join(debug_images_dir, filename)

        # Save the image to disk as a PNG file
        image.save(file_path, 'PNG')

def split_string_every_n_chars(input_string, n):
    return [input_string[i:i+n] for i in range(0, len(input_string), n)]

def generate_subframe(text: str, font: ImageFont, font_size: Tuple[int, int], canvas_size: Tuple[int, int], fill: Tuple[int, int, int]) -> Image:
    # Wrap text into lines that fit the canvas width

    text = text.encode('latin-1', 'ignore').decode('latin-1')

    lines = wrap_text(text, font, font_size, canvas_size[0])

    # Calculate the total height needed for the wrapped text
    total_height = (len(lines) + 2) * font_size[1]
    
    # Create a new image with the calculated width and height
    base = PILImage.new("RGB", (canvas_size[0], total_height))
    draw = ImageDraw.Draw(base)

    text_pos_y = 0

    # Draw each line of text
    for line in lines:
        draw.text((0, text_pos_y), line, font=font, fill=fill)
        text_pos_y += font_size[1]  # Move to the next line position
    
    return base

def append_subframes(frames: list[Image]) -> Image:
    width = frames[0].width
    total_height = sum(frame.height for frame in frames)
    append_image = PILImage.new('RGB', (width, total_height))

    current_height = 0

    for frame in frames:
        append_image.paste(frame, (0, current_height))
        current_height += frame.height
    
    return append_image