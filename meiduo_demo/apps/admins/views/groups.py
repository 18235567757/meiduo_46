from django.contrib.auth.models import Group,Permission
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.admins.seriailizer.groups import GroupSerializer
from apps.admins.seriailizer.permissions import PermissionSerializer
from apps.admins.utils import pagenum


class GroupView(ModelViewSet):
    # 指定序列化器
    serializer_class = GroupSerializer
    # 指定查询结果集
    queryset = Group.objects.all()
    # 指定分页器
    pagination_class = pagenum

    def simple(self, request):
        data = Permission.objects.all()

        ser = PermissionSerializer(data, many=True)

        return Response(ser.data)