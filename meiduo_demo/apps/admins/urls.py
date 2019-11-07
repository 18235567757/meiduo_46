from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from apps.admins.views import static
from apps.admins.views import users
urlpatterns = [
    # 后台登陆
    url(r'^authorizations/', obtain_jwt_token),
    # 用户总数统计
    url(r'^statistical/total_count/', static.UserTotalCountView.as_view()),
    # 日增用户统计
    url(r'^statistical/day_increment/$', static.UserDayCountView.as_view()),
    # 日下单用户统计
    url(r'^statistical/day_orders/$', static.UserDayOrdersCountView.as_view()),
    # 日活跃用户统计
    url(r'^statistical/day_active/$', static.UserDayActiveCountView.as_view()),
    # 月增用户统计
    url(r'^statistical/month_increment/$', static.UserMonthCountView.as_view()),
    # 日分类商品的访问量
    url(r'statistical/goods_day_views/$', static.GoodsCountView.as_view()),
    # 用户管理
    url(r'^users/$', users.UserView.as_view()),
]