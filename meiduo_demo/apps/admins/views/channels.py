from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.goods.models import GoodsChannel, GoodsChannelGroup, GoodsCategory
from apps.admins.seriailizer.channels import ChannelsSerializer, GroupSerializer, GoodsCategorySerializer
from apps.admins.utils import pagenum


class ChannelsView(ModelViewSet):
    serializer_class = ChannelsSerializer

    queryset = GoodsChannel.objects.all()

    pagination_class = pagenum

    # 频道组选项展示
    def channel_types(self, request):
        data = GoodsChannelGroup.objects.all()

        ser = GroupSerializer(data, many=True)

        return Response(ser.data)

    # 商品一级分类展示
    def categories(self, request):
        data = GoodsCategory.objects.all()

        ser = GoodsCategorySerializer(data, many=True)

        return Response(ser.data)
