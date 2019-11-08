from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.admins.seriailizer.sku import SKUserializer, GoodsCategorySerializer, SPUSpecificationSerializer
from apps.admins.utils import pagenum
from apps.goods.models import SKU, GoodsCategory, SPU, SKUSpecification


class SKUView(ModelViewSet):
    # 指定序列化器
    serializer_class = SKUserializer
    # 指定查询结果集
    # queryset = SKU.objects.all()
    # 指定分页器
    pagination_class = pagenum

    # 重写get_queryset方法
    def get_queryset(self):

        keyword = self.request.query_params.get('keyword')

        if keyword == '' or keyword is None:
            # 返回所有数据
            return SKU.objects.all()
        else:
            # 返回查询数据
            return SKU.objects.filter(name__contains=keyword)

    # 获取三级分类的业务
    def simple(self, request):
        # 查询分类表获取三级分类
        data = GoodsCategory.objects.filter(subs=None)
        # 返回三级分类信息
        ser = GoodsCategorySerializer(data, many=True)
        return Response(ser.data)

    def specs(self, request, pk):
        """
        spu商品id

        :param request:
        :return:
        """
        # 根据spuid查询spu对象
        spu = SPU.objects.get(id=pk)
        # 根据spu获取规格信息
        specs = spu.specs.all()
        # 返回规格信息
        ser = SPUSpecificationSerializer(specs, many=True)

        return Response(ser.data)