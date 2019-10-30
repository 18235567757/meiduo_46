from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^placeorder/$',views.PlaceOrderView.as_view(),name='placeorder'),
    url(r'^orders/commit/$',views.OrderCommitView.as_view(),name='ordercommit'),
    url(r'^orders/success/$',views.OrderSuccessView.as_view(), name='success'),
    url(r'^orders/info/(?P<page_num>\d+)/$', views.InfoView.as_view(), name='orders'),
    url(r'^orders/comment/$', views.CommentView.as_view()),
    url(r'^comment/(?P<sku_id>\d+)/$', views.CommentSKUView.as_view()),
]