
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

def getFontSize(rowHeight):
	if rowHeight == 48 or rowHeight == 47:
		return 33
	if rowHeight == 46 or rowHeight == 45:
		return 32
	if rowHeight == 44 or rowHeight == 43:
		return 31
	if rowHeight == 42:
		return 30
	if rowHeight == 41:
		return 29
	if rowHeight == 40:
		return 28
	if rowHeight == 39:
		return 27
	if rowHeight == 38 or rowHeight == 37:
		return 26
	if rowHeight == 36 or rowHeight == 35:
		return 25
	if rowHeight == 34:
		return 24
	if rowHeight == 33:
		return 23
	if rowHeight == 32 or rowHeight == 31:
		return 22
	if rowHeight == 30 or rowHeight == 29:
		return 21
	if rowHeight == 28:
		return 19
	if rowHeight == 27:
		return 19
	if rowHeight == 26:
		return 19
	if rowHeight == 25:
		return 18
	if rowHeight == 24 or rowHeight == 23:
		return 17
	if rowHeight == 22:
		return 16
	if rowHeight == 21:
		return 15
	if rowHeight == 20:
		return 14
	if rowHeight < 30:
		return rowHeight-6
	return 26