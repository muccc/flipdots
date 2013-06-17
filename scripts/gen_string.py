import Image, ImageFont, ImageDraw, sys

IMG_SIZE = (40, 16)
FONT_SIZE = 12
FONT_OFFSET= (2,2)

C_BLACK = (0, 0, 0)
C_WHITE = (255, 255, 255)

STRING = "fnord"

if len(sys.argv) > 1:
    STRING = sys.argv[1]

image = Image.new("RGBA", IMG_SIZE, C_BLACK)
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()
draw.text(FONT_OFFSET, STRING, font=font, fill=C_WHITE)

#image.save("out.png")

imgmap = []
for pixel in image.getdata():
    r, g, b, a = pixel
    if r == 255:
        imgmap.append(1)
    else:
        imgmap.append(0)

print imgmap

