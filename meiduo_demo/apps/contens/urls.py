from django.conf.urls import url

from apps.contens import views

urlpatterns = [
    url(r'^contens/$', views.IndexView.as_view(), name='index'),

]