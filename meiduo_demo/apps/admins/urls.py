from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from apps.admins.views import spce,static, users, options, images

from rest_framework.routers import DefaultRouter
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
    # 获取spu商品信息
    url(r'^goods/simple/$', spce.SpecView.as_view(({'get': 'simple'}))),
    # 获取商品规格信息
    url(r'^goods/specs/simple/$', options.OptionView.as_view(({'get': 'simple'}))),
    # 获取商品图片信息
    url(r'^skus/simple/$', images.SKUImageView.as_view(({'get': 'simple'}))),
]

router = DefaultRouter()
router.register('goods/specs', spce.SpecView, base_name='specs')
router.register('specs/options', options.OptionView, base_name='options')
router.register('skus/images', images.SKUImageView, base_name='images')
urlpatterns += router.urls
