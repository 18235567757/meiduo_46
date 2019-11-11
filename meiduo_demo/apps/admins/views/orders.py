from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from apps.admins.seriailizer.orders import OrderInfoserializer
from apps.admins.utils import pagenum
from apps.orders.models import OrderInfo


class OrderInfoView(ReadOnlyModelViewSet):
    # 指定序列化器
    serializer_class = OrderInfoserializer
    # 指定查询结果集
    queryset = OrderInfo.objects.all()
    # 指定分页器
    pagination_class = pagenum

    def get_queryset(self):

        keyword = self.request.query_params.get('keyword')

        if keyword == '' or keyword is None:
            return OrderInfo.objects.all()

        else:
            return OrderInfo.objects.filter(order_id__contains=keyword)

    def status(self, request, pk):
        try:
            order = OrderInfo.objects.get(order_id=pk)
        except:
            return Response({'error': '订单编号错误'}, status=400)
        status = request.data.get('status')

        order.status = status
        order.save()

        return Response({'status': status})
