from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.admins.seriailizer.orders import OrderInfoserializer
from apps.admins.utils import pagenum
from apps.orders.models import OrderInfo


class OrderInfoView(ModelViewSet):
    # 指定序列化器
    serializer_class = OrderInfoserializer
    # 指定查询结果集
    queryset = OrderInfo.objects.all()
    # 指定分页器
    pagination_class = pagenum
