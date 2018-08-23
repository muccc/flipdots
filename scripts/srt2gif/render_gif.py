import sys
import warnings
import cairo
import pysrt

FPS = 10
SLIDE_FRAMES = 3

class Drawer:
    def __init__(self, context, width, height):
        fo = cairo.FontOptions()
        fo.set_antialias(cairo.ANTIALIAS_NONE)
        context.set_font_options(fo)

        context.select_font_face("Sans",
                            cairo.FONT_SLANT_NORMAL,
                            cairo.FONT_WEIGHT_NORMAL)
        context.set_font_size(10)
        self.context = context
        self.width = width
        self.height = height
        self.text = []
        self._lines = 5
        self._line_height = self.height / self._lines

        self._sliding = False
        self._slide_frame = 0

    def draw_frame(self):
        self.context.set_source_rgb(0, 0, 0)
        self.context.rectangle(0, 0, width, height)
        self.context.fill()
        self.context.set_source_rgb(1, 1, 1)

        if self._sliding:
            self._slide_frame += 1
        if self._slide_frame >= SLIDE_FRAMES:
            self._sliding = False

        for i, line in enumerate(self.text[-self._lines-1:]):
            x_bearing, y_bearing, t_width, t_height, x_advance, y_advance = \
                self.context.text_extents(line)

            if t_width > self.width:
                warnings.warn("Text wider than surface")

            slide = self._slide_frame * (self._line_height / SLIDE_FRAMES)
            line_y = self._line_height * i - slide 
            x = - x_bearing
            y = - y_bearing + line_y

            self.context.move_to(x, y)
            self.context.show_text(line)
    
    def add_text(self, text):
        if self._sliding:
            warnings.warn("can't keep up, still animating previous text (%s)" % text)
        self.text.append(text)
        if len(self.text) <= self._lines:
            return 
        self._sliding = True
        self._slide_frame = 0

width, height = 96, 80 

surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
cr = cairo.Context(surface)
cr.scale(1,1)

drawer = Drawer(cr, width, height)

srt = pysrt.open(sys.argv[1])
lines = len(srt)

frame = 0
index = 0

post_frames = 0

while True:
    secs = frame / FPS
    now = {"seconds": secs}
    if index < lines:
        line = srt[index]

        if line.start <= now:
            drawer.add_text(line.text)
            index += 1
    else:
        # All lines are completed, now only let the animation finish
        if post_frames > SLIDE_FRAMES:
            break
        post_frames += 1

    drawer.draw_frame()
    surface.write_to_png("{:0>5}.png".format(frame))

    frame += 1
