from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.admins.seriailizer.spus import SPUSerializer
from apps.admins.utils import pagenum
from apps.goods.models import SPU


class SPUView(ModelViewSet):
    # 指定序列化器
    serializer_class = SPUSerializer
    # 指定查询结果集
    queryset = SPU.objects.all()
    # 指定分页器
    pagination_class = pagenum