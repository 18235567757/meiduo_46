from rest_framework.response import Response


# 自定义jwt认证方法
from apps.users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义jwt认证成功返回数据
    """
    return {
        'username': user.username,
        'id': user.id,
        'token': token,
    }

from rest_framework.pagination import PageNumberPagination


# 自定义分页器
class pagenum(PageNumberPagination):
    page_size_query_param = 'pagesize'

    max_page_size = 8

    def get_paginated_response(self, data):

        return Response({
            'counts': self.page.paginator.count,
            'lists': data,
            'page': self.page.number,
            'pages': self.page.paginator.num_pages,
            'pagesize': self.max_page_size

        })


