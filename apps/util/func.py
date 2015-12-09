
# UNITS CONVERSION

def millisToString(millis):
	hours, x = divmod(int(millis), 3600000)
	mins, x  = divmod(x, 60000)
	secs, x  = divmod(x, 1000)
	return "%d.%03d" % (secs, x) if mins == 0 else "%d:%02d.%03d" % (mins, secs, x)


#-#####################################################################################################################################-#


# COLOR CONVERSION

def rgb(color, a = 1, bg = False):
	r = color[0] / 255
	g = color[1] / 255
	b = color[2] / 255
	if bg == False:
		return r, g, b, a
	else:
		return r, g, b