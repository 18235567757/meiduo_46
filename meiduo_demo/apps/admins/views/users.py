from rest_framework.generics import ListCreateAPIView

from apps.admins.seriailizer.users import UserSerializers
from apps.admins.utils import pagenum
from apps.users.models import User


class UserView(ListCreateAPIView):

    serializer_class = UserSerializers

    queryset = User.objects.filter(is_staff=False)

    pagination_class = pagenum

    def get_queryset(self):
        # 根据keyword参数返回不同的查询集结果
        keyword = self.request.query_params.get('keyword')

        if keyword == '' or keyword is None:
            return User.objects.filter(is_staff=False)

        else:
            return User.objects.filter(is_staff=False, username__contains=keyword)






