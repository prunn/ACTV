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
    if r > 1:
        r = 1
    elif r < 0:
        r = 0
    if g > 1:
        g = 1
    elif g < 0:
        g = 0
    if b > 1:
        b = 1
    elif b < 0:
        b = 0
    if a > 1:
        a = 1
    elif a < 0:
        a = 0
    if not bg:
        return r, g, b, a
    else:
        return r, g, b


def getFontSize(row_height):
    if row_height == 70:
        return 54
    if row_height == 69:
        return 53
    if row_height == 68:
        return 52
    if row_height == 67:
        return 51
    if row_height == 66:
        return 50
    if row_height == 65:
        return 49
    if row_height == 64:
        return 48
    if row_height == 63:
        return 47
    if row_height == 62:
        return 46
    if row_height == 61:
        return 45
    if row_height == 60:
        return 44
    if row_height == 59:
        return 43
    if row_height == 58:
        return 42
    if row_height == 57:
        return 41
    if row_height == 56:
        return 40
    if row_height == 55:
        return 39
    if row_height == 54:
        return 38
    if row_height == 53:
        return 37
    if row_height == 52:
        return 36
    if row_height == 51:
        return 35
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
