from django.contrib.auth.models import Permission, ContentType
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.admins.seriailizer.permissions import PermissionSerializer, ContentTypeSerializer
from apps.admins.utils import pagenum


class PermissionView(ModelViewSet):
    # 指定序列化器
    serializer_class = PermissionSerializer
    # 指定查询结果集
    queryset = Permission.objects.all()
    # 指定分页器
    pagination_class = pagenum

    def simple(self, request):
        data = ContentType.objects.all()

        ser = ContentTypeSerializer(data, many=True)

        return Response(ser.data)
