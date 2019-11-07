from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.admins.seriailizer.images import SKUImageSerializer, SKUSerializer
from apps.admins.utils import pagenum
from apps.goods.models import SKUImage, SKU


class SKUImageView(ModelViewSet):
    # 指定序列化器
    serializer_class = SKUImageSerializer
    # 指定查询结果集
    queryset = SKUImage.objects.all()
    # 指定分页器
    pagination_class = pagenum

    # 自定义获取图片信息
    def simple(self, request):
        # 查询图片表
        data = SKU.objects.all()
        # 序列化返回
        ser = SKUSerializer(data, many=True)

        return Response(ser.data)