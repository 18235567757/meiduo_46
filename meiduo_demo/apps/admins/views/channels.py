from rest_framework.viewsets import ModelViewSet
from apps.goods.models import GoodsChannel
from apps.admins.seriailizer.channels import ChannelsSerializer
from apps.admins.utils import pagenum


class ChannelsView(ModelViewSet):

    serializer_class = ChannelsSerializer

    queryset = GoodsChannel.objects.all()

    pagination_class = pagenum

