from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^oauth_callback/$', views.QQloginView.as_view(), name='qqlogin'),

]