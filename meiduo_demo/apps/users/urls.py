from django.conf.urls import url
from . import views

urlpatterns = [

    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UsernameCountView.as_view(), name='usernamecontent'),
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view(), name='mobilecontent'),
    url(r'^login/$', views.LogView.as_view(), name='login'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    url(r'^center/$', views.UserCenterInfo.as_view(), name='center'),
    url(r'^emails/$', views.EmailView.as_view(), name='email'),
    url(r'^emailsactive/$', views.EmailActiveView.as_view(), name='emailsactive'),
    url(r'^address/$', views.AddressView.as_view(), name='address'),



]


