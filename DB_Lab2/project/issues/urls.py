from django.conf.urls import url

from . import views

app_name = 'issues'
urlpatterns = [
    url(r'^$', views.list_issues, name='index'),
    url(r'^create$', views.issue_create, name='create'),
    url(r'^(?P<issue_id>[0-9]+)/$', views.issue_view, name='view'),
    url(r'^user/(?P<user_id>[0-9]+)/$', views.view_user, name='view_user'),
    url(r'^(?P<issue_id>[0-9]+)/delete$', views.issue_delete, name='delete'),
    url(r'^reload_db$', views.reload_db, name='reload_db')
]
