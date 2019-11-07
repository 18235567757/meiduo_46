from rest_framework import serializers
from apps.goods.models import GoodsVisitCount


class GoodsCountSerializers(serializers.ModelSerializer):

    category = serializers.StringRelatedField(read_only=True)

    class Mate:
        model = GoodsVisitCount
        fields = ('category', 'count')
