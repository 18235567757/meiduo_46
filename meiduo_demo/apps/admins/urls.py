from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from apps.admins.views import spce, static, users, options, images, orders, sku, spus, brands, groups,permissions

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
    url(r'^goods/(?P<pk>\d+)/specs/$', sku.SKUView.as_view(({'get': 'specs'}))),
    # 获取品牌信息
    url(r'^goods/brands/simple/$', spus.SPUView.as_view(({'get': 'brand'}))),
    # 获取一级分类
    url(r'^goods/channel/categories/$', spus.SPUView.as_view(({'get': 'channel'}))),
    # 获取二级分类
    url(r'^goods/channel/categories/(?P<pk>\d+)/$', spus.SPUView.as_view(({'get': 'channel2'}))),
    # 上传图片
    url(r'^goods/images/$', spus.SPUView.as_view((({'post': 'images'})))),
    # 修改订单状态信息
    url(r'^orders/(?P<pk>\d+)/status/$', orders.OrderInfoView.as_view(({'put':'status'}))),
    #
    url(r'^goods/categories/$', brands.BrandView.as_view(({'get': 'categories'}))),
    #
    url(r'^permission/simple/$', groups.GroupView.as_view({'get': 'simple'})),

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
# 品牌路由
router.register('goods/brands', brands.BrandView, base_name='brands')
# 商品SPU路由   goods/(.*)
router.register('goods', spus.SPUView, base_name='goods')
# 权限路由
router.register('permission/perms', permissions.PermissionView, base_name='perms')
# 用户权限
router.register('permission/groups', groups.GroupView, base_name='groups')
urlpatterns += router.urls

