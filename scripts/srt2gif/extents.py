from math import pi
import cairo


def draw(cr, width, height):
    fo = cairo.FontOptions()
    fo.set_antialias(cairo.ANTIALIAS_NONE)
    cr.set_line_width(0.04)

    utf8 = "cairo"

    cr.select_font_face("Sans",
                        cairo.FONT_SLANT_NORMAL,
                        cairo.FONT_WEIGHT_NORMAL)
    cr.set_font_options(fo)

    cr.set_font_size(12)
    x_bearing, y_bearing, width, height, x_advance, y_advance = \
        cr.text_extents(utf8)
    print(cr.text_extents(utf8))
    x = 40 - (width / 2 + x_bearing)
    y = 40 - (height / 2 + y_bearing)

    cr.move_to(x, y)
    cr.show_text(utf8)

width, height = 96, 80 

surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
cr = cairo.Context(surface)
cr.scale(1,1)
cr.set_source_rgb(1, 1, 1)
cr.fill()
draw(cr, width, height)
surface.write_to_png("txt.png")

