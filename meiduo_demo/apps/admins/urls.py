from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from . import views
urlpatterns = [
    # 后台登陆
    url(r'^authorizations/', obtain_jwt_token),
    # 用户总数统计
    url(r'^statistical/total_count/', views.UserTotalCountView.as_view()),
    # 日增用户统计
    url(r'^statistical/day_increment/$', views.UserDayCountView.as_view()),
    # 日下单用户统计
    url(r'^statistical/day_orders/$', views.UserDayOrdersCountView.as_view()),
    # 日活跃用户统计
    url(r'^statistical/day_active/$', views.UserDayActiveCountView.as_view()),
    # 月增用户统计
    url(r'^statistical/month_increment/$', views.UserMonthCountView.as_view()),
    # 日分类商品的访问量
    url(r'statistical/goods_day_views/$', views.GoodsCountView.as_view()),
]