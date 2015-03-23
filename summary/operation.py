from summary.models import Video, Frame, Summary, FrameEqualizer, Viewer
from summary.mathtool import *
from decimal import *

def validtime (time, prevtime, endtime):
	if time >= endtime or time == 0:
		return False
	elif time != prevtime:
		return 1
	else:
		return False

def pickbesttime():
	if Video.objects.all()[0].gettotalview() <= 10:
		return True
	summary = Summary.objects.all()[0]
	mean_base = float(meanvalue_base())
	dev_base = standarddeviation_base(mean_base)
	base = mean_base - 0.5 * dev_base
	mean = meanvalue()
	dev = standarddeviation(mean)
	minimum = float(mean) + 1.3 * dev
	segment = picklinkedframes(base, minimum)
	summary.summarizedseconds = segment
	summary.save()

def equalizerupdate():
	duration = Video.objects.all()[0].duration
	viewers = Viewer.objects.filter(unread = True)
	import time
	if len(viewers) == 0:
		return False
	for i in viewers:
		diff = time.gmtime().tm_sec-i.latestresponsetime
		if diff >6 or diff < -6:
			#frames where ppl left should be punished, but only those where ppl are not on rewind
			if (i.prevtime > 5) and (i.prevtime + 4 < Video.objects.all()[0].duration):
				for k in range(i.prevtime - 5,i.prevtime + 4):
					eq = FrameEqualizer.objects.all()[k]
					eq.value += Decimal('1')
					eq.save()
			for k in range(i.highestframe -1):
				if k == duration:
					break;
				eq = FrameEqualizer.objects.all()[k]
				eq.value += Decimal('1')
				eq.save()
			i.unread = False
			i.save()

def pseudoframe(time, viewer):
	vid = Video.objects.all()[0]
	count = vid.pastips.count(viewer.ip) - 1
	time = int(time)
	frame = Frame.objects.filter(index=time)[0]
	frame.value = int(frame.value + 1 * int(2**count))/1.0
	frame.save()

def reset():
	vid = Video.objects.all()[0]
	for i in range(0, vid.duration):
		n = Frame.objects.all()[i]
		n.value = 1
		n.save()
		n = FrameEqualizer.objects.all()[i]
		n.value = 1
		n.save()
	#redoing the equalizer
	for i in Viewer.objects.all():
		i.unread = True
		i.save()
	equalizerupdate()
	#redoing the frame
	for i in Viewer.objects.all():
		myStr = i.timehistory.split('\n')
		for k in myStr:
			if k != "":
				pseudoframe(k, i)