from django.db import models

class Video(models.Model):
    name = models.CharField(max_length=3000)
    duration = models.IntegerField()
    pastips = models.CharField(max_length=10000, default = "")
    vidid = models.CharField(max_length=15, default = "")
    def __unicode__(self): 
        return self.name
    def initialize(self):
        for i in range(0, self.duration * 1):
            f = Frame(index = i, value = 1, video = self)
            f.save()
            g = FrameEqualizer(index = i, value = 1, video = self)
            g.save()
    def gettotalview(self):
        return len(self.pastips) / 14

class Frame (models.Model):
    index = models.IntegerField(default = 0)
    value = models.DecimalField(max_digits=5, decimal_places=2)
    video = models.ForeignKey(Video)
    def __unicode__(self): 
        return str(self.index)

class FrameEqualizer(models.Model):
    index = models.IntegerField(default = 0)
    value = models.DecimalField(max_digits=5, decimal_places=2)
    video = models.ForeignKey(Video)
    def __unicode__(self): 
        return str(self.index)

class Summary(models.Model):
    fullvid = models.ForeignKey(Video)
    method = models.IntegerField(default = 0)
    summarizedseconds = models.CharField(max_length=1500)
    def __unicode__(self): 
        return "summary"

class Viewer(models.Model):
    ip = models.CharField(max_length=100)
    highestframe = models.IntegerField(default = 1)
    unread = models.BooleanField(default = True)
    isactive = models.BooleanField(default = True)
    latestresponsetime = models.IntegerField(default = 0)
    prevtime = models.IntegerField(default=-1)
    timehistory = models.CharField(max_length=5000)
    def __unicode__(self):
        return self.ip

