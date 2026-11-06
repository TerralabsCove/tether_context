# Writes a US Letter PDF of tag36h11 tags at true size. Print at 100% and check the 10 cm bar.
import cv2, numpy as np, sys
from PIL import Image, ImageDraw, ImageFont
DPI = 300
px = lambda cm: cm / 2.54 * DPI
page = Image.new("L", (int(8.5 * DPI), int(11 * DPI)), 255)
draw = ImageDraw.Draw(page)
font = ImageFont.load_default(size=44)
d = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)
y = int(px(1.5))
draw.text((int(px(2)), y), "tag36h11 test sheet - print at 100%, no scaling", fill=0, font=font)
y += 70
draw.rectangle((int(px(2)), y, int(px(2)) + round(px(10)), y + 14), fill=0)
draw.text((int(px(2)), y + 22), "this bar must measure 10.0 cm", fill=0, font=font)
y += 110
for tag_id, cm in [(2, 8), (1, 5), (0, 3)]:
    cell = round(px(cm) / 8)        # 8 cells across the black square
    side = cell * 8
    tag = cv2.aruco.generateImageMarker(d, tag_id, side)
    page.paste(Image.fromarray(tag), (int(px(2)), y))
    draw.text((int(px(2)) + side + 50, y + side // 2 - 50),
              f"id {tag_id}\nblack square {side / DPI * 2.54:.2f} cm", fill=0, font=font)
    y += side + int(px(1.5))
page.point(lambda v: 255 if v > 127 else 0).convert("1", dither=Image.Dither.NONE).save(sys.argv[1], resolution=DPI)
