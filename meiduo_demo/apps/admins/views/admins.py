from django.contrib.auth.models import Group
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.admins.seriailizer.admins import AdminSerializers
from apps.admins.seriailizer.groups import GroupSerializer
from apps.admins.utils import pagenum
from apps.users.models import User


class AdminView(ModelViewSet):

    serializer_class = AdminSerializers

    queryset = User.objects.filter(is_staff=True)

    pagination_class = pagenum

    def group(self, request):

        data = Group.objects.all()

        ser = GroupSerializer(data, many=True)

        return Response(ser.data)
