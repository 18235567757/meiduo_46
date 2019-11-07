from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from apps.admins.seriailizer.spce import SPUSpceSerializer,SPUSerializer
from apps.admins.utils import pagenum
from apps.goods.models import SPUSpecification,SPU


class SpecView(ModelViewSet):

    # 指定序列化器
    serializer_class = SPUSpceSerializer
    # 指定查询结果集
    queryset = SPUSpecification.objects.all()
    # 指定分页器
    pagination_class = pagenum

    # 自定义获取SPU商品信息
    def simple(self, request):
        # 查询spu表
        data = SPU.objects.all()
        # 序列化返回
        ser = SPUSerializer(data, many=True)

        return Response(ser.data)