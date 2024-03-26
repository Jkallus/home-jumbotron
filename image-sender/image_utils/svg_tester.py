import svgwrite
import datetime
import math
from wand.image import Image
from wand.color import Color

# Function to calculate the angle for the clock hands
def calc_angle(hand, max_units):
    return 360 * (hand / max_units)

# Get the current time
now = datetime.datetime.now()
hours = now.hour % 12 + now.minute / 60  # Adjust hours for 12-hour clock format
minutes = now.minute
seconds = now.second

# Calculate angles for clock hands
hour_angle = calc_angle(hours, 12)
minute_angle = calc_angle(minutes, 60)
second_angle = calc_angle(seconds, 60)

# Clock parameters
clock_center = (150, 150)
clock_radius = 135
hour_hand_length = 0.5 * clock_radius
minute_hand_length = 0.7 * clock_radius
second_hand_length = 0.9 * clock_radius

# Create a new SVG drawing
dwg = svgwrite.Drawing('analog_clock.svg', size=(300, 300))

# Draw clock circle with a specified stroke width
dwg.add(dwg.circle(center=clock_center, r=clock_radius, stroke='green', fill='none', stroke_width=7))

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

# Draw clock numbers in bold and purple
for number in range(1, 13):
    angle = calc_angle(number, 12) - 90  # Offset by 90 degrees to start from 12 o'clock
    radian_angle = math.radians(angle)
    text_x = clock_center[0] + (clock_radius - 20) * math.cos(radian_angle) + 2
    text_y = clock_center[1] + (clock_radius - 20) * math.sin(radian_angle) + 14
    text_anchor = 'middle'
    # Use font-weight 'bold' and fill color 'purple' for the numbers
    dwg.add(dwg.text(str(number), insert=(text_x, text_y), font_size='36px', font_family='Arial', font_weight='bold', text_anchor=text_anchor, alignment_baseline='middle', fill='purple'))

# # Save the drawing to a file
# dwg.save()
    
svg_data = dwg.tostring()

# Read the SVG data with Wand and convert it to a PNG blob
with Image(blob=svg_data.encode('utf-8'), resolution=128) as img:
    img.format = 'png'
    img.resize(128, 128)
    
    # Save PNG to a blob
    png_blob = img.make_blob('png')

# Now `png_blob` contains the binary data of the PNG image.
# You can write it to a file or use it as needed.
with open('analog_clock.png', 'wb') as out_file:
    out_file.write(png_blob)
