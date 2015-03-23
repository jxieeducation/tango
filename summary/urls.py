from django.conf.urls import patterns, url

from summary import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^values/$', views.values, name='values'),
    url(r'^graph/$', views.graph, name='graph'),
    url(r'^summary/$', views.summary, name='summary'),
    url(r'^comments/$', views.comments, name="comments"),

    url(r'^ajax/$', views.theajax, name="ajax"),
    url(r'^startajax/$', views.startajax, name="startajax"),
    url(r'^comments/commentajax/$', views.commentajax, name="commentajax"),
)