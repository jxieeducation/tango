from django.shortcuts import render
from summary.models import Video, Frame, Summary, FrameEqualizer, Viewer
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from operation import validtime, pickbesttime, equalizerupdate
from mathtool import findip, stringtoseconds
import time

def index(request):
	context = {'url': Video.objects.all()[0].vidid}
	return render(request, 'index.html', context)

def values(request):
    equalizerupdate()
    #pickbesttime ()
    valueslist = []
    val1 =[]
    val2 = []
    for i in range(1, Video.objects.all()[0].duration):
        n = Frame.objects.all()[i].value
        m = FrameEqualizer.objects.all()[i].value
        val = float(n / m)
        valueslist += [val]
        val1 += [n]
        val2 += [m]
    context = {'num':val1, 'denom':val2, 'Frame':valueslist, 'counts':range(1, Video.objects.all()[0].duration)}
    return render(request, 'values.html', context)

def graph (request):
    valueslist = []
    val1 =[]
    val2 = []
    for i in range(1, Video.objects.all()[0].duration):
        n = Frame.objects.all()[i].value
        m = FrameEqualizer.objects.all()[i].value
        val = float(n / m)
        valueslist += [val]
        val1 += [n]
        val2 += [m]
    context = {'view': Video.objects.all()[0].gettotalview(),'Frame':valueslist, 'counts':range(1, Video.objects.all()[0].duration), 'num': val1, 'denom': val2}
    return render(request, 'graph.html', context)

def comments (request):
    #equalizerupdate()
    #pickbesttime ()
    context = {'url': Video.objects.all()[0].vidid}
    return render(request, 'comments.html', context)

def summary(request):
    #equalizerupdate()
    #pickbesttime ()
    sec = Summary.objects.all()[0].summarizedseconds
    finallist = stringtoseconds(sec)
    context = {'secondslist':finallist, 'list': sec, 'url': Video.objects.all()[0].vidid}
    return render(request, 'summary.html', context)

@csrf_exempt
def startajax(request):
    if request.method == 'POST' and request.is_ajax():
        n = Video.objects.all()[0]
        #ip address part
        ip = findip (request)
        viewer = Viewer()
        viewer.ip = ip
        n.pastips += ip
        n.pastips += " "
        n.save()
        viewer.save()
        return HttpResponse("success")
    else:
        return HttpResponse("Not authorized.")

@csrf_exempt
def theajax(request):
    if request.method == 'POST' and request.is_ajax():

        thetime = int(request.POST['time'])
        isactive = request.POST['active']

        vid = Video.objects.all()[0]

        #updates the viewer's highestframe
        ip = findip(request)

        k = Viewer.objects.filter(ip = ip)
        if not k:
            viewer = Viewer()
            viewer.ip = ip
            viewer.timehistory = ""
            viewer.highestframe = thetime
        else:
            viewer = k[len(k) - 1]
        
        viewer.latestresponsetime = time.gmtime().tm_sec
        if thetime > viewer.highestframe:
            viewer.highestframe = thetime
            viewer.save()
        if viewer.isactive == False and isactive ==True and thetime >= 4:
            for i in range(thetime - 3, thetime):
                n = Frame.objects.all()[i]    
                n.value += 1
                n.save()
        elif viewer.isactive == True and isactive == False and thetime >= 4:
            for i in range(thetime - 3, thetime):
                n = FrameEqualizer.objects.all()[i]    
                n.value += 1
                n.save()
        viewer.isactive = isactive

        #adds onto the Frame values
        prevtime = viewer.prevtime
        viewer.prevtime = thetime

        endtime = vid.duration

        if validtime(thetime, prevtime, endtime) and isactive == "true":
            viewer.timehistory = viewer.timehistory + str(thetime) + "\n"

            count = vid.pastips.count(ip) - 1
            #this means that the user went backwards
            if thetime < viewer.highestframe:
                count = int(count * 2)
            if count > 2: #8
                count = 2

            frame = Frame.objects.filter(index=thetime)[0]
            frame.value = int(frame.value + 1 * int(2**count))/1.0
            frame.save()

        viewer.save()
        return HttpResponse("success")
    else:
        return HttpResponse("Not authorized.")

@csrf_exempt
def commentajax(request):
    if request.method == 'POST' and request.is_ajax():
        thecomment = request.POST['thecomment']
        #print(thecomment)
        from commentparser import parsecomment
        n = parsecomment(thecomment)
        if n:
            length = Video.objects.all()[0].duration
            if n < length:
                count = 10
                if 10 + n >= length:
                    count = length - n - 1
                while count > 0:
                    #first
                    k = Frame.objects.all()[count + n]
                    k.value *= 1.1
                    k.save()
                    count -= 1
        return HttpResponse("success")
    else:
        return HttpResponse("Not authorized.")