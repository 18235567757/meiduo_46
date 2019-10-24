from datetime import timezone

from django import http
from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.goods.models import GoodsCategory, SKU, GoodsVisitCount
from apps.goods.utils import get_breadcrumb
from utils.response_code import RETCODE

class DetailVisitView(View):
    """详情页分类商品访问量"""

    def post(self, request, category_id):
        """记录分类商品访问量"""
        # 分类ID
        try:
            category = GoodsCategory.objects.filter(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseBadRequest('缺少必传参数')

        # 获取今天的日期
        from django.utils import timezone
        today = timezone.localdate()
        try:
            vc = GoodsVisitCount.objects.get(category=category, date=today)

        except GoodsVisitCount.DoesNotExist:
            GoodsVisitCount.objects.create(
                category=category,
                date=today,
                count=1
            )

            return http.JsonResponse({'code':RETCODE.OK, 'errmsg':'ok'})
        else:
            vc.count+=1
            vc.save()
            return http.JsonResponse({'code':RETCODE.OK, 'errmsg':'OK'})


class ListView(View):
    """商品列表页"""

    def get(self, request, category_id, page_num):
        """提供商品列表页"""
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return render(request, '404.html')
            # 尽量不要将表的信息,暴露出去
            # 排序字段是使用的查询字符串 ?sort=
            # default:以上架时间
            # hot   :热销 销量
            # price :价格
        breadcrumb = get_breadcrumb(category)

        sort = request.GET.get('sort')
        if sort == 'default':
            order_field = 'create_time'
        elif sort == 'hot':
            order_field = 'sales'
        else:
            order_field = 'price'

        data = SKU.objects.filter(category=category).order_by(order_field)

        from django.core.paginator import Paginator
        # 3.1创建分页对象
        paginator = Paginator(object_list=data, per_page=5)

        # per_page : 每页多少条数据

        # 3.2获取指定页面的数据
        page_data = paginator.page(page_num)

        # 3.3获取总页数
        total_page = paginator.num_pages

        context = {

            'breadcrumb': breadcrumb,  # 面包屑导航
            'sort': sort,  # 排序字段
            'category': category,  # 第三级分类
            'page_skus': page_data,  # 分页后数据
            'total_page': total_page,  # 总页数
            'page_num': page_num,  # 当前页码
        }
        return render(request, 'list.html', context)

# class DetailView(View):
#     """商品详情页"""
#
#     def get(self, request, sku_id):
#         """提供商品详情页"""
#         return render(request, 'detail.html')
class HotSKUView(View):

    def get(self, request, category_id):
        try:
            category = GoodsCategory.objects.filter(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.JsonResponse({'code':RETCODE.NODATAERR, 'errmsg':'没有收到数据'})
        skus = SKU.objects.filter(category=category, is_launched=True).order_by('-sales')[:2]

        hot_skus=[

        ]
        for sku in skus:
            hot_skus.append({
                'id': sku.id,
                'default_image_url': sku.default_image.url,
                'name': sku.name,
                'price': sku.price
            })

        return http.JsonResponse({'code':RETCODE.OK, 'errmsg':'ok', 'hot_skus':hot_skus})