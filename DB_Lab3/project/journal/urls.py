from django.conf.urls import url

from . import views

app_name = 'journals'
urlpatterns = [
    url(r'^$', views.ListJournalsView.as_view(), name='index'),
    url(r'^create$', views.add, name='create'),
    url(r'^(?P<journal_id>[0-9A-Za-z]+)/$', views.JournalDetailView.as_view(), name='view'),
    url(r'^top_students', views.top_students, name='top_students'),
    url(r'^scholarship', views.scholarship, name='scholarship'),
    url(r'^avarage', views.avarage, name='avarage'),
    url(r'^sort', views.sort, name='sort')
]