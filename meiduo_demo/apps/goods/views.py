from datetime import timezone

from django import http
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.contens.utils import get_categories
from apps.goods.models import GoodsCategory, SKU, GoodsVisitCount
from apps.goods.utils import get_breadcrumb
from utils.response_code import RETCODE

class DetailVisitView(View):
    """详情页分类商品访问量"""

    def post(self, request, category_id):
        """记录分类商品访问量"""
        # 分类ID
        try:
            category = GoodsCategory.objects.get(id=category_id)
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

class DetailView(View):
    """商品详情页"""
    def get(self,request,sku_id):

        # 获取当前sku的信息
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return render(request, '404.html')

        # 查询商品频道分类
        categories = get_categories()
        # 查询面包屑导航
        breadcrumb = get_breadcrumb(sku.category)

        # 构建当前商品的规格键
        sku_specs = sku.specs.order_by('spec_id')
        sku_key = []
        for spec in sku_specs:
            sku_key.append(spec.option.id)
        # 获取当前商品的所有SKU
        skus = sku.spu.sku_set.all()
        # 构建不同规格参数（选项）的sku字典
        spec_sku_map = {}
        for s in skus:
            # 获取sku的规格参数
            s_specs = s.specs.order_by('spec_id')
            # 用于形成规格参数-sku字典的键
            key = []
            for spec in s_specs:
                key.append(spec.option.id)
            # 向规格参数-sku字典添加记录
            spec_sku_map[tuple(key)] = s.id
        # 获取当前商品的规格信息
        goods_specs = sku.spu.specs.order_by('id')
        # 若当前sku的规格信息不完整，则不再继续
        if len(sku_key) < len(goods_specs):
            return
        for index, spec in enumerate(goods_specs):
            # 复制当前sku的规格键
            key = sku_key[:]
            # 该规格的选项
            spec_options = spec.options.all()
            for option in spec_options:
                # 在规格参数sku字典中查找符合当前规格的sku
                key[index] = option.id
                option.sku_id = spec_sku_map.get(tuple(key))
            spec.spec_options = spec_options

        # 渲染页面
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'specs': goods_specs,
        }

        return render(request, 'detail.html', context)


class HotSKUView(View):
        # 热销排行展示
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




