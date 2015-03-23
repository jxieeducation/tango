from cmath import sqrt
from summary.models import Video, Frame, Summary, FrameEqualizer, Viewer
from decimal import *

def findip (request):
	#request.META['REMOTE_ADDR'] = request.META['HTTP_X_REAL_IP']
	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		ip = x_forwarded_for.split(',')[0]
	else:
		ip = request.META.get('REMOTE_ADDR')
	return ip

def stringtoseconds(thestring):
	secondslist = []
	startindex, endindex = 0,0
	s, p = 0, 0
	while "to" in thestring:
		middleindex = thestring.index("to")
		s = int(thestring[startindex:middleindex])
		startindex = middleindex + 2
		
		if p == 0:
			secondslist += [(0,s)]
		else:
			secondslist += [(p, s)]

		endindex = thestring.index(",")
		p = int(thestring[startindex:endindex])
		
		startindex = endindex + 1
		if len(thestring) > startindex:
			thestring = thestring[startindex:]
			startindex, endindex = 0,0
		else:
			secondslist += [(p, -99)]
			thestring = ""		
	return secondslist

def meanvalue_base():
	total = 0
	for i in range(Video.objects.all()[0].duration):
		total += Frame.objects.all()[i].value 
	return total / Video.objects.all()[0].duration

def standarddeviation_base(mean):
	total = 0
	for i in range(Video.objects.all()[0].duration):
		total += (float(Frame.objects.all()[i].value) - mean)
	return float(sqrt (total / Video.objects.all()[0].duration).real)

def meanvalue():
	total = 0
	for i in range(Video.objects.all()[0].duration):
		total += Frame.objects.all()[i].value / FrameEqualizer.objects.all()[i].value
	return total / Video.objects.all()[0].duration

def standarddeviation(mean):
	total = 0
	for i in range(Video.objects.all()[0].duration):
		total += (Frame.objects.all()[i].value / FrameEqualizer.objects.all()[i].value - mean)
	return float(sqrt (total / Video.objects.all()[0].duration).real)

def abovevalue(minimum, count = 0, upper = 3, lower = 3.5, start = 0, end = Video.objects.all()[0].duration):
	array = []
	duration = end-start
	for i in range(start, end):
		if Frame.objects.all()[i].value > minimum:
			array += [i]
	return array

	#if len(array) > duration/upper:
	#	return abovevalue (minimum*1.1, count + 1, upper, lower, start, end)
	#elif len(array) > duration/lower:
	#	return array
	#else:
	#	return abovevalue (minimum*0.9 , count + 1, upper, lower, start, end)

def balancedvaluehelper (array, minimum, count = 0, length = 0, upper = 6, lower = 9):
	thearray = []
	duration = len(array)
	for i in range(0, duration):
		val = array[i]
		if Frame.objects.all()[val].value / FrameEqualizer.objects.all()[val].value > minimum:
			thearray += [val]
	#print len(array)
	if count == 25:
		return thearray
	if len(thearray) > length/upper:
		#print "top"
		return balancedvaluehelper (array, minimum*1.054, count + 1, length)
	elif len(thearray) > length/lower:
		return thearray
	else:
		#print "low"
		return balancedvaluehelper (array, minimum*0.95, count + 1, length)


def balancedvalue (array, minimum):
	balancedarray = []
	duration = Video.objects.all()[0].duration
	token = duration / 45

	for i in range(0, token):
		temparray = []
		#print i
		for k in array:
			if (k >= (1 + (duration/token) * i)) and (k <= (1 + (duration/token) * (i + 1))):
				temparray += [k]
		if len(temparray) <= duration * 0.008:
			balancedarray += temparray
		else:
			print "start"
			print temparray
			newarray = balancedvaluehelper(temparray, minimum, 0, len(temparray))
			print "end"
			print newarray
			balancedarray += newarray
	return balancedarray

def linger(thevalue, plus_or_minus, themax, threshold = Decimal('0.3')):
	changed = False
	count = 1
	endvalue = 0
	oldbase = Frame.objects.all()[thevalue].value / FrameEqualizer.objects.all()[thevalue].value
	newbase = oldbase
	oldpercent = 0
	currentpercent = 0
	while count <= themax:
		if plus_or_minus:
			tempvalue = thevalue + count
		else:
			tempvalue = thevalue - count
		newbase = Frame.objects.all()[tempvalue].value / FrameEqualizer.objects.all()[tempvalue].value
		currentpercent = (newbase - oldbase) / oldbase
		if oldpercent - currentpercent > threshold:
			endvalue = tempvalue
			if oldpercent == 0:
				oldpercent = currentpercent
				changed = True
			elif (oldpercent - currentpercent > oldpercent * Decimal('2.0')):
				if changed:
					oldpercent = currentpercent				
		oldbase = newbase 
		count += 1
	#print changed, thevalue, endvalue
	if changed:
		return endvalue
	elif threshold >= Decimal('0.03'):
		return linger(thevalue, plus_or_minus, themax, threshold - Decimal('0.02'))
	else:
		return thevalue

def postlingervalue (thevalue):
	duration = Video.objects.all()[0].duration
	themax = int(duration * 0.05)
	if thevalue + themax >= duration:
		themax = duration - thevalue - 1
	return linger (thevalue, True, themax)
	 
def prelingervalue (thevalue):
	duration = Video.objects.all()[0].duration
	themax = int(duration * 0.05)
	if thevalue - themax < 0:
		themax = thevalue 
	return linger (thevalue, False, themax)

def linkvalues (index, array, gap = 0.03):
	originalindex = index
	count = 0
	endindex = index
	duration = Video.objects.all()[0].duration
	while (index+1 < len(array)) and (array[index] + duration * gap >= array[index + 1]):
		endindex = index
		count += 1
		index += 1
	if count == 0:
		return endindex
	return endindex + 1

#2nd way of creating a summary
def picklinkedframes(base, minimum):
	segment = ""
	mynum = 1
	thearray = []
	thearray = abovevalue (base)
	print "base"
	print thearray, len(thearray)

	array = []
	array += balancedvalue(thearray, minimum)

	print array, len (array)
	
	index, oldindex = 0, 0
	hasdiscardedtime = False
	tempstring = ""
	k = 0
	while index < len(array):
		k = linkvalues (index, array, 0.08)
		#print(array[index], array[k])
		if k != index:
			thelinger = prelingervalue (array[index])
			#disabled
			if thelinger <= oldindex and oldindex != 0:
				if hasdiscardedtime == True:
					tempstring = tempstring[:tempstring.index("to") + 2]
				else:
					segment = segment[:segment.rindex("to") + 2]
			else:
				if thelinger == 0:
					thelinger = 1
				tempstring = ""
				tempstring += str(thelinger)
				tempstring += "to"
				originalindex = thelinger
			index = k

			thelinger = postlingervalue(array[index])
			tempstring += str(thelinger)
			tempstring += ","
			oldindex = thelinger

			if thelinger - originalindex > Video.objects.all()[0].duration * 0.01:
				segment += tempstring
				hasdiscardedtime = False
			else:
				hasdiscardedtime = True
		index += 1
	print segment
	return segment