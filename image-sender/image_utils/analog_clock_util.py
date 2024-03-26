from io import BytesIO
import PIL
import svgwrite
import datetime
import math
from wand.image import Image
from wand.color import Color
from PIL.Image import Image as PILImage
import PIL.Image

def get_clock_frame() -> PILImage:
    # Function to calculate the angle for the clock hands
    def calc_angle(hand, max_units):
        return 360 * (hand / max_units)

    # Get the current time
    now = datetime.datetime.now()
    hours = now.hour % 12 + now.minute / 60  # Adjust hours for 12-hour clock format
    seconds = now.second + now.microsecond / 1e6  # Include microseconds for smooth sweeping
    minutes = now.minute + seconds / 60
    

    # Calculate angles for clock hands
    hour_angle = calc_angle(hours, 12)
    minute_angle = calc_angle(minutes, 60)
    second_angle = calc_angle(seconds, 60)

    # Clock parameters
    clock_center = (150, 150)
    clock_radius = 138
    hour_hand_length = 0.55 * clock_radius
    minute_hand_length = 0.8 * clock_radius
    second_hand_length = 0.95 * clock_radius

    # Create a new SVG drawing
    dwg = svgwrite.Drawing('analog_clock.svg', size=(300, 300))

    # Draw clock circle with a specified stroke width
    dwg.add(dwg.circle(center=clock_center, r=clock_radius, stroke='green', fill='black', stroke_width=5))
    
    # Draw clock numbers in bold and purple
    for number in range(1, 13):
        angle = calc_angle(number, 12) - 90  # Offset by 90 degrees to start from 12 o'clock
        radian_angle = math.radians(angle)
        text_x = clock_center[0] + (clock_radius - 32) * math.cos(radian_angle) + 2
        text_y = clock_center[1] + (clock_radius - 32) * math.sin(radian_angle) + 14
        text_anchor = 'middle'
        # Use font-weight 'bold' and fill color 'purple' for the numbers
        dwg.add(dwg.text(str(number), insert=(text_x, text_y), font_size='42px', font_family='Arial', font_weight='bold', text_anchor=text_anchor, alignment_baseline='middle', fill='purple'))

    # Draw minute tick marks
    for minute in range(60):
        angle = calc_angle(minute, 60) - 90  # Offset by 90 degrees to start from 12 o'clock
        radian_angle = math.radians(angle)
        inner_tick_radius = clock_radius - 10  # Default radius where tick marks start (for 1-minute marks)
        outer_tick_radius = clock_radius  # Radius where tick marks end

        # Calculate the start and end points for the tick marks
        start_x = clock_center[0] + outer_tick_radius * math.cos(radian_angle)
        start_y = clock_center[1] + outer_tick_radius * math.sin(radian_angle)

        # Check if the tick mark is for a 5-minute interval
        if minute % 5 == 0:
            # Longer tick marks for every 5 minutes (hours)
            inner_tick_radius = clock_radius - 15  # Longer tick marks for 5-minute intervals
            end_x = clock_center[0] + inner_tick_radius * math.cos(radian_angle)
            end_y = clock_center[1] + inner_tick_radius * math.sin(radian_angle)
            dwg.add(dwg.line(start=(start_x, start_y), end=(end_x, end_y), stroke='green', stroke_width=4))
        else:
            # Shorter tick marks for minutes
            end_x = clock_center[0] + inner_tick_radius * math.cos(radian_angle)
            end_y = clock_center[1] + inner_tick_radius * math.sin(radian_angle)
            dwg.add(dwg.line(start=(start_x, start_y), end=(end_x, end_y), stroke='green', stroke_width=2))

    # Function to draw clock hands
    def draw_hand(center, length, angle, stroke, stroke_width):
        radian_angle = math.radians(angle - 90)  # Offset by 90 degrees to start from 12 o'clock
        end_x = center[0] + length * math.cos(radian_angle)
        end_y = center[1] + length * math.sin(radian_angle)
        dwg.add(dwg.line(start=center, end=(end_x, end_y), stroke=stroke, stroke_width=stroke_width))

    # Draw clock hands with specified colors for hour and minute hands
    draw_hand(clock_center, hour_hand_length, hour_angle, stroke='green', stroke_width=4)
    draw_hand(clock_center, minute_hand_length, minute_angle, stroke='green', stroke_width=3)
    draw_hand(clock_center, second_hand_length, second_angle, stroke='red', stroke_width=2)

    svg_data = dwg.tostring()

    # Read the SVG data with Wand and convert it to a PNG blob
    with Image(blob=svg_data.encode('utf-8'), resolution=128, background=Color('black')) as img:
        img.format = 'png'
        img.resize(128, 128)
        
        # Save PNG to a blob
        png_blob = img.make_blob('png')

    png_stream = BytesIO(png_blob)
    pil_image = PIL.Image.open(png_stream)
    return pil_image