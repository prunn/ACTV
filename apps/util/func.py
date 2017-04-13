# UNITS CONVERSION
def millisToString(millis):
    hours, x = divmod(int(millis), 3600000)
    mins, x = divmod(x, 60000)
    secs, x = divmod(x, 1000)
    return "%d.%03d" % (secs, x) if mins == 0 else "%d:%02d.%03d" % (mins, secs, x)


# COLOR CONVERSION
def rgb(color, a=1, bg=False):
    r = color[0] / 255
    g = color[1] / 255
    b = color[2] / 255
    if not bg:
        return r, g, b, a
    else:
        return r, g, b


def getFontSize(row_height):
    if row_height == 50 or row_height == 49:
        return 34
    if row_height == 48 or row_height == 47:
        return 33
    if row_height == 46 or row_height == 45:
        return 32
    if row_height == 44 or row_height == 43:
        return 31
    if row_height == 42:
        return 30
    if row_height == 41:
        return 29
    if row_height == 40:
        return 28
    if row_height == 39:
        return 27
    if row_height == 38 or row_height == 37:
        return 26
    if row_height == 36 or row_height == 35:
        return 25
    if row_height == 34:
        return 24
    if row_height == 33:
        return 23
    if row_height == 32 or row_height == 31:
        return 22
    if row_height == 30 or row_height == 29:
        return 21
    if row_height == 28:
        return 19
    if row_height == 27:
        return 19
    if row_height == 26:
        return 19
    if row_height == 25:
        return 18
    if row_height == 24 or row_height == 23:
        return 17
    if row_height == 22:
        return 16
    if row_height == 21:
        return 15
    if row_height == 20:
        return 14
    if row_height < 30:
        return row_height - 6
    return 26
