def parsecomment(thestring):
	if ":" not in thestring:
		return False
	index = thestring.index(":")
	if index + 1 == len(thestring) or (not thestring[index + 1].isdigit()):
		return False
	higher, lower, bottom = 0, 0, 0
	if index - 2 >= 0 and ((thestring[index - 2].isdigit()) and (thestring[index - 1].isdigit())):
		higher = int(thestring[index-2:index])
	elif index - 1 >= 0 and (thestring[index - 1].isdigit()):
		higher = int(thestring[index-1])
	else:
		higher = 0

	if index + 2 < len(thestring) and ((thestring[index + 2].isdigit()) and (thestring[index + 1].isdigit())):
		lower = int(thestring[index+1:index+3])
	else:
		lower = int(thestring[index+1])
	lower += higher * 60

	#this checks if the time is actually hours:minutes:seconds
	if index + 5 < len(thestring) and ((thestring[index + 4].isdigit()) and (thestring[index + 5].isdigit())):
		bottom = int(thestring[index+4:index+6])
	elif index + 4 < len(thestring) and thestring[index + 4].isdigit():
		bottom = int(thestring[index+4])
	else:
		return lower
	bottom += lower * 60
	return bottom