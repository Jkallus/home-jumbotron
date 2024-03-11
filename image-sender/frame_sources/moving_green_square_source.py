from PIL import Image, ImageDraw
from frame_sources.frame_source import FrameSource


class MovingSquareSource(FrameSource):
    def __init__(self):
        super().__init__("Moving Green Square")
        self.square_x_position = 31
        self.square_y_position = 20
        self.movement_direction = 1 # 1 for right, -1 for left
        

    def create_frame(self) -> Image:
        # Set square properties and image size
        square_size = 4
        square_color = (0, 255, 0)  # Green color in RGB
        background_color = (0, 0, 0)  # Black color in RGB

        # Create new image with black background
        img = Image.new("RGB", self.image_size, background_color)
        draw = ImageDraw.Draw(img)

        # Calculate the square's corner positions
        square_left = self.square_x_position
        square_right = square_left + square_size
        square_top = self.square_y_position
        square_bottom = square_top + square_size

        # Draw the green square
        draw.rectangle([(square_left, square_top), (square_right - 1, square_bottom - 1)], fill=square_color)

        # Update square_x_position for next call
        self.square_x_position += self.movement_direction

        # Check for horizontal bounds and change direction if necessary. 
        if square_right >= (self.image_size[0] - 1) and self.movement_direction > 0:
            self.movement_direction *= -1  # Reverse direction to left
        elif square_left <= 0 and self.movement_direction < 0:
            self.movement_direction *= -1  # Reverse direction to right

        return imgG