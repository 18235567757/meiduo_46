from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from apps.admins.seriailizer.options import SpecificationOption,SPUOptionsSerializer
from apps.admins.seriailizer.spce import SPUSpceSerializer
from apps.admins.utils import pagenum
from apps.goods.models import SPUSpecification


class OptionView(ModelViewSet):

    # 指定序列化器
    serializer_class = SPUOptionsSerializer
    # 指定查询结果集
    queryset = SpecificationOption.objects.all()
    # 指定分页器
    pagination_class = pagenum

    # 自定义获取规格信息
    def simple(self, request):
        # 查询规格表
        data = SPUSpecification.objects.all()
        # 序列化返回
        ser = SPUSpceSerializer(data, many=True)

        return Response(ser.data)