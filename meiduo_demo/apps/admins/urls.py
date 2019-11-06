from django.conf.urls import url
from .utils import jwt_response_payload_handler
from . import views
urlpatterns = [
    url(r'^authorizations/', jwt_response_payload_handler),
    url(r'^statistical/total_count/', views.UserTotalCountView.as_view()),
    url(r'^statistical/day_increment/$', views.UserDayCountView.as_view()),
    url(r'^statistical/day_orders/$', views.UserDayOrdersCountView.as_view()),
    url(r'^statistical/month_increment/$', views.UserMonthCountView.as_view()),
]