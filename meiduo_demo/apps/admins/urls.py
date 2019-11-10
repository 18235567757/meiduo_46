from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from apps.admins.views import spce, static, users, options, images, orders, sku, spus

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
    # 获取三级类别
    url(r'^skus/categories/$', sku.SKUView.as_view(({'get': 'simple'}))),
    # 获取sku规格数据
    url(r'goods/(?P<pk>\d+)/specs/$', sku.SKUView.as_view(({'get': 'specs'})))
]

router = DefaultRouter()
# 规格表路由
router.register('goods/specs', spce.SpecView, base_name='specs')
# 规格选项表路由
router.register('specs/options', options.OptionView, base_name='options')
# 图片展示路由
router.register('skus/images', images.SKUImageView, base_name='images')
# 订单路由
router.register('orders', orders.OrderInfoView, base_name='orders')
# 商品sku路由
router.register('skus', sku.SKUView, base_name='skus')
# 商品SPU路由
router.register('goods', spus.SPUView, base_name='goods')
urlpatterns += router.urls
