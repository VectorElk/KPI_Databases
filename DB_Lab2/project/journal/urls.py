from django.conf.urls import url

from . import views

app_name = 'journals'
urlpatterns = [
    url(r'^$', views.main, name='index'),
    url(r'^create$', views.add, name='create'),
    url(r'^(?P<issue_id>[0-9A-Za-z]+)/$', views.main, name='view'),
]