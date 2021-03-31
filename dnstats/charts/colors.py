import colorsys


def get_color(color: int):
    """
    Given a integer create a color. This is to be used in loop. The colors will go around the color wheel. Then
    the saturation will change. Then the value (think brightness) will change.

    :param color: number of color to produce
    :return: the color produced in hex
    """
    color_string = str(color).zfill(3)
    h = 0.1 * int(color_string[2])
    s = 0.1 * (10 - int(color_string[1]))
    v = 0.1 * (10 - int(color_string[0]))
    color = colorsys.hsv_to_rgb(h, s, v)
    result = "#"
    for color_part in color:
        if color_part == 0.0:
            result += "00"
        else:
            result += str(hex(round(255 * color_part)).zfill(2)[2:])

    return result
