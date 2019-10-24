from django.conf.urls import url

from apps.goods import views

urlpatterns = [
    url(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)/$', views.ListView.as_view(), name='list'),
    url(r'^hot/(?P<category_id>\d+)/$', views.HotSKUView.as_view(), name='hot'),
    url(r'^detail/(?P<sku_id>\d+)/$',views.DetailVisitView.as_view(), name='visit'),

]