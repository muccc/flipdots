import cairo


def get_size(text, font_name, font_size):
    width, height = 1,1

    surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
    cr = cairo.Context(surface)
    cr.scale(1,1)

    fo = cairo.FontOptions()
    fo.set_antialias(cairo.ANTIALIAS_NONE)

    utf8 = text

    cr.select_font_face(font_name,
                        cairo.FONT_SLANT_NORMAL,
                        cairo.FONT_WEIGHT_NORMAL)
    cr.set_font_options(fo)

    cr.set_font_size(font_size)
    #print(cr.text_extents(utf8))
    return cr.text_extents(utf8)[2:4]

if __name__ == '__main__':
    print get_size("cairo", "sans", 12)

